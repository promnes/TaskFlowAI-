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
# ========================================================
# AI BOT INSTRUCTION / PROJECT CONTEXT
# ========================================================
# PROJECT: Comprehensive Telegram Financial + Gaming Bot
# ENTRY POINT: comprehensive_bot.py
# GOAL:
#   - Read all project files (handlers, services, models, utils)
#   - Understand current implemented features
#   - Identify missing features and gaps
#   - Plan incremental execution of missing features
#   - Ensure all features run through comprehensive_bot.py only
#
# EXISTING FEATURES:
#   - Wallet system: deposits/withdrawals for companies
#   - Users select company & payment method
#   - Admin panel with basic operations
#   - Async architecture (Aiogram v3 + Async SQLAlchemy)
#   - Multi-language support (i18n)
#   - Broadcast system
#   - Admin authorization via @admin_required
#
# REQUIRED NEW FEATURES / DOMAINS:
# 1. Games Engine:
#     - Game selection
#     - Play sessions linked to user wallet
#     - Profit/loss calculation
#     - Win probability / algorithm control
#     - Per-user, per-region overrides
#     - Anti-cheat logging
# 2. User Profile & Security:
#     - Require phone number on login (contact card or manual)
#     - Warning if incorrect input
#     - Profile image & documents upload
#     - Password recovery & chat restoration
#     - Badges based on activity
# 3. Agents (Wakils):
#     - Admin creates agent accounts
#     - Agents manage payment methods for users
#     - Track deposits/withdrawals
#     - Commission engine (weekly)
#     - Search engine for agent activity and user requests
# 4. Complaints System:
#     - Users submit complaints tied to transactions
#     - Agents data hidden from users
#     - Admin resolves, auto-adjusting balances and commissions
# 5. Affiliate / Marketing system:
#     - Generate unique referral codes
#     - Track new users and commissions
#     - Dashboard for affiliate performance
# 6. Admin Dashboard:
#     - Global search and filters
#     - Algorithm control for games
#     - Balance adjustments
#     - Access to logs for each user/account
#     - Upload new games
#
# EXECUTION PLAN:
#   1. Read all files (handlers, services, models, utils)
#   2. Parse implemented features vs missing ones
#   3. Create domain modules for each missing feature
#   4. Register all new routers/services in comprehensive_bot.py
#   5. Preserve async correctness
#   6. Preserve i18n patterns
#   7. Preserve existing admin authorization
#   8. Incrementally implement features, starting with:
#       - Ledger / logging / user profiles
#       - Games MVP
#       - Agents
#       - Affiliates
#       - Complaints
#       - Security enhancements
#       - Admin dashboard improvements
#
# EXPECTED AI BEHAVIOR:
#   - Do NOT skip any file
#   - Fully understand models, routers, and services
#   - Keep comprehensive_bot.py as the single entry point
#   - Identify missing functionality and gaps
#   - Suggest or scaffold missing modules incrementally
#   - Maintain existing user flows and async patterns
# ========================================================
