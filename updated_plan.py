import os

from dotenv import load_dotenv

load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-pro",
)


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str,
) -> str:

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        return f"""
UPDATED FITBUDDY WORKOUT PLAN

Original goal: {goal}
Intensity: {intensity}

USER FEEDBACK:
{feedback}

UPDATED PLAN NOTES:

The plan has been revised according to the submitted feedback.

DAY 1 — FULL BODY
• Keep a 5–10 minute warm-up.
• Bodyweight squats — 3 × 10
• Incline push-ups — 3 × 8
• Glute bridges — 3 × 12
• Plank — 3 × 20 seconds

DAY 2 — CARDIO
• Brisk walking — 20–30 minutes
• Add comfortable intervals if appropriate.

DAY 3 — UPPER BODY
• Incline push-ups — 3 × 8–12
• Resistance-band rows — 3 × 10
• Shoulder mobility — 5 minutes

DAY 4 — RECOVERY
• Easy walking
• Gentle mobility
• Stretching

DAY 5 — LOWER BODY
• Squats — 3 × 10
• Reverse lunges — 3 × 8 each side
• Glute bridges — 3 × 15

DAY 6 — CORE + CARDIO
• Walking — 20 minutes
• Dead bugs — 3 × 10
• Bird dogs — 3 × 10
• Plank — 3 × 20 seconds

DAY 7 — REST
• Rest or gentle movement.

The plan has been adapted based on the user's feedback.
Increase or decrease difficulty gradually and stop if exercise causes pain.
"""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "google-genai is not installed."
        ) from exc

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are FitBuddy.

Revise the following workout plan according to user feedback.

GOAL:
{goal}

INTENSITY:
{intensity}

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Requirements:
- Keep the plan at 7 days.
- Apply the user's requested changes where reasonable.
- Keep the requested intensity in mind.
- Include warm-up, workout, rest, and recovery.
- Avoid medical claims.
- Do not recommend dangerous activities.
- Do not prescribe medication.
- Clearly present the updated plan.

Return only the updated plan.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text or original_plan