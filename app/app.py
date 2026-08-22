from fastapi import FastAPI, HTTPException
from .schemas import NewPost, ResponsePost
from app.database import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifetime(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifetime)