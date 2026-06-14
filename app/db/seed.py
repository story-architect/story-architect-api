from app.core.database import SessionLocal
from app.models import DiscoveryQuestion, FlowTypeEnum

CHARACTER_QUESTIONS = [
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_wound",
        "question_text": "What is the wound this character carries?",
        "order_index": 1,
        "suggested_answers": ["Abandonment", "Betrayal", "Failure", "Loss of a loved one"],
    },
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_fear",
        "question_text": "What fear grew from that wound?",
        "order_index": 2,
        "suggested_answers": ["Fear of intimacy", "Fear of success", "Fear of being alone", "Fear of helplessness"],
    },
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_lie",
        "question_text": "What lie does this character believe protects them?",
        "order_index": 3,
        "suggested_answers": [
            "'I don't need anyone'",
            "'If I'm perfect, I won't be rejected'",
            "'Emotions are a weakness'",
        ],
    },
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_behavior",
        "question_text": "How does this lie affect their behavior?",
        "order_index": 4,
        "suggested_answers": ["Pushing people away", "Overworking", "People-pleasing", "Avoidance"],
    },
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_consequence",
        "question_text": "What story consequence does this create?",
        "order_index": 5,
        "suggested_answers": ["Alienating allies", "Missing crucial opportunities", "Making dangerous mistakes"],
    },
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_conflict",
        "question_text": "What conflict does this create?",
        "order_index": 6,
        "suggested_answers": ["Clashing with mentors", "Ruining a romance", "Failing the initial challenge"],
    },
    {
        "flow_type": FlowTypeEnum.CHARACTER_DISCOVERY,
        "question_key": "char_transformation",
        "question_text": "What must they learn to transform?",
        "order_index": 7,
        "suggested_answers": ["To trust again", "To forgive themselves", "To accept help", "To face reality"],
    },
]

RELATIONSHIP_QUESTIONS = [
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_importance",
        "question_text": "Why are these two characters important to each other?",
        "order_index": 1,
        "suggested_answers": ["Shared history", "Complementary skills", "Mutual goal", "Trauma bonding"],
    },
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_truth_a",
        "question_text": "What truth can Character A tell everyone except Character B?",
        "order_index": 2,
        "suggested_answers": ["They love them", "They betrayed them", "They are leaving", "They know their secret"],
    },
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_truth_b",
        "question_text": "What truth can Character B tell everyone except Character A?",
        "order_index": 3,
        "suggested_answers": ["They resent them", "They are protecting them", "They are responsible for their pain"],
    },
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_protect",
        "question_text": "What are they trying to protect each other from?",
        "order_index": 4,
        "suggested_answers": [
            "The villain's plot",
            "A painful truth",
            "Their own destructive habits",
            "Society's judgment",
        ],
    },
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_misunderstanding",
        "question_text": "What misunderstanding does this create?",
        "order_index": 5,
        "suggested_answers": [
            "Thinking the other doesn't care",
            "Believing they are enemies",
            "Assuming they are a burden",
        ],
    },
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_risk",
        "question_text": "What is the current relationship risk?",
        "order_index": 6,
        "suggested_answers": ["Permanent separation", "Betrayal", "Physical harm", "Losing trust completely"],
    },
    {
        "flow_type": FlowTypeEnum.RELATIONSHIP_DISCOVERY,
        "question_key": "rel_truth_demand",
        "question_text": "What truth will eventually demand to be spoken?",
        "order_index": 7,
        "suggested_answers": [
            "The real reason they stayed",
            "The identity of the traitor",
            "The extent of their sacrifice",
        ],
    },
]


def seed_questions(db):
    print("Seeding discovery questions...")
    for q_data in CHARACTER_QUESTIONS + RELATIONSHIP_QUESTIONS:
        existing = db.query(DiscoveryQuestion).filter(DiscoveryQuestion.question_key == q_data["question_key"]).first()
        if not existing:
            q = DiscoveryQuestion(**q_data)
            db.add(q)
            print(f"Added: {q.question_text}")
    db.commit()
    print("Seeding complete.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_questions(db)
    finally:
        db.close()
