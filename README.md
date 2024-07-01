# bitrixogram
A simple async framework for creating Bitrix24 chat bots in 'aiogram'-like style over Bitrix24 REST API  

Supports Bitrix REST API and webhooks, requires JSON format support from the service  
Should work on Python 3.x  

## Documentation
Available on https://github.com/lxxr/bitrixogram

## Dependencies
- aiohttp
- asyncio
- logging

## Example:

### Project sample structure
```
├── bot.py
├── handlers
│   ├── any_handler.py
│   └── message_handler.py
├── keyboards
│   └── main_keyboard.py
├── commands
│   └── commands.py
├── config
│   └── config.py
```

### Create Bot and add routers for handle messages.

```python
import asyncio
from aiohttp import ClientSession
import logging

from bitrixogram.core import BitrixBot,WebhookListener,Dispatcher
from handlers import messages_handler, any_handler

import config.settings as config
import commands.commands as reg_commands


async def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                         level=logging.INFO)
    logger = logging.getLogger(__name__)
    async with ClientSession() as session:
        bx= BitrixBot(config.bitrix_bot_endpoint,config.bitrix_bot_auth,config.bitrix_bot_id, session) 
        await bx.register_commands(reg_commands.commands)
        dp = Dispatcher()
                
        dp.add_router(messages_handler.message_router(bx)) 	            #1
        #.....................................................
        dp.add_router(any_handler.any_router(bx))                           #N
        
        webhooks = WebhookListener(host=config.server_whook_addr_ip, port=config.server_whook_port, dispatcher=dp)
        await webhooks.start()
        logger.info("Bitrix bot webhook listener started")
        
    
        while True:
            await asyncio.sleep(3600)
            logging.info("[Bot] Still active...")
 
if __name__ == "__main__":
    asyncio.run(main())
```

### Handler example

```python
from bitrixogram.core import Router,FSMContext,MagicFilter,Message,Command,State,StatesGroup
from bitrixogram.attach import ReplyAttachMarkup, ReplyAttachBuilder, GridLayout
from keyboards.main_keyboard import get_main_kb

F = MagicFilter()
router = Router()


class TestState(StatesGroup):
    test1_state = State()
    test2_state = State()

def any_router(bx):
    @router.message(TestState.test1_state,((F.text()=="test2") | (F.text()=="test3")))
    async def handle_message_add_event_test_state1(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        state= await fsm.get_state()
        print(f"get state test1: {state}")
        await bx.send_message(
            chat_id=chat_id,
            text="any router test - state1"
        )
        await fsm.set_state(TestState.test2_state)
        
    @router.message(TestState.test2_state,(F.text()))        
    async def handle_message_add_event_test_state2(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        state= await fsm.get_state()
        print(f"get state test2: {state}")
        await bx.send_message(
            chat_id=chat_id,
            text="any router test - state2"
        )        
        await fsm.clear_state()
        
    @router.message(F.text()=="test")
    async def handle_message_add_event_test(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        await fsm.set_state(TestState.test1_state)
        state= await fsm.get_state()
        print(f"set state: {state}")
        await bx.send_message(
            chat_id=chat_id,
            text="any router test"
        
        )
        
    @router.message(F.text())
    async def handle_message_add_event_other_text(message: Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()
        await bx.send_message(chat_id, "Any text handler")
        
    @router.callback_query(F.command())
    async def handle_message_add_event_other_command(command:Command, fsm:FSMContext):
        message_id = command.get_message_id()
	builder = ReplyAttachBuilder()

	column_layout = builder.grid_column_layout().add_item(name="priority", value="High").add_item(name="Category", value="Task")
	block_layout = builder.grid_block_layout().add_item(name="Description", value="new version of API", width=250).add_item(name="Category", value="Task", width=100)
	line_layout = builder.grid_line_layout().add_item(name="Priority", value="High", color="#ff0000", width=250).add_item(name="Category", value="Task")
	#attach example
	attach = (builder
	    .user(name="John Smith", avatar="{image_link}", link="https://api.bitrix24.com/")
	    .link(name="Issue #12345: new API \"Webhook listener\"", link="https://api.bitrix24.com/", desc="release notes", preview="{image_link}", width=1000, height=638)
	    .message("API version [B]im 1.1.0[/B]")
	    .delimiter(size=200, color="#c6c6c6")
	    .grid(column_layout)
	    .grid(block_layout)
	    .grid(line_layout)
	    .image(link="{image_link}", name="img name", preview="{image_preview_link}", width=1000, height=638)
	    .file(link="{file_link}", name="image.jpg", size=1500000)
	    .build()).to_dict()

	keyboard=get_main_kb()
        await bx.command_answer(command=command,text=f"This is command - {command.get_command_name()}", attach=attach ,keyboard=keyboard)

    return router
```
### Keyboard example

```python
from bitrixogram.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="-",command="dec")
    kb.button(text="+",command ="inc")
    kb.button(text="=",command = "sum")
    kb.button(text="5",command = "info")
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True)
```

### Commands example
```python

import config.settings as config

whook_endpoint = config.ip_whook_endpoint
commands = [
              {'COMMAND': 'inc',  'TITLE': '+','PARAMS': 'text', 'EVENT_COMMAND_ADD': whook_endpoint},
              {'COMMAND': 'dec',  'TITLE': '-','PARAMS': 'text', 'EVENT_COMMAND_ADD': whook_endpoint},
	      {'COMMAND': 'info', 'TITLE': '?','PARAMS': 'text', 'EVENT_COMMAND_ADD': whook_endpoint},
              {'COMMAND': 'sum',  'TITLE': '=','PARAMS': 'text', 'EVENT_COMMAND_ADD': whook_endpoint} ]

```

### Config example
```python
#endpoints  
bitrix_bot_endpoint=" https://xxx.xxx.xxx/rest/xx/xxx/" #Webhook for REST API
ip_whook_endpoint='http://WEBHOOK_IP_ADDRESS:WEBHOOK_PORT/' #External webhook server

#webhook server 
server_whook_addr_ip = "LOCAL_SERVER_IP" # Check route from ext interface
server_whook_port = LOCAL_SERVER_PORT

#bitrix bot auth and id
bitrix_bot_auth = "YOUR_BOT_AUTH_TOKEN" #Check in bitrix bot settings
bitrix_bot_id=BITRIX_BOT_CLIENT_ID #Check in bitrix bot settings
```

