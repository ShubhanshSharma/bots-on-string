from langchain_openai import ChatOpenAI
from app.core.config import get_settings
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

settings = get_settings()

# Initialize OpenAI Chat model
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.8,
    openai_api_key=settings.OPENAI_API_KEY,
)

async def generate_response(prompt: str, context: str = "") -> str:
    """
    Generate a GPT-based response with optional contextual data.
    """
    full_prompt = f"Context:\n{context}\n\nUser: {prompt}\nAI:"
    response = await llm.ainvoke(full_prompt)
    return response.content

def generate_reply(user_input: str, context_docs: list[str]) -> str:
    context_text = "\n".join(context_docs or [])
    prompt = f"Context:\n{context_text}\n\nUser: {user_input}\nAssistant:"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful chatbot."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()