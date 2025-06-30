import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from thoughts.api.models import ThoughtDB, Base
from thoughts.core.config import settings

def generate_test_data():
    """
    Generates a test database with 50 self-reflective thoughts.
    """
    if os.path.exists(settings.TEST_DATABASE_URL.replace("sqlite:///", "")):
        os.remove(settings.TEST_DATABASE_URL.replace("sqlite:///", ""))

    engine = create_engine(settings.TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    thoughts = [
        "What is one thing I could do today to make tomorrow better?",
        "Am I using my time wisely?",
        "What am I avoiding that I know I need to do?",
        "Is this aligned with my long-term goals?",
        "What is a recent failure I can learn from?",
        "How can I be more present in my daily life?",
        "What is something I'm grateful for right now?",
        "Am I taking care of my physical and mental health?",
        "What would my ideal self do in this situation?",
        "What is a limiting belief I'm holding onto?",
        "How can I step out of my comfort zone this week?",
        "What relationship in my life needs more of my attention?",
        "Am I holding onto any resentment that I need to let go of?",
        "What is a skill I want to develop?",
        "How can I contribute to my community or the world in a meaningful way?",
        "What is a book I should read that could change my perspective?",
        "Am I living authentically?",
        "What is one small thing I can do to bring joy to someone else today?",
        "What does success look like to me, and am I on the right path?",
        "How can I be more compassionate towards myself and others?",
        "What is a fear that is holding me back?",
        "Am I communicating my needs effectively in my relationships?",
        "What is something I have been procrastinating on and why?",
        "What are my top 3 priorities right now?",
        "How can I simplify my life?",
        "What is a passion I've been neglecting?",
        "Am I open to new ideas and perspectives?",
        "What is one positive habit I want to cultivate?",
        "How do I want to be remembered?",
        "What is a difficult conversation I need to have?",
        "Am I spending enough time in nature?",
        "What is something that energizes me?",
        "How can I be a better listener?",
        "What is a boundary I need to set?",
        "Am I celebrating my small wins?",
        "What is a mistake I keep repeating?",
        "How can I practice more self-discipline?",
        "What does my ideal day look like, and how can I make it a reality?",
        "Am I learning from my past, or am I defined by it?",
        "What is something I can do to reduce my stress levels?",
        "How can I be more creative in my work or personal life?",
        "What is a piece of advice I would give to my younger self?",
        "Am I taking on too much responsibility?",
        "What is a quality I admire in others that I want to cultivate in myself?",
        "How can I be more mindful of my impact on the environment?",
        "What is a project I'm excited about?",
        "Am I challenging my own assumptions?",
        "What is something I'm proud of, but rarely acknowledge?",
        "How can I be more patient with myself and the process?",
        "What is one step I can take today towards a long-term dream?"
    ]

    db = SessionLocal()
    for thought_content in thoughts:
        thought = ThoughtDB(content=thought_content)
        db.add(thought)
    db.commit()
    db.close()
    print("Test database generated with 50 thoughts.")

if __name__ == "__main__":
    generate_test_data() 