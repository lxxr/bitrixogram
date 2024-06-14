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
    def __init__(self, bot_endpoint:str,  bot_token: str,bot_id:str, session: ClientSession):
        self.bot_token = bot_token
        self.base_url = bot_endpoint
        self.base_id = bot_id
        self.dispatcher = Dispatcher()
        self.fsm = FSM()        
        self.session = session  

                
    async def register_commands(self,commands):
     
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
        
        data = {
            'BOT_ID': self.base_id,
            'MESSAGE_ID': message_id,            
            'COMPLETE': complete
        }
        logging.debug(f"delete_message data: {data}")   
        response = await self.rest_command("imbot.message.delete", params=data)
        return response
 
    async def command_update_message(self, text: str, command: 'Command' , attach:Dict[str, Any] = None, chat_id: int = None,message_id: int = None, keyboard: 'ReplyKeyboardMarkup' = None):
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
       url = self.base_url + 'imbot.register'
       data = {'EVENT_HANDLER': webhook_url}
       async with self.session.post(url, json=data) as response:
           return await response.json()

    async def handle_update(self, update: Dict[str, Any]):
        self.dispatcher.process_update(self, update, self.fsm)

    async def register_message_handler(self, handler: Callable, commands: List[str] = None, state: str = None):
        self.dispatcher.register_message_handler(handler, commands, state)
    
    def flatten_params(self,json_data, parent_key='', separator='_'):
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
    def __init__(self, state: str = None):
        self.state = state
        self.data = {}        
         
        
    async def set_state(self, state: str):
        self.state = state

    async def get_state(self) -> str:
        return self.state

    async def update_data(self, **kwargs):
        self.data.update(kwargs)

    async def get_data(self):
        return self.data
    
    async def get_chat_id(self) -> int:
        return self.chat_id

class FSM:
    def __init__(self):
        self.contexts = {}

    async def get_context(self, chat_id: int) -> FSMContext:
        if chat_id not in self.contexts:
            self.contexts[chat_id] = FSMContext()
        return self.contexts[chat_id]

class Message:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def get_text(self) -> str:
        return self.data.get('data[PARAMS][MESSAGE]', '')

    def get_message_id(self) -> int:
        return int(self.data.get('data[PARAMS][MESSAGE_ID]', 0))

    def get_chat_id(self) -> int:
        return int(self.data.get('data[PARAMS][DIALOG_ID]', 0))

    def get_user_id(self) -> int:
        return int(self.data.get('data[USER][ID]', 0))

    def get_raw_data(self) -> Dict[str, Any]:
        return self.data


class Command:
    def __init__(self, data: Dict[str, Any], parsed_data: Dict[str, Any]):
        self.data = data
        self.parsed_data = parsed_data

    def get_command_name(self) -> str:
        return self.parsed_data.get('command', '')

    def get_command_id(self) -> str:
        return self.parsed_data.get('command_id', '')

    def get_command_params(self) -> str:
        return self.parsed_data.get('command_params', '')

    def get_command_raw_params(self) -> Dict[str, Any]:
        return self.parsed_data

    def get_chat_id(self) -> int:
        return int(self.data.get('data[PARAMS][DIALOG_ID]', 0))

    def get_user_id(self) -> int:
        return int(self.data.get('data[USER][ID]', 0))

    def get_message_id(self) -> int:
        return int(self.data.get('data[PARAMS][MESSAGE_ID]', 0))    

    def get_raw_data(self) -> Dict[str, Any]:
        return self.data



class MagicFilter:
    def __init__(self, filter_func: Callable[[Union[Message, Command], 'FSMContext'], Union[bool, Awaitable[bool]]] = None):
        self.filter_func = filter_func

    @classmethod
    def text(cls):
        return cls(lambda obj, fsm_context: isinstance(obj, Message))

    @classmethod
    def command(cls):
        return cls(lambda obj, fsm_context: isinstance(obj, Command))

    def lower(self, expected_text: str):
        return MagicFilter(lambda obj, fsm_context: isinstance(obj, Message) and obj.get_text().lower() == expected_text.lower())

    def startswith(self, expected_text: str):
        return MagicFilter(lambda obj, fsm_context: isinstance(obj, Message) and obj.get_text().lower().startswith(expected_text))

    async def __call__(self, obj: Union[Message, Command], fsm_context: 'FSMContext') -> bool:
        if self.filter_func:
            result = self.filter_func(obj, fsm_context)
            if asyncio.iscoroutine(result):
                return await result
            return result
        return True

    def _combine(self, other, op):
        return MagicFilter(lambda obj, fsm_context: op(self.__call__(obj, fsm_context), other.__call__(obj, fsm_context)))

    def __and__(self, other):
        return self._combine(other, operator.and_)

    def __or__(self, other):
        return self._combine(other, operator.or_)

    def __eq__(self, other):
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) == other)

    def __ne__(self, other):
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) != other)

    def __lt__(self, other):
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) < other)

    def __le__(self, other):
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) <= other)

    def __gt__(self, other):
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) > other)

    def __ge__(self, other):
        return MagicFilter(lambda obj, fsm_context: self._get_value(obj) >= other)

    def __getitem__(self, key):
        return MagicFilter(lambda obj, fsm_context: self._get_nested_value(obj.get_raw_data(), key))

    def _get_value(self, obj: Union[Message, Command]) -> Any:
        return obj.get_text() if isinstance(obj, Message) else obj.get_command_name()

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        keys = key.split('.')
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k)
            else:
                return None
        return data
#     def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:        
#         if isinstance(data, dict):
#             json_str = json.dumps(data)            
#             json_data = json.loads(json_str)
#             value = json_data[key]            
#         else:
#             return None
#         return value    

    @property
    def message(self):
        return self

class Dispatcher:
    def __init__(self):
        self.routers = []
        self.FSM = FSM()


    def add_router(self, router):
        self.routers.append(router)

    async def process_update(self, update: Dict[str, Any], fsm: 'FSM'):
        for router in self.routers:
            handled = await router.handle_message(update)
            if handled:
                break  
            else:
                handled = await router.handle_callback_query(update)
                if handled:
                    break    

class Router:
    def __init__(self):
        self.message_handlers = []
        self.routers = []
        self.callback_query_handlers = {}
        self.fsm = FSM()

    def message(self, filter: MagicFilter):
        def decorator(func: Callable):
            self.message_handlers.append((filter, func))
            return func

        return decorator

    def callback_query(self, filter: MagicFilter):
        def decorator(func: Callable):
            self.callback_query_handlers[func.__name__] = (filter, func)
            return func
        return decorator

    def add_router(self, router: 'Router'):
        self.routers.append(router)

    def register_message_handler(self, handler: Callable, filter: MagicFilter = None):
        self.message_handlers.append((filter, handler))

    async def handle_message(self, message_data: Dict[str, Any]) -> bool:
        if message_data.get('event') == "ONIMBOTMESSAGEADD":
            message = Message(message_data)
            fsm_context = await self.fsm.get_context(message.get_chat_id()) if message.get_chat_id() else FSMContext()

            for filter_, handler in self.message_handlers:
                if await filter_(message, fsm_context):
                    await handler(message, fsm_context)
                    return True
            return False

    async def parse_command_data(self, data: dict) -> dict:
        command_data = {}

        for key, value in data.items():
            if key.startswith('data[COMMAND]'):
                parts = key.split('[')[2:]
                command_key = parts[1][:-1]
                command_data[command_key.lower()] = value

        await asyncio.sleep(0)
        return command_data

    async def handle_callback_query(self, data: Dict[str, Any]) -> bool:
        if data.get('event') == "ONIMCOMMANDADD":
            parsed_data = await self.parse_command_data(data)
            command = Command(data, parsed_data)
            fsm_context = await self.fsm.get_context(command.get_chat_id()) if command.get_chat_id() else FSMContext()

            for handler_name, (filter_, handler) in self.callback_query_handlers.items():
                if await filter_(command, fsm_context):
                    await handler(command, fsm_context)
                    return True
        return False

class WebhookListener:
    def __init__(self, host: str, port: int, dispatcher: Dispatcher ):
        self.host = host
        self.port = port        
        self.dispatcher = dispatcher
        self.session = ClientSession() 

    async def handle_post(self, request):
        data = await request.post()
        data = dict(data)
        logging.debug(f"webhook handle post: {data}")
        await self.dispatcher.process_update(data, FSM())
        
        return web.Response(text="OK")

    async def start(self):
        app = web.Application()
        app.router.add_post('/', self.handle_post)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
    
    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
