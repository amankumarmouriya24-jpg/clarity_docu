"""AI Service for clarity_doc.

Handles: Chat/Q&A, Document Summarization/Analysis, Code Generation/Review.
Uses: Anthropic Claude API.
"""

import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


def chat_with_ai(user_message, conversation_history=None):
    """Multi-turn chat assistant."""
    messages = conversation_history or []
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are a helpful assistant for the clarity_doc project.",
        messages=messages,
    )

    reply = response.content[0].text
    messages.append({"role": "assistant", "content": reply})
    return {"reply": reply, "history": messages}


def summarize_document(document_text, mode="summary"):
    """Summarize a document in the requested mode."""
    prompts = {
        "summary": "Summarize this document in 3-5 sentences.",
        "bullets": "Extract the 5-7 most important points as bullet points.",
        "analysis": "Analyze this document. Identify main themes, key arguments, and insights.",
        "qa": "Generate 5 insightful Q&A pairs based on this document.",
    }
    prompt = prompts.get(mode, prompts["summary"])

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\n---DOCUMENT---\n{document_text}",
            }
        ],
    )
    return response.content[0].text


def analyze_document_with_questions(document_text, questions):
    """Answer specific questions about a document."""
    formatted = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(questions))

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Answer these questions based on the document:\n{formatted}"
                    f"\n\n---DOCUMENT---\n{document_text}"
                ),
            }
        ],
    )
    return {"answers": response.content[0].text, "questions": questions}


def generate_code(description, language="python"):
    """Generate code from a plain-English description."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=(
            f"You are an expert {language} developer. "
            "Return only clean, well-commented code."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Write {language} code that does:\n{description}",
            }
        ],
    )
    return response.content[0].text


def review_code(code, language="python"):
    """Review code for bugs, security issues, and improvements."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system="You are a senior software engineer doing a code review.",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Review this {language} code for bugs, security issues, "
                    f"and improvements:\n\n```{language}\n{code}\n```"
                ),
            }
        ],
    )
    return {"review": response.content[0].text, "language": language}
