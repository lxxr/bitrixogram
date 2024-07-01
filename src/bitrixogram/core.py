# -*- coding: utf-8 -*-
"""
Created on Sun May 19 17:57:43 2024

@author: Aleksey Rublev RCBD.org
"""
from aiohttp import web, ClientSession
import asyncio

from typing import Callable, List, Dict, Any, Union, Awaitable 
import operator
from .keyboard import ReplyKeyboardMarkup

import logging


class BitrixBot:
    """
    Класс для взаимодействия с Bitrix24 через чат-бот.

    Атрибуты:
        bot_token (str): Токен для авторизации бота.
        base_url (str): URL для взаимодействия с Bitrix24.
        base_id (str): ID бота.
        dispatcher (Dispatcher): Диспетчер для обработки сообщений.
        fsm (FSM): Машина состояний для обработки состояний сообщений.
        session (ClientSession): Сессия для выполнения HTTP-запросов.
    """

    def __init__(self, bot_endpoint:str,  bot_token: str,bot_id:str, session: ClientSession):
        """
        Инициализирует BitrixBot с заданными параметрами.

        Args:
            bot_endpoint (str): Базовый URL для Bitrix24.
            bot_token (str): Токен для авторизации.
            bot_id (str): ID бота.
            session (ClientSession): Сессия для выполнения HTTP-запросов.
        """
        self.bot_token = bot_token
        self.base_url = bot_endpoint
        self.base_id = bot_id
        self.dispatcher = Dispatcher()
        self.fsm = FSM()        
        self.session = session  
                
    async def register_commands(self,commands):
        """
        Регистрирует команды для бота в Bitrix24.
    
        Args:
            commands (list): Список команд для регистрации.
        """     
        for command in commands:
            await self.rest_command('imbot.command.register', {
                'BOT_ID': self.base_id,
                'COMMAND': command['COMMAND'],
                'COMMON': 'Y',
                'HIDDEN': 'Y',
                'EXTRANET_SUPPORT': 'N',
                'CLIENT_ID': self.bot_token,
                'LANG': [{'LANGUAGE_ID': 'en', 'TITLE': command['TITLE'], 'PARAMS': command['PARAMS']}],
                'EVENT_COMMAND_ADD': command['EVENT_COMMAND_ADD']
            })
      

    async def send_message(self, chat_id: int, text: str, attach:Dict[str, Any] = None, keyboard: 'ReplyKeyboardMarkup' = None):
        """
        Отправляет сообщение в чат.

        Args:
            chat_id (int): ID чата.
            text (str): Текст сообщения.
            attach (Dict[str, Any], optional): Вложения к сообщению.
            keyboard (ReplyKeyboardMarkup, optional): Клавиатура для сообщения.
        """
        data = {
            'DIALOG_ID': chat_id,
            'MESSAGE': text,
        }
        if attach:
            data['ATTACH'] = attach
        else:
            data['ATTACH'] = ''
        if keyboard:
            data['KEYBOARD'] = keyboard.to_dict()
        logging.debug(f"send_message data: {data}")            
        response = await self.rest_command("imbot.message.add", params=data)
        return response
    
    
    async def command_answer(self,command: 'Command', text: str, attach:Dict[str, Any] = None,  keyboard: 'ReplyKeyboardMarkup' = None):             
        """
       Отвечает на команду.

       Args:
           command (Command): Команда, на которую нужно ответить.
           text (str): Текст ответа.
           attach (Dict[str, Any], optional): Вложения к сообщению.
           keyboard (ReplyKeyboardMarkup, optional): Клавиатура для сообщения.
       """       
        data = {
            'BOT_ID': self.base_id,
            'COMMAND': command.get_command_name(),
            'MESSAGE_ID': command.get_message_id(),
            'MESSAGE': text            
        }
        if attach:
            data['ATTACH'] = attach
        if keyboard:
            data['KEYBOARD'] = keyboard.to_dict()
        logging.debug(f"command_answer_message data: {data}")   
        response = await self.rest_command("imbot.command.answer", params=data)
        return response
    
    async def message_delete(self, message_id: int, complete: str ="Y"):
        """
        Удаляет сообщение.

        Args:
            message_id (int): ID сообщения.
            complete (str, optional): Статус завершения. По умолчанию "Y".
        """        
        data = {
            'BOT_ID': self.base_id,
            'MESSAGE_ID': message_id,            
            'COMPLETE': complete
        }
        logging.debug(f"delete_message data: {data}")   
        response = await self.rest_command("imbot.message.delete", params=data)
        return response
 
    async def command_update_message(self, text: str, command: 'Command' , attach:Dict[str, Any] = None, chat_id: int = None,message_id: int = None, keyboard: 'ReplyKeyboardMarkup' = None):
        """
        Обновляет сообщение от команды.

        Args:
            text (str): Новый текст сообщения.
            command (Command): Команда, для которой обновляется сообщение.
            attach (Dict[str, Any], optional): Вложения к сообщению.
            chat_id (int, optional): ID чата. Если не задан, используется ID чата из команды.
            message_id (int, optional): ID сообщения. Если не задан, используется ID сообщения из команды.
            keyboard (ReplyKeyboardMarkup, optional): Клавиатура для сообщения.
        """
        if chat_id == None:
            chat_id=command.get_chat_id()
        if message_id == None:
            message_id=command.get_message_id()
            
        data = {
            'DIALOG_ID': chat_id,
            'MESSAGE': text,
            'BOT_ID': self.base_id,
            'MESSAGE_ID': message_id
            
        }
        if attach:
            data['ATTACH'] = attach
        else:
            data['ATTACH'] = ''
        if keyboard:
            data['KEYBOARD'] = keyboard.to_dict()
        else:
            data['KEYBOARD'] = ''
            
        logging.debug(f"command_update_message data: {data}")            
        response = await self.rest_command("imbot.message.update", params=data) 
        return response

    async def update_message(self,  text: str, message: 'Message' , attach:Dict[str, Any] = None, chat_id: int = None, message_id: int = None, keyboard: 'ReplyKeyboardMarkup' = None):
        """
        Обновляет сообщение.

        Args:
            text (str): Новый текст сообщения.
            message (Message): Сообщение, которое нужно обновить.
            attach (Dict[str, Any], optional): Вложения к сообщению.
            chat_id (int, optional): ID чата. Если не задан, используется ID чата из сообщения.
            message_id (int, optional): ID сообщения. Если не задан, используется ID сообщения из сообщения.
            keyboard (ReplyKeyboardMarkup, optional): Клавиатура для сообщения.
        """
        if chat_id == None:            
            chat_id=message.get_chat_id()
        if message_id == None:
            message_id=message.get_message_id()

        data = {
            'DIALOG_ID': chat_id,
            'MESSAGE': text,
            'BOT_ID': self.base_id,
            'MESSAGE_ID': message_id                        
        }
        if attach:
            data['ATTACH'] = [attach]
        else:
            data['ATTACH'] = ''
        if keyboard:
            data['KEYBOARD'] = keyboard.to_dict()
        else:
            data['KEYBOARD'] = ''
        logging.debug(f"update_message data: {data}")            
        response = await self.rest_command("imbot.message.update", params=data) 
        return response


    async def set_webhook(self, webhook_url: str):
        """
        Устанавливает вебхук для получения обновлений от Bitrix24.
    
        Args:
            webhook_url (str): URL вебхука.
        """
        url = self.base_url + 'imbot.register'
        data = {'EVENT_HANDLER': webhook_url}
        async with self.session.post(url, json=data) as response:
            return await response.json()

    async def handle_update(self, update: Dict[str, Any]):
        """
        Обрабатывает обновление от Bitrix24.

        Args:
            update (Dict[str, Any]): Данные обновления.
        """
        self.dispatcher.process_update(self, update, self.fsm)

    async def register_message_handler(self, handler: Callable, commands: List[str] = None, state: str = None):
        """
        Регистрирует обработчик сообщений.

        Args:
            handler (Callable): Функция-обработчик сообщений.
            commands (List[str], optional): Список команд для обработки.
            state (str, optional): Состояние для обработки.
        """
        self.dispatcher.register_message_handler(handler, commands, state)
    
    def flatten_params(self,json_data, parent_key='', separator='_'):
        """
        Преобразует параметры в плоский формат.

        Args:
            json_data (dict): Данные для преобразования.
            parent_key (str, optional): Родительский ключ.
            separator (str, optional): Разделитель для ключей.

        Returns:
            dict: Преобразованные данные.
        """
        items = {}
        for key, value in json_data.items():
            new_key = f'{parent_key}[{key}]' if parent_key else key
            if isinstance(value, dict):
                items.update(self.flatten_params(value, new_key, separator))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    items.update(self.flatten_params(item, f'{new_key}[{i}]', separator))
            else:
                items[new_key] = value
        return items
        
  
    async def rest_command(self, method, params=None):
        """
        Выполняет команду REST API.

        Args:
            method (str): Метод API.
            params (dict, optional): Параметры для метода.

        Returns:
            dict: Ответ от API.
        """
        query_url = self.base_url + method
        query_data = {**params}
        if query_data.get("CLIENT_ID", None) is None: 
            query_data["CLIENT_ID"] = self.bot_token
        logging.debug(f"ImBot send data \n URL: {query_url} \n PARAMS: {query_data}")
        flattern_data = self.flatten_params(query_data)
        async with self.session.post(query_url, data=flattern_data) as response:
            result = await response.json()
            logging.debug(f"response : {result}")
            return result

class FSMContext:
    """
    Класс, представляющий контекст конечного автомата (FSM) для конкретного чата.

    Attributes:
        chat_id (int): Идентификатор чата.
        state (State): Текущее состояние.
        data (dict): Дополнительные данные, связанные с контекстом.
    """

    def __init__(self, chat_id: int):
        """
        Инициализация контекста FSM для конкретного чата.

        Args:
            chat_id (int): Идентификатор чата.
        """
        self.chat_id = chat_id
        self.state = None
        self.data = {}

    async def set_state(self, state: 'State'):
        """
        Устанавливает состояние контекста.

        Args:
            state (State): Новое состояние.
        """
        self.state = state

    async def get_state(self):
        """
        Возвращает текущее состояние контекста.

        Returns:
            State: Текущее состояние.
        """
        return self.state

    async def clear_state(self):
        """
        Очищает состояние контекста, устанавливая его в None.
        """
        self.state = None

    async def update_data(self, **kwargs):
        """
        Обновляет дополнительные данные контекста.

        Args:
            **kwargs: Пары ключ-значение для обновления данных.
        """
        self.data.update(kwargs)

    async def get_data(self):
        """
        Возвращает дополнительные данные контекста.

        Returns:
            dict: Дополнительные данные.
        """
        return self.data

    async def get_chat_id(self) -> int:
        """
        Возвращает идентификатор чата.

        Returns:
            int: Идентификатор чата.
        """
        return self.chat_id


class FSM:
    """
    Класс, представляющий конечный автомат (FSM) для управления контекстами различных чатов.

    Attributes:
        contexts (dict): Словарь, где ключ - идентификатор чата, а значение - контекст FSM.
    """

    def __init__(self):
        """
        Инициализация FSM.
        """
        self.contexts: Dict[int, FSMContext] = {}

    async def get_context(self, chat_id: int) -> FSMContext:
        """
        Возвращает контекст FSM для заданного чата. Если контекст не существует, он создается.

        Args:
            chat_id (int): Идентификатор чата.

        Returns:
            FSMContext: Контекст FSM для заданного чата.
        """
        if chat_id not in self.contexts:
            self.contexts[chat_id] = FSMContext(chat_id)
        return self.contexts[chat_id]
    

class Message:
    """
    Класс, представляющий сообщение в чате Bitrix24.

    Attributes:
        data (Dict[str, Any]): Сырой словарь данных сообщения.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Инициализация сообщения.

        Args:
            data (Dict[str, Any]): исходное сообщение из ответа сервера.
        """
        self.data = data

    def get_text(self) -> str:
        """
        Возвращает текст сообщения [PARAMS][MESSAGE].

        Returns:
            str: Текст сообщения.
        """
        return self.data.get('data[PARAMS][MESSAGE]', '')

    def get_message_id(self) -> int:
        """
        Возвращает идентификатор сообщения [PARAMS][MESSAGE_ID].

        Returns:
            int: Идентификатор сообщения.
        """
        return int(self.data.get('data[PARAMS][MESSAGE_ID]', 0))

    def get_chat_id(self) -> int:
        """
        Возвращает идентификатор чата, в котором было отправлено сообщение.

        Returns:
            int: Идентификатор чата [PARAMS][DIALOG_ID].
        """
        return int(self.data.get('data[PARAMS][DIALOG_ID]', 0))

    def get_user_id(self) -> int:
        """
        Возвращает идентификатор пользователя, отправившего сообщение.

        Returns:
            int: Идентификатор пользователя [USER][ID].
        """
        return int(self.data.get('data[USER][ID]', 0))

    def get_raw_data(self) -> Dict[str, Any]:
        """
        Возвращает исходное сообщение от сервера.

        Returns:
            Dict[str, Any]: Сырой словарь данных.
        """
        return self.data


class Command:
    """
    Класс, представляющий команду.

    Attributes:
        data (Dict[str, Any]): сообщение от сервера.
        parsed_data (Dict[str, Any]): Распарсенные данные команды.
    """

    def __init__(self, data: Dict[str, Any], parsed_data: Dict[str, Any]):
        """
        Инициализация команды.

        Args:
            data (Dict[str, Any]): сообщение ответа на команду от сервера.
            parsed_data (Dict[str, Any]): Распарсенные данные команды.
        """
        self.data = data
        self.parsed_data = parsed_data

    def get_command_name(self) -> str:
        """
        Возвращает имя команды.

        Returns:
            str: Имя команды.
        """
        return self.parsed_data.get('command', '')

    def get_command_id(self) -> str:
        """
        Возвращает идентификатор команды.

        Returns:
            str: Идентификатор команды.
        """
        return self.parsed_data.get('command_id', '')

    def get_command_params(self) -> str:
        """
        Возвращает параметры команды.

        Returns:
            str: Параметры команды.
        """
        return self.parsed_data.get('command_params', '')

    def get_command_raw_params(self) -> Dict[str, Any]:
        """
        Возвращает словарь параметров команды в исходном виде.

        Returns:
            Dict[str, Any]: Сырой словарь параметров команды.
        """
        return self.parsed_data

    def get_chat_id(self) -> int:
        """
        Возвращает идентификатор чата, в котором была вызвана команда [PARAMS][DIALOG_ID].

        Returns:
            int: Идентификатор чата.
        """
        return int(self.data.get('data[PARAMS][DIALOG_ID]', 0))

    def get_user_id(self) -> int:
        """
        Возвращает идентификатор пользователя, вызвавшего команду [USER][ID].

        Returns:
            int: Идентификатор пользователя.
        """
        return int(self.data.get('data[USER][ID]', 0))

    def get_message_id(self) -> int:
        """
        Возвращает идентификатор сообщения, связанного с командой [PARAMS][MESSAGE_ID].

        Returns:
            int: Идентификатор сообщения.
        """
        return int(self.data.get('data[PARAMS][MESSAGE_ID]', 0))

    def get_raw_data(self) -> Dict[str, Any]:
        """
        Возвращает исходные словарь данных ответа на команду.

        Returns:
            Dict[str, Any]: Сырой словарь данных.
        """
        return self.data


class MagicFilter:
    """
    Класс для создания магических фильтров, которые можно применять к объектам сообщения или команды с учетом контекста FSM.

    Attributes:
        filter_func (Callable[[Union[Message, Command], 'FSMContext'], Union[bool, Awaitable[bool]]]): Функция фильтрации.
    """

    def __init__(self, filter_func: Callable[[Union[Message, Command], 'FSMContext'], Union[bool, Awaitable[bool]]] = None):
        """
        Инициализация MagicFilter.

        Args:
            filter_func (Callable[[Union[Message, Command], 'FSMContext'], Union[bool, Awaitable[bool]]], optional): Функция фильтрации.
        """
        self.filter_func = filter_func

    @classmethod
    def text(cls):
        """
        Создает фильтр для объектов типа Message.

        Returns:
            MagicFilter: Фильтр для сообщений.
        """
        return cls(lambda obj, fsm_context: isinstance(obj, Message))

    @classmethod
    def command(cls):
        """
        Создает фильтр для объектов типа Command.

        Returns:
            MagicFilter: Фильтр для команд.
        """
        return cls(lambda obj, fsm_context: isinstance(obj, Command))

    @classmethod
    def state(cls, expected_state: 'State'):
        """
        Создает фильтр для проверки состояния FSM.

        Args:
            expected_state (State): Ожидаемое состояние.

        Returns:
            MagicFilter: Фильтр для проверки состояния.
        """
        async def filter_func(obj, fsm_context):
            current_state = await fsm_context.get_state()
            return current_state == expected_state
        return cls(filter_func)

    def lower(self, expected_text: str):
        """
        Создает фильтр для проверки текста сообщения (без учета регистра).

        Args:
            expected_text (str): Ожидаемый текст.

        Returns:
            MagicFilter: Фильтр для проверки текста сообщения.
        """
        return MagicFilter(lambda obj, fsm_context: isinstance(obj, Message) and obj.get_text().lower() == expected_text.lower())

    def startswith(self, expected_text: str):
        """
        Создает фильтр для проверки, начинается ли текст сообщения с указанного текста.

        Args:
            expected_text (str): Ожидаемый начальный текст.

        Returns:
            MagicFilter: Фильтр для проверки начального текста сообщения.
        """
        return MagicFilter(lambda obj, fsm_context: isinstance(obj, Message) and obj.get_text().lower().startswith(expected_text))

    async def __call__(self, obj: Union['Message', 'Command'], fsm_context: 'FSMContext') -> bool:
        """
        Применяет фильтр к объекту сообщения или команды.

        Args:
            obj (Union[Message, Command]): Объект сообщения или команды.
            fsm_context (FSMContext): Контекст состояния FSM.

        Returns:
            bool: Результат применения фильтра.
        """
        if self.filter_func:
            result = self.filter_func(obj, fsm_context)
            if asyncio.iscoroutine(result):
                return await result
            return result
        return True

    def _combine(self, other, op):
        """
        Объединяет два фильтра с использованием указанной логической операции.

        Args:
            other (MagicFilter): Другой фильтр.
            op (Callable[[bool, bool], bool]): Логическая операция.

        Returns:
            MagicFilter: Объединенный фильтр.
        """
        async def combined_filter(obj: Union['Message', 'Command'], fsm_context: 'FSMContext') -> bool:
            self_result = await self.__call__(obj, fsm_context)
            other_result = await other.__call__(obj, fsm_context)
            return op(self_result, other_result)
        return MagicFilter(combined_filter)

    def __and__(self, other):
        """
        Объединяет два фильтра с использованием логической операции AND.

        Args:
            other (MagicFilter): Другой фильтр.

        Returns:
            MagicFilter: Объединенный фильтр.
        """
        return self._combine(other, operator.and_)

    def __or__(self, other):
        """
        Объединяет два фильтра с использованием логической операции OR.

        Args:
            other (MagicFilter): Другой фильтр.

        Returns:
            MagicFilter: Объединенный фильтр.
        """
        return self._combine(other, operator.or_)

    def __eq__(self, other):
        """
        Создает фильтр для проверки равенства значения.

        Args:
            other (Any): Значение для сравнения.

        Returns:
            MagicFilter: Фильтр для проверки равенства.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) == other)

    def __ne__(self, other):
        """
        Создает фильтр для проверки неравенства значения.

        Args:
            other (Any): Значение для сравнения.

        Returns:
            MagicFilter: Фильтр для проверки неравенства.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) != other)

    def __lt__(self, other):
        """
        Создает фильтр для проверки, меньше ли значение.

        Args:
            other (Any): Значение для сравнения.

        Returns:
            MagicFilter: Фильтр для проверки, меньше ли значение.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) < other)

    def __le__(self, other):
        """
        Создает фильтр для проверки, меньше ли или равно значение.

        Args:
            other (Any): Значение для сравнения.

        Returns:
            MagicFilter: Фильтр для проверки, меньше ли или равно значение.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) <= other)

    def __gt__(self, other):
        """
        Создает фильтр для проверки, больше ли значение.

        Args:
            other (Any): Значение для сравнения.

        Returns:
            MagicFilter: Фильтр для проверки, больше ли значение.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) > other)

    def __ge__(self, other):
        """
        Создает фильтр для проверки, больше ли или равно значение.

        Args:
            other (Any): Значение для сравнения.

        Returns:
            MagicFilter: Фильтр для проверки, больше ли или равно значение.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) >= other)

    def __getitem__(self, key):
        """
        Создает фильтр для получения значения по ключу из сырых данных объекта.

        Args:
            key (str): Ключ для доступа к значению в сыром словаре данных.

        Returns:
            MagicFilter: Фильтр для получения значения по ключу.
        """
        return MagicFilter(lambda obj, fsm_context: self._get_nested_value(obj.get_raw_data(), key))

    def _get_value(self, obj: Union[Message, Command]) -> Any:
        """
        Возвращает значение объекта для фильтрации.

        Args:
            obj (Union[Message, Command]): Объект сообщения или команды.

        Returns:
            Any: Значение объекта.
        """
        return obj.get_text() if isinstance(obj, Message) else obj.get_command_name()

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """
        Возвращает вложенное значение по ключу из словаря данных.

        Args:
            data (Dict[str, Any]): Словарь данных.
            key (str): Ключ для доступа к вложенному значению.

        Returns:
            Any: Вложенное значение.
        """
        keys = key.split('.')
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k)
            else:
                return None
        return data

    @property
    def message(self):
        """
        Свойство для получения фильтра сообщений.

        Returns:
            MagicFilter: Фильтр сообщений.
        """
        return self

class State:
    """
    Класс, представляющий отдельное состояние.

    Атрибуты:
        name (str): Имя состояния.
    """

    def __init__(self, name: str = None):

        self.name = name

    def set_name(self, name: str):
        """
        Устанавливает имя состояния.

        Args:
            name (str): Имя состояния.
        """
        self.name = name

    def __eq__(self, other):

        if isinstance(other, State):
            return self.name == other.name
        return False

    def __repr__(self):
        return f"State(name={self.name})"


class StatesGroup:
    """
    Класс, представляющий группу состояний.

    Метакласс автоматически присваивает имена состояниям на основе атрибутов класса.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in cls.__dict__.items():
            if isinstance(value, State):
                value.set_name(name)

    def __repr__(self):
        states = {name: value for name, value in self.__class__.__dict__.items() if isinstance(value, State)}
        return f"StatesGroup(states={states})"

class Dispatcher:
    """
    Класс для диспетчеризации обновлений и маршрутизации их к соответствующим обработчикам.

    Attributes:
        routers (List['Router']): Список маршрутизаторов для обработки сообщений и команд.
        FSM (FSM): Состояние машины состояний для управления контекстом.
    """

    def __init__(self):
        """Инициализирует Dispatcher с пустым списком маршрутизаторов и FSM."""
        self.routers = []
        self.FSM = FSM()

    def add_router(self, router: 'Router'):
        """
        Добавляет маршрутизатор в список маршрутизаторов.

        Args:
            router (Router): Маршрутизатор для добавления.
        """
        self.routers.append(router)

    async def process_update(self, update: Dict[str, Any]):
        """
        Обрабатывает обновление, проходя по маршрутизаторам и вызывая соответствующие обработчики.

        Args:
            update (Dict[str, Any]): Данные обновления.
        """
        for router in self.routers:
            handled = await router.handle_message(update)
            if handled:
                break
            handled = await router.handle_callback_query(update)
            if handled:
                break


class Router:
    """
    Класс для маршрутизации сообщений и команд к соответствующим обработчикам.

    Attributes:
        message_handlers (List[Tuple[List[Union[MagicFilter, 'State']], Callable]]): Список обработчиков сообщений.
        callback_query_handlers (Dict[str, Tuple[List[Union[MagicFilter, 'State']], Callable]]): Словарь обработчиков команд.
        routers (List['Router']): Список вложенных маршрутизаторов.
        fsm (FSM): Состояние машины состояний для управления контекстом.
    """

    def __init__(self):
        """Инициализирует Router с пустыми списками обработчиков и вложенных маршрутизаторов."""
        self.message_handlers = []
        self.callback_query_handlers = {}
        self.routers = []
        self.fsm = FSM()

    def message(self, *filters: Union[MagicFilter, 'State']):
        """
        Декоратор для регистрации обработчика сообщений с указанными фильтрами.

        Args:
            *filters (Union[MagicFilter, State]): Фильтры для обработчика.

        Returns:
            Callable: Декоратор для регистрации обработчика.
        """
        def decorator(func: Callable):
            self.message_handlers.append((list(filters), func))
            return func
        return decorator

    def callback_query(self, *filters: Union[MagicFilter, 'State']):
        """
        Декоратор для регистрации обработчика команд с указанными фильтрами.

        Args:
            *filters (Union[MagicFilter, State]): Фильтры для обработчика.

        Returns:
            Callable: Декоратор для регистрации обработчика.
        """
        def decorator(func: Callable):
            self.callback_query_handlers[func.__name__] = (list(filters), func)
            return func
        return decorator

    def add_router(self, router: 'Router'):
        """
        Добавляет вложенный маршрутизатор в список маршрутизаторов.

        Args:
            router (Router): Вложенный маршрутизатор для добавления.
        """
        self.routers.append(router)

    async def handle_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Обрабатывает сообщение, проходя по списку обработчиков и вызывая соответствующие.

        Args:
            message_data (Dict[str, Any]): Данные сообщения.

        Returns:
            bool: True, если обработчик найден и выполнен, иначе False.
        """
        if message_data.get('event') == "ONIMBOTMESSAGEADD":
            message = Message(message_data)
            fsm_context = await self.fsm.get_context(message.get_chat_id()) if message.get_chat_id() else FSMContext()

            for filters, handler in self.message_handlers:
                if await self._apply_filters(filters, message, fsm_context):
                    logging.debug(f"Handler {handler.__name__} matched for message: {message.get_text()}")
                    await handler(message, fsm_context)
                    return True
            return False

    async def handle_callback_query(self, data: Dict[str, Any]) -> bool:
        """
        Обрабатывает команду, проходя по списку обработчиков и вызывая соответствующие.

        Args:
            data (Dict[str, Any]): Данные команды.

        Returns:
            bool: True, если обработчик найден и выполнен, иначе False.
        """
        if data.get('event') == "ONIMCOMMANDADD":
            parsed_data = await self.parse_command_data(data)
            command = Command(data, parsed_data)
            fsm_context = await self.fsm.get_context(command.get_chat_id()) if command.get_chat_id() else FSMContext()

            for handler_name, (filters, handler) in self.callback_query_handlers.items():
                if await self._apply_filters(filters, command, fsm_context):
                    logging.debug(f"Callback handler {handler_name} matched for command: {command.get_command_name()}")
                    await handler(command, fsm_context)
                    return True
        return False

    async def _apply_filters(self, filters: List[Union[MagicFilter, State]], obj: Union[Message, Command], fsm_context: FSMContext) -> bool:
        """
        Применяет список фильтров к объекту сообщения или команды.
    
        Args:
            filters (List[Union[MagicFilter, State]]): Список фильтров.
            obj (Union[Message, Command]): Объект сообщения или команды.
            fsm_context (FSMContext): Контекст состояния FSM.
    
        Returns:
            bool: True, если все фильтры пройдены, иначе False.
        """
        results = []
        for f in filters:
            if isinstance(f, State):
                current_state = await fsm_context.get_state()
                results.append(current_state == f)
            elif callable(f):  # Проверяем, является ли f callable
                results.append(await f(obj, fsm_context))
            else:                
                results.append(False)  # Возможно, нужно обработать другие типы фильтров или состояния
        
        return all(results)

    async def parse_command_data(self, data: dict) -> dict:
        """
        Парсит данные команды из словаря.

        Args:
            data (dict): Словарь данных команды.

        Returns:
            dict: Распарсенные данные команды.
        """
        command_data = {}

        for key, value in data.items():
            if key.startswith('data[COMMAND]'):
                parts = key.split('[')[2:]
                command_key = parts[1][:-1]
                command_data[command_key.lower()] = value

        await asyncio.sleep(0)
        return command_data

class WebhookListener:
    """
    Класс для прослушивания вебхуков и обработки входящих запросов.

    Attributes:
        host (str): Хост для прослушивания.
        port (int): Порт для прослушивания.
        dispatcher (Dispatcher): Диспетчер для обработки обновлений.
        session (ClientSession): Сессия для HTTP-запросов.
    """

    def __init__(self, host: str, port: int, dispatcher: Dispatcher):
        """
        Инициализация WebhookListener.

        Args:
            host (str): Хост для прослушивания.
            port (int): Порт для прослушивания.
            dispatcher (Dispatcher): Диспетчер для обработки обновлений.
        """
        self.host = host
        self.port = port
        self.dispatcher = dispatcher
        self.session = ClientSession()

    async def handle_post(self, request):
        """
        Обрабатывает POST-запрос вебхука.

        Args:
            request (Request): Запрос вебхука.

        Returns:
            Response: Ответ с текстом "OK".
        """
        data = await request.post()
        data = dict(data)
        logging.debug(f"webhook handle post: {data}")
        await self.dispatcher.process_update(data)
        return web.Response(text="OK")

    async def start(self):
        """
        Запускает прослушивание вебхуков.
        """
        app = web.Application()
        app.router.add_post('/', self.handle_post)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

    async def close(self):
        """
        Закрывает HTTP-сессию.
        """
        await self.session.close()

    async def __aenter__(self):
        """
        Контекстный менеджер для асинхронного запуска прослушивания.

        Returns:
            WebhookListener: Ссылка на себя.
        """
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Контекстный менеджер для асинхронного завершения прослушивания.

        Args:
            exc_type (Type[BaseException]): Тип исключения.
            exc_val (BaseException): Значение исключения.
            exc_tb (TracebackType): Объект трассировки исключения.
        """
        await self.close()