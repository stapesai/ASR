import whisper
import gradio as gr
import torch
import os

def fp32_model_medium(audio, lang):
    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(medium_fp32.device)

    # decode the audio
    options = whisper.DecodingOptions(language=lang)
    result = whisper.decode(medium_fp32, mel, options)
    torch.cuda.empty_cache()
    return result.text

def fp16_model_medium(audio, lang):
    return medium_fp16.transcribe(audio, language=lang, skip_special_tokens=True)

# def fp16_model_large_v2(audio, lang):
#     torch.cuda.empty_cache()
#     return large_v2_fp16.transcribe(audio, language=lang, skip_special_tokens=True)

def int8_fp16_medium(audio, lang):
    torch.cuda.empty_cache()
    segments, info = medium_int8_fp16.transcribe(audio, language=lang, beam_size=1, without_timestamps=False)
    return ' '.join([segment.text for segment in segments])

# def int8_fp16_large_v2(audio, lang):
#     torch.cuda.empty_cache()
#     segments, info = large_v2_int8_fp16.transcribe(audio, language=lang, beam_size=1, without_timestamps=False)
#     return ' '.join([segment.text for segment in segments])

def int8_medium(audio, lang):
    torch.cuda.empty_cache()
    segments, info = medium_int8.transcribe(audio, language=lang, beam_size=1, without_timestamps=False)
    return ' '.join([segment.text for segment in segments])

# def int8_large_v2(audio, lang):
#     torch.cuda.empty_cache()
#     segments, info = large_v2_int8.transcribe(audio, language=lang, beam_size=1, without_timestamps=False)
#     return ' '.join([segment.text for segment in segments])

# Load Models
medium_fp32 = whisper.load_model('medium', download_root='./models/compiled', device='cuda')
from models.output.whisper_medium_fp16_transformers import Model
medium_fp16 = Model('models/output/whisper_medium_fp16_transformers', device='cuda')

# from models.output.whisper_large_v2_fp16_transformers import Model
# large_v2_fp16 = Model('models/output/whisper_large_v2_fp16_transformers', device='cuda')

from faster_whisper import WhisperModel
medium_int8_fp16 = WhisperModel('models/output/whisper_medium_int8_float16_ct2', device='cuda', compute_type='int8_float16')
medium_int8 = WhisperModel('models/output/whisper_medium_int8_ct2', device='cuda', compute_type='int8')

# large_v2_int8_fp16 = WhisperModel('models/output/whisper_large_v2_int8_float16_ct2', device='cuda', compute_type='int8_float16')
# large_v2_int8 = WhisperModel('models/output/whisper_large_v2_int8_ct2', device='cuda', compute_type='int8')

def transcribe(microphone, upload, lang):
    file_pth = microphone or upload

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(file_pth)
    audio = whisper.pad_or_trim(audio)

    return [
        fp32_model_medium(audio, lang),
        fp16_model_medium(audio, lang),
        int8_fp16_medium(audio, lang),
        int8_medium(audio, lang),
        # fp16_model_large_v2(audio, lang),
        # int8_fp16_large_v2(audio, lang),
        # int8_large_v2(audio, lang),
    ]

gr.Interface(
    title='JARVIS Speech to Text Demo',
    fn=transcribe,
    inputs=[
        gr.Audio(source="microphone", type="filepath", label="Speak", interactive=True),
        gr.Audio(source="upload", type="filepath", label="Upload Audio File", interactive=True),
        gr.Dropdown(['en', 'hi'], label="Language"),
    ],
    outputs=[
        gr.Textbox(label="FP32 Model Medium"),
        gr.Textbox(label="FP16 Model Medium"),
        gr.Textbox(label="int8_fp16 Model Medium"),
        gr.Textbox(label="int8 Model Medium"),
        # gr.Textbox(label="FP16 Model Large-v2"),
        # gr.Textbox(label="int8_fp16 Model Large-v2"),
        # gr.Textbox(label="int8 Model Large-v2"),
        ],
    live=True).launch(
        server_name='127.0.0.1', 
        server_port=8080, 
        share=True
    )
