from lib2to3.pytree import Base
from typing import TextIO

from sympy import content
import vk_api.vk_api
import telebot
import threading
import random
import time
import os
import sys
import pyglet
import urllib.request

from pyrogram import Client, filters    
from PIL import Image
from random import *
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

token = "ae88620090e527af17a115b15acfad4f5bdcfe007a4184225df81d0055e7fe1543eb40dc29250d994fae4"

vk = vk_api.VkApi(token = token)
api = vk.get_api()
longpoll = VkBotLongPoll(vk, 203206891)

Teletoken = '5241034302:AAGctdn4nzpgX0srmueUkYxSU_YlmodU9Nw'
Telbot = telebot.TeleBot(Teletoken)

TeleId = "429162266"
ids = 0
mssg = ""

'''
TO DO: 
    GITHUB
    TELEGRAM RESPONSE
'''

def bd_update(bd):
    file = open(os.path.join(sys.path[0], 'bd.txt'), "r")
    nbd = int(file.readline())
    for i in range (nbd):
        bd.add(str(file.readline()))
    file.close()

def black_update(black):
    file = open(os.path.join(sys.path[0], 'black.txt'), "w")
    nbd = len(black)
    file.write(str(nbd) + "\n")
    for i in range (nbd):
        file.write(i)
    file.close()

def file_print():
    file = open(os.path.join(sys.path[0], 'bd.txt'), "r")
    nbd = int(file.readline())
    Telbot.send_message(TeleId, nbd)
    for i in range (nbd):
        Telbot.send_message(TeleId, file.readline())
    file.close()

def printBD(bd):
    for i in bd:
        Telbot.send_message(TeleId, "ID: " + "/" + i + "Name: " + get_name(int(i)))

def get_name(from_user):
    user = vk.method("users.get", {"user_ids": from_user})
    name = user[0]['first_name'] +  ' ' + user[0]['last_name']
    return name

def get_title(chat_id):
    if chat_id == 1:
        return "Хантеры"
    elif chat_id == 2:
        return "Test"
    elif chat_id == 5:
        return "Сохры недохацкеров"
    elif chat_id == 4:
        return "Недохацкеры"

def add_to_file(i):
    file = open(os.path.join(sys.path[0], 'bd.txt'), "w")
    nbd = len(bd) + 1
    file.write(str(nbd) + "\n")
    for j in bd:
        file.write(str(j))
    file.write(str(i) + "\n")
    Telbot.send_message(TeleId, "Successfully added to database")
    file.close()


def get_res_photo(i):
    j = 0
    for v in i['sizes']:
        j += 1
    return int(j-1)

def get_res_vid(i):
    j = 0
    for v in i['image']:
        j += 1
    return int(j-1)

def get_event(event, mssag):
    try:
        mssag = mssag + "ID: /" + str(event['from_id']) + "\nName: " + str(get_name(str(event['from_id']))) + "\n"
        if event['text'] != "":
            mssag = mssag + "Text: " + str(event['text'])
        Telbot.send_message(TeleId, mssag)
        if event['attachments'] != []:
            for i in event['attachments']:
                if i['type'] == 'photo':
                    url = i["photo"]["sizes"][int(get_res_photo(i["photo"]))]['url']
                    Telbot.send_photo(TeleId, url)
                if i['type'] == 'video':
                    url = i["video"]["image"][int(get_res_vid(i["video"]))]['url']
                    Telbot.send_video(TeleId, url)
                if i['type'] == "audio_message":
                    url = i['audio_message']['link_ogg']
                    Telbot.send_audio(TeleId, url)
                if i['type'] == "doc":
                    if i['doc']['title'] != "": Telbot.send_message(TeleId, "Doc name: " + str(i['doc']['title']))
                    url = i['doc']['url']
                    Telbot.send_document(TeleId, url)
                if i['type'] == 'wall':
                    if (str(i['wall']['text'])) != "": Telbot.send_message(TeleId, "Wall text:\n" + str(i['wall']['text']))
                    for j in i['wall']['attachments']:
                        if j['type'] == 'photo':
                            url = j["photo"]["sizes"][int(get_res_photo(j["photo"]))]['url']
                            Telbot.send_photo(TeleId, url)
                        if j['type'] == 'video':
                            url = j["video"]["image"][int(get_res_vid(j["video"]))]['url']
                            Telbot.send_video(TeleId, url)
        global mssg
        try:
            if event['fwd_messages']:
                for i in event['fwd_messages']:
                    Telbot.send_message(TeleId, "Forwarded:")
                    mssg = ""
                    get_event(i, mssg)
        except BaseException as err:
            if ('fwd_messages' in str(err)):
                pass
        try:
            if event['reply_message']:
                Telbot.send_message(TeleId, "Forwarded:")
                mssg = ""
                get_event(event['reply_message'], mssg)
        except BaseException as err:
            if ('reply_message' in str(err)):
                pass

    except BaseException as err:
        if ("Read timed out" in str(err)):
            time.sleep(2)
            mssag = ""
            get_event(event, mssag)
            pass
        else:
            Telbot.send_message(TeleId, "Error while getting event: " + str(err))

def get_history(event):
    global mssg
    mssg = ""
    try:
        for i in reversed(event['items']):
            get_event(i, mssg)
    except BaseException as err:
        Telbot.send_message(TeleId, "Error while getting chat history: " + str(err))

def write_msg(id, text):
    vk.method('messages.send', {'user_id' : id, 'message' : text, 'random_id': 0})
def send_attach(id, attach):
    vk.method('messages.send', {'user_id' : id, 'attachment': attach, 'random_id': 0})



def init_Vk():
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    global fwd_depth
                    global mssg
                    mssg = ""
                    fwd_depth = 0
                    if event.from_user:

                        #Database autoupdate:
                        if (str(event.object['message']['from_id']) in bd and str(event.object['message']['from_id']) in black):
                            file = open(os.path.join(sys.path[0], 'bd.txt'), "w")
                            nbd = len(bd) + 1
                            file.write(str(nbd) + "\n")
                            for i in bd:
                                file.write(str(i))
                            file.write(str(event.object['message']['from_id']) + "\n")
                            file.close()
                            Telbot.send_message(TeleId, "New contact added: " + get_name(str(event.object['message']['from_id'])))
                            bd_update(bd)
                                    
                        #Events:
                        t = threading.Thread(target = get_event(event.object['message'], mssg))
                        t.start()
                                                        
                    elif event.from_chat:
                        mssg = "Chat: " + str(get_title(event.chat_id)) + "\n"
                        t = threading.Thread(target  = get_event(event.object['message'], mssg))
                        t.start()
        except BaseException as err:
            if "HTTPSConnectionPool" in str(err):
                time.sleep(5)
                pass



def init_Tele():
    while True:
        try:
            @Telbot.message_handler(content_types=['text'])
            def handle_text(message):

                if (message.text == "/help"):
                    t = threading.Thread(target = printBD(bd))
                    t.start()
                    
                elif (message.text == "/status"):
                    Telbot.send_message(TeleId, "All systems normal...\nPID: " + str(os.getpid()))

                elif (message.text == "/update"):
                    try:
                        t = threading.Thread(target = bd_update(bd))
                        t.start()
                        t.join()
                        Telbot.send_message(TeleId, "Database updated")
                    except BaseException as err:
                        Telbot.send_message(TeleId, "Error while updating database: " + str(err))

                elif (message.text == "/bdfile"):
                    file_print()
                
                elif (message.text == '/reboot'):
                    Telbot.send_message(TeleId, "Rebooting...")
                    os.system("reboot") 

                elif ("/add " in message.text):
                    i = str(message.text)
                    i = i.replace('/add ', '', 1)
                    t = threading.Thread(target = add_to_file(i))
                    t.start()
                    t.join()
                    t = threading.Thread(target = bd_update(bd))
                    t.start()
                    t.join()
                    
                elif ("/history " in message.text):
                    i = str(message.text)
                    i = i.replace('/history ', '', 1)
                    try:
                        id = i[0:9]
                        colvo = i[10:]
                        event = vk.method('messages.getHistory', {'user_id' : id, 'count' : colvo})
                        t = threading.Thread(target = get_history(event))

                    except BaseException as err:
                        Telbot.send_message(TeleId, "Error wile starting history dump: " + str(err))

                elif ("/blacklist " in message.text):
                    i = str(message.text)
                    i = i.replace('/blacklist ', '', 1)
                    try:
                        black.add(i)
                        bd.remove(i)
                        t = threading.Thread(target = bd_update(bd))
                        t.start()
                        t.join()
                        t = threading.Thread(target = black_update(bd))
                        t.start()
                        t.join()
                        Telbot.send_message(TeleId, "Successfully added to blacklist")
                    except BaseException as err:
                        Telbot.send_message(TeleId, "Error while adding to blacklist: " + str(err))

                elif ("/unblack " in message.text):
                    i = str(message.text)
                    i = i.replace('/unblack ', '', 1)
                    try:
                        black.remove(i)
                        bd.add(i)
                        t = threading.Thread(target = bd_update(bd))
                        t.start()
                        t.join()
                        t = threading.Thread(target = black_update(bd))
                        t.start()
                        t.join()
                        Telbot.send_message(TeleId, "Successfully removed from blacklist")
                    except BaseException as err:
                        Telbot.send_message(TeleId, "Error while removing from blacklist: " + str(err))    

                elif (str(message.text)[0] == "/" and str(message.text)[1] != "/"):
                    try:
                        global ids
                        i = str(message.text)
                        i = i.replace('/', '', 1)
                        ids = int(i)
                        Telbot.send_message(TeleId, "Reciever specified: " + get_name(ids))
                    except BaseException as err:
                        Telbot.send_message(TeleId, "Error occured while setting reciever id: " + str(err))

                elif (str(message.text)[0] != "/"):
                    try:
                        write_msg(ids, message.text)
                        Telbot.send_message(TeleId, "Sent to " + get_name(ids))
                    except BaseException as err:
                        Telbot.send_message(TeleId, "Error occured while sending message: " + str(err))

            @Telbot.message_handler(content_types=['sticker'])
            def handle_docs_audio(message):
                file_info = Telbot.get_file(message.sticker.file_id)
                Telbot.send_document(TeleId, file_info)
                #urllib.request.urlretrieve(f'http://api.telegram.org/file/bot{Teletoken}/{file_info.file_path}', '/home/qtk/Teletemp/{file_info_file_path}')
                #send_attach(ids, '/home/qtk/Teletemp/{file_info_file_path}')

            Telbot.polling(none_stop=True, interval = 0, timeout = 60)
            
        except BaseException as err:
            if ("Read timed out" in str(err)):
                time.sleep(5)
                pass

try:
    bd = set()
    bd_update(bd)
except BaseException as err:
    Telbot.send_message(TeleId, "Error while updating database: " + str(err))

#Black initiation
try:
    black = set()
    file = open(os.path.join(sys.path[0], 'black.txt'), "r")
    nbd = int(file.readline())
    for i in range (nbd):
        black.add(str(file.readline()))
    file.close()
except BaseException as err:
    Telbot.send_message(TeleId, "Error while updating blacklist: " + str(err))

t2 = threading.Thread( target=init_Tele )
t1 = threading.Thread( target=init_Vk )
t1.start()
t2.start()
Telbot.send_message(TeleId, "All systems are yours,\nwelcome back, Pilot\n/help")
t1.join()
t2.join()

#sound = open(os.path.join(sys.path[0], 'sounds/WelcomeBackPilot.ogg'), "rb")
#Telbot.send_audio(TeleId, sound)