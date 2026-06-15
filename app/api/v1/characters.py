from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Character, CharacterArchitectureReport, Story
from app.schemas.character import CharacterCreate, CharacterPulseResponse, CharacterResponse, CharacterUpdate
from app.schemas.report import (
    NarrativeConsequenceResponse,
    PatternEmergingResponse,
    StoryEngineResponse,
    WhereStoryBeginsResponse,
    WhyThisMattersResponse,
)
from app.services.event_service import handle_character_created
from app.services.insight_generator import get_character_deterministic_fields, get_pattern_emerging_fields
from app.services.report_builder import generate_character_report, get_answer_text

router = APIRouter()


@router.post("/stories/{story_id}/characters", response_model=CharacterResponse)
def create_character_for_story(story_id: UUID, character_in: CharacterCreate, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    character = Character(**character_in.model_dump(), story_id=story_id)
    db.add(character)
    db.commit()
    db.refresh(character)
    handle_character_created(db, character.story_id, character.id, character.name)
    return character


@router.get("/stories/{story_id}/characters", response_model=List[CharacterResponse])
def get_characters_for_story(story_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    characters = db.query(Character).filter(Character.story_id == story_id).offset(skip).limit(limit).all()
    return characters


@router.get("/characters/{character_id}", response_model=CharacterResponse)
def get_character(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.put("/characters/{character_id}", response_model=CharacterResponse)
def update_character(character_id: UUID, character_in: CharacterUpdate, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    update_data = character_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    db.commit()
    db.refresh(character)
    return character


@router.delete("/characters/{character_id}", response_model=CharacterResponse)
def delete_character(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    db.delete(character)
    db.commit()
    return character


@router.get("/characters/{character_id}/story-engine", response_model=StoryEngineResponse)
def get_story_engine(character_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )
    if not report:
        report = generate_character_report(db, character_id)
    return StoryEngineResponse(
        emotional_wound=report.emotional_wound or "Not discovered yet.",
        fear=report.deepest_fear or "Not discovered yet.",
        protective_lie=report.protective_lie or "Not discovered yet.",
        relationship_pattern=report.relationship_pattern or "Not discovered yet.",
        story_conflict=report.conflict_created or "Not discovered yet.",
        transformation=report.transformation or "Not discovered yet.",
    )


@router.get("/characters/{character_id}/why-this-matters", response_model=WhyThisMattersResponse)
def get_why_this_matters(character_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )
    if not report:
        report = generate_character_report(db, character_id)
    return WhyThisMattersResponse(
        main_statement="This belief doesn't just shape who your character is. It shapes what happens to them.",
        relationships="People struggle to get close.",
        choices="Important opportunities are rejected.",
        conflict="The character creates the very outcome they fear.",
        dramatic_potential=report.dramatic_potential or "Not discovered yet.",
    )


@router.get("/characters/{character_id}/narrative-consequence", response_model=NarrativeConsequenceResponse)
def get_narrative_consequence(character_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )
    if not report:
        report = generate_character_report(db, character_id)

    # Generate main statement dynamically based on protective lie
    lie_text = report.protective_lie or ""
    main_statement = (
        f"Because this character believes {lie_text.lower().replace('.', '')}, they push away the people most capable of helping them."
        if lie_text and lie_text != "Not discovered yet."
        else "Not discovered yet."
    )

    return NarrativeConsequenceResponse(
        main_statement=main_statement,
        protective_lie=report.protective_lie or "Not discovered yet.",
        behavior=report.behavior or "Not discovered yet.",
        story_consequence=report.narrative_consequence or "Not discovered yet.",
        conflict_created=report.conflict_created or "Not discovered yet.",
    )


@router.get("/characters/{character_id}/where-story-begins", response_model=WhereStoryBeginsResponse)
def get_where_story_begins(character_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )
    if not report:
        report = generate_character_report(db, character_id)
    return WhereStoryBeginsResponse(
        key_insight=report.story_beginning_summary or "Not discovered yet.",
        inciting_relationship=report.inciting_relationship or "Not discovered yet.",
        central_conflict=report.central_conflict or "Not discovered yet.",
        transformation=report.transformation or "Not discovered yet.",
        final_statement="We now understand not only who this character is. We understand why their story exists.",
    )


@router.get("/characters/{character_id}/pattern-emerging", response_model=PatternEmergingResponse)
def get_pattern_emerging(character_id: UUID, db: Session = Depends(get_db)):
    report = (
        db.query(CharacterArchitectureReport).filter(CharacterArchitectureReport.character_id == character_id).first()
    )
    if not report:
        report = generate_character_report(db, character_id)

    answers = {"char_lie": report.protective_lie or "", "char_wound": report.deepest_fear or ""}

    fields = get_pattern_emerging_fields(db, character_id, answers)

    return PatternEmergingResponse(
        title="A Pattern Is Emerging",
        pattern_name=fields["pattern_name"],
        insight=fields["insight"],
        supporting_text=fields["supporting_text"],
        next_discovery_hint=fields["next_discovery_hint"],
    )


@router.get("/characters/{character_id}/pulse", response_model=CharacterPulseResponse)
def get_character_pulse(character_id: UUID, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    wound = get_answer_text(db, "char_wound", character_id=character_id)
    fear = get_answer_text(db, "char_fear", character_id=character_id)
    lie = get_answer_text(db, "char_lie", character_id=character_id)

    answers = {
        "char_lie": lie,
        "char_consequence": get_answer_text(db, "char_consequence", character_id=character_id),
        "char_relationship_pattern": get_answer_text(db, "char_relationship_pattern", character_id=character_id),
    }
    insights = get_character_deterministic_fields(db, character_id, answers)

    from app.models.discovery import DiscoveryEvent

    latest_event = (
        db.query(DiscoveryEvent)
        .filter(DiscoveryEvent.character_id == character_id)
        .order_by(DiscoveryEvent.created_at.desc())
        .first()
    )

    # Calculate simple progress based on events count
    events_count = db.query(DiscoveryEvent).filter(DiscoveryEvent.character_id == character_id).count()
    progress = min(100, int((events_count / 10) * 100))

    latest_disc_str = "CHARACTER_CREATED"
    if latest_event:
        latest_disc_str = latest_event.event_type.value if hasattr(latest_event.event_type, "value") else str(latest_event.event_type)

    return CharacterPulseResponse(
        progress=progress,
        wound=wound,
        fear=fear,
        lie=lie,
        most_likely_conflict=insights.get("central_conflict", "Not discovered yet."),
        latest_discovery=latest_disc_str,
    )
