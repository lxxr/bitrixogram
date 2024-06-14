# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 09:43:25 2024

@author:  Aleksey Rublev RCBD.org
"""

from typing import List, Dict, Union, Any

class ReplyAttachMarkup:
    def __init__(self):
        self.attach = []

    def add_user_block(self, name: str, avatar: str = None, link: Union[str, Dict[str, int]] = None) -> 'ReplyAttachMarkup':
        user_block = {"USER": {"NAME": name}}
        if avatar:
            user_block["USER"]["AVATAR"] = avatar
        if isinstance(link, str):
            user_block["USER"]["LINK"] = link
        elif isinstance(link, dict):
            for key, value in link.items():
                user_block["USER"][key] = value
        self.attach.append(user_block)
        return self

    def add_link_block(self, name: str, link: Union[str, Dict[str, int]], desc: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachMarkup':
        link_block = {"LINK": {"NAME": name, "LINK": link}}
        if desc:
            link_block["LINK"]["DESC"] = desc
        if preview:
            link_block["LINK"]["PREVIEW"] = preview
        if width:
            link_block["LINK"]["WIDTH"] = width
        if height:
            link_block["LINK"]["HEIGHT"] = height
        self.attach.append(link_block)
        return self

    def add_message_block(self, message: str) -> 'ReplyAttachMarkup':
        self.attach.append({"MESSAGE": message})
        return self

    def add_delimiter_block(self, size: int = None, color: str = None) -> 'ReplyAttachMarkup':
        delimiter_block = {"DELIMITER": {}}
        if size:
            delimiter_block["DELIMITER"]["SIZE"] = size
        if color:
            delimiter_block["DELIMITER"]["COLOR"] = color
        self.attach.append(delimiter_block)
        return self

    def add_grid_block(self, grid_layout: List[Dict[str, Union[str, int]]]) -> 'ReplyAttachMarkup':
        self.attach.append({"GRID": grid_layout})
        return self

    def add_image_block(self, link: str, name: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachMarkup':
        image_block = {"IMAGE": {"LINK": link}}
        if name:
            image_block["IMAGE"]["NAME"] = name
        if preview:
            image_block["IMAGE"]["PREVIEW"] = preview
        if width:
            image_block["IMAGE"]["WIDTH"] = width
        if height:
            image_block["IMAGE"]["HEIGHT"] = height
        self.attach.append(image_block)
        return self

    def add_file_block(self, link: str, name: str = None, size: int = None) -> 'ReplyAttachMarkup':
        file_block = {"FILE": {"LINK": link}}
        if name:
            file_block["FILE"]["NAME"] = name
        if size:
            file_block["FILE"]["SIZE"] = size
        self.attach.append(file_block)
        return self

    def to_dict(self) -> List[Dict[str, Any]]:
        return self.attach

class GridLayout:
    def __init__(self, display: str):
        self.display = display
        self.items = []

    def add_item(self, name: str = None, value: str = None, color: str = None, chat_id: int = None, user_id: int = None, link: str = None, width: int = None) -> 'GridLayout':
        item = {"DISPLAY": self.display}
        if name:
            item["NAME"] = name
        if value:
            item["VALUE"] = value
        if color:
            item["COLOR"] = color
        if chat_id:
            item["CHAT_ID"] = chat_id
        if user_id:
            item["USER_ID"] = user_id
        if link:
            item["LINK"] = link
        if width:
            item["WIDTH"] = width
        self.items.append(item)
        return self

    def to_dict(self) -> List[Dict[str, Union[str, int]]]:
        return self.items

class ReplyAttachBuilder:
    def __init__(self):
        self.markup = ReplyAttachMarkup()

    def user(self, name: str, avatar: str = None, link: Union[str, Dict[str, int]] = None) -> 'ReplyAttachBuilder':
        self.markup.add_user_block(name, avatar, link)
        return self

    def link(self, name: str, link: Union[str, Dict[str, int]], desc: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachBuilder':
        self.markup.add_link_block(name, link, desc, preview, width, height)
        return self

    def message(self, message: str) -> 'ReplyAttachBuilder':
        self.markup.add_message_block(message)
        return self

    def delimiter(self, size: int = None, color: str = None) -> 'ReplyAttachBuilder':
        self.markup.add_delimiter_block(size, color)
        return self

    def grid_column_layout(self) -> GridLayout:
        return GridLayout(display="COLUMN")

    def grid_block_layout(self) -> GridLayout:
        return GridLayout(display="BLOCK")

    def grid_line_layout(self) -> GridLayout:
        return GridLayout(display="LINE")

    def grid(self, grid_layout: GridLayout) -> 'ReplyAttachBuilder':
        self.markup.add_grid_block(grid_layout.to_dict())
        return self

    def image(self, link: str, name: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachBuilder':
        self.markup.add_image_block(link, name, preview, width, height)
        return self

    def file(self, link: str, name: str = None, size: int = None) -> 'ReplyAttachBuilder':
        self.markup.add_file_block(link, name, size)
        return self

    def build(self) -> ReplyAttachMarkup:
        return self.markup