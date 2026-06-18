from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models import Character, DiscoveryAnswer, DiscoveryQuestion, FlowTypeEnum, Relationship, Story, User
from app.schemas.discovery import (
    DiscoveryAnswerCreate,
    DiscoveryAnswerResponse,
    DiscoveryAnswerUpdate,
    DiscoveryQuestionResponse,
)
from app.services.event_service import handle_question_answered

router = APIRouter()


def _validate_story(db: Session, story_id: UUID, user_id: UUID) -> None:
    if not db.query(Story).filter(Story.id == story_id, Story.user_id == user_id).first():
        raise HTTPException(status_code=404, detail="Story not found")


def _get_discovery_question(db: Session, question_id: UUID) -> DiscoveryQuestion:
    question = db.query(DiscoveryQuestion).filter(DiscoveryQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


def _validate_answer_target(db: Session, answer_in: DiscoveryAnswerCreate, question: DiscoveryQuestion) -> None:
    if question.flow_type == FlowTypeEnum.CHARACTER_DISCOVERY:
        if not answer_in.character_id:
            raise HTTPException(status_code=400, detail="character_id is required for character discovery questions")
        if (
            not db.query(Character)
            .filter(Character.id == answer_in.character_id, Character.story_id == answer_in.story_id)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Character not found in this story")
    elif question.flow_type == FlowTypeEnum.RELATIONSHIP_DISCOVERY:
        if not answer_in.relationship_id:
            raise HTTPException(
                status_code=400, detail="relationship_id is required for relationship discovery questions"
            )
        if (
            not db.query(Relationship)
            .filter(Relationship.id == answer_in.relationship_id, Relationship.story_id == answer_in.story_id)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Relationship not found in this story")


def _get_existing_answer(db: Session, answer_in: DiscoveryAnswerCreate) -> DiscoveryAnswer | None:
    if answer_in.character_id:
        return (
            db.query(DiscoveryAnswer)
            .filter(
                DiscoveryAnswer.character_id == answer_in.character_id,
                DiscoveryAnswer.question_id == answer_in.question_id,
            )
            .first()
        )
    if answer_in.relationship_id:
        return (
            db.query(DiscoveryAnswer)
            .filter(
                DiscoveryAnswer.relationship_id == answer_in.relationship_id,
                DiscoveryAnswer.question_id == answer_in.question_id,
            )
            .first()
        )
    return None


def _upsert_discovery_answer(db: Session, answer_in: DiscoveryAnswerCreate) -> DiscoveryAnswer:
    existing_answer = _get_existing_answer(db, answer_in)
    if existing_answer:
        existing_answer.selected_answer = answer_in.selected_answer
        existing_answer.custom_answer = answer_in.custom_answer
        db.commit()
        db.refresh(existing_answer)
        return existing_answer

    answer = DiscoveryAnswer(**answer_in.model_dump())
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.get("/questions", response_model=List[DiscoveryQuestionResponse])
def get_discovery_questions(flow_type: FlowTypeEnum = Query(...), db: Session = Depends(get_db)):
    questions = (
        db.query(DiscoveryQuestion)
        .filter(DiscoveryQuestion.flow_type == flow_type)
        .order_by(DiscoveryQuestion.order_index)
        .all()
    )
    return questions


@router.post("/answers", response_model=DiscoveryAnswerResponse)
def create_discovery_answer(
    answer_in: DiscoveryAnswerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _validate_story(db, answer_in.story_id, current_user.id)
    question = _get_discovery_question(db, answer_in.question_id)
    _validate_answer_target(db, answer_in, question)
    final_answer = _upsert_discovery_answer(db, answer_in)

    answer_val = final_answer.custom_answer or final_answer.selected_answer or ""
    unlocked = handle_question_answered(
        db,
        story_id=answer_in.story_id,
        question_text=question.question_text,
        answer_text=answer_val,
        character_id=answer_in.character_id,
        relationship_id=answer_in.relationship_id,
    )
    # We set unlocked_events dynamically on the response object
    # Pydantic will pick it up since the model allows extra/dynamic fields or we mapped it
    final_answer.unlocked_events = unlocked
    return final_answer


@router.get("/characters/{character_id}/answers", response_model=List[DiscoveryAnswerResponse])
def get_character_answers(
    character_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if (
        not db.query(Character)
        .join(Story)
        .filter(Character.id == character_id, Story.user_id == current_user.id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Character not found")
    answers = db.query(DiscoveryAnswer).filter(DiscoveryAnswer.character_id == character_id).all()
    return answers


@router.get("/relationships/{relationship_id}/answers", response_model=List[DiscoveryAnswerResponse])
def get_relationship_answers(
    relationship_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if (
        not db.query(Relationship)
        .join(Story)
        .filter(Relationship.id == relationship_id, Story.user_id == current_user.id)
        .first()
    ):
        raise HTTPException(status_code=404, detail="Relationship not found")
    answers = db.query(DiscoveryAnswer).filter(DiscoveryAnswer.relationship_id == relationship_id).all()
    return answers


@router.put("/answers/{answer_id}", response_model=DiscoveryAnswerResponse)
def update_discovery_answer(
    answer_id: UUID,
    answer_in: DiscoveryAnswerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = (
        db.query(DiscoveryAnswer)
        .join(Story)
        .filter(DiscoveryAnswer.id == answer_id, Story.user_id == current_user.id)
        .first()
    )
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    update_data = answer_in.model_dump(exclude_unset=True)
    if "selected_answer" in update_data:
        answer.selected_answer = update_data["selected_answer"]
    if "custom_answer" in update_data:
        answer.custom_answer = update_data["custom_answer"]

    db.commit()
    db.refresh(answer)

    from app.models.discovery import EventTypeEnum
    from app.services.event_service import create_event

    create_event(
        db,
        story_id=answer.story_id,
        character_id=answer.character_id,
        relationship_id=answer.relationship_id,
        event_type=EventTypeEnum.ANSWER_UPDATED,
        event_metadata={"answer_id": str(answer.id), "question_id": str(answer.question_id)},
    )

    from app.models.report import CharacterArchitectureReport, RelationshipArchitectureReport

    if answer.character_id:
        report = (
            db.query(CharacterArchitectureReport)
            .filter(CharacterArchitectureReport.character_id == answer.character_id)
            .first()
        )
        if report:
            report.is_stale = True
            report.stale_reason = "answer_updated"
            db.commit()
    elif answer.relationship_id:
        report = (
            db.query(RelationshipArchitectureReport)
            .filter(RelationshipArchitectureReport.relationship_id == answer.relationship_id)
            .first()
        )
        if report:
            report.is_stale = True
            report.stale_reason = "answer_updated"
            db.commit()

    return answer
