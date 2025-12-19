"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from sqlmodel import Session, select

from .db import init_db, get_engine
from .models import Activity, Participant


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities (persistent DB)")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")


@app.on_event("startup")
def on_startup():
    # Initialize DB and seed sample activities if empty
    init_db()
    engine = get_engine()
    with Session(engine) as session:
        count = session.exec(select(Activity)).first()
        if not count:
            seed_activities(session)
            session.commit()


def seed_activities(session: Session):
    samples = [
        {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        {
            "name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        {
            "name": "Gym Class",
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
    ]

    for a in samples:
        activity = Activity(
            name=a["name"],
            description=a.get("description"),
            schedule=a.get("schedule"),
            max_participants=a.get("max_participants"),
        )
        session.add(activity)
        session.flush()
        for email in a.get("participants", []):
            session.add(Participant(email=email, activity_id=activity.id))


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    engine = get_engine()
    with Session(engine) as session:
        activities = session.exec(select(Activity)).all()

        result = {}
        for a in activities:
            # load participants
            participants = [p.email for p in a.participants] if a.participants else []
            result[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": participants,
            }
        return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    engine = get_engine()
    with Session(engine) as session:
        activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # load participants count
        participants = session.exec(select(Participant).where(Participant.activity_id == activity.id)).all()

        if any(p.email == email for p in participants):
            raise HTTPException(status_code=400, detail="Student is already signed up")

        if activity.max_participants and len(participants) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        participant = Participant(email=email, activity_id=activity.id)
        session.add(participant)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    engine = get_engine()
    with Session(engine) as session:
        activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant = session.exec(
            select(Participant).where(Participant.activity_id == activity.id, Participant.email == email)
        ).first()

        if not participant:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(participant)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}

