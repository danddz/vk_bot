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
        self.list_commands = ['обнять', 'шлёпнуть', 'шлепнуть', 'укусить', 'погладить', 'поцеловать', 'ударить', 'поздравить', 'убить', 'обосрать', 'покебол', 'война']
        
        self.game = dict()
            
        self.list_mute = dict()
        self.user_csv = pd.read_csv('files/user.csv')
        
        self.server_flag = 1 # 0
        self.time = time.time()
        
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
            if time.time() > self.time + 20:
                self.upload = VkUpload(self.vk)
                self.time = time.time()
                    
            event_type = event.type

            if event_type == VkBotEventType.MESSAGE_NEW:
                event_text = event.object.message['text']
                event_from_user = event.object.message['from_id'] == event.object.message['peer_id']
                event_from_chat = event.object.message['from_id'] != event.object.message['peer_id']
                event_msg = event.object.message
                    
                if event_text and event_from_user:
                    if event_text.split()[0].lower() == '/test3' or event_text.split()[0].lower() == '/тест3':
                        self.test_user(event_msg)

                if event_text and event_from_chat:
                    if event_text.split()[0].lower() in self.list_commands:
                        self.rp_commands(event_msg)
                    elif event_text.split()[0].lower() == '/список' and len(event_text.split()) == 2 and event_text.split()[1].lower() == 'рп':
                        self.print_list_rp(event_msg)
                    elif event_text.split()[0].lower() == 'токсик':
                        self.beskin_tomato(event_msg)
                    elif event_text.split()[0][:4].lower() == 'бот,' and event_text.split()[-1][-1].lower() == '?' and 'какая' in event_text.split() and ('вероятность,' in event_text.split() or 'вероятность' in event_text.split()):
                        self.get_answer_2(event_msg)
                    elif event_text.split()[0][:4].lower() == 'бот,' and event_text.split()[-1][-1].lower() == '?':
                        self.get_answer(event_msg)
                    elif event_text.split()[0].lower() == '/стрим':
                        self.stream_notification(event_msg)
                    elif event_text.split()[0].lower() == '/test3' or event_text.split()[0].lower() == '/тест3':
                        self.test(event_msg)
                    elif event_text.split()[0].lower() == '/стоп':
                        if self.checking_access_rights(event_msg, ['admin']):
                            return False
                    
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
        
    def name_user(self, user_id):
        people = self.vk.users.get(user_ids=user_id, fields='sex')[0]
        first_name, last_name = people['first_name'], people['last_name']
        name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
        sex = people['sex']
        return name, sex
    
    def name_to_user(self, user_id, case):
        people = self.vk.users.get(user_ids=user_id, fields=f'sex, first_name_{case}, last_name_{case}')[0]
        first_name, last_name = people[f'first_name_{case}'], people[f'last_name_{case}']
        name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
        sex = people['sex']
        return name, sex
    
    def beskin_tomato(self, event):
        msg = '@besklo получает смачное попадание в лицо помидором'
        self.messages_send(event, msg)
        
    def get_answer(self, event):
        if random.randint(0, 1) == 0:
            msg = 'Да'
        else:
            msg = 'Нет'
        self.messages_send(event, msg)
        
    def get_answer_2(self, event):
        tmp = random.randint(0, 100)
        msg = f'Вероятность {tmp}%'
        self.messages_send(event, msg)
        
    def print_list_rp(self, event):
        tmp = str()
        for i in self.list_commands:
            tmp += i + ', '
        tmp = tmp[:-2]
        msg = f'Список доступных команд: {tmp}'
        self.messages_delete(event, event['conversation_message_id'])
        self.messages_send(event, msg)
    
    def rp_commands(self, event):
        try:
            text = event['text'].split()
            from_id = event['from_id']

            if len(event['text'].split()) == 2 and '@' in event['text'].split()[1].lower():
                to_id = text[1].split('|')[0][3:]
            elif 'reply_message' in event.keys():
                to_id = event['reply_message']['from_id']
            elif event['fwd_messages'] != []:
                to_id = event['fwd_messages'][0]['from_id']
            else:
                return 0

            dict_commands = {'обнять': 'обнял',
                            'шлёпнуть': 'шлёпнул',
                            'шлепнуть': 'шлёпнул',
                            'укусить': 'укусил',
                            'погладить': 'погладил',
                            'поцеловать': 'поцеловал',
                            'ударить': 'ударил',
                            'поздравить': 'поздравил',
                            'убить': 'убил',
                            'обосрать': 'обосрал',
                            'покебол': 'кинул',
                            'война': 'объявил'}

            dict_smile = {'обнять': '🤗',
                         'шлёпнуть': '🖐',
                         'шлепнуть': '🖐',
                         'укусить': '🧛‍♀',
                         'погладить': '👋',
                         'поцеловать': '💋',
                         'ударить': '👊',
                         'поздравить': '🥳',
                         'убить': '☠',
                         'обосрать': '💩',
                         'покебол': 'покебол ⚾ в',
                         'война': 'войну 🗡'}

            dict_case = {'обнять': 'acc',
                        'шлёпнуть': 'acc',
                        'шлепнуть': 'acc',
                        'укусить': 'acc',
                        'погладить': 'acc',
                        'поцеловать': 'acc',
                        'ударить': 'acc',
                        'поздравить': 'acc',
                        'убить': 'acc',
                        'обосрать': 'acc',
                        'покебол': 'acc',
                        'война': 'dat'}

            from_name, from_sex = self.name_user(from_id)
            to_name, to_sex = self.name_to_user(to_id, dict_case[text[0].lower()])
            msg_text = dict_commands[text[0].lower()]
            msg_smile = dict_smile[text[0].lower()]

            if from_sex == 1:
                msg = f'{from_name} {msg_text}а {msg_smile} {to_name}'
            else:
                msg = f'{from_name} {msg_text} {msg_smile} {to_name}'

            self.messages_delete(event, event['conversation_message_id'])
            self.messages_send(event, msg, flag=1)
        except Exception as e:
            msg = 'rp_commands'
            self.add_error(msg + str(e))
        
    def stream_notification(self, event):
        try:
            if str(event['from_id']) == '271884149':
                file_name = 'reich'
            elif str(event['from_id']) == '61925283':
                file_name = 'olegova'
            elif str(event['from_id']) == '156032946':
                file_name = 'reich'
            else:
                return 0

            msg = str()
            with open(f'files/stream_{file_name}.txt', 'r+', encoding='utf-8') as file:
                msg = ''.join(i for i in file.readlines())

            tmp = 'https://sun9-85.userapi.com/impg/nOP32io1qRfyFxvSJanAvGhLi8nRelmjXkFUTA/qwdRMO-AW0g.jpg?size=736x900&quality=95&sign=8a31e9a89292e1bb009f701e0ed91f70&type=album'
            img = requests.get(tmp).content
            f = BytesIO(img)
            response = self.upload.photo_messages(f)[0]
            owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
            attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

            self.messages_delete(event, event['conversation_message_id'])
            self.messages_send(event, msg, attachments=attachment, flag=1)
        except Exception as e:
            msg = 'stream_notification'
            self.add_error(msg + str(e))
            
bot = bot_vk(vk_session)
bot.start()
