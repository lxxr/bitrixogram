# -*- coding: utf-8 -*-
"""
Created on Sun May 19 13:22:13 2024

@author: Aleksey Rublev RCBD.org
"""

from typing import List, Dict, Any

class ReplyKeyboardMarkup:
    def __init__(self, keyboard: List[List[Dict[str, Any]]], resize_keyboard: bool = True):
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard

    def to_dict(self) -> Dict[str, Any]:
        return self.keyboard


class ReplyKeyboardBuilder:
    def __init__(self):
        self.buttons = []
        self.current_line = []

    def button(self, text: str, command: str = None, command_params: Any = None,block:str = "Y", link: str = None,width:int = 200, bg_color: str = "#29619b", text_color: str = "#fff", display: str = "LINE", disabled="N") -> 'ReplyKeyboardBuilder':
        button = {"TEXT": text}
        if command:
            button["COMMAND"] = command
        if command_params:
            button["COMMAND_PARAMS"] = command_params
        if link:
            button["LINK"] = link
        if bg_color:
            button["BG_COLOR"] = bg_color
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
        if self.current_line:
            self.buttons.extend(self.current_line)
            self.current_line = [{"TYPE": "NEWLINE"}]
            self.buttons.extend(self.current_line)
            self.current_line = []
        return self

    def adjust(self, buttons_per_line: int) -> 'ReplyKeyboardBuilder':
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
        if self.current_line:
            self.buttons.append(self.current_line)
        return ReplyKeyboardMarkup(keyboard=self.buttons, resize_keyboard=resize_keyboard)

