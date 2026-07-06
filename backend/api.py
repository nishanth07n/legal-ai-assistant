from cpu_runtime import force_cpu_runtime

force_cpu_runtime()

from fastapi import FastAPI
from pydantic import BaseModel
from .orchestrator import run_agents

app = FastAPI()


class AnalyzeRequest(BaseModel):
    text: str
    role: str


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    result = run_agents(request.text, request.role)
    return result
