"""
One-time migration script: assign usernames to existing users who don't have one.
Run ONCE after deploying the new code:
    cd backend && python migrate_usernames.py
"""
from __future__ import annotations

import asyncio
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select

from database import async_session
from models import User


async def main() -> None:
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == None))  # noqa: E711
        users = result.scalars().all()

        if not users:
            print("No users without username found.")
            return

        taken_result = await db.execute(
            select(User.username).where(User.username.is_not(None))
        )
        taken: set[str] = {row[0] for row in taken_result.all()}

        for user in users:
            base = re.sub(r"[^a-z0-9._-]", "", user.email.split("@")[0].lower())[:30] or "user"
            candidate = base
            i = 1
            while candidate in taken or len(candidate) < 3:
                candidate = f"{base}{i}"
                i += 1
            user.username = candidate
            taken.add(candidate)
            print(f"  {user.email} → username: {candidate}")

        await db.commit()
        print(f"Updated {len(users)} users.")


asyncio.run(main())
