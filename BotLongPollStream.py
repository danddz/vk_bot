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
        self.peer_id = 2000000004  # 2000000002/2000000004
        
        self.channel_names = {'txc_gonza': False, 'dochka_deputata': False, 'toxic_team_bot': False, 'lisha328': False}
        
        self.server_flag = 1 # 0
        self.time = time.time()
        self.time_stream = time.time()
        
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
        while True:
            if time.time() > self.time + 20:
                self.upload = VkUpload(self.vk)
                self.time = time.time()
            
            if time.time() > self.time_stream + 60:
                self.stream()
                self.time_stream = time.time()
#                 print(self.channel_names)
        
    def messages_send(self, event, msg, attachments=[], peer_id=None, keyboard=None, flag=0, links=0):
        if peer_id == None:
            peer_id=event['peer_id']
        conversation_message_id = self.vk.messages.send(
            peer_id=peer_id,
            message=msg,
            random_id=time.time() * 1000,
            keyboard=keyboard,
            attachment=attachments,
            dont_parse_links=links,
            disable_mentions=flag
        )
        return conversation_message_id
    
    def add_error(self, msg_error):
        tmp_lines = list()
        now = time.ctime(int(time.time()))
        with open('files/errors.txt', 'r+', encoding='utf-8') as file:
            tmp_lines = file.readlines()
        tmp_lines.append(msg_error + ' ' + now + '\n')
        with open('files/errors.txt', 'w+', encoding='utf-8') as file:
            for i in tmp_lines:
                file.write(i)
        
    def name_user(self, user_id):
        people = self.vk.users.get(user_ids=user_id, fields='sex')[0]
        first_name, last_name = people['first_name'], people['last_name']
        name = '@id{user_id} ({first_name} {last_name})'.format(user_id=user_id, first_name=first_name, last_name=last_name)
        sex = people['sex']
        return name, sex
    
    @staticmethod
    def stream_check(channel_name):
        URL = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
        authURL = 'https://id.twitch.tv/oauth2/token'
        Client_ID = 'iw3tmxj532yaddrsy6dja21tc6qxdy'
        Secret  = 'yu5uhj40tyjvbrc9qox1p75wo5gxm9'

        AutParams = {'client_id': Client_ID,
                     'client_secret': Secret,
                     'grant_type': 'client_credentials'
                     }

        AutCall = requests.post(url=authURL, params=AutParams)
        access_token = AutCall.json()['access_token']

        head = {
        'Client-ID' : Client_ID,
        'Authorization' :  "Bearer " + access_token
        }

        r = requests.get(URL, headers = head).json()['data']

        if r:
            r = r[0]
            if r['type'] == 'live':
                return True
            else:
                return False
        else:
            return False
                
    def stream_notification(self, file_name):
        msg = str()
        with open(f'files/stream/{file_name}.txt', 'r+', encoding='utf-8') as file:
            msg = ''.join(i for i in file.readlines())

        tmp = str()
        with open(f'files/stream/img_{file_name}.txt', 'r+', encoding='utf-8') as file:
            tmp = ''.join(i for i in file.readlines())
        img = requests.get(tmp).content
        f = BytesIO(img)
        response = self.upload.photo_messages(f)[0]
        owner_id, photo_id, access_key = response['owner_id'], response['id'], response['access_key']
        attachment = 'photo{owner_id}_{photo_id}_{access_key}'.format(owner_id=owner_id, photo_id=photo_id, access_key=access_key)

        self.messages_send(None, msg, peer_id=self.peer_id,attachments=attachment, flag=1, links=1)
        
    def stream(self):
        for i in self.channel_names:
            if not self.channel_names[i]:
                if self.stream_check(i):
                    self.stream_notification(i)
                    self.channel_names[i] = True
            else:
                if not self.stream_check(i):
                    self.channel_names[i] = False
                    
bot = bot_vk(vk_session)
bot.start()
