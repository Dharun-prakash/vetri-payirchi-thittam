from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import User
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# HOME
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


# ============================================================
# GENERATE WORKOUT
# ============================================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,

    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:
        user_input = UserInput(
            username=username.strip(),
            user_id=user_id.strip(),
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        existing_user = (
            db.query(User)
            .filter(User.user_id == user_input.user_id)
            .first()
        )

        # Generate workout plan
        workout_plan = generate_workout_gemini(
            username=user_input.username,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
        )

        # Generate nutrition tip
        nutrition_tip = generate_nutrition_tip_with_flash(
            user_input.goal
        )

        # Update existing user
        if existing_user:

            existing_user.username = user_input.username
            existing_user.age = user_input.age
            existing_user.weight = user_input.weight
            existing_user.goal = user_input.goal
            existing_user.intensity = user_input.intensity
            existing_user.original_plan = workout_plan
            existing_user.updated_plan = None
            existing_user.feedback = None
            existing_user.nutrition_tip = nutrition_tip

            user = existing_user

        # Create new user
        else:

            user = User(
                user_id=user_input.user_id,
                username=user_input.username,
                age=user_input.age,
                weight=user_input.weight,
                goal=user_input.goal,
                intensity=user_input.intensity,
                original_plan=workout_plan,
                nutrition_tip=nutrition_tip,
            )

            db.add(user)

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "workout_plan": user.original_plan,
                "nutrition_tip": user.nutrition_tip,
                "message": "Your personalized plan has been generated.",
                "error": None,
            },
        )

    except ValueError as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(exc),
            },
            status_code=400,
        )

    except Exception as exc:

        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": f"Unable to generate workout: {exc}",
            },
            status_code=500,
        )


# ============================================================
# SUBMIT FEEDBACK
# ============================================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),
    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id.strip())
        .first()
    )

    if not user:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": "User ID was not found.",
            },
            status_code=404,
        )

    try:

        feedback_request = FeedbackRequest(
            user_id=user_id.strip(),
            feedback=feedback.strip(),
        )

        current_plan = (
            user.updated_plan
            or user.original_plan
        )

        revised_plan = update_workout_plan(
            original_plan=current_plan,
            feedback=feedback_request.feedback,
            goal=user.goal,
            intensity=user.intensity,
        )

        user.updated_plan = revised_plan
        user.feedback = feedback_request.feedback

        user.nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user.goal
            )
        )

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "workout_plan": user.updated_plan,
                "nutrition_tip": user.nutrition_tip,
                "message": "Your plan was updated using your feedback.",
                "error": None,
            },
        )

    except Exception as exc:

        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "workout_plan": user.updated_plan or user.original_plan,
                "nutrition_tip": user.nutrition_tip,
                "message": None,
                "error": f"Unable to update plan: {exc}",
            },
            status_code=500,
        )


# ============================================================
# VIEW ALL USERS
# ============================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users,
        },
    )


# ============================================================
# API - ALL USERS
# ============================================================

@router.get("/api/users")
def api_users(
    db: Session = Depends(get_db),
):

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return [
        {
            "id": user.id,
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "original_plan": user.original_plan,
            "updated_plan": user.updated_plan,
            "feedback": user.feedback,
            "nutrition_tip": user.nutrition_tip,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            ),
        }
        for user in users
    ]


# ============================================================
# API - SINGLE USER
# ============================================================

@router.get("/api/users/{user_id}")
def api_user(
    user_id: str,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:

        return JSONResponse(
            status_code=404,
            content={
                "detail": "User not found."
            },
        )

    return {
        "id": user.id,
        "user_id": user.user_id,
        "username": user.username,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "original_plan": user.original_plan,
        "updated_plan": user.updated_plan,
        "feedback": user.feedback,
        "nutrition_tip": user.nutrition_tip,
        "created_at": (
            user.created_at.isoformat()
            if user.created_at
            else None
        ),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
def health_check():

    return {
        "status": "ok",
        "application": "FitBuddy",
    }