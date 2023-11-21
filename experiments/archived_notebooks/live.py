"""
# Working with live data
    1. Start PyAudio stream and listen it.
"""

# Config
# 19: pulse audio
MIC_IDX :int = 19
MIC_SAMPLE_RATE :int = 44100
SPK_IDX :int = 19
SPK_SAMPLE_RATE :int = 44100
CHUNK_SIZE :int = 1024

ENERGY_THRESHOLD :int = 1000
RECORD_TIMEOUT :int = 2
PHASE_TIMEOUT :int = 3

import pyaudio
from threading import Thread
from queue import Queue
from time import sleep
import numpy as np
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
import speech_recognition as sr
from io import BytesIO
from IPython.display import Audio

# from models.output.whisper_medium_fp16_transformers import Model
# model = Model('models/output/whisper_medium_fp16_transformers')

# Init PyAudio
pa = pyaudio.PyAudio()

# Init Queue
frames = Queue()
audio_data = Queue()

# List Devices
devices = []
for device_index in range(pa.get_device_count()):
    device_info = pa.get_device_info_by_index(device_index)
    devices.append(device_info)

microphones = [device for device in devices if device['maxInputChannels'] > 0]
for idx, microphone in enumerate(microphones):
    print(f"Microphone {microphone['index']}: {microphone['name']} InputCh:{microphone['maxInputChannels']} SampleRate:{microphone['defaultSampleRate']} OutCh:{microphone['maxOutputChannels']}")

speakers = [device for device in devices if device['maxOutputChannels'] > 0 and 'NVidia' not in device['name']]
for idx, speaker in enumerate(speakers):
    print(f"Speaker {speaker['index']}: {speaker['name']} InputCh:{speaker['maxInputChannels']} SampleRate:{speaker['defaultSampleRate']} OutCh:{speaker['maxOutputChannels']}")

# We use SpeechRecognizer to record our audio because it has a nice feauture where it can detect when speech ends.
recorder = sr.Recognizer()
recorder.energy_threshold = ENERGY_THRESHOLD
# Definitely do this, dynamic energy compensation lowers the energy threshold dramtically to a point where the SpeechRecognizer never stops recording.
recorder.dynamic_energy_threshold = False
source = sr.Microphone(sample_rate=16000, device_index=MIC_IDX)
with source:
    recorder.adjust_for_ambient_noise(source)

def record_callback(_, audio: sr.AudioData):
    # data = audio.get_raw_data()
    # audio_data.put(data)
    print('callback')
    audio_data.put(audio)
    # audio_=np.frombuffer(audio.get_wav_data(convert_rate=16000), dtype=np.float16)
    # print(audio_.shape, audio_.dtype, audio)
    # audio_ = audio_[~np.isnan(audio_)]
    # # audio_ = model._pad_or_trim(audio_)
    # audio_data.put(audio_)

# Create a background thread that will pass us raw audio bytes.
# We could do this manually but SpeechRecognizer provides a nice helper.
recorder.listen_in_background(source, record_callback, phrase_time_limit=RECORD_TIMEOUT)

# Start Stream
mic_stream = pa.open(
    rate=MIC_SAMPLE_RATE, 
    channels=1, 
    format=pyaudio.paFloat32, 
    input=True,
    # output=False,
    input_device_index=MIC_IDX,
    # output_device_index=SPK_IDX,
    frames_per_buffer=CHUNK_SIZE,
    start=True,
)
spk_stream = pa.open(
    rate=SPK_SAMPLE_RATE, 
    channels=1, 
    format=pyaudio.paFloat32, 
    # input=True,
    output=True,
    # input_device_index=MIC_IDX,
    output_device_index=SPK_IDX,
    # frames_per_buffer=CHUNK_SIZE,
    start=True,
)

def read_stream(stream):
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.put(data)
        # print(len(data))
        
def write_stream(stream):
    errors = 0
    while True:
        if frames.empty():
            print("No frames left", errors, end='\r')
            errors += 1
            continue
        
        data = frames.get()
        stream.write(data, exception_on_underflow=False)
        sleep(.005)
        
# Thread(target=read_stream, args=(mic_stream,)).start()
# sleep(2)
# Thread(target=write_stream, args=(spk_stream,)).start()

while True:
    if audio_data.empty():
        continue
    data = audio_data.get()
    data = sr.AudioData(data.get_raw_data(), source.SAMPLE_RATE, source.SAMPLE_WIDTH)
    data = BytesIO(data.get_wav_data())
    data = np.frombuffer(data.read(), dtype=np.float16)
    audio = data[~np.isnan(data)]
    # audio = model._pad_or_trim(audio)
    print(audio.shape, audio.dtype, audio)
    Audio(audio, rate=16000, autoplay=True)
    # text = model.transcribe(audio)
    # print(text)
    
    

# while mic_stream.is_active():
#     data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
    # text = model.transcribe(audio=np.frombuffer(data, dtype=np.float16))
    # print(text)
    # spk_stream.write(data, exception_on_underflow=False)

# Stop Stream
# mic_stream.stop_stream()
# mic_stream.close()
# spk_stream.stop_stream()
# spk_stream.close()

# pa.terminate()