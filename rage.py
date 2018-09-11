# -*- coding: utf-8 -*-

# Логика ведения диалога c роботом Рэйдж:
# 1. Робот записывает нашу речь и сохраняет в wav-файл
# 2. После чего он преобразовывает сохраненный wav-файл в текст
# 3. Затем он подключается к своей базе данных и ищет ответ на ваш текст
# 4. Если робот нашел ответ, то он превращает его в wav-файл

import pyaudio
import wave
import pygame
import requests
import sqlite3
from lxml import etree

# записывает нашу речь в wav-файл с помощью Pyaudio и Wave
def record():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 3
    WAVE_RECORD_FILENAME = "record.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* идет запись звука")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* запись остановлена")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_RECORD_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# преобразовывает нашу речь (wav-файл) в текст
def speech_to_text():
    key = '54526d6f-3723-4a60-b9a7-15e69bee621e'
    uuid = '88F1A7CB90D9D1B6A40D50465DE28C54'
    post = '/asr_xml?key=' + key + '&uuid=' + uuid + '&topic=queries'
    url = 'https://asr.yandex.net' + post
    headers = {"Content-Type": 'audio/x-wav'}
    data = open('record.wav', 'rb').read()
    tmp = requests.post(url, headers=headers, data=data)
    tree = etree.XML(tmp.content)
    tr1 = tree.xpath("/recognitionResults/variant/text()")
    for string_text in tr1:
        text = string_text
    return text

# преобразовывает текст в речь и записывает ее в wav-файл
def text_to_speech(text):
    url = 'https://tts.voicetech.yandex.net/tts?text='
    get_file = requests.get(url + text + '&format=wav&speaker=ermil')
    open('play.wav', 'wb').write(get_file.content)

# воспроизводит полученный wav-файл c помощью pygame
def play():
    pygame.init()
    pygame.mixer.Sound('play.wav').play()

# делает соединение с базой данных
connection = sqlite3.connect('base.db')
cursor = connection.cursor()
cursor.execute("SELECT * FROM commands")
rows = cursor.fetchall()

# запуск робота
while True:
    record()
    answer = "Я тебя не понимаю"
    text = speech_to_text()
    print "Я услышал: ", text
    for comand in rows:
        if text == comand[0]:
            answer = comand[1]
    if text == u"Выключись":
        break
    text_to_speech(answer)
    play()
