# -*- coding: utf-8 -*-
import os
from config import Config
from flask import Flask, send_from_directory
from werkzeug.contrib.fixers import ProxyFix
import logging
from gtts import gTTS
from pydub import AudioSegment
import hashlib
try:
    from urllib.parse import unquote_plus
except:
    from urllib import unquote_plus

config = Config()

app = Flask(__name__)
logging.getLogger('flask_tts').setLevel(logging.DEBUG)

STORAGE_DIR = os.environ['STORAGE_DIR']


@app.route('/generate/<lang>/<text>')
def generate(lang, text):
    lang = lang.lower()
    text = unquote_plus(text)
    tts = gTTS(text=text, lang=lang)
    filename = lang+'_'+hashlib.sha1(text.encode('punycode')).hexdigest()+'.mp3'
    if os.path.isfile(STORAGE_DIR+filename):
        return send_from_directory(STORAGE_DIR, filename)

    tts.save(STORAGE_DIR+filename)
    sound = AudioSegment.from_file(STORAGE_DIR+filename, format='mp3')
    sound = sound.apply_gain(+8.0)
    sound.export(STORAGE_DIR+filename,
                 format="mp3",
                 bitrate="48k",
                 parameters=['-ac','2','-ar', '16000'])
    return send_from_directory(STORAGE_DIR, filename)


if __name__ == '__main__':
    # Be sure to set config.debug_mode to False in production
    port = int(os.environ.get("PORT", config.port))
    if port != config.port:
        config.debug = False
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', debug=config.debug_mode, port=port)
