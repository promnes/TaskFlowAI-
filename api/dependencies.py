#!/usr/bin/env python3
"""
Database dependencies for FastAPI
"""

from sqlalchemy.ext.asyncio import AsyncSession


async def get_db():
    """Get database session - to be injected from main.py"""
    from api.main import async_session_maker
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
