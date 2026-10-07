from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .core import SCENARIO_MAP, benchmark_summary, evaluate_attempt, list_scenarios

BASE=Path(__file__).resolve().parent
app=FastAPI(title="DevStart",version="1.0.0",description="Interactive API onboarding and recovery benchmark")
app.mount('/static',StaticFiles(directory=BASE/'static'),name='static')
SESSIONS: dict[str,list[dict[str,Any]]] = {}

class Attempt(BaseModel):
    session_id: str | None = None
    headers: dict[str,str] = Field(default_factory=dict)
    body: Any = None
    path_params: dict[str,str] = Field(default_factory=dict)

@app.get('/',include_in_schema=False)
def home(): return FileResponse(BASE/'static'/'index.html')

@app.get('/health')
def health(): return {'status':'ok','service':'devstart','version':'1.0.0'}

@app.post('/api/sessions')
def create_session():
    sid='ds_'+uuid4().hex[:12]; SESSIONS[sid]=[]; return {'session_id':sid,'scenario_count':len(SCENARIO_MAP)}

@app.get('/api/scenarios')
def scenarios(): return {'scenarios':list_scenarios()}

@app.post('/api/scenarios/{scenario_id}/attempt')
def attempt(scenario_id:str,payload:Attempt):
    if scenario_id not in SCENARIO_MAP: raise HTTPException(404,'Unknown scenario')
    sid=payload.session_id or 'anonymous'
    SESSIONS.setdefault(sid,[])
    result=evaluate_attempt(scenario_id,headers=payload.headers,body=payload.body,path_params=payload.path_params)
    row={'scenario_id':scenario_id,**result}; SESSIONS[sid].append(row)
    return {'session_id':sid,'scenario':SCENARIO_MAP[scenario_id].__dict__,'result':result,'benchmark':benchmark_summary(SESSIONS[sid])}

@app.get('/api/sessions/{session_id}')
def session(session_id:str):
    if session_id not in SESSIONS: raise HTTPException(404,'Session not found')
    return {'session_id':session_id,'attempts':SESSIONS[session_id],'benchmark':benchmark_summary(SESSIONS[session_id])}
