# This is the MAIN entry point of the app. It:
#   1. Creates the FastAPI application
#   2. Plugs in all the ready-made authentication routes (login, register, etc.)
#   3. Defines our own custom routes: upload a post, delete a post, get the feed

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from .schemas import UserCreate, UserRead, UserUpdate
from .database import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from .images import imageKit
from pathlib import Path
import shutil, os, uuid, tempfile
from app.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifetime(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifetime)

# Adds:  POST /auth/jwt/login   and   POST /auth/jwt/logout
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

# Adds:  POST /auth/register
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Adds:  POST /auth/forgot-password 
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)

# Adds:  POST /auth/request-verify-token
app.include_router(
    fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)

# Adds:  GET/PATCH/DELETE /users/me 
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)



# ROUTE: Upload a new post (image or video)
# -----------------------------------------------------------------------------
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imageKit.files.upload(
            file=Path(temp_file_path),
            file_name=file.filename,
            tags=["Backend Upload"],
            use_unique_file_name=True,
        )

        post = Post(
            user_id=user.id,
            caption=caption,
            file_type="video" if file.content_type.startswith("video/") else "image",
            url=upload_result.url,
            file_name=upload_result.name,
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()



# ROUTE: Delete a post
# -----------------------------------------------------------------------------
@app.delete("/post/{post_id}")
async def delete_file(
    post_id: str, 
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You don't have permission to delete this post"
            )

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ROUTE: Get the feed (all posts, newest first)
# -----------------------------------------------------------------------------
@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),  # must be logged in
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]

    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown"),
            }
        )

    return {"posts": posts_data}
