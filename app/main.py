import os

from fastapi import FastAPI

from app.api.routes import router
from app.config import settings

if settings.langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project

app = FastAPI(title="Autonomous Blog Generation Agent")
app.include_router(router)
