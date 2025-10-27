from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

@app.post("/v1/chat")
async def chat(req: ChatRequest, x_api_key: str = Header(...)):
    # 1. validate API key -> get tenant_id, chatbot_id
    tenant_id, chatbot_id = validate_api_key(x_api_key)
    # 2. embed query
    q_vec = embed_text(req.message)
    # 3. vector search with filter tenant_id+chatbot_id
    docs = vector_db.search(q_vec, filter={"tenant_id": tenant_id, "chatbot_id": chatbot_id}, top_k=5)
    # 4. build prompt + include conversation memory (Redis)
    prompt = build_prompt(docs, req.message, tenant_id, chatbot_id, req.session_id)
    # 5. call Gemini LLM
    resp = call_gemini(prompt)
    # 6. store session memory, log usage
    save_session_memory(req.session_id, req.message, resp)
    log_usage(tenant_id, chatbot_id, x_api_key, req.message, resp)
    return {"answer": resp, "sources": [d.metadata for d in docs]}
