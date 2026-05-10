import os
from dotenv import load_dotenv

from openai import OpenAI
from google import genai
import anthropic


load_dotenv()


def ask_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "OPENAI_API_KEY is missing. Please add it to your .env file."

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def ask_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "GEMINI_API_KEY is missing. Please add it to your .env file."

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def ask_claude(prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return "ANTHROPIC_API_KEY is missing. Please add it to your .env file."

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.content[0].text


def ask_ai(provider: str, prompt: str) -> str:
    if not prompt:
        return "Please enter a prompt."

    try:
        provider = provider.lower()

        if provider == "openai / gpt":
            return ask_openai(prompt)

        if provider == "gemini":
            return ask_gemini(prompt)

        if provider == "claude":
            return ask_claude(prompt)

        return "Unsupported AI provider."

    except Exception as error:
        return f"AI Provider Error:\n\n{str(error)}"