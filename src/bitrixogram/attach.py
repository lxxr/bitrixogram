# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 09:43:25 2024

@author:  Aleksey Rublev RCBD.org
"""

from typing import List, Dict, Union, Any

class ReplyAttachMarkup:
    """
    Класс для создания структурированных вложений сообщений.

    """
    def __init__(self):
        """
        Инициализирует пустой список attach для хранения блоков вложений.
        """     
        self.attach = []

    def add_user_block(self, name: str, avatar: str = None, link: Union[str, Dict[str, int]] = None) -> 'ReplyAttachMarkup':
        """
        Добавляет блок пользователя в attach.
    
        Args:
            name: Имя пользователя.
            avatar: URL аватара пользователя (опционально).
            link: URL или словарь с дополнительными данными о ссылке (опционально).
        """     
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
        """
        Добавляет в attach блок со ссылкой на ресурс, описанием и картинкой-пояснением  
        Args:
            name: Текст для ссылки.
            link: URL ссылки.
            desc: Описание ссылки (опционально).
            preview: URL превью изображения (опционально).
            width: Ширина изображения (опционально).
            height: Высота изображения (опционально).
        """     
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
        """
        Добавляет блок сообщения в attach.
        Args:
           message: Содержание сообщения.
        """   
        self.attach.append({"MESSAGE": message})
        return self

    def add_delimiter_block(self, size: int = None, color: str = None) -> 'ReplyAttachMarkup':
        """
        Добавляет блок разделителя в attach.
        Args:
           size: Размер разделителя (опционально).
           color: Цвет разделителя (опционально).
        """   
        delimiter_block = {"DELIMITER": {}}
        if size:
            delimiter_block["DELIMITER"]["SIZE"] = size
        if color:
            delimiter_block["DELIMITER"]["COLOR"] = color
        self.attach.append(delimiter_block)
        return self

    def add_grid_block(self, grid_layout: List[Dict[str, Union[str, int]]]) -> 'ReplyAttachMarkup':
        """
        Добавляет блок GRID в attach.
        Args:
          grid_layout: Список словарей, описывающих структуру сетки.
        """   
        self.attach.append({"GRID": grid_layout})
        return self

    def add_image_block(self, link: str, name: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachMarkup':
        """
        Добавляет блок изображения в attach.
        Args:
            link: URL изображения.
            name: Название изображения (опционально).
            preview: URL превью изображения (опционально).
            width: Ширина изображения (опционально).
            height: Высота изображения (опционально).
        """   
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
        """
        Добавляет блок файла в attach.
        Args:
            link: URL файла.
            name: Название файла (опционально).
            size: Размер файла (опционально).
        """   
        file_block = {"FILE": {"LINK": link}}
        if name:
            file_block["FILE"]["NAME"] = name
        if size:
            file_block["FILE"]["SIZE"] = size
        self.attach.append(file_block)
        return self

    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Возвращает список словарей, представляющих структурированные вложения.

        """   
        return self.attach

class GridLayout:
    """
    Класс GridLayout представляет собой сетку элементов с определенным типом отображения.

    Args:
    - display: str - тип отображения сетки (COLUMN, BLOCK или LINE).
    - items: List[Dict[str, Union[str, int]]] - список элементов сетки.
    """

    def __init__(self, display: str):
        """
        Инициализирует новый экземпляр класса GridLayout с указанным типом отображения.

        Args:
        - display: str - тип отображения сетки (COLUMN, BLOCK или LINE).
        """
        self.display = display
        self.items = []

    def add_item(self, name: str = None, value: str = None, color: str = None, chat_id: int = None, user_id: int = None, link: str = None, width: int = None) -> 'GridLayout':
        """
        Добавляет элемент в текущую сетку.

        Args:
        - name: str - название элемента.
        - value: str - значение элемента (опционально).
        - color: str - цвет элемента (опционально).
        - chat_id: int - идентификатор чата (опционально).
        - user_id: int - идентификатор пользователя (опционально).
        - link: str - ссылка элемента (опционально).
        - width: int - ширина элемента (опционально).

        Возвращает:
        - Экземпляр класса GridLayout для цепочного вызова методов.
        """
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
        """
        Преобразует список элементов сетки в формат списка словарей.

        """
        return self.items

class ReplyAttachBuilder:
    """
    Класс ReplyAttachBuilder предоставляет удобный интерфейс для построения вложений сообщений.

    Args:
    - markup: ReplyAttachMarkup - объект для сборки вложений сообщения.
    """

    def __init__(self):
        """
        Инициализирует новый экземпляр класса ReplyAttachBuilder.
        """
        self.markup = ReplyAttachMarkup()

    def user(self, name: str, avatar: str = None, link: Union[str, Dict[str, int]] = None) -> 'ReplyAttachBuilder':
        """
        Добавляет блок пользователя во вложение.

        Args:
        - name: str - имя пользователя.
        - avatar: str - URL аватара пользователя (опционально).
        - link: Union[str, Dict[str, int]] - URL или словарь с дополнительными данными о ссылке (опционально).

        """
        self.markup.add_user_block(name, avatar, link)
        return self

    def link(self, name: str, link: Union[str, Dict[str, int]], desc: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachBuilder':
        """
        Добавляет блок ссылки во вложение.

        Args:
        - name: str - название ссылки.
        - link: Union[str, Dict[str, int]] - URL или словарь с дополнительными данными о ссылке.
        - desc: str - описание ссылки (опционально).
        - preview: str - URL превью изображения (опционально).
        - width: int - ширина изображения (опционально).
        - height: int - высота изображения (опционально).

        """
        self.markup.add_link_block(name, link, desc, preview, width, height)
        return self

    def message(self, message: str) -> 'ReplyAttachBuilder':
        """
        Добавляет блок сообщения во вложение.

        Args:
        - message: str - содержание сообщения.

        """
        self.markup.add_message_block(message)
        return self

    def delimiter(self, size: int = None, color: str = None) -> 'ReplyAttachBuilder':
        """
        Добавляет блок-разделитель во вложение.

        Args:
        - size: int - размер разделителя (опционально).
        - color: str - цвет разделителя (опционально).

        """
        self.markup.add_delimiter_block(size, color)
        return self

    def grid_column_layout(self) -> GridLayout:
        """
        Создает и возвращает объект GridLayout для столбцовой сетки.

        """
        return GridLayout(display="COLUMN")

    def grid_block_layout(self) -> GridLayout:
        """
        Создает и возвращает объект GridLayout для блочной сетки.

        """
        return GridLayout(display="BLOCK")

    def grid_line_layout(self) -> GridLayout:
        """
        Создает и возвращает объект GridLayout для линейной сетки.

        """
        return GridLayout(display="LINE")

    def grid(self, grid_layout: GridLayout) -> 'ReplyAttachBuilder':
        """
        Добавляет блок сетки во вложение.

        Args:
        - grid_layout: GridLayout - объект, представляющий структуру сетки.

        """
        self.markup.add_grid_block(grid_layout.to_dict())
        return self

    def image(self, link: str, name: str = None, preview: str = None, width: int = None, height: int = None) -> 'ReplyAttachBuilder':
        """
        Добавляет блок изображения во вложение.

        Args:
        - link: str - URL изображения.
        - name: str - название изображения (опционально).
        - preview: str - URL превью изображения (опционально).
        - width: int - ширина изображения (опционально).
        - height: int - высота изображения (опционально).

        """
        self.markup.add_image_block(link, name, preview, width, height)
        return self

    def file(self, link: str, name: str = None, size: int = None) -> 'ReplyAttachBuilder':
        """
        Добавляет блок файла во вложение.

        Args:
        - link: str - URL файла.
        - name: str - название файла (опционально).
        - size: int - размер файла (опционально).

        """
        self.markup.add_file_block(link, name, size)
        return self

    def build(self) -> ReplyAttachMarkup:
        """
        Возвращает объект ReplyAttachMarkup сформированного вложения.

        """
        return self.markup