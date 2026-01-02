"""
Support and contact handler
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.auth import get_user_by_id
from handlers.keyboards import get_main_menu_keyboard, get_cancel_keyboard
from handlers.states import SupportStates
from models import SupportTicket
from datetime import datetime

router = Router()


@router.message(F.text.contains("الدعم") | F.text.contains("Support"), StateFilter(None))
async def start_support(
    message: Message,
    state: FSMContext,
    i18n: any,
    user_language: str,
):
    """Start support ticket"""
    
    text = i18n.get_text("support.choose_category", user_language)
    
    # Create category keyboard
    keyboard = get_support_category_keyboard(user_language)
    
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(SupportStates.waiting_for_category)
    await state.update_data(user_language=user_language)


@router.callback_query(SupportStates.waiting_for_category)
async def process_category(
    query: any,
    state: FSMContext,
    i18n: any,
    user_language: str,
):
    """Process category selection"""
    
    category = query.data.split("_")[1]
    
    await state.update_data(support_category=category)
    
    text = i18n.get_text("support.enter_message", user_language)
    keyboard = get_cancel_keyboard(user_language)
    
    await query.message.edit_text(text)
    await query.message.answer("", reply_markup=keyboard)
    
    await state.set_state(SupportStates.waiting_for_message)
    await query.answer()


@router.message(SupportStates.waiting_for_message)
async def process_message(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    i18n: any,
    user_language: str,
):
    """Process support message"""
    
    user = await get_user_by_id(session, message.from_user.id)
    
    if not user:
        await message.answer(i18n.get_text("error.user_not_found", user_language))
        return
    
    state_data = await state.get_data()
    category = state_data.get("support_category", "general")
    
    # Create support ticket
    ticket = SupportTicket(
        user_id=user.id,
        category=category,
        subject=message.text[:100],
        message=message.text,
        status="OPEN",
    )
    
    session.add(ticket)
    await session.commit()
    
    text = i18n.get_text("support.ticket_created", user_language)
    text += f"\nTicket ID: #{ticket.id}"
    
    keyboard = get_main_menu_keyboard(user_language)
    
    await message.answer(text, reply_markup=keyboard)
    await state.clear()


def get_support_category_keyboard(language: str = "ar"):
    """Get support category keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    categories = {
        "ar": [
            ("💰 مالي", "cat_financial"),
            ("🔧 تقني", "cat_technical"),
            ("❓ عام", "cat_general"),
        ],
        "en": [
            ("💰 Financial", "cat_financial"),
            ("🔧 Technical", "cat_technical"),
            ("❓ General", "cat_general"),
        ]
    }
    
    buttons = []
    for text, data in categories.get(language, categories["ar"]):
        buttons.append([InlineKeyboardButton(text=text, callback_data=data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
