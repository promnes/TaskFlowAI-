# Copilot Instructions – LangSense (STRICT CODING MODE)

You are GitHub Copilot working on the LangSense (TaskFlowAI) codebase.

====================
ABSOLUTE RULES
====================
1. OUTPUT CODE ONLY.
2. DO NOT explain anything.
3. DO NOT describe what the code does.
4. DO NOT add comments unless explicitly requested.
5. DO NOT generate documentation, markdown, or README files.
6. DO NOT create files unless explicitly instructed.
7. DO NOT suggest improvements unless explicitly asked.
8. DO NOT change architecture or patterns.
9. DO NOT output anything other than valid source code.

Your job is ONLY to understand the project and write or modify code.

====================
PROJECT OVERVIEW
====================
LangSense is a financial services system composed of:
- Telegram Bot (Aiogram v3)
- FastAPI REST API
- React Native Mobile App (Expo)

All components share the same async SQLAlchemy ORM defined in models.py.

====================
DATABASE RULES
====================
- models.py is the single source of truth.
- Use SQLAlchemy 2.0 async ORM only.
- Always use AsyncSession and async_sessionmaker.
- Do not duplicate models.
- Store dynamic data in JSON fields (extra_data).

====================
TELEGRAM BOT RULES
====================
- Framework: aiogram v3
- Router-based handlers only.
- All routers must be registered in bot.py.
- session_maker is injected via middleware.
- Explicit session.commit() is REQUIRED after writes.
- Use FSM for multi-step input.
- All user-facing text MUST use get_text(key, language).
- Do NOT hardcode text.
- RTL support for Arabic is mandatory.

Handler pattern:
async def handler(message, state, session_maker):
    async with session_maker() as session:
        ...
        await session.commit()

====================
FASTAPI RULES
====================
- Async routes only.
- JWT auth via get_current_user.
- DB access via Depends(get_db).
- Do NOT manually commit inside API routes.
- Use schemas from api/schemas.py.
- Follow existing route structure.

Route pattern:
@router.post("/endpoint")
async def endpoint(current_user=Depends(get_current_user), session=Depends(get_db)):
    ...

====================
FINANCIAL LOGIC
====================
- Every financial action MUST create an Outbox record.
- Use OutboxType and OutboxStatus enums only.
- Store extra fields in Outbox.extra_data.
- No financial logic outside Outbox system.

====================
BROADCAST SYSTEM
====================
- Use broadcast_service queue only.
- Respect rate limits.
- Track delivery using OutboxRecipient.
- Do not introduce new messaging mechanisms.

====================
MOBILE APP RULES
====================
- Framework: React Native (Expo).
- API access only through api.js.
- JWT stored in AsyncStorage.
- Follow existing navigation and screen patterns.
- Do NOT alter backend behavior.

====================
PROHIBITED
====================
- No explanations
- No logs
- No refactoring unless requested
- No tests unless requested
- No architecture changes

====================
REQUIRED
====================
- Minimal, correct, production-ready code
- Match existing style exactly
- Assume environment variables are configured

END OF INSTRUCTIONS
