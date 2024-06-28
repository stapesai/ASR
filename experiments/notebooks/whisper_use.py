 from transformers import pipeline
 from datasets import Audio
 import warnings
 from pvrecorder import PvRecorder
 import numpy
 from numpy.linalg import norm
 import sys
 from threading import Thread
 import time
 from collections import deque
 from sentence_transformers import SentenceTransformer, util
 
 warnings.filterwarnings("ignore")
 
 print("Loading speech recognizer...", flush=True, end=' ')
 speech_recognizer = pipeline("automatic-speech-recognition", 
                              model="openai/whisper-large-v2",
                              device="cuda:0")
 print("Loaded.", flush=True)
 
 print("Loading sentence transformer...", flush=True, end=' ')
 paraphrase = SentenceTransformer('paraphrase-MiniLM-L6-v2')
 print("Loaded.", flush=True)
 
 def str_to_vec(text):
     return paraphrase.encode(text)
 
 recorder = PvRecorder(device_index=-1, frame_length=512)
 print(recorder.selected_device, flush=True)
 
 sample_rate = 16000 #speech_recognizer.feature_extractor.sampling_rate
 
 audio = deque()
 recording = True
 
 def record_audio():
     global audio
     while recording:
         audio.extend(recorder.read())
 
 record_thread = Thread(target=record_audio)
 recorder.start()
 record_thread.start()
 
 def cosdiff(a, b):
     return (a @ b.T) / (norm(a)*norm(b))
 
 def process_conversation(text, vec):
     global conversation
     #print(text, flush=True)
     conversation.append((text, vec))
 
 max_samples = sample_rate * 30
 conversation = []
 last_text = ""
 last_vec = []
 ghosts = ["you", "You", "NO!"]
 
 try:
     while True:
         while len(audio) > max_samples:
             audio.popleft()
         if len(audio) > sample_rate:
             text = speech_recognizer(numpy.asarray(audio))["text"].strip()
             vec = str_to_vec(text)
             if len(last_vec) == len(vec):
                 cos_sim = cosdiff(vec, last_vec)
                 if not text in ghosts: # How I wish they didn't scream
                     print(f'{cos_sim:0.2f} ' + text, flush=True, end='\r')
                     if cos_sim >= 0.999:
                         print("                                                                               ", end='\r')
                         process_conversation(text, vec)
                         audio.clear()
                         text = ""
                         vec = []
             last_vec = vec
             last_text = text    
 
 except KeyboardInterrupt:
     recording = False
     recorder.stop()
 finally:
     recording = False
     recorder.delete()