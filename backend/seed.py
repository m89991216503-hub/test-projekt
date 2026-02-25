"""Create default users in the database."""
import asyncio
from database import engine, Base, async_session
from models import User
from auth import hash_password
from sqlalchemy import select


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "demo@example.com"))
        if result.scalar_one_or_none() is None:
            user = User(email="demo@example.com", hashed_password=hash_password("demo123"))
            session.add(user)
            await session.commit()
            print("Created user: demo@example.com / demo123")
        else:
            print("User demo@example.com already exists")

        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is None:
            admin = User(
                email="admin@localhost",
                username="admin",
                hashed_password=hash_password("admin"),
                is_admin=True,
            )
            session.add(admin)
            await session.commit()
            print("Created admin: admin / admin")
        else:
            print("Admin user already exists")

    await engine.dispose()


asyncio.run(main())
