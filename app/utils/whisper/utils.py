# Path: utils/whisper/utils.py

import io
import ffmpeg
import numpy as np
import torch
import torch.nn.functional as F
from typing import BinaryIO, Union

SAMPLE_RATE = 16000
CHUNK_LENGTH = 30  # 30-second chunks
N_SAMPLES = CHUNK_LENGTH * SAMPLE_RATE  # 480000 samples in a 30-second chunk

def load_audio(file: Union[BinaryIO, bytearray], sr: int = SAMPLE_RATE, start_time: int = 0, dtype=np.float32):
    """
    Load an audio file into a numpy array at the specified sampling rate.
    Args:
        file (Union[BinaryIO, bytes]): The audio file to transcribe.
        sr (int): The sample rate for the audio file.
        start_time (int): The start time for loading audio.
        dtype: The data type for the output array.
    Returns:
        numpy.ndarray: The loaded audio array.
    """
    try:
        if isinstance(file, bytearray):
            file = io.BytesIO(file)
        
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=file.read())
        )

        # out, _ = (
        #     ffmpeg.input("pipe:", threads=0)
        #     .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
        #     .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=file.read())
        # )
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode()
        print(f"Failed to load audio: {error_message}")
        raise RuntimeError(f"Failed to load audio: {error_message}") from e
    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e

    return np.frombuffer(out, np.int16).flatten().astype(dtype) / 32768.0

def pad_or_trim(array, length: int = N_SAMPLES, *, axis: int = -1):
    """
    Pad or trim the audio array to N_SAMPLES, as expected by the encoder.
    """
    if torch.is_tensor(array):
        if array.shape[axis] > length:
            array = array.index_select(
                dim=axis, index=torch.arange(length, device=array.device)
            )

        if array.shape[axis] < length:
            pad_widths = [(0, 0)] * array.ndim
            pad_widths[axis] = (0, length - array.shape[axis])
            array = F.pad(array, [pad for sizes in pad_widths[::-1] for pad in sizes])
    else:
        if array.shape[axis] > length:
            array = array.take(indices=range(length), axis=axis)

        if array.shape[axis] < length:
            pad_widths = [(0, 0)] * array.ndim
            pad_widths[axis] = (0, length - array.shape[axis])
            array = np.pad(array, pad_widths)

    return array
