
from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.gpt_service import generate_reply
from services.gemini_service import generate_summary, extract_action_items, rewrite_draft


class PromptRequest(BaseModel):
    prompt: str = Field(..., max_length=8000, description="Email text or prompt")


class RewriteRequest(BaseModel):
    text: str = Field(..., max_length=8000, description="Draft text to rewrite")
    tone: str = Field(..., max_length=50, description="Tone such as Professional, Friendly, Concise")


router = APIRouter()


@router.post("/reply")
def gpt_reply(request: PromptRequest):
    reply = generate_reply(request.prompt)
    return {"reply": reply}


@router.post("/gemini/summarize")
async def gemini_summarize(request: PromptRequest):
    summary = await generate_summary(request.prompt)
    return {"reply": summary}


@router.post("/gemini/actions")
async def gemini_actions(request: PromptRequest):
    actions = await extract_action_items(request.prompt)
    return {"reply": actions}


@router.post("/gemini/rewrite")
async def gemini_rewrite(request: RewriteRequest):
    rewritten = await rewrite_draft(request.text, request.tone)
    return {"reply": rewritten}
