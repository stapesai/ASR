# Path: utils/whisper/__init__.py

from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    WhisperConfig,
)
import torch
import time
from typing import Tuple, BinaryIO

from app.utils.whisper.utils import load_audio, pad_or_trim
from app.config import settings

SAMPLE_RATE = 16000

processor = WhisperProcessor.from_pretrained(settings.MODEL_PATH)

config = WhisperConfig.from_pretrained(settings.MODEL_PATH)

model = (
    WhisperForConditionalGeneration(config=config)
    .from_pretrained(
        settings.MODEL_PATH,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    .to("cuda:0")
)
model.eval()


def transcribe(audio_file: BinaryIO) -> Tuple[str, float]:
    """
    Transcribe an audio file to text.
    Args:
        file_path (BinaryIO): The audio file to transcribe.
    """
    start_time = time.perf_counter()

    audio = load_audio(audio_file)

    # Save audio to disk (only for dev env)
    import soundfile as sf

    sf.write("temp_last_audio.wav", audio, SAMPLE_RATE)

    audio = pad_or_trim(audio)

    input_features = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").input_features.to(device=model.device, dtype=model.dtype)

    with torch.no_grad():
        logits = model.generate(
            input_features=input_features,
            language="en",
            forced_decoder_ids=None,
            use_cache=True,
            return_timestamps=False,
        )

    transcription = processor.batch_decode(logits, skip_special_tokens=True)[0]

    end_time = time.perf_counter()

    return transcription, end_time - start_time
