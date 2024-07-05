# Path: utils/whisper/__init__.py

from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    WhisperConfig,
)
import torch
from time import perf_counter
from typing import Tuple, BinaryIO

from .utils import load_audio, pad_or_trim

SAMPLE_RATE = 16000
MODEL_PATH = "models/whisper/whisper-tiny"

processor = WhisperProcessor.from_pretrained(MODEL_PATH)

config = WhisperConfig.from_pretrained(MODEL_PATH)

model = WhisperForConditionalGeneration(config=config).from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
).to('cuda:0')
model.eval()

def transcribe(audio_file: BinaryIO) -> Tuple[str, float]:
    """
    Transcribe an audio file to text.
    Args:
        file_path (BinaryIO): The audio file to transcribe.
    """
    start_time = perf_counter()
    
    audio = load_audio(audio_file)
    audio = pad_or_trim(audio)
    
    input_features = processor(
        audio, sampling_rate=SAMPLE_RATE, return_tensors="pt"
        ).input_features.to(device=model.device, dtype=model.dtype)
    
    with torch.no_grad():
        logits = model.generate(
            input_features=input_features,
            language='en',
            use_cache=True,
            return_timestamps=False,
        )
    
    transcription = processor.batch_decode(logits, skip_special_tokens=True)[0]

    end_time = perf_counter()
    
    return transcription, end_time - start_time
