import os

from dotenv import load_dotenv

load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-pro",
)


def _demo_workout(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:
    return f"""
FITBUDDY 7-DAY WORKOUT PLAN

Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal.title()}
Intensity: {intensity.title()}

IMPORTANT:
This is a general wellness example and not medical advice.
Adjust exercises to your ability and stop if you experience pain,
dizziness, or unusual discomfort.

DAY 1 — FULL BODY

Warm-up:
• 5–10 minutes of easy walking
• Arm circles
• Hip rotations

Main workout:
• Bodyweight squats — 3 sets × 10 reps
• Incline push-ups — 3 sets × 8 reps
• Glute bridges — 3 sets × 12 reps
• Bird dogs — 3 sets × 10 each side
• Plank — 3 × 20–30 seconds

Cooldown:
• 5 minutes of gentle stretching

DAY 2 — CARDIO

Warm-up:
• 5 minutes easy walking

Main workout:
• Brisk walking — 20–30 minutes
• Step-ups — 3 sets × 10 each leg
• Standing knee raises — 3 sets × 12

Cooldown:
• Gentle leg stretching

DAY 3 — UPPER BODY

Warm-up:
• 5–10 minutes

Main workout:
• Incline push-ups — 3 × 8–12
• Resistance-band rows — 3 × 10
• Shoulder raises — 3 × 10
• Wall push-ups — 2 × 12
• Dead bug — 3 × 10 each side

Cooldown:
• Shoulder and upper-back stretches

DAY 4 — RECOVERY

• Easy walking — 15–20 minutes
• Gentle mobility exercises
• Light stretching
• Focus on hydration and sleep

DAY 5 — LOWER BODY

Warm-up:
• 5–10 minutes easy movement

Main workout:
• Squats — 3 × 10
• Reverse lunges — 3 × 8 each leg
• Glute bridges — 3 × 15
• Calf raises — 3 × 15
• Wall sit — 3 × 20–30 seconds

Cooldown:
• Gentle lower-body stretching

DAY 6 — CORE + CARDIO

Warm-up:
• 5 minutes walking

Main workout:
• Brisk walking — 20 minutes
• Dead bugs — 3 × 10
• Bird dogs — 3 × 10 each side
• Plank — 3 × 20 seconds
• Marching in place — 3 × 45 seconds

Cooldown:
• Gentle stretching

DAY 7 — REST AND RECOVERY

• Optional easy walk
• Gentle stretching
• Hydration
• Relaxation
• Prepare for the next week

PROGRESSION:
Start comfortably. Increase repetitions or duration gradually
rather than making large changes at once.
"""


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        return _demo_workout(
            username,
            age,
            weight,
            goal,
            intensity,
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file or enable DEMO_MODE=true."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "google-genai is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a structured 7-day general fitness plan for the following user.

Name: {username}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Preferred intensity: {intensity}

Requirements:

1. Provide exactly 7 days.
2. Include:
   - Day focus
   - Warm-up
   - Main workout
   - Sets/repetitions or duration
   - Rest guidance
   - Cooldown/recovery
3. Make the plan appropriate for the requested intensity.
4. Keep the plan practical and easy to follow.
5. Do not claim to diagnose, treat, or prevent disease.
6. Do not prescribe medication or supplements.
7. Include a short safety note.
8. Use clear plain-text formatting.
9. Do not invent medical conditions.

Return only the workout plan.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text or "No workout plan was generated."