from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Character, DiscoveryAnswer, DiscoveryQuestion, FlowTypeEnum, Relationship, Story
from app.schemas.discovery import (
    DiscoveryAnswerCreate,
    DiscoveryAnswerResponse,
    DiscoveryQuestionResponse,
)

router = APIRouter()


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
def create_discovery_answer(answer_in: DiscoveryAnswerCreate, db: Session = Depends(get_db)):
    # Validate story
    if not db.query(Story).filter(Story.id == answer_in.story_id).first():
        raise HTTPException(status_code=404, detail="Story not found")

    # Validate question
    question = db.query(DiscoveryQuestion).filter(DiscoveryQuestion.id == answer_in.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Validate either character or relationship is provided based on flow_type
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

    # Upsert logic - if an answer already exists for this question + character/relationship combination, update it instead
    existing_answer = None
    if answer_in.character_id:
        existing_answer = (
            db.query(DiscoveryAnswer)
            .filter(
                DiscoveryAnswer.character_id == answer_in.character_id,
                DiscoveryAnswer.question_id == answer_in.question_id,
            )
            .first()
        )
    elif answer_in.relationship_id:
        existing_answer = (
            db.query(DiscoveryAnswer)
            .filter(
                DiscoveryAnswer.relationship_id == answer_in.relationship_id,
                DiscoveryAnswer.question_id == answer_in.question_id,
            )
            .first()
        )

    if existing_answer:
        existing_answer.selected_answer = answer_in.selected_answer
        existing_answer.custom_answer = answer_in.custom_answer
        db.commit()
        db.refresh(existing_answer)
        return existing_answer
    else:
        answer = DiscoveryAnswer(**answer_in.model_dump())
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer


@router.get("/characters/{character_id}/answers", response_model=List[DiscoveryAnswerResponse])
def get_character_answers(character_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Character).filter(Character.id == character_id).first():
        raise HTTPException(status_code=404, detail="Character not found")
    answers = db.query(DiscoveryAnswer).filter(DiscoveryAnswer.character_id == character_id).all()
    return answers


@router.get("/relationships/{relationship_id}/answers", response_model=List[DiscoveryAnswerResponse])
def get_relationship_answers(relationship_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Relationship).filter(Relationship.id == relationship_id).first():
        raise HTTPException(status_code=404, detail="Relationship not found")
    answers = db.query(DiscoveryAnswer).filter(DiscoveryAnswer.relationship_id == relationship_id).all()
    return answers
