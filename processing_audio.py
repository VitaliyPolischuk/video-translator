from google.cloud import texttospeech
import os
from pathlib import Path

from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS

import calendar
import time
import math
import re
import requests
from gtts import gTTS
from gtts_token.gtts_token import Token

def _patch_faulty_function(self):
    if self.token_key is not None:
        return self.token_key

    timestamp = calendar.timegm(time.gmtime())
    hours = int(math.floor(timestamp / 3600))

    results = requests.get("https://translate.google.com/")
    tkk_expr = re.search("(tkk:*?'\d{2,}.\d{3,}')", results.text).group(1)
    tkk = re.search("(\d{5,}.\d{6,})", tkk_expr).group(1)
    
    a , b = tkk.split('.')

    result = str(hours) + "." + str(int(a) + int(b))
    self.token_key = result
    return result


# Monkey patch faulty function.
Token._get_token_key = _patch_faulty_function

def synthesize_text(text, lang ,audio_output='output.mp3'):
    tts=gTTS(text=text, lang=lang)
    tts.save(audio_output)
    # The response's audio_content is binary.
    # with open(audio_output, 'wb') as out:
    #     out.write(response.audio_content)
    #     print('Audio content written to file' + audio_output)
# synthesize_text("Hello")

# def create_audio(speech, ):
def create_audio(speech, path, output_audio):
    input_audio_folder = os.path.join(
        Path().resolve(),
        path)

    input_audio_files = os.listdir(input_audio_folder)
    # print(input_audio_files[0].split('.')[0][-1])
    sorted_files = sorted(input_audio_files, key=lambda x: int(x.split('.')[0][-1]))
    audio_out_file = output_audio
    sorted_files = [input_audio_folder + '/' + file for file in sorted_files]


    def get_silence(end,start):
        print('==================')
        print((start-end)*1000)
        print('==================')
        return AudioSegment.silent(duration=(start-end)*1000)

    def get_audio(path):
        return AudioSegment.from_mp3(path)

    silence_list = []
    try:
        for i, val in enumerate(speech):
            if i == 0:
                silence_list.append(get_silence(0,speech[i]['start']))
            silence_list.append(get_silence(speech[i]['end'],speech[i+1]['start']))
    #         print(f"{speech[i]['end']} - {speech[i+1]['start']}")
    except IndexError:
        pass

    # print(sorted_files[0])
    start_audio = get_audio(sorted_files[0])
    final_song = silence_list[0]
    try:
        for i, audio in enumerate(sorted_files):
            if i == 0:
                final_song += get_audio(sorted_files[i])
            else:
                final_song += silence_list[i]
                final_song += get_audio(sorted_files[i])
    except IndexError:
        pass

    #Either save modified audio
    final_song.export(audio_out_file, format="wav")

#Or Play modified audio
# play(final_song)

