# -*- coding: utf-8 -*-
"""
Created on Sun May 19 13:22:13 2024

@author: Aleksey Rublev RCBD.org
"""

from typing import List, Dict, Any

class ReplyKeyboardMarkup:
    """
    Класс ReplyKeyboardMarkup представляет собой клавиатуру ответа в формате Telegram.

    Args:
    - keyboard: List[List[Dict[str, Any]]] - двумерный список кнопок клавиатуры.
    - resize_keyboard: bool - флаг, указывающий на возможность изменения размера клавиатуры.
    """

    def __init__(self, keyboard: List[List[Dict[str, Any]]], resize_keyboard: bool = True):
        """
        Инициализирует новый экземпляр класса ReplyKeyboardMarkup с указанным списком кнопок и настройками размера.

        Args:
        - keyboard: List[List[Dict[str, Any]]] - двумерный список кнопок клавиатуры.
        - resize_keyboard: bool - флаг, указывающий на возможность изменения размера клавиатуры (по умолчанию True).
        """
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует клавиатуру в формат словаря.

        Возвращает:
        - Словарь, представляющий клавиатуру.
        """
        return self.keyboard


class ReplyKeyboardBuilder:
    """
    Класс ReplyKeyboardBuilder предоставляет удобный интерфейс для построения клавиатуры ответа.

    Args:
    - buttons: List[Dict[str, Any]] - список кнопок клавиатуры.
    - current_line: List[Dict[str, Any]] - текущая строка кнопок клавиатуры.
    """

    def __init__(self):
        """
        Инициализирует новый экземпляр класса ReplyKeyboardBuilder.
        """
        self.buttons = []
        self.current_line = []

    def button(self, text: str, command: str = None, command_params: Any = None, block: str = "Y", link: str = None, width: int = 200, bg_color: str = "#29619b",bg_color_token: str = "base", text_color: str = "#fff", display: str = "LINE", disabled: str = "N") -> 'ReplyKeyboardBuilder':
        """
        Добавляет кнопку в текущую строку клавиатуры.

        Args:
        - text: str - текст кнопки.
        - command: str - команда для кнопки (опционально).
        - command_params: Any - параметры команды (опционально).
        - block: str - флаг блокировки кнопки (по умолчанию "Y").
        - link: str - ссылка для кнопки (опционально).
        - width: int - ширина кнопки (по умолчанию 200).
        - bg_color: str - цвет фона кнопки (по умолчанию "#29619b").
        - bg_color_token: str -  токен для цвета кнопки в чате. Может принимать одно из следующих значений: primary, secondary, alert, base По умолчанию имеет значение base.
        - text_color: str - цвет текста кнопки (по умолчанию "#fff").
        - display: str - тип отображения кнопки (по умолчанию "LINE").
        - disabled: str - флаг отключения кнопки (по умолчанию "N").

        """
        button = {"TEXT": text}
        if command:
            button["COMMAND"] = command
        if command_params:
            button["COMMAND_PARAMS"] = command_params
        if link:
            button["LINK"] = link
        if bg_color:
            button["BG_COLOR"] = bg_color
        if bg_color_token:
            button["BG_COLOR_TOKEN"] = bg_color_token            
        if text_color:
            button["TEXT_COLOR"] = text_color
        if display:
            button["DISPLAY"] = display
        if block:
            button["BLOCK"] = block
        if width:
            button["WIDTH"] = width
        if disabled:
            button["DISABLED"] = disabled
            
        self.current_line.append(button)
        return self

    def newline(self) -> 'ReplyKeyboardBuilder':
        """
        Завершает текущую строку кнопок и переходит на новую строку.

        """
        if self.current_line:
            self.buttons.extend(self.current_line)
            self.current_line = [{"TYPE": "NEWLINE"}]
            self.buttons.extend(self.current_line)
            self.current_line = []
        return self

    def adjust(self, buttons_per_line: int) -> 'ReplyKeyboardBuilder':
        """
        Приводит клавиатуру к заданному числу кнопок в строке.

        Args:
        - buttons_per_line: int - количество кнопок в строке.

        """
        if self.current_line:
            self.buttons.extend(self.current_line)
            self.current_line = []

        adjusted_keyboard = []
        count = 0

        for button in self.buttons:
            if button == {"TYPE": "NEWLINE"}:
                adjusted_keyboard.append(button)
                count = 0
            else:
                if count >= buttons_per_line:
                    adjusted_keyboard.append({"TYPE": "NEWLINE"})
                    count = 0
                adjusted_keyboard.append(button)
                count += 1

        self.buttons = adjusted_keyboard
        return self

    def as_markup(self, resize_keyboard: bool = True) -> ReplyKeyboardMarkup:
        """
        Возвращает объект ReplyKeyboardMarkup, представляющий построенную клавиатуру.

        Args:
        - resize_keyboard: bool - флаг изменения размера клавиатуры (по умолчанию True).

        Возвращает:
        - Объект ReplyKeyboardMarkup с построенной клавиатурой.
        """
        if self.current_line:
            self.buttons.append(self.current_line)
        return ReplyKeyboardMarkup(keyboard=self.buttons, resize_keyboard=resize_keyboard)