# -*- coding: utf-8 -*-
"""
Created on Sun May 19 13:58:21 2024

@author: Aleksey Rublev RCBD.org
"""

import asyncio
from aiohttp import ClientSession
import logging

from bitrixogram.core import BitrixBot,WebhookListener,Dispatcher

from handlers import barleybreak_handler

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
                
        dp.add_router(barleybreak_handler.barleybreak_router(bx))                          
        
        webhooks = WebhookListener(host=config.server_whook_addr_ip, port=config.server_whook_port, dispatcher=dp)
        await webhooks.start()
        logger.info("Bitrix bot webhook listener started")
        
    
        while True:
            await asyncio.sleep(3600)
            logging.info("Bitrix bot active...")
 
if __name__ == "__main__":
    asyncio.run(main())

