#!/usr/bin/env python3

import time
import socket
import pyaudio
import snowboydecoder
import subprocess
import os
import speech_recognition as sr
import json
from urllib.parse import unquote
from tts import say
from time import sleep

import urllib.request

home = os.path.abspath(os.path.dirname(__file__)) 
#Адрес до MajorDomo 
urlmjd = 'http://192.168.2.62'



def detected():
   try:
       if ALARMKWACTIVATED == "1":
           subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       index = pyaudio.PyAudio().get_device_count() - 1
       print (index)
       r = sr.Recognizer()
       with sr.Microphone(index) as source:
           r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать. 
           
           audio = r.listen(source, timeout = 10)
           if ALARMTTS == "1":
               subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           print("Processing !")
           #command=r.recognize_wit(audio, key="2S2VKVFO5X7353BN4X6YBX56L4S2IZT4")
           command=r.recognize_google(audio, language="ru-RU")
           print(command)
           if ALARMSTT == "1":
               subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           link=urlmjd+'/command.php?qry=' + urllib.parse.quote_plus(command)
           f=urllib.request.urlopen(link)
   except  sr.UnknownValueError as e:
           print("Произошла ошибка  {0}".format(e))
		   #detected ()
   except sr.RequestError as e:
           print("Произошла ошибка  {0}".format(e))
           say ("Произошла ошибка  {0}".format(e))

   except sr.WaitTimeoutError:
           print ("Я ничего не услышала")
           say ("Я ничего не услышала")

		   



def parse(conn, addr):# обработка соединения в отдельной функции
    data = b""
    
    while not b"\r\n" in data: # ждём первую строку
        tmp = conn.recv(1024)
		
        if not tmp:   # сокет закрыли, пустой объект
            #print ("tmp error")
            break
        else:
            data += tmp
            print ("OK tmp")
    
    if not data:      # данные не пришли
        return        # не обрабатываем
        
    udata = data.decode("utf-8")
    # берём только первую строку
    udata = udata.split("\r\n", 1)[0]
    print (udata)
    # разбиваем по пробелам нашу строку
    method, text = udata.split(":", maxsplit=1)
    #text = address[address.find("tts:")+1:]
    #text = unquote(text)
    if method == 'tts' :
       sleep(0.5)
       say (text)
    if method == 'ask' :
       detected()
    if method == 'settings' : 
       settings = text
       json_string = settings
              
       with open(home+'/config.xml', 'w', encoding='utf-8') as file:
           json.dump(json_string, file)
       jsonimport()
       
def jsonimport():
    global ID, TITLE, NAME, LINKEDROOM, PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, SENSITIVITY, ALARMKWACTIVATED, ALARMTTS, ALARMSTT
    with open(home+'/config.xml') as data_file:    
           json_data = json.load(data_file)
		   
    parsed_data = json.loads(json_data)
    ID = parsed_data["ID"] #номер терминала
    TITLE = parsed_data["TITLE"] #навазние терминала 
    NAME = parsed_data["NAME"] #Системное имя
    LINKEDROOM = parsed_data["LINKEDROOM"] #Расположение 
    IP = parsed_data["IP"]
    PROVIDERTTS = parsed_data["PROVIDERTTS"] # Сервис синтеза речи
    APIKEYTTS = parsed_data["APIKEYTTS"] #Ключ API сервиса синтеза речи:
    PROVIDERSTT = parsed_data["PROVIDERSTT"] #Сервис распознования речи
    APIKEYSTT = parsed_data["APIKEYSTT"] #Ключ API сервиса распознования речи:
    SENSITIVITY = parsed_data["SENSITIVITY"] #Чувствительность реагирования на ключевое слово
    ALARMKWACTIVATED = parsed_data["ALARMKWACTIVATED"] #Сигнал о распозновании ключевого слова
    ALARMTTS = parsed_data["ALARMTTS"] #Сигнал перед сообщением
    ALARMSTT = parsed_data["ALARMSTT"] #Сигнал перед начале распознования речи
    print (ALARMTTS)
    
       



jsonimport()	   
sock = socket.socket()
sock.bind( ("", 7999) )
sock.listen(1)


try:
    while 1: # работаем постоянно
        conn, addr = sock.accept()
        conn.settimeout(2.0)
        print("New connection from " + addr[0])
        try:
            parse(conn, addr)

        except socket.timeout:
            print (addr, "timeout")
        
		
        finally:
            # так при любой ошибке
            # сокет закроем корректно
            conn.close()
finally: sock.close()
# так при возникновении любой ошибки сокет
# всегда закроется корректно и будет всё хорошо