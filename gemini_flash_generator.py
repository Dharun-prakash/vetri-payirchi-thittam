import os

from dotenv import load_dotenv

load_dotenv()


MODEL_NAME = os.getenv(
    "GEMINI_NUTRITION_MODEL",
    "gemini-2.5-flash",
)


def _demo_tip(goal: str) -> str:
    tips = {
        "weight loss": (
            "Prioritize regular balanced meals, vegetables, "
            "whole grains, protein-rich foods, and adequate hydration. "
            "Avoid making extreme food restrictions."
        ),
        "muscle gain": (
            "Include a source of protein in balanced meals, "
            "such as eggs, beans, lentils, dairy, fish, or lean meat, "
            "and support training with adequate overall food and sleep."
        ),
        "general wellness": (
            "Aim for balanced meals, regular hydration, "
            "adequate sleep, and a variety of fruits and vegetables."
        ),
        "flexibility": (
            "Stay hydrated and include balanced meals with fruits, "
            "vegetables, protein sources, and whole grains."
        ),
        "strength": (
            "Support strength training with balanced meals containing "
            "protein, carbohydrates, healthy fats, and adequate fluids."
        ),
    }

    return tips.get(
        goal.lower(),
        tips["general wellness"],
    )


def generate_nutrition_tip_with_flash(goal: str) -> str:

    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    if demo_mode:
        return _demo_tip(goal)

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
Provide one concise nutrition or recovery tip for a person
whose fitness goal is: {goal}.

Rules:
- Maximum 120 words.
- General wellness information only.
- No diagnosis.
- No medication advice.
- No extreme dieting.
- Keep the advice practical.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text or "Stay hydrated and maintain balanced meals."