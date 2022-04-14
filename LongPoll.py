#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
import vk_api
import random
import time
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from io import BytesIO
from vk_api.upload import VkUpload
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import Pokemon
import info_pokemon
#from vk_api.keyboard import VkKeyboard, VkKeyboardColor

with open('files/token_0.txt', 'r', encoding='utf-8') as file:
    vk_session = vk_api.VkApi(token=file.readline())
    
class bot_vk():
    def __init__(self, vk_session):
        self.vk_session = vk_session
        self.longpoll = VkLongPoll(self.vk_session, wait=25) #, group_id=207883458
        self.vk = vk_session.get_api()
        self.upload = VkUpload(self.vk)
        self.list_name_category = ['admin'] #, ['admin', 'moderator', 'support']
        self.bot_2_id = 686552933
        
        self.user_csv = pd.read_csv('files/user.csv')
        
        self.server_flag = 1
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
                    
            if event.type == VkEventType.MESSAGE_NEW and event.text and event.from_user:
                event_text = event.text
                if event_text.split()[0].lower() == '/test2' or event_text.split()[0].lower() == '/тест2':
                    self.test_user(event)
            
            if event.type == VkEventType.CHAT_UPDATE and event.from_chat:
                self.message_greeting(event)
            if event.type == VkEventType.MESSAGE_NEW and event.text and event.from_chat:
                event_msg = self.vk.messages.getById(peer_id=event.peer_id, message_ids=event.message_id)['items'][0]
                event_text = event_msg['text']
                if len(event_text.split()) == 0:
                    continue
                if event_text.split()[0].lower() == '/test2' or event_text.split()[0].lower() == '/тест2':
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
        
    def messages_send(self, event, msg, attachments=[], keyboard=None, flag=0):
        self.vk.messages.send(
            peer_id=event['peer_id'],
            message=msg,
            random_id=time.time() * 1000,
            keyboard=keyboard,
            attachment=attachments,
            disable_mentions=flag
        )
         
    def messages_send_user(self, event, msg, attachments=[], keyboard=None):
        self.vk.messages.send(
            peer_id=event.user_id,
            message=msg,
            random_id=time.time() * 1000,
            keyboard=keyboard,
            attachment=attachments
        )
        
    def messages_delete(self, event, message_id_delete=[]):
        self.vk.messages.delete(
            peer_id=event['peer_id'],
            conversation_message_ids=message_id_delete,
            delete_for_all=1
            )
    
    def kick_user_by_bot(self, peer_id, ids):
        self.vk.messages.removeChatUser(chat_id=peer_id-2000000000, user_id=ids)
        
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
            self.add_error('Bot 2:' + msg + str(e))
            
bot = bot_vk(vk_session)
bot.start()
