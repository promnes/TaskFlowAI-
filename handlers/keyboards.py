"""
Keyboard builders for Telegram bot
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from services.i18n_service import get_i18n_service


def get_main_menu_keyboard(language: str = "ar") -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    i18n = get_i18n_service()
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=i18n.get_text("menu.balance", language)
                ),
                KeyboardButton(
                    text=i18n.get_text("menu.deposit", language)
                ),
            ],
            [
                KeyboardButton(
                    text=i18n.get_text("menu.withdraw", language)
                ),
                KeyboardButton(
                    text=i18n.get_text("menu.transactions", language)
                ),
            ],
            [
                KeyboardButton(
                    text=i18n.get_text("menu.support", language)
                ),
                KeyboardButton(
                    text=i18n.get_text("menu.settings", language)
                ),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="العربية 🇸🇦",
                    callback_data="lang_ar"
                ),
                InlineKeyboardButton(
                    text="English 🇬🇧",
                    callback_data="lang_en"
                ),
            ]
        ]
    )


def get_confirm_keyboard(language: str = "ar") -> InlineKeyboardMarkup:
    """Confirm/Cancel keyboard"""
    i18n = get_i18n_service()
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get_text("button.confirm", language),
                    callback_data="confirm_yes"
                ),
                InlineKeyboardButton(
                    text=i18n.get_text("button.cancel", language),
                    callback_data="confirm_no"
                ),
            ]
        ]
    )


def get_admin_menu_keyboard(language: str = "ar") -> ReplyKeyboardMarkup:
    """Admin panel menu"""
    i18n = get_i18n_service()
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=i18n.get_text("admin.pending_deposits", language)
                ),
                KeyboardButton(
                    text=i18n.get_text("admin.pending_withdrawals", language)
                ),
            ],
            [
                KeyboardButton(
                    text=i18n.get_text("admin.users", language)
                ),
                KeyboardButton(
                    text=i18n.get_text("admin.analytics", language)
                ),
            ],
            [
                KeyboardButton(
                    text=i18n.get_text("menu.main", language)
                ),
            ],
        ],
        resize_keyboard=True,
    )


def get_cancel_keyboard(language: str = "ar") -> ReplyKeyboardMarkup:
    """Cancel operation keyboard"""
    i18n = get_i18n_service()
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=i18n.get_text("button.cancel", language)
                ),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
