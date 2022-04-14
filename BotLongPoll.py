#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import vk_api
import random
import time
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from io import BytesIO
from vk_api.upload import VkUpload
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import Pokemon
import info_pokemon
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json

with open('files/token_0.txt', 'r', encoding='utf-8') as file:
    vk_session = vk_api.VkApi(token=file.readline())
    

class bot_vk():
    def __init__(self, vk_session):
        self.vk_session = vk_session
        self.longpoll = VkBotLongPoll(self.vk_session, wait=25, group_id=200008678) #, group_id=207883458  /  200008678
        self.vk = vk_session.get_api()
        self.upload = VkUpload(self.vk)
        self.list_name_category = ['admin', 'moderator'] #, ['admin', 'moderator', 'support']
        
        self.game = dict()
        self.game_msg = [list()]
        self.game_time_life = 60  # 60
            
        self.list_mute = dict()
        self.user_csv = pd.read_csv('files/user.csv')
        
        self.server_flag = 1 # 0
        self.chat_flag = 1
        self.time = time.time()
        
        self.raid_flag = 0
        self.raid_creator = ''
        self.raid_creator_info = list()
        self.raid_boss = ''
        
        self.all_commands = ['обнять', 'шлёпнуть', 'шлепнуть', 'укусить', 'погладить', 'поцеловать', 'ударить', 'поздравить', 'убить', 'обосрать', 'покебол', 'война'] + ['/тест', '/тест2', '/тест3', '/test', '/test2', '/test3', '/список', 'токсик', 'бот,']
        self.commands_msg = [list(), list()]
        
    def start(self):
        if self.server_flag == 0:
            self.check_msg()
        else:
            while True:
                try:
                    if self.check_msg() == False:
                        break
                except: #requests.exceptions.ReadTimeout
                    msg = "Переподключение к серверам ВК"
                    self.add_error(msg)
                    time.sleep(3)
    
    def check_msg(self):
        for event in self.longpoll.listen():
#             print(event)
            if time.time() > self.time + 20:
                self.upload = VkUpload(self.vk)
                self.time = time.time()
                    
            event_type = event.type
            if len(self.game) != 0:
                self.keyboard_battle_delete_auto(event.object)
                
            if event_type == VkBotEventType.MESSAGE_NEW:
                event_text = event.object.message['text']
                event_from_user = event.object.message['from_id'] == event.object.message['peer_id']
                event_from_chat = event.object.message['from_id'] != event.object.message['peer_id']
                event_msg = event.object.message
                    
                if event_text and event_from_user:
                    if event_text.split()[0].lower() == '/test' or event_text.split()[0].lower() == '/тест':
                        self.test_user(event_msg)

                if event_from_chat:
                    self.check_mute(event_msg)
                    self.update_mute(event_msg)

                if event_text and event_from_chat:
#                     print(event_text)
                    if event_text.split()[0].lower() == '/правила':
                        self.rules(event_msg)
                    elif event_text.split()[0].lower() == '/botadmin':
                        self.print_category(event_msg, self.list_name_category)
                    elif event_text.split()[0].lower() == '/admin' or event_text.split()[0].lower() == '/админ':
                        self.admin_list(event_msg)
                    elif event_text.split()[0].lower() == 'delete' and event_text.split()[1].lower() in self.list_name_category:
                        if self.checking_access_rights(event_msg, ['admin']):
                            self.delete_category(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'append' and event_text.split()[1].lower() in self.list_name_category:
                        members = self.vk.messages.getConversationMembers(peer_id=event_msg['peer_id'])
                        for i in members["items"]:
                             if i["member_id"] == event_msg['from_id']:
                                admin = i.get('is_admin', False)
                        if admin or self.checking_access_rights(event_msg, ['admin']):
                            self.append_category(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'del' or event_text.split()[0].lower() == '/del':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.delete_message(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'ban' or event_text.split()[0].lower() == '/ban':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.ban_user(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'unban' or event_text.split()[0].lower() == '/unban':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.unban_user(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'kick' or event_text.split()[0].lower() == '/kick':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.kick_user(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'mute' or event_text.split()[0].lower() == '/mute':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.mute(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == 'unmute' or event_text.split()[0].lower() == '/unmute':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.unmute(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == '/бой' and len(self.game) == 0 and self.raid_flag == 0:
                        self.keyboard_battle(event_msg)
                    elif event_text.split()[0].lower() == '/бойотмена' and len(self.game) != 0:
                        self.keyboard_battle_delete(event_msg)
                    elif event_text.split()[0].lower() == '/pokemon' or event_text.split()[0].lower() == '/покемон':
                        self.get_pokemon(event_msg)
                    elif event_text.split()[0].lower() == '/p' or event_text.split()[0].lower() == '/п':
                        self.get_pokemon_full(event_msg)
                    elif event_text.split()[0].lower() == '/рейдбосс' and self.raid_flag == 0:
                        self.raid(event_msg)
                    elif event_text.split()[0].lower() == '/рейд' and self.raid_flag == 0:
                        self.quick_raid(event_msg)
                    elif event_text.split()[0].lower() == '/отмена' and self.raid_flag == 1:
                        self.cancellation_raid(event_msg)
                    elif event_text.split()[0].lower() == '/беру' and self.raid_flag == 1:
                        self.raid_take(event_msg)
                    elif event_text.split()[0].lower() == '/участвую' and self.raid_flag == 1:
                        self.raid_participate(event_msg)
                    elif event_text.split()[0].lower() == '/help':
                        self.print_help(event_msg)
                    elif event_text.split()[0].lower() == '/adminhelp':
                        if self.checking_access_rights(event_msg, ['admin', 'moderator']):
                            self.print_admin_help(event_msg)
                        else:
                            self.insufficient_rights(event_msg)
                    elif event_text.split()[0].lower() == '/oldinfo'or event_text.split()[0].lower() == '/олдинфо':
                        self.old_info_about_user(event_msg)
                    elif event_text.split()[0].lower() == '/addinfo':
                        self.user_info(event_msg)
                    elif event_text.split()[0].lower() == '/info' or event_text.split()[0].lower() == '/инфо':
                        self.info_about_user(event_msg)
                    elif event_text.split()[0].lower() == '/рейтинг':
                        self.number_messages_about_user(event_msg)
                    elif event_text.split()[0].lower() == '/ранг':
                        self.rank_criterion(event_msg)
                    elif event_text.split()[0].lower() == '/top' or event_text.split()[0].lower() == '/топ':
                        self.top_users(event_msg, 1)
                    elif event_text.split()[0].lower() == '/topraid' or event_text.split()[0].lower() == '/топрейдов':
                        self.top_users(event_msg, 2)
                    elif event_text.split()[0].lower() == '/topparticipate' or event_text.split()[0].lower() == '/топучастия':
                        self.top_users(event_msg, 3)
                    elif event_text.split()[0].lower() == '/topbattle' or event_text.split()[0].lower() == '/топцуефа' or event_text.split()[0].lower() == '/топбой':
                        self.top_users(event_msg, 4)
                    elif event_text.split()[0].lower() == '/test' or event_text.split()[0].lower() == '/тест':
                        self.test(event_msg)
                    elif event_text.split()[0].lower() == '/список' and len(event_text.split()) == 2 and event_text.split()[1].lower() == 'рп':
                        self.print_list_rp(event_msg)
                    elif event_text.split()[0].lower() == '/keyboard':
                        if self.checking_access_rights(event_msg, ['admin']):
                            self.main_keyboard(event_msg)
                    elif event_text.split()[0].lower() == '/стоп':
                        if self.checking_access_rights(event_msg, ['admin']):
                            return False
                    elif event_text.split()[0].lower() == '/смена':
                        if self.checking_access_rights(event_msg, ['admin']):
                            self.change_type_raid(event_msg)
                    elif event_text.split()[0].lower() == '/отм':
                        if self.checking_access_rights(event_msg, ['admin']):
                            self.admin_cancellation_raid(event_msg)
                    elif '@all' in event_text and '@allexceptpragov' not in event_text:
                        self.delete_all(event_msg)
                    elif event_text.split()[0].lower() not in self.all_commands:
                        self.append_message(int(event_msg['from_id']))
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                self.check_keyboard(event.object)
                    
                
                    
    def checking_access_rights(self, event, rights_category: list):
        flag = 0
        for i in rights_category:
            with open('files/{i}.txt'.format(i=i), 'r+', encoding='utf-8') as file:
                if str(event['from_id']) in ''.join(file.readlines()):
                    flag = 1
        if flag == 1:
            return True
        return False

    def add_error(self, msg_error):
        tmp_lines = list()
        now = time.ctime(int(time.time()))
        with open('files/errors.txt', 'r+', encoding='utf-8') as file:
            tmp_lines = file.readlines()
        tmp_lines.append(msg_error + ' ' + now + '\n')
        with open('files/errors.txt', 'w+', encoding='utf-8') as file:
            for i in tmp_lines:
                file.write(i)
    
    def test(self, event):
        msg = 'Бот работает в штатном режиме'
        self.messages_send(event, msg)

    def test_user(self, event):
        msg = 'Бот работает в штатном режиме'
        self.messages_send_user(event, msg)
        
    def insufficient_rights(self, event):
#         self.vk.messages.send(
#             peer_id=event.peer_id,
#             message='У вас недостаточно прав для выполнения данного действия',
#             random_id=random.randint(1, 1000)
#         )
        pass
        
    def messages_send(self, event, msg, attachments=[], peer_id=None, keyboard=None, flag=0):
        if peer_id == None:
            peer_id=event['peer_id']
        conversation_message_id = self.vk.messages.send(
            peer_id=peer_id,
            message=msg,
            random_id=time.time() * 1000,
            keyboard=keyboard,
            attachment=attachments,
            disable_mentions=flag
        )
        return conversation_message_id
        
    def messages_send_user(self, event, msg,attachments=[], keyboard=None):
        self.vk.messages.send(
            peer_id=event['peer_id'],
            message=msg,
            random_id=time.time() * 1000,
            keyboard=keyboard,
            attachment=attachments
        )
        
    def messages_delete(self, event, message_id_delete=[], peer_id=None):
        if peer_id == None:
            peer_id=event['peer_id']
        self.vk.messages.delete(
            peer_id=peer_id,
            conversation_message_ids=message_id_delete,
            delete_for_all=1
            )
    
    def kick_user_by_bot(self, peer_id, ids):
        self.vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=ids)
     
    def updt(self):
        self.vk.messages.send(
            peer_id=156032946,
            message='Bot is OK.',
            random_id=time.time() * 1000
        )
    
    def check_main_keyboard(self, event):
        text = event.payload.get('text')

        if text == '/info':
            event['text'] = '/info'
            event['from_id'] = event.user_id
            self.info_about_user(event, flag_keyboard=1)
        elif text == '/рейтинг':
            event['text'] = '/рейтинг'
            event['from_id'] = event.user_id
            self.number_messages_about_user(event, flag_keyboard=1)
        elif text == '/ранг':
            event['text'] = '/ранг'
            event['from_id'] = event.user_id
            self.rank_criterion(event, flag_keyboard=1)
        elif text == '/список рп':
            event['text'] = '/список рп'
            event['from_id'] = event.user_id
            self.print_list_rp(event, flag_keyboard=1)
        elif text == '/топ':
            event['text'] = '/топ'
            event['from_id'] = event.user_id
            self.print_top_keyboard(event, flag_keyboard=1)
        elif text == '/бой' and self.raid_flag == 0:
            if len(self.game) == 0:
                event['text'] = '/бой'
                event['from_id'] = event.user_id
                self.keyboard_battle(event, flag_keyboard=1)
            
        self.vk.messages.sendMessageEventAnswer(
            event_id=event.event_id,
            user_id=event.user_id,
            peer_id=event.peer_id)
        
    def main_keyboard(self, event, flag_keyboard=0):
        settings = dict(one_time=False, inline=False)
        keyboard_1 = VkKeyboard(**settings)

        keyboard_1.add_callback_button(label='Инфо', color=VkKeyboardColor.SECONDARY, payload={"type": "main", "text": "/info"})
        keyboard_1.add_callback_button(label='Рейтинг', color=VkKeyboardColor.SECONDARY, payload={"type": "main", "text": "/рейтинг"})
        keyboard_1.add_callback_button(label='Ранги', color=VkKeyboardColor.SECONDARY, payload={"type": "main", "text": "/ранг"})
        keyboard_1.add_line()
        keyboard_1.add_callback_button(label='Список РП', color=VkKeyboardColor.SECONDARY, payload={"type": "main", "text": "/список рп"})
        keyboard_1.add_callback_button(label='Топ пользователей', color=VkKeyboardColor.SECONDARY, payload={"type": "main", "text": "/топ"})
        keyboard_1.add_line()
        keyboard_1.add_callback_button(label='Бой', color=VkKeyboardColor.SECONDARY, payload={"type": "main", "text": "/бой"})
        if flag_keyboard == 0:
            self.vk.messages.send(
                random_id=time.time() * 1000,
                peer_id=event['peer_id'],
                keyboard=keyboard_1.get_keyboard(),
                message='keyboard')
        else:
            return keyboard_1.get_keyboard()
        
    def print_top_keyboard(self, event, flag_keyboard=0):
        msg = f'Топ 🔝:'
        msg = f'&#12288;'
        if flag_keyboard == 0:
            self.messages_delete(event, event['conversation_message_id'])
        last_id = self.messages_send(event, msg, keyboard=self.top_keyboard(), flag=1)
        tmp = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=last_id)['items'][0]['conversation_message_id']
        self.commands_msg[0].append(tmp)
        if len(self.commands_msg[0]) > 1:
            self.messages_delete(event, self.commands_msg[0][0])
            del self.commands_msg[0][0]
        
    def top_keyboard(self):
        settings = dict(one_time=False, inline=True)
        keyboard_1 = VkKeyboard(**settings)

        keyboard_1.add_callback_button(label='✉✉✉', color=VkKeyboardColor.SECONDARY, payload={"type": "top", "text": "/топ 1"})
        keyboard_1.add_callback_button(label='⚔⚔⚔', color=VkKeyboardColor.SECONDARY, payload={"type": "top", "text": "/топ 2"})
        keyboard_1.add_line()
        keyboard_1.add_callback_button(label='👥👥👥', color=VkKeyboardColor.SECONDARY, payload={"type": "top", "text": "/топ 3"})
        keyboard_1.add_callback_button(label='🏆🏆🏆', color=VkKeyboardColor.SECONDARY, payload={"type": "top", "text": "/топ 4"})
        
        return keyboard_1.get_keyboard()
        
    def check_top_keyboard(self, event):
        text = event.payload.get('text')
        
        if text == '/топ 1':
            event['text'] = '/топ'
            event['from_id'] = event.user_id
            self.top_users(event, 1, flag_keyboard=1)
        elif text == '/топ 2':
            event['text'] = '/топ'
            event['from_id'] = event.user_id
            self.top_users(event, 2, flag_keyboard=1)
        elif text == '/топ 3':
            event['text'] = '/топ'
            event['from_id'] = event.user_id
            self.top_users(event, 3, flag_keyboard=1)
        elif text == '/топ 4':
            event['text'] = '/топ'
            event['from_id'] = event.user_id
            self.top_users(event, 4, flag_keyboard=1)
            
        r = self.vk.messages.sendMessageEventAnswer(event_id=event.event_id, user_id=event.user_id, peer_id=event.peer_id)
        
    def check_raid_keyboard(self, event):
        text = event.payload.get('text')

        if text == '/участвую':
            event['text'] = '/участвую'
            event['from_id'] = event.user_id
            self.raid_participate(event, flag_keyboard=1)
        
        self.vk.messages.sendMessageEventAnswer(
            event_id=event.event_id,
            user_id=event.user_id,
            peer_id=event.peer_id)
        
    def raid_keyboard(self):
        settings = dict(one_time=False, inline=True)
        keyboard_1 = VkKeyboard(**settings)

        keyboard_1.add_callback_button(label='Участвовать', color=VkKeyboardColor.SECONDARY, payload={"type": "raid", "text": "/участвую"})
        keyboard_1.add_line()
        label = f'@all ⚔ Сбор на рейд {self.raid_boss}'
        keyboard_1.add_button(label=label, color=VkKeyboardColor.SECONDARY)
        return keyboard_1.get_keyboard()
    
    def name_user(self, user_id):
        people = self.vk.users.get(user_ids=user_id)[0]
        first_name, last_name = people['first_name'], people['last_name']
        name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
        return name
    
    def check_keyboard(self, event):
        if event.payload.get('type') == 'main':
            self.check_main_keyboard(event)
            return 0
        elif event.payload.get('type') == 'raid':
            self.check_raid_keyboard(event)
            return 0
        elif event.payload.get('type') == 'top':
            self.check_top_keyboard(event)
            return 0
                                                                                             
        flag = False
        if 'player_1' in self.game.keys() and event.user_id == self.game['player_1']:
            flag = True
            self.game['flag_1'] = True
            if event.payload.get('type') == 'grass':
                self.game['player_1_type'] = 0
            elif event.payload.get('type') == 'fire':
                self.game['player_1_type'] = 1
            elif event.payload.get('type') == 'water':
                self.game['player_1_type'] = 2
        elif 'player_2' in self.game.keys():
            flag = True
            if self.game['player_2'] != -1:
                if event.user_id == self.game['player_2']:
                    self.game['flag_2'] = True
                    if event.payload.get('type') == 'grass':
                        self.game['player_2_type'] = 0
                    elif event.payload.get('type') == 'fire':
                        self.game['player_2_type'] = 1
                    elif event.payload.get('type') == 'water':
                        self.game['player_2_type'] = 2
            else:
                self.game['player_2'] = event.user_id
                self.game['flag_2'] = True
                if event.payload.get('type') == 'grass':
                    self.game['player_2_type'] = 0
                elif event.payload.get('type') == 'fire':
                    self.game['player_2_type'] = 1
                elif event.payload.get('type') == 'water':
                    self.game['player_2_type'] = 2

        if flag:
            r = self.vk.messages.sendMessageEventAnswer(event_id=event.event_id, user_id=event.user_id, peer_id=event.peer_id)
            if self.game['flag_1'] and self.game['flag_2']:
                player_1 = self.name_user(self.game['player_1'])
                player_2 = self.name_user(self.game['player_2'])
                msg = f'Дуэль между {player_1} x {player_2}'
                self.messages_delete(event, event.conversation_message_id)
                last_id = self.messages_send(event, msg, flag=1)
                self.game['conversation_message_id'] = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=last_id)['items'][0]['conversation_message_id']
                self.game_msg[0].append(self.game['conversation_message_id'])
                #last_id = self.vk.messages.edit(peer_id=event.peer_id, message=msg, conversation_message_id=event.conversation_message_id, disable_mentions=1)
                self.rock_paper_scissors(event, 1)
                self.rock_paper_scissors(event, 2)
                
    def keyboard_battle_delete(self, event):
        text, text_id = '', ''
        self.messages_delete(event, event['conversation_message_id'])
        if 'reply_message' not in event.keys() and len(event['fwd_messages']) == 0:
            msg = 'Перешлите сообщение о создании игры'
            self.messages_send(event, msg)
            return 0
        elif event['fwd_messages'] != []:
            text = event['fwd_messages'][0]['text']
            text_id = event['fwd_messages'][0]['conversation_message_id']
        elif 'reply_message' in event.keys():
            text = event['reply_message']['text']
            text_id = event['reply_message']['conversation_message_id']

        if not('бой' in text.lower() and 'игрока' in text.lower()):
            msg = 'Перешлите сообщение о создании игры'
            self.messages_send(event, msg)
            return 0

        if not(event['from_id'] == self.game['player_1'] or self.checking_access_rights(event, ['admin', 'moderator'])):
            msg = 'Отменить игру может только ее создатель или администратор'
            self.messages_send(event, msg)
            return 0

        people = self.vk.users.get(user_ids=self.game['player_1'])[0]
        first_name, last_name = people['first_name'], people['last_name']

        msg = 'Игра игрока @id{user_id} ({first_name} {last_name}) отменена.'.format(user_id=self.game['player_1'], first_name=first_name, last_name=last_name)

        last_id = self.vk.messages.edit(peer_id=event['peer_id'], message=msg, conversation_message_id=text_id)
        self.game_msg[0].append(text_id)
        
        self.game = dict()
        
    def keyboard_battle_delete_auto(self, event):
        if time.time() > self.game['time'] + self.game_time_life:
            if 'message' in event.keys():
                event = event['message']
            people = self.vk.users.get(user_ids=self.game['player_1'])[0]
            first_name, last_name = people['first_name'], people['last_name']
            msg = 'Игра игрока @id{user_id} ({first_name} {last_name}) отменена автоматически.'.format(user_id=self.game['player_1'], first_name=first_name, last_name=last_name)
            conversation_message_id = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=self.game['conversation_message_id'])['items'][0]['conversation_message_id']
            last_id = self.vk.messages.edit(peer_id=event['peer_id'], message=msg, conversation_message_id=conversation_message_id)

            self.game_msg[0] = list()
            self.game_msg[0].append(conversation_message_id)
            
            self.game = dict()
    
    def keyboard_battle(self, event, flag_keyboard=0):
        if flag_keyboard == 0:
            self.messages_delete(event, event['conversation_message_id'])
        if len(event['text'].split()) != 2:
            if 'reply_message' in event.keys():
                user_id = event['reply_message']['from_id']
            else:
                user_id = -1
        else:
            tmp_id = event['text'].split()[1]
            if 'id' in tmp_id and '@' in tmp_id:
                user_id = tmp_id[1:-1].split('|')[0][2:]
            else:
                msg = 'Неправильная форма запроса.'
                self.messages_send(event, msg)
        
        settings = dict(one_time=False, inline=True)
        keyboard_1 = VkKeyboard(**settings)

        keyboard_1.add_callback_button(label='Трава', color=VkKeyboardColor.POSITIVE, payload={"type": "grass"})
        keyboard_1.add_callback_button(label='Огонь', color=VkKeyboardColor.NEGATIVE, payload={"type": "fire"})
        keyboard_1.add_callback_button(label='Вода', color=VkKeyboardColor.PRIMARY, payload={"type": "water"})

        name = self.name_user(event['from_id'])
        
        if user_id == -1:
            msg = f'Бой игрока {name} со случайным игроком.'
        else:
            name_2 = self.name_user(user_id)
            msg = f'Бой игрока {name} с игроком {name_2}.'
        
        self.game['time'] = time.time()
        self.game['conversation_message_id'] = self.messages_send(event, msg, keyboard=keyboard_1.get_keyboard(), flag=1)
        
        self.game['player_1'] = int(event['from_id'])
        self.game['player_2'] = int(user_id)
        self.game['flag_1'] = False
        self.game['flag_2'] = False
        
        if len(self.game_msg) == 2:
            for i in self.game_msg[1]:
                self.messages_delete(event, i)
            self.game_msg[1], self.game_msg[0] = self.game_msg[0], list()
        elif len(self.game_msg) == 1:
            self.game_msg.append(list())
            self.game_msg[1], self.game_msg[0] = self.game_msg[0], list()
        
    def check(self):
        if self.game['player_1_type'] == self.game['player_2_type']:
            return 0
        
        if self.game['player_1_type'] == 2 and self.game['player_2_type'] == 1:
            return 1
        if self.game['player_1_type'] == 2 and self.game['player_2_type'] == 0:
            return 2
        
        if self.game['player_1_type'] == 1 and self.game['player_2_type'] == 0:
            return 1
        if self.game['player_1_type'] == 1 and self.game['player_2_type'] == 2:
            return 2

        if self.game['player_1_type'] == 0 and self.game['player_2_type'] == 2:
            return 1
        if self.game['player_1_type'] == 0 and self.game['player_2_type'] == 1:
            return 2
        
        return 'Error'
        
    def rock_paper_scissors(self, event, number_player):
        try:
            list_pokemon = [[[1, 152, 252, 387, 495, 650, 810], [4, 155, 255, 390, 498, 653, 813], [7, 158, 258, 393, 501, 656, 816]],
                            [[2, 153, 253, 388, 496, 651, 811], [5, 156, 256, 391, 499, 654, 814], [8, 159, 259, 394, 502, 657, 817]],
                            [[3, 154, 254, 389, 497, 652, 812], [6, 157, 257, 392, 500, 655, 815], [9, 160, 260, 395, 503, 658, 818]]]
            dick_pokemon_name = {'1': 'Бульбазавра',
                                '2': 'Айвизавра',
                                '3': 'Венузавра',
                                '4': 'Чармандера',
                                '5': 'Чармелеона',
                                '6': 'Чаризарда',
                                '7': 'Сквиртла',
                                '8': 'Вартортла',
                                '9': 'Бластойза',
                                '152': 'Чикорита',
                                '153': 'Бейлифа',
                                '154': 'Меганиума',
                                '155': 'Синдаквила',
                                '156': 'Квилава',
                                '157': 'Тайфложна',
                                '158': 'Тотодайла',
                                '159': 'Кроконава',
                                '160': 'Фералигатора',
                                '252': 'Трикко',
                                '253': 'Гровайла',
                                '254': 'Септайла',
                                '255': 'Торчика',
                                '256': 'Комбаскена',
                                '257': 'Блазикена',
                                '258': 'Мадкипа',
                                '259': 'Марштомпа',
                                '260': 'Свамперта',
                                '387': 'Тортвига',
                                '388': 'Гротла',
                                '389': 'Тортерра',
                                '390': 'Чимчара',
                                '391': 'Монферно',
                                '392': 'Инфернейпа',
                                '393': 'Пиплапа',
                                '394': 'Принплапа',
                                '395': 'Эмполеона',
                                '495': 'Снайви',
                                '496': 'Сервайна',
                                '497': 'Серпериора',
                                '498': 'Тепига',
                                '499': 'Пигнита',
                                '500': 'Эмбора',
                                '501': 'Ошавотта',
                                '502': 'Девотта',
                                '503': 'Самурота',
                                '650': 'Чеспина',
                                '651': 'Квилладина',
                                '652': 'Чеснаута',
                                '653': 'Феннекина',
                                '654': 'Брейксена',
                                '655': 'Делфокса',
                                '656': 'Фроки',
                                '657': 'Фрогадира',
                                '658': 'Грениндзя',
                                '810': 'Груки',
                                '811': 'Тваки',
                                '812': 'Риллабума',
                                '813': 'Скорбанни',
                                '814': 'Рабута',
                                '815': 'Синдерэйса',
                                '816': 'Соббла',
                                '817': 'Дриззайла',
                                '818': 'Интелеона'
                                }


            if number_player == 1:
                user_id = self.game['player_1']
                name = self.name_user(user_id)

                evolution = random.randint(0, 2)
                self.game['evolution'] = evolution

                type_pokemon = self.game['player_1_type']
                id_pokemon = random.randint(0, len(list_pokemon[evolution][type_pokemon]) - 1)
                pokemon_id = list_pokemon[evolution][type_pokemon][id_pokemon]

                poke_info = info_pokemon.pokemon_input(str(pokemon_id))
                poke_name = dick_pokemon_name[poke_info[1]]
                self.game['player_1_poke_name'] = poke_name

                tmp = poke_info[2]
                img = requests.get(tmp).content
                f = BytesIO(img)
                response = self.upload.photo_messages(f)[0]
                owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']

                attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)
                msg = f'Тренер {name} выбрал {poke_name}.'

                last_id = self.messages_send(event, msg, peer_id=event.peer_id, attachments=attachment, flag=1)
                conversation_message_id = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=last_id)['items'][0]['conversation_message_id']
                self.game_msg[0].append(conversation_message_id)

            elif number_player == 2:
                user_id = self.game['player_2']
                name = self.name_user(user_id)

                evolution = self.game['evolution']
                type_pokemon = self.game['player_2_type']
                id_pokemon = random.randint(0, len(list_pokemon[evolution][type_pokemon]) - 1)
                pokemon_id = list_pokemon[evolution][type_pokemon][id_pokemon]

                poke_info = info_pokemon.pokemon_input(str(pokemon_id))
                poke_name = dick_pokemon_name[poke_info[1]]
                self.game['player_2_poke_name'] = poke_name

                tmp = poke_info[2]
                img = requests.get(tmp).content
                f = BytesIO(img)
                response = self.upload.photo_messages(f)[0]
                owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']

                attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)
                msg = f'Тренер {name} выбрал {poke_name}.'

                last_id = self.messages_send(event, msg, peer_id=event.peer_id, attachments=attachment, flag=1)
                conversation_message_id = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=last_id)['items'][0]['conversation_message_id']
                self.game_msg[0].append(conversation_message_id)

                flag = self.check()

                user_id = self.game['player_1']
                player_1_name = self.name_user(user_id)

                player_1_poke_name = self.game['player_1_poke_name']
                if flag == 0:
                    msg = f'Ничья между тренерами {player_1_name} и {name}.'
                elif flag == 1:
                    user_id = self.game['player_1']
                    msg = f'Победил {player_1_name}, благодаря сокрушительному удару {player_1_poke_name}.'
                    self.append_message(int(user_id), type_message='Number of wins in rock paper scissors')
                elif flag == 2:
                    user_id = self.game['player_2']
                    msg = f'Победил {name}, использовав в последний момент заряженную атаку {poke_name}.'
                    self.append_message(int(user_id), type_message='Number of wins in rock paper scissors')

                last_id = self.messages_send(event, msg, peer_id=event.peer_id, flag=1)
                conversation_message_id = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=last_id)['items'][0]['conversation_message_id']
                self.game_msg[0].append(conversation_message_id)
                self.game = dict()
            
        except Exception as e:
            msg = 'Error in rock_paper_scissors'
            self.add_error(msg + str(e))
        
    def get_pokemon(self, event):
        try:
            if len(event['text'].split()) < 2:
                return 0

            text = event['text'].split()[1].lower()
            poke_info = info_pokemon.pokemon_input(text)

            if poke_info == -1:
                msg = 'Данный покемон не найден.'
                self.messages_send(event, msg)
                return 0

            with open('files/pokemon_info_text.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(file.readlines())

            poke_name = poke_info[0][0].upper() + poke_info[0][1:]

            poke_type = str()
            for i in poke_info[3]:
                poke_type += f'{i}, '
            poke_type = poke_type[:-2]

            vulnerable = str()
            for i in range(len(poke_info[4])):
                vulnerable += f'{poke_info[4][i]}, '
            vulnerable = vulnerable[:-2]

            resistant = str()
            for i in range(len(poke_info[6])):
                resistant += f'{poke_info[6][i]}, '
            resistant = resistant[:-2]

            msg = msg.format(name=poke_name, poke_id=poke_info[1], poke_type=poke_type, vulnerable=vulnerable,
                     resistant=resistant)

            tmp = poke_info[2]
            img = requests.get(tmp).content
            f = BytesIO(img)

            response = self.upload.photo_messages(f)[0]
            owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
            attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)
            self.messages_delete(event, event['conversation_message_id'])
            self.messages_send(event, msg, attachments=attachment)
        except Exception as e:
            msg = 'Error in get_pokemon'
            self.add_error(msg + str(e))
        
    def get_pokemon_full(self, event):
        text = event['text'].split()[1].lower()
        poke_info = info_pokemon.pokemon_input(text)
        
        if poke_info == -1:
            msg = 'Данный покемон не найден.'
            self.messages_send(event, msg)
            return 0
        
        with open('files/pokemon_info_text_full.txt', 'r+', encoding='utf-8') as file:
            msg = ''.join(file.readlines())
            
        poke_name = poke_info[0][0].upper() + poke_info[0][1:]
        
        poke_type = str()
        for i in poke_info[3]:
            poke_type += f'{i}, '
        poke_type = poke_type[:-2]
        
        vulnerable = str()
        for i in range(len(poke_info[4])):
            vulnerable += f'{poke_info[4][i]}({poke_info[5][i]}), '
        vulnerable = vulnerable[:-2]
    
        resistant = str()
        for i in range(len(poke_info[6])):
            resistant += f'{poke_info[6][i]}({poke_info[7][i]}), '
        resistant = resistant[:-2]
        
        poke_quick_move = str()
        for i in range(len(poke_info[8])):
            poke_quick_move += f'{poke_info[8][i]}{poke_info[9][i]}, '
        poke_quick_move = poke_quick_move[:-2]
        
        poke_main_move = str()
        for i in range(len(poke_info[10])):
            poke_main_move += f'{poke_info[10][i]}{poke_info[11][i]}, '
        poke_main_move = poke_main_move[:-2]
        
        msg = msg.format(name=poke_name, poke_id=poke_info[1], poke_type=poke_type, vulnerable=vulnerable,
                         resistant=resistant, quick_move=poke_quick_move, main_move=poke_main_move)
        
        tmp = poke_info[2]
        img = requests.get(tmp).content
        f = BytesIO(img)

        response = self.upload.photo_messages(f)[0]
        owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
        attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)
        self.messages_send(event, msg, attachments=attachment)
        
    def print_list_rp(self, event, flag_keyboard=0):
        tmp = str()
        for i in self.all_commands:
            tmp += i + ', '
        tmp = tmp[:-2]
        msg = f'Список доступных команд: {tmp}'
        
        if flag_keyboard == 0:
            self.messages_delete(event, event['conversation_message_id'])
            
        self.messages_send(event, msg)
        
    def rank_criterion(self, event, flag_keyboard=0):
        with open('files/rank_criterion.txt', 'r+', encoding='utf-8') as file:
            msg = ''.join(file.readlines())
        if flag_keyboard == 0:
            self.messages_delete(event, event['conversation_message_id'])
        self.messages_send(event, msg)
        
    def top_users(self, event, top_type=1, flag_keyboard=0):
        text = event['text'].split()

        number_top = 10

        df = pd.read_csv('files/user.csv')
        
        if top_type == 1:
            index = top_type - 1
            str_1 = 'сообщениям'
            str_2 = 'сообщений'
            res = df.sort_index().sort_values('Number of messages', kind='mergesort').iloc[::-1]
        elif top_type == 2:
            index = top_type - 1
            str_1 = 'созданию рейдов'
            str_2 = 'рейдов'
            res = df.sort_index().sort_values('Number of leader raids', kind='mergesort').iloc[::-1]
        elif top_type == 3:
            index = top_type - 1
            str_1 = 'участиям в рейдах'
            str_2 = 'рейдов'
            res = df.sort_index().sort_values('Number of raid participants', kind='mergesort').iloc[::-1]
        elif top_type == 4:
            index = top_type - 1
            str_1 = 'боям'
            str_2 = 'побед'
            res = df.sort_index().sort_values('Number of wins in rock paper scissors', kind='mergesort').iloc[::-1]

        if len(text) > 1 and text[1].isdigit():
            if int(text[1]) <= 50 and int(text[1]) >= 1:
                if int(text[1]) > df.shape[0]:
                    number_top = df.shape[0] - 2
                else:
                    number_top = int(text[1])
            else:
                number_top = 50

        msg = f'🏆 Топ-{number_top} активистов по {str_1}\n\n'
        for i in range(number_top):
            user_id = res.iloc[i, 0]
            people = self.vk.users.get(user_ids=user_id)[0]
            first_name, last_name = people['first_name'], people['last_name']

            name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
            msg += f'{i + 1}. {name} - {res.iloc[i, 6 + index]} {str_2}\n'
          
        if flag_keyboard == 0:
            self.messages_delete(event, event['conversation_message_id'])
        last_id = self.messages_send(event, msg, flag=1)
        tmp = self.vk.messages.getById(peer_id=event['peer_id'], message_ids=last_id)['items'][0]['conversation_message_id']
        self.commands_msg[1].append(tmp)
        if len(self.commands_msg[1]) > 1:
            self.messages_delete(event, self.commands_msg[1][0])
            del self.commands_msg[1][0]
        
    def check_rank_user(self, user_id):
        df = pd.read_csv('files/user.csv')
        
        message = df.loc[df['User_id'] == user_id, 'Number of messages'].values[0]
        raid_leader = df.loc[df['User_id'] == user_id, 'Number of leader raids'].values[0]
        raid_participant = df.loc[df['User_id'] == user_id, 'Number of raid participants'].values[0]
        number_rock_paper_scissors = df.loc[df['User_id'] == user_id, 'Number of wins in rock paper scissors'].values[0]
        
        # Бегинер - Начальный ранг
        # Грейт - 500 сообщений 2 рейдов или 5 участий в рейде
        # Эксперт - 1100 сообщений 10 рейдов или 20 участий в рейде
        # Ветеран - 2000 сообщений 20 рейдов (либо 10 рейдов и 15 участий) и побед в кнб 200
        # Ультра - 3500 сообщений 30 рейдов и 20 участий и побед в кнб 500
        # Мастер - 5000 сообщений 50 рейдов и 50 участий и побед в кнб 1000

        if message >= 5000 and (raid_leader >= 50 and raid_participant >= 50) and number_rock_paper_scissors >= 1000:
            return 'Master'
        elif message >= 3500 and (raid_leader >= 30 and raid_participant >= 20) and number_rock_paper_scissors >= 500:
            return 'Ultra'
        elif message >= 2000 and (raid_leader >= 20 or (raid_leader >= 10 and raid_participant >= 15)) and number_rock_paper_scissors >= 200:
            return 'Veteran'
        elif message >= 1100 and (raid_leader >= 10 or raid_participant >= 20):
            return 'Expert'
        elif message >= 500 and (raid_leader >= 2 or raid_participant >= 5):
            return 'Great'
        else:
            return 'Beginner'

    
    @staticmethod
    def append_new_user(user_id, nick_pg=0, code_pg=0, level_pg=0, nick_unite=0, code_unite=0, message=0, raid_leader=0, raid_participant=0, number_rock_paper_scissors=0):
        new_row = {'User_id': int(user_id),
                   'Nick in Pokemon Go': nick_pg,
                   'Friendship code in Pokemon Go': code_pg,
                   'Level in Pokemon Go': level_pg,
                   'Nick in Pokemon Unite': nick_unite,
                   'Friendship code in Pokemon Unite': code_unite,
                   'Number of messages': message,
                   'Number of leader raids': raid_leader,
                   'Number of raid participants': raid_participant,
                   'Number of wins in rock paper scissors': number_rock_paper_scissors
                  }
        return new_row
        
    def append_message(self, user_id, type_message='Number of messages'):
        try:
            if user_id < 0:
                return 0

            df = pd.read_csv('files/user.csv')

            if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):
                df.loc[df['User_id'] == user_id, type_message] += 1
            else:
                new_row = self.append_new_user(user_id, message=1)
                df = df.append(new_row, ignore_index=True)

            df.to_csv('files/user.csv', index=False)
        except Exception as e:
            msg = 'Error in append_message'
            self.add_error(msg + str(e))

    def old_info_about_user(self, event):
        if len(event['text'].split()) != 2:
            if 'reply_message' in event.keys():
                user_id = event['reply_message']['from_id']
            else:
                user_id = event['from_id']
            self.old_print_user_info(event, user_id)
        else:
            tmp_id = event['text'].split()[1]
            if 'id' in tmp_id and '@' in tmp_id:
                user_id = tmp_id[1:-1].split('|')[0][2:]
                self.old_print_user_info(event, user_id)
            else:
                msg = 'Неправильная форма запроса. Если вы хотите получить информацию о другом пользователе, вам надо переслать сообщение или упомянуть пользователя после /oldinfo. Например: /oldinfo @hare_hare'
                self.messages_send(event, msg)
        
    def append_user_info(self, user_id, nick_pg, code_pg, level_pg, nick_unite, code_unite):
        try:
            df = pd.read_csv('files/user.csv')

            if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):

                if nick_pg == None:
                    nick_pg = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Go']
                if code_pg == None:
                    code_pg = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Go']
                if level_pg == None:
                    level_pg = df.loc[df['User_id'] == user_id, 'Level in Pokemon Go']
                if nick_unite == None:
                    nick_unite = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Unite']
                if code_unite == None:
                    code_unite = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Unite']

                df.loc[df['User_id'] == user_id, 'Nick in Pokemon Go'] = nick_pg
                df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Go'] = str(code_pg)
                df.loc[df['User_id'] == user_id, 'Level in Pokemon Go'] = level_pg
                df.loc[df['User_id'] == user_id, 'Nick in Pokemon Unite'] = nick_unite
                df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Unite'] = code_unite

            else:
                new_row = self.append_new_user(int(user_id), nick_pg, code_pg, level_pg, nick_unite, code_unite, 0)
                df = df.append(new_row, ignore_index=True)

            df.to_csv('files/user.csv', index=False)
        except Exception as e:
            msg = 'Error in append_user_info'
            self.add_error(msg + str(e))
    
    def old_print_user_info(self, event, about=0):
        try:
            if about == 0:
                user_id = event['from_id']
            else:
                user_id = int(about)

            df = pd.read_csv('files/user.csv')

            if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):
                nick_pg = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Go'].values[0]
                code_pg = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Go'].values[0]
                level_pg = df.loc[df['User_id'] == user_id, 'Level in Pokemon Go'].values[0]
                nick_unite = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Unite'].values[0]
                code_unite = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Unite'].values[0]

                with open('files/user_info_text.txt', 'r+', encoding='utf-8') as file:
                    msg = ''.join(file.readlines())

                people = self.vk.users.get(user_ids=user_id)[0]
                first_name, last_name = people['first_name'], people['last_name']
                name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
                msg = msg.format(name=name, nick_pg=nick_pg, code_pg=code_pg, level_pg=level_pg, nick_unite=nick_unite, code_unite=code_unite)
            else:
                msg = 'Информации о данном пользователе нет.'

            self.messages_delete(event, event['conversation_message_id'])
            self.messages_send(event, msg, flag=1)
        except Exception as e:
            msg = 'Error in old_print_user_info'
            self.add_error(msg + str(e))
            
    @staticmethod
    def create_image(k, first_name, last_name, nick_pg, code_pg, level_pg, nick_unite, code_unite):
        image = Image.open("files/rank/{k}.png".format(k=k))

        font = ImageFont.truetype("files/Pokemon.ttf", 34)
        font_2 = ImageFont.truetype("files/Pokemon.ttf", 59)
        drawer = ImageDraw.Draw(image)
        
        n = (21 - len(first_name + last_name)) // 2
#         n = 0
        text = ' ' * n + first_name + ' ' + last_name
#         text = 'З' + 'a' * 22
        x, y = 110, 197 #390, 211
        offset = 4
        shadowColor = (242, 144, 58)
        
        for off in range(offset):
            drawer.text((x-off, y), text, font=font_2, fill=shadowColor)
            drawer.text((x+off, y), text, font=font_2, fill=shadowColor)
            drawer.text((x, y+off), text, font=font_2, fill=shadowColor)
            drawer.text((x, y-off), text, font=font_2, fill=shadowColor)
            drawer.text((x-off, y+off), text, font=font_2, fill=shadowColor)
            drawer.text((x+off, y+off), text, font=font_2, fill=shadowColor)
            drawer.text((x-off, y-off), text, font=font_2, fill=shadowColor)
            drawer.text((x+off, y-off), text, font=font_2, fill=shadowColor)

        drawer.text((x,y), text, font=font_2, fill="#fff")
        
        
        a = [nick_pg, code_pg, level_pg, nick_unite, code_unite]
        coordinates = [(468, 752), (340, 792), (445, 832), (510, 891), (345, 932)]
        offset = 4
        shadowColor = (95, 48, 211)
        
        for i in range(len(a)):
            text = str(a[i])
            x, y = coordinates[i]
            for off in range(offset):
                drawer.text((x-off, y), text, font=font, fill=shadowColor)
                drawer.text((x+off, y), text, font=font, fill=shadowColor)
                drawer.text((x, y+off), text, font=font, fill=shadowColor)
                drawer.text((x, y-off), text, font=font, fill=shadowColor)
                drawer.text((x-off, y+off), text, font=font, fill=shadowColor)
                drawer.text((x+off, y+off), text, font=font, fill=shadowColor)
                drawer.text((x-off, y-off), text, font=font, fill=shadowColor)
                drawer.text((x+off, y-off), text, font=font, fill=shadowColor)

            drawer.text((x,y), text, font=font, fill="#fff")
            
        image.save('tmp_img.png')
    
    def info_about_user(self, event, flag_keyboard=0):
        if len(event['text'].split()) != 2:
            if 'reply_message' in event.keys():
                user_id = event['reply_message']['from_id']
            else:
                user_id = event['from_id']
            self.print_user_info(event, user_id, flag_keyboard)
        else:
            tmp_id = event['text'].split()[1]
            if 'id' in tmp_id and '@' in tmp_id:
                user_id = tmp_id[1:-1].split('|')[0][2:]
                self.print_user_info(event, user_id, flag_keyboard)
            else:
                msg = 'Неправильная форма запроса. Если вы хотите получить информацию о другом пользователе, вам надо переслать сообщение или упомянуть пользователя после /info. Например: /info @hare_hare'
                self.messages_send(event, msg)
        
    def print_user_info(self, event, about=0, flag_keyboard=0):
        if about == 0:
            user_id = event['from_id']
        else:
            user_id = int(about)

        df = pd.read_csv('files/user.csv')

        if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):
            nick_pg = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Go'].values[0]
            code_pg = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Go'].values[0]
            level_pg = df.loc[df['User_id'] == user_id, 'Level in Pokemon Go'].values[0]
            nick_unite = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Unite'].values[0]
            code_unite = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Unite'].values[0]
            
            people = self.vk.users.get(user_ids=user_id)[0]
            first_name, last_name = people['first_name'], people['last_name']
            
            if 'ё' in first_name:
                first_name = first_name.replace('ё', 'е')
            if 'ё' in last_name:
                last_name = last_name.replace('ё', 'е')
            
            k = self.check_rank_user(user_id)
            self.create_image(k, first_name, last_name, nick_pg, code_pg, level_pg, nick_unite, code_unite)
            
            msg = str()
            response = self.upload.photo_messages('tmp_img.png')[0]
            owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
            attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

            self.messages_send(event, msg, attachments=attachment, flag=1)
            
            if os.path.isfile('tmp_img.jpg'):
                os.remove('tmp_img.jpg')
            
        else:
            msg = 'Информации о данном пользователе нет.'
            self.messages_send(event, msg)
        if flag_keyboard == 0:
            self.messages_delete(event, event['conversation_message_id'])
        
    def user_info(self, event):
        try:
            user_id = event['from_id']
            text = event['text'].split()

            if len(text) == 6:
                self.append_user_info(user_id, text[1], text[2], text[3], text[4], text[5])
                msg = 'Информация добавлена.'
            else:
                msg = 'Неправильный ввод данных. Пример: /addinfo Ник_ПОГО Тег_ПОГО Левл_ПОГО Ник_Юнайт Тег_Юнайт'

            self.messages_delete(event, event['conversation_message_id'])
            self.messages_send(event, msg)
        except Exception as e:
            msg = 'Error in user_info'
            self.add_error(msg + str(e))
    
    def number_messages(self, event, about=0, flag_keyboard=0):
        if about == 0:
            user_id = event['from_id']
        else:
            user_id = int(about)

        df = pd.read_csv('files/user.csv')

        if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):
            messages = df.loc[df['User_id'] == user_id, 'Number of messages'].values[0]
            raid_create = df.loc[df['User_id'] == user_id, 'Number of leader raids'].values[0]
            raid_participate = df.loc[df['User_id'] == user_id, 'Number of raid participants'].values[0]
            number_rock_paper_scissors = df.loc[df['User_id'] == user_id, 'Number of wins in rock paper scissors'].values[0]
            
            people = self.vk.users.get(user_ids=user_id)[0]
            first_name, last_name = people['first_name'], people['last_name']
            name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
            
            with open('files/number_messages_text.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(file.readlines())
            
            msg = msg.format(name=name, messages=messages, raid_create=raid_create, raid_participate=raid_participate, number_rock_paper_scissors=number_rock_paper_scissors)
            if flag_keyboard == 0:
                self.messages_delete(event, event['conversation_message_id'])
            self.messages_send(event, msg, flag=1)
            
    def number_messages_about_user(self, event, flag_keyboard=0):
        
        if len(event['text'].split()) != 2:
            if 'reply_message' in event.keys():
                user_id = event['reply_message']['from_id']
            else:
                user_id = event['from_id']
            self.number_messages(event, user_id, flag_keyboard)
        else:
            tmp_id = event['text'].split()[1]
            if 'id' in tmp_id and '@' in tmp_id:
                user_id = tmp_id[1:-1].split('|')[0][2:]
                self.number_messages(event, user_id, flag_keyboard)
            else:
                msg = 'Неправильная форма запроса. Если вы хотите получить информацию о другом пользователе, вам надо переслать сообщение или упомянуть пользователя после /рейтинг. Например: /рейтинг @hare_hare'
                self.messages_send(event, msg)
        
    def message_greeting(self, event):
        try:
            #print(event.__dict__)
            evt = {'peer_id': event.peer_id}

            with open('files/ban_list.txt', 'r+', encoding='utf-8') as file:
                lines = [i for i in file.readlines()]
                if event.update_type == VkChatEventType.USER_JOINED:
                    if str(event.info['user_id']) in ''.join(lines):
                        self.kick_user_by_bot(evt['peer_id'], event.info['user_id'])
                        return 0

            if event.update_type == VkChatEventType.USER_LEFT:
                id_user = event.info['user_id']
                people = self.vk.users.get(user_ids = id_user)[0]
                first_name, last_name = people['first_name'], people['last_name']
                msg = 'Участник @id{id_user} ({first_name} {last_name}) покинул чат.'.format(id_user=id_user, first_name=first_name, last_name=last_name)
                self.messages_send(evt, msg)
                self.kick_user_by_bot(evt['peer_id'], event.info['user_id'])
                lines.append(str(event.info['user_id']))
                with open('files/ban_list.txt', 'w+', encoding='utf-8') as file:
                    for i in lines:
                        file.write(i + ' kick' + '\n')

            if event.update_type == VkChatEventType.USER_JOINED:
                id_user = event.info['user_id']
                people = self.vk.users.get(user_ids = id_user)[0]
                first_name, last_name = people['first_name'], people['last_name']
                msg = str()
                with open('files/greeting.txt', 'r+', encoding='utf-8') as file:
                    msg = ''.join(file.readlines())
                msg = msg.format(id_user=id_user, first_name=first_name, last_name=last_name)
                self.messages_send(evt, msg, flag=1)

        except Exception as e:
            msg = 'Error in message_greeting'
            self.add_error(msg + str(e))
            
    def delete_all(self, event):
        if event['from_id'] != self.raid_creator:
            self.messages_delete(event, event['conversation_message_id'])
    
    def change_type_raid(self, event):
        if self.chat_flag == 0:
            self.chat_flag = 1
            msg = 'Смена типа рейда произведена. Сообщение о рейде отправляется с основного бота'
        else:
            self.chat_flag = 0
            msg = 'Смена типа рейда произведена. Сообщение о рейде отправляется с дополнительного бота'
            
        self.messages_send(event, msg)
        self.messages_delete(event, event['conversation_message_id'])
        
    def raid_participate(self, event, flag_keyboard=0):
        try:
            user_id = event['from_id']
            df = pd.read_csv('files/user.csv')
            people = self.vk.users.get(user_ids=user_id)[0]
            first_name, last_name = people['first_name'], people['last_name']
            flag = 0

            if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):
                nick_pg = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Go'].values[0]
                code_pg = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Go'].values[0]
                level_pg = df.loc[df['User_id'] == user_id, 'Level in Pokemon Go'].values[0]

                if str(nick_pg) != '0' and str(code_pg) != '0' and str(level_pg) != '0':
                    msg = '@id{user_id} ({first_name} {last_name}) \nНик: {nick_pg}\nКод: {code_pg}\nУровень: {level_pg}'.format(user_id=user_id, first_name=first_name, last_name=last_name,
                                                                                                                             nick_pg=nick_pg, code_pg=code_pg, level_pg=level_pg)
                else:
                    flag = 1
            else:
                flag = 1

            if flag == 1:
                msg = 'Информация о игроке @id{user_id} ({first_name} {last_name}) не найдена.'.format(user_id=user_id, first_name=first_name, last_name=last_name)

            self.messages_send(event, msg)
            if flag_keyboard == 0:
                self.messages_delete(event, event['conversation_message_id'])
        except Exception as e:
            msg = 'Error in raid_participate'
            self.add_error(msg + str(e))
        
    def raid_take(self, event):
        try:
            message = event
            #print(message)
            fwd_messages = message['fwd_messages']
            message_id_delete = list()
            list_players = list()
            list_nicks = list()
            self.messages_delete(event, event['conversation_message_id'])
            if fwd_messages == []:
                msg = 'Перешлите сообщение о создании рейда и сообщения игроков, которых берете на рейд'
                self.messages_send(event, msg)
                return 0
            elif not('@all' in fwd_messages[0]['text'].lower() and 'рейд' in fwd_messages[0]['text'].lower()):
                msg = 'Перешлите сообщение о создании рейда и сообщения игроков, которых берете на рейд'
                self.messages_send(event, msg)
                return 0
            elif message['from_id'] != self.raid_creator:
                msg = 'Брать игроков на рейд может только создать рейда'
                self.messages_send(event, msg)
                return 0
            else:
                message_id_delete.append(fwd_messages[0]['conversation_message_id'])
                for i in range(1, len(fwd_messages)):
                    message_id_delete.append(fwd_messages[i]['conversation_message_id'])
                    id_user = int(fwd_messages[i]['from_id'])

                    if id_user < 0:
                        list_players.append(fwd_messages[i]['text'])
                        id_user = int(fwd_messages[i]['text'].split('\n')[0].split('|')[0][3:])
                        list_nicks.append(fwd_messages[i]['text'])
                    else:
                        people = self.vk.users.get(user_ids=id_user)[0]
                        first_name, last_name = people['first_name'], people['last_name']
                        list_players.append('@id{id_user} ({first_name} {last_name})'.format(id_user=id_user, first_name=first_name, last_name=last_name) + '\n' + fwd_messages[i]['text'])

                    self.append_message(int(id_user), type_message='Number of raid participants')

                #print(list_players)
            msg = str()
            with open('files/raid_take.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(file.readlines())

            people = self.vk.users.get(user_ids=self.raid_creator)[0]
            first_name, last_name = people['first_name'], people['last_name']
            name = '@id{raid_creator} ({first_name} {last_name})'.format(raid_creator=self.raid_creator, first_name=first_name, last_name=last_name)

            msg = msg.format(boss=self.raid_creator_info[1], name=name, nick=self.raid_creator_info[2], friendship_code=self.raid_creator_info[3], level=self.raid_creator_info[4])
            msg_tmp = '\n\n'.join(list_players)

            tmp = fwd_messages[0]['attachments'][0]['photo']['sizes'][4]['url']
            img = requests.get(tmp).content
            f = BytesIO(img)

            response = self.upload.photo_messages(f)[0]
            owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
            attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)


            self.messages_send(event, msg + msg_tmp, attachments=attachment, keyboard=self.main_keyboard(event, flag_keyboard=1))
            self.messages_delete(event, message_id_delete)

            self.append_message(int(self.raid_creator), type_message='Number of leader raids')

            self.raid_flag = 0
            self.raid_creator = ''
            self.raid_creator_info = list()
        
        except Exception as e:
            msg = 'Error in raid_take'
            self.add_error(msg + str(e))
    
    def raid(self, event): #/рейдбосс имя_босса ник тег_дружбы уровень количество_игроков
        try:
            message = event
            text = message['text'].split()
            tmp = message['attachments']
            self.raid_creator = event['from_id']
            if len(text) == 8: #/рейдбосс имя ник 1234 5678 9012 50 5
                text[3] = ''.join(text[3:6])
                del text[4]
                del text[4]
            if tmp != [] and len(text) == 6:
                tmp = tmp[0]['photo']['sizes'][4]['url']
                img = requests.get(tmp).content
                f = BytesIO(img)

                msg = str()
                with open('files/raid.txt', 'r+', encoding='utf-8') as file:
                    msg = ''.join(file.readlines())
                msg = msg.format(boss=text[1], number_players=text[5], nick=text[2], friendship_code=text[3], level=text[4])

                self.raid_creator_info = text
                self.raid_boss = text[1]
                
                response = self.upload.photo_messages(f)[0]
                owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
                attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

                if self.chat_flag == 1:
                    self.messages_send(event, msg, attachments=attachment, keyboard=self.raid_keyboard()) #при отправке от имени группы в беседу
                else:
                    msg += '|||' + tmp #при отправке на страницу, а с нее в беседу
                    self.send_info_bot_2(event, msg, attachments=attachment) #при отправке на страницу, а с нее в беседу

                self.messages_delete(event, message['conversation_message_id'])
                self.raid_flag = 1
            else:
                msg = 'Неправильная форма запроса. Должна быть прикреплена фотография рейда и текст вида: /рейдбосс имя_босса ник тег_дружбы уровень количество_игроков'
                self.messages_send(event, msg)
        except Exception as e:
            msg = 'Error in raid'
            self.add_error(msg + str(e))
    
    def quick_raid(self, event): #/рейд имя_босса
        try:
            message = event
            text = message['text'].split()
            tmp = message['attachments']
            self.raid_creator = event['from_id']
            number_players = 5

            user_id = int(self.raid_creator)

            df = pd.read_csv('files/user.csv')

            if str(user_id) in list(df['User_id'].values) or int(user_id) in list(df['User_id'].values):
                nick_pg = df.loc[df['User_id'] == user_id, 'Nick in Pokemon Go'].values[0]
                code_pg = df.loc[df['User_id'] == user_id, 'Friendship code in Pokemon Go'].values[0]
                level_pg = df.loc[df['User_id'] == user_id, 'Level in Pokemon Go'].values[0]
            else:
                msg = 'Информации о вашем аккаунте нет в базе данных бота, поэтому добавьте ее через /addinfo или создайте рейд через /рейдбосс'
                self.messages_send(event, msg)
                return 0

            if len(str(nick_pg)) <= 2 or len(str(code_pg)) != 12:
                msg = 'Информации о вашем аккаунте нет в базе данных бота, поэтому добавьте ее через /addinfo или создайте рейд через /рейдбосс'
                self.messages_send(event, msg)
                return 0

            if tmp != [] and len(text) == 2:
                tmp = tmp[0]['photo']['sizes'][4]['url']
                img = requests.get(tmp).content
                f = BytesIO(img)

                msg = str()
                with open('files/raid.txt', 'r+', encoding='utf-8') as file:
                    msg = ''.join(file.readlines())
                msg = msg.format(boss=text[1], number_players=number_players, nick=nick_pg, friendship_code=code_pg, level=level_pg)

                self.raid_creator_info = text + [nick_pg, code_pg, level_pg]
                self.raid_boss = text[1]
                
                response = self.upload.photo_messages(f)[0]
                owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
                attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

                if self.chat_flag == 1:
                    self.messages_send(event, msg, attachments=attachment, keyboard=self.raid_keyboard()) #при отправке от имени группы в беседу
                else:
                    msg += '|||' + tmp #при отправке на страницу, а с нее в беседу
                    self.send_info_bot_2(event, msg, attachments=attachment) #при отправке на страницу, а с нее в беседу

                self.messages_delete(event, message['conversation_message_id'])
                self.raid_flag = 1
            else:
                msg = 'Неправильная форма запроса. Должна быть прикреплена фотография рейда и текст вида: /рейд имя_босса'
                self.messages_send(event, msg)
        except Exception as e:
            msg = 'Error in quick raid'
            self.add_error(msg + str(e))
    
    def admin_cancellation_raid(self, event):
        if self.raid_flag == 1:
            self.raid_flag = 0
            self.raid_creator = ''
            self.raid_creator_info = list()
            msg = 'Рейд отменен администратором.'
        else:
            msg = 'Нет активных рейдов.'
            
        self.messages_send(event, msg, keyboard=self.main_keyboard(event, flag_keyboard=1))
        self.messages_delete(event, event['conversation_message_id'])
        
    
    def cancellation_raid(self, event):
        try:
            text, text_id = '', ''
            self.messages_delete(event, event['conversation_message_id'])
            if 'reply_message' not in event.keys() and event['fwd_messages'] == []:
                msg = 'Перешлите сообщение о создании рейда'
                self.messages_send(event, msg)
                return 0
            elif event['fwd_messages'] != []:
                text = event['fwd_messages'][0]['text']
                text_id = event['fwd_messages'][0]['conversation_message_id']
            elif 'reply_message' in event.keys():
                text = event['reply_message']['text']
                text_id = event['reply_message']['conversation_message_id']

            if not('@all' in text.lower() and 'рейд' in text.lower()):
                msg = 'Перешлите сообщение о создании рейда'
                self.messages_send(event, msg)
                return 0

            if not(event['from_id'] == self.raid_creator or self.checking_access_rights(event, ['admin', 'moderator'])):
                msg = 'Отменить рейд может только его создатель или администратор'
                self.messages_send(event, msg)
                return 0
            if event['from_id'] == self.raid_creator:
                destroyer = 'создателем'
            else:
                destroyer = 'администратором @id{ids}'.format(ids=event['from_id'])

            self.messages_delete(event, text_id)
            #self.messages_delete(event, event['conversation_message_id'])


            people = self.vk.users.get(user_ids=self.raid_creator)[0]
            first_name, last_name = people['first_name'], people['last_name']

            msg = 'Рейд игрока @id{user_id} ({first_name} {last_name}) отменен {destroyer}.'.format(user_id=self.raid_creator, first_name=first_name, last_name=last_name, destroyer=destroyer)

            self.messages_send(event, msg, keyboard=self.main_keyboard(event, flag_keyboard=1))
            self.raid_flag = 0
            self.raid_creator = ''
            self.raid_creator_info = list()
        
        except Exception as e:
            msg = 'Error in cancellation_raid'
            self.add_error(msg + str(e))
            
            
    def send_info_bot_2(self, event, msg, attachments=[]):
        self.vk.messages.send(
            peer_id=self.bot_2_id,
            message=msg,
            random_id=time.time() * 1000,
            attachment=attachments
        )
    
    def kick_user(self, event):
        try:
            tmp = event
            message_id_delete = list()
            if len(tmp['text'].split()) != 2:
                ids = tmp['reply_message']['from_id']
                self.vk.messages.removeChatUser(chat_id=tmp['peer_id']-2000000000, user_id=ids)
                message_id_delete.append(tmp['reply_message']['conversation_message_id'])

            elif '@' in event['text'].split()[1]:
                k = tmp['text'].split()[-1]
                k = k[k.find('id') + 2:k.find('|')]
                self.vk.messages.removeChatUser(chat_id=tmp['peer_id']-2000000000, user_id=k)

            message_id_delete.append(tmp['conversation_message_id'])
            self.messages_delete(event, message_id_delete)
        except Exception as e:
            msg = 'Error in ban_user'
            self.add_error(msg + str(e))
            
    def kick_user_by_id(self, event, id_user):
        self.vk.messages.removeChatUser(chat_id=event['peer_id']-2000000000, user_id=id_user)
        
    def ban_user(self, event):
        try:
            lines = list()
            id_users = list()
            message_id_delete = list()

            message_id_delete.append(event['conversation_message_id'])

            with open('files/ban_list.txt', 'r+', encoding='utf-8') as file:
                lines = [i for i in file.readlines()]

            if len(event['text'].split()) != 2:
                if 'reply_message' in event.keys():
                    from_id = int(event['reply_message']['from_id'])
                    message_id_delete.append(event['reply_message']['conversation_message_id'])
                    if from_id > 0:
                        id_users.append(from_id)
                    else:
                        text = event['reply_message']['text']
                        id_users.append(int(text[text.find('[id') + 3:text.find('|')]))
                elif event['fwd_messages'] != []:
                    fwd_messages = event['fwd_messages']
                    for i in range(0, len(fwd_messages)):
                        message_id_delete.append(fwd_messages[i]['conversation_message_id'])
                        from_id = int(fwd_messages[i]['from_id'])
                        if from_id > 0:
                            id_users.append(fwd_messages[i]['from_id'])
                        else:
                            text = fwd_messages[i]['text']
                            id_users.append(int(text[text.find('[id') + 3:text.find('|')]))
                else:
                    msg = 'Неправильная форма запроса. Необхоимо переслать сообщение или упомянуть. Например: /ban @hare_hare'
                    self.messages_send(event, msg)
                    return 0
            else:
                tmp_id = event['text'].split()[1]
                if 'id' in tmp_id and '@' in tmp_id:
                    id_users.append(int(tmp_id[1:-1].split('|')[0][2:]))
                else:
                    msg = 'Неправильная форма запроса. Необхоимо переслать сообщение или упомянуть. Например: /ban @hare_hare'
                    self.messages_send(event, msg)
                    return 0

            for id_user in id_users:
                self.kick_user_by_id(event, id_user)
                lines.append(str(id_user) + '\n')

                with open('files/ban_list.txt', 'w+', encoding='utf-8') as file:
                    for i in lines:
                        file.write(i)

                people = self.vk.users.get(user_ids = id_user)[0]
                first_name, last_name = people['first_name'], people['last_name']
                msg = 'Пользователь @id{id_user} ({first_name} {last_name}) заблокирован'.format(id_user=id_user, first_name=first_name, last_name=last_name)
                self.messages_send(event, msg)
            self.messages_delete(event, message_id_delete)
            
        except Exception as e:
            msg = 'Error in ban_user'
            self.add_error(msg + str(e))
        
    def unban_user(self, event):
        try:
            message_id_delete = list()
            message_id_delete.append(event['conversation_message_id'])
            
            if len(event['text'].split()) > 1:
                tmp_id = event['text'].split()[1]
            else:
                msg = 'Неправильная форма запроса. Необхоимо упомянуть пользователя. Например: /unban @hare_hare'
                self.messages_send(event, msg)
                return 0
            
            if 'id' in tmp_id and '@' in tmp_id:
                id_user = tmp_id[1:-1].split('|')[0][2:]
            else:
                msg = 'Неправильная форма запроса. Необхоимо упомянуть пользователя. Например: /unban @hare_hare'
                self.messages_send(event, msg)
                return 0
                
            lines = list()
            with open('files/ban_list.txt', 'r+', encoding='utf-8') as file:
                for i in file.readlines():
                    if id_user not in i:
                        lines.append(i)
            with open('files/ban_list.txt', 'w+', encoding='utf-8') as file:
                for i in lines:
                    file.write(i)

            people = self.vk.users.get(user_ids = id_user)[0]
            first_name, last_name = people['first_name'], people['last_name']
            msg = 'Пользователь @id{id_user} ({first_name} {last_name}) разблокирован'.format(id_user=id_user, first_name=first_name, last_name=last_name)
            self.messages_send(event, msg)
            self.messages_delete(event, message_id_delete)
            
        except Exception as e:
            msg = 'Error in unban_user'
            self.add_error(msg + str(e))
    
    def check_mute(self, event):
        try:
            if str(event['from_id']) in self.list_mute.keys():
                self.messages_delete(event, event['conversation_message_id'])
            
        except Exception as e:
            msg = 'Error in check_mute'
            self.add_error(msg + str(e))
    
    def update_mute(self, event):
        try:
            list_to_delete = list()
            for i in self.list_mute:
                if self.list_mute[i] < time.time():
                    list_to_delete.append(i)
            for i in list_to_delete:
                self.list_mute.pop(i)
            
        except Exception as e:
            msg = 'Error in update_mute'
            self.add_error(msg + str(e))
    
    def mute(self, event):
        try:
            tmp = event
            message_id_delete = list()
            if len(tmp['text'].split()) != 3:
                ids = tmp['reply_message']['from_id']
                self.list_mute[ids] = float(tmp['text'].split()[1]) + time.time()
                message_id_delete.append(tmp['reply_message']['conversation_message_id'])
                minute = tmp['text'].split()[1]

            elif '@' in event['text'].split()[1]:
                ids = tmp['text'].split()[1]
                ids = ids[ids.find('id') + 2:ids.find('|')]
                minute = tmp['text'].split()[2]
                self.list_mute[ids] = float(tmp['text'].split()[2]) * 60 + time.time()

            message_id_delete.append(tmp['conversation_message_id'])
            self.messages_delete(event, message_id_delete)


            msg = 'Пользователь @id{ids} получил мут на {minute} минут'.format(ids=ids, minute=minute)
            self.messages_send(event, msg)
        except:
            msg = 'Неправильная форма запроса. Пример: mute @id time'
            self.messages_send(event, msg)
            
    def unmute(self, event):
        try:
            tmp = event
            message_id_delete = list()
            
            if '@' in event['text'].split()[1]:
                ids = tmp['text'].split()[1]
                ids = ids[ids.find('id') + 2:ids.find('|')]

            message_id_delete.append(tmp['conversation_message_id'])
            self.messages_delete(event, message_id_delete)
            
            if ids in self.list_mute.keys():
                self.list_mute.pop(ids)
            msg = 'С пользователя @id{ids} снимается мут'.format(ids=ids)
            self.messages_send(event, msg)
        except:
            msg = 'Неправильная форма запроса. Пример: unmute @id'
            self.messages_send(event, msg)
        
    def delete_message(self, event):
        try:
            tmp = event
            if tmp['fwd_messages'] == []:
                message_id_delete = [tmp['reply_message']['conversation_message_id']]
            else:
                message_id_delete = [i['conversation_message_id'] for i in tmp['fwd_messages']]
            message_id_delete.append(tmp['conversation_message_id'])
            self.messages_delete(event, message_id_delete)
        except Exception as e:
            msg = 'Error in delete_message'
            self.add_error(msg + str(e))
            
    def rules(self, event):
        try:
            msg = str()
            with open('files/rules.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(i for i in file.readlines())
            
            tmp = 'https://sun9-85.userapi.com/impg/nOP32io1qRfyFxvSJanAvGhLi8nRelmjXkFUTA/qwdRMO-AW0g.jpg?size=736x900&quality=95&sign=8a31e9a89292e1bb009f701e0ed91f70&type=album'
            img = requests.get(tmp).content
            f = BytesIO(img)
            response = self.upload.photo_messages(f)[0]
            owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
            attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

            self.messages_send(event, msg, attachments=attachment, flag=1)
        except Exception as e:
            msg = 'Error in rules'
            self.add_error(msg + str(e))
               
    def admin_list(self, event):
        try:
            msg = str()
            with open('files/admin_list.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(i for i in file.readlines())
            
            tmp = 'https://sun9-85.userapi.com/impg/nOP32io1qRfyFxvSJanAvGhLi8nRelmjXkFUTA/qwdRMO-AW0g.jpg?size=736x900&quality=95&sign=8a31e9a89292e1bb009f701e0ed91f70&type=album'
            img = requests.get(tmp).content
            f = BytesIO(img)
            response = self.upload.photo_messages(f)[0]
            owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
            attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

            self.messages_send(event, msg, attachments=attachment, flag=1)
        except Exception as e:
            msg = 'Error in rules'
            self.add_error(msg + str(e))
            
    def print_help(self, event):
        try:
            with open('files/documentation.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(i for i in file.readlines())
                self.messages_send(event, msg)
        except Exception as e:
            msg = 'Error in print_help'
            self.add_error(msg + str(e))
    
    def print_admin_help(self, event):
        try:
            with open('files/admin_documentation.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(i for i in file.readlines())
                self.messages_send(event, msg)
        except Exception as e:
            msg = 'Error in print_admin_help'
            self.add_error(msg + str(e))
 
    def delete_category(self, event):
        try:
            str_ = event['text'].lower().split()
            flag = 0
            lines_new = list()
            with open('files/{str_}.txt'.format(str_=str_[1]), 'r+', encoding='utf-8') as file:
                for i in file.readlines():
                    if i != str_[-1] + '\n':
                        lines_new.append(i)
                    else:
                        flag = 1
                        msg = 'Данный пользователь удален из {str_}'.format(str_=str_[1])
                        self.messages_send(event, msg)

            if flag == 1:
                with open('files/{str_}.txt'.format(str_=str_[1]), 'w+', encoding='utf-8') as file:
                    for i in lines_new:
                        file.write(i)
            else:
                msg = 'Данный пользователь не является {str_}'.format(str_=str_[1])
                self.messages_send(event, msg)
        except Exception as e:
            msg = 'Error in delete_category'
            self.add_error(msg + str(e))
            
    def print_category(self, event, name):
        try:
            msg = str()
            lines = list()
            for str_ in name:
                with open('files/{str_}.txt'.format(str_=str_), 'r+', encoding='utf-8') as file:
                    lines = file.readlines()
                if lines != '':
                    msg += 'Список {str_}:\n'.format(str_=str_)
                    for i in lines:
                        user_id = i[1:-1].split('|')[0][2:]
                        people = self.vk.users.get(user_ids=user_id)[0]
                        first_name, last_name = people['first_name'], people['last_name']
                        name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
                        msg += '{line}\n'.format(line=name)
            self.messages_send(event, msg, flag=1)
        except Exception as e:
            msg = 'Error in print_category'
            self.add_error(msg + str(e))
            
    def append_category(self, event):
        try:
            str_ = event['text'].lower().split()
            flag = 0
            if '@' not in str_[2]:
                msg = 'Неправильно указан id пользователя. Пример @hare_hare'
                self.messages_send(event, msg)
                return 0

            with open('files/{str_}.txt'.format(str_=str_[1]), 'r+', encoding='utf-8') as file:
                lines = [i for i in file.readlines()]
                if str_[-1] + '\n' in lines:
                    msg = 'Данный пользователь уже является {str_}'.format(str_=str_[1])
                    self.messages_send(event, msg)
                else:
                    flag = 1
                    lines.append(str_[-1] + '\n')
                    msg = 'Данный пользователь добавлен в список {str_}'.format(str_=str_[1])
                    self.messages_send(event, msg)
                if flag == 1:
                    with open('files/{str_}.txt'.format(str_=str_[1]), 'w+', encoding='utf-8') as file:
                        for i in lines:
                            file.write(i)
        except Exception as e:
            msg = 'Error in append_category'
            self.add_error(msg + str(e))
            
            
bot = bot_vk(vk_session)
bot.start()
