import calendar

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2, 1,),
) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру из произвольного словаря текст->callback_data.
    """
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(
            InlineKeyboardButton(
                text=text,
                callback_data=data
            )
        )
    return keyboard.adjust(*sizes).as_markup()


def get_url_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,),
) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с кнопками-ссылками.
    """
    keyboard = InlineKeyboardBuilder()
    for text, url in btns.items():
        keyboard.add(
            InlineKeyboardButton(
                text=text,
                url=url
            )
        )
    return keyboard.adjust(*sizes).as_markup()


def get_inline_mix_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1, 1, 2,),
) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с комбинированными кнопками: часть — callback, часть — url.
    """
    keyboard = InlineKeyboardBuilder()
    for text, value in btns.items():
        if '://' in value:
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    url=value
                )
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=value
                )
            )
    return keyboard.adjust(*sizes).as_markup()
