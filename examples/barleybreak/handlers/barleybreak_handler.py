# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 21:42:35 2024

@author:  Aleksey Rublev RCBD.org
"""

from bitrixogram.core import Router, FSMContext, MagicFilter,Message,Command
from keyboards.barleybreak_keyboard import get_barleybreak_kb
from typing import List
import random

router = Router()
F = MagicFilter()

def barleybreak_router(bx):
    def init_game_state() -> List[int]:
        state = list(range(1, 16)) + [0]
        random.shuffle(state)
        return state    

    @router.message(F.text().lower("пятнашки"))
    async def handle_fifteen_game(message:Message, fsm: FSMContext):        
        chat_id = message.get_chat_id()        
                       
        game_state = await fsm.get_data()
        if not game_state or 'game_state' not in game_state or not isinstance(game_state['game_state'], list) or len(game_state['game_state']) != 16:
            game_state = init_game_state()
            await fsm.update_data(game_state=game_state)
        
        else:            
            game_state = init_game_state()
            await fsm.update_data(game_state=game_state)
            
        
        keyboard = get_fifteens_kb(game_state)
        
        result = await bx.send_message(chat_id = chat_id, text="Игра в пятнашки", keyboard=keyboard)
        await fsm.update_data(game_message=result['result'])
      
    @router.callback_query(F.command() == "move")
    async def handle_move(command:Command, fsm: FSMContext):
        command_params=command.get_command_params()
        game_data = await fsm.get_data()
        if 'game_state' not in game_data:
            return
        
        game_state = game_data['game_state']
        num = int(command_params) if command_params!='' else 0
    
        zero_index = game_state.index(0)
        num_index = game_state.index(num)
        
        if (abs(zero_index - num_index) == 1 and zero_index // 4 == num_index // 4) or abs(zero_index - num_index) == 4:
            game_state[zero_index], game_state[num_index] = game_state[num_index], game_state[zero_index]
            await fsm.update_data(game_state=game_state)
        
        keyboard = get_fifteens_kb(game_state)
        
        result = await bx.command_update_message(command=command, text="Игра в пятнашки", keyboard=keyboard)
        await fsm.update_data(game_message=result['result'])
        
        
    return router