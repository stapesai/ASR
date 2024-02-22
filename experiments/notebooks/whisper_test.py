
import argparse
import os
import sys
import warnings
import whisper
from pathlib import Path
import subprocess
import torch
import shutil
import numpy as np
parser = argparse.ArgumentParser(
    description="OpenAI Whisper Automatic Speech Recognition")
parser.add_argument("-l", dest="audiolanguage", type=str, help="Language spoken in the audio, use Auto detection to let Whisper detect the language. Select from the following languages['Auto detection', 'Afrikaans', 'Albanian', 'Amharic', 'Arabic', 'Armenian', 'Assamese', 'Azerbaijani', 'Bashkir', 'Basque', 'Belarusian', 'Bengali', 'Bosnian', 'Breton', 'Bulgarian', 'Burmese', 'Castilian', 'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Faroese', 'Finnish', 'Flemish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Haitian', 'Haitian Creole', 'Hausa', 'Hawaiian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Javanese', 'Kannada', 'Kazakh', 'Khmer', 'Korean', 'Lao', 'Latin', 'Latvian', 'Letzeburgesch', 'Lingala', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 'Maltese', 'Maori', 'Marathi', 'Moldavian', 'Moldovan', 'Mongolian', 'Myanmar', 'Nepali', 'Norwegian', 'Nynorsk', 'Occitan', 'Panjabi', 'Pashto', 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Pushto', 'Romanian', 'Russian', 'Sanskrit', 'Serbian', 'Shona', 'Sindhi', 'Sinhala', 'Sinhalese', 'Slovak', 'Slovenian', 'Somali', 'Spanish', 'Sundanese', 'Swahili', 'Swedish', 'Tagalog', 'Tajik', 'Tamil', 'Tatar', 'Telugu', 'Thai', 'Tibetan', 'Turkish', 'Turkmen', 'Ukrainian', 'Urdu', 'Uzbek', 'Valencian', 'Vietnamese', 'Welsh', 'Yiddish', 'Yoruba'] ", default="English")
parser.add_argument("-p", dest="inputpath", type=str,
                    help="Path of the input file", default="test.wav")
parser.add_argument("-v", dest="typeverbose", type=str,
                    help="Whether to print out the progress and debug messages. ['Live transcription', 'Progress bar', 'None']", default="Live transcription")
parser.add_argument("-g", dest="outputtype", type=str,
                    help="Type of file to generate to record the transcription. ['All', '.txt', '.vtt', '.srt']", default="All")
parser.add_argument("-s", dest="speechtask", type=str,
                    help="Whether to perform X->X speech recognition (`transcribe`) or X->English translation (`translate`). ['transcribe', 'translate']", default="transcribe")
parser.add_argument("-n", dest="numSteps", type=int,
                    help="Number of Steps", default=50)
parser.add_argument("-t", dest="decodingtemperature", type=int,
                    help="Temperature to increase when falling back when the decoding fails to meet either of the thresholds below.", default=0.15)
parser.add_argument("-b", dest="beamsize", type=int,
                    help="Number of Images", default=5)
parser.add_argument("-o", dest="output", type=str,
                    help="Output Folder where to store the ouputs", default="")

args = parser.parse_args()
device = torch.device('cuda:0')
print('Using device:', device, file=sys.stderr)

Model = 'base'
whisper_model = whisper.load_model(Model)
video_path_local = os.getcwd()+args.inputpath
file_name = os.path.basename(video_path_local)
output_file_path = args.output

if os.path.splitext(video_path_local)[1] == ".mp4":
    video_path_local_wav = os.path.splitext(file_name)[0]+".wav"
    result = subprocess.run(["ffmpeg", "-i", str(video_path_local), "-vn", "-acodec",
                            "pcm_s16le", "-ar", "16000", "-ac", "1", str(video_path_local_wav)])


# add language parameters
# Language spoken in the audio, use Auto detection to let Whisper detect the language.
#  ['Auto detection', 'Afrikaans', 'Albanian', 'Amharic', 'Arabic', 'Armenian', 'Assamese', 'Azerbaijani', 'Bashkir', 'Basque', 'Belarusian', 'Bengali', 'Bosnian', 'Breton', 'Bulgarian', 'Burmese', 'Castilian', 'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Faroese', 'Finnish', 'Flemish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Gujarati', 'Haitian', 'Haitian Creole', 'Hausa', 'Hawaiian', 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Javanese', 'Kannada', 'Kazakh', 'Khmer', 'Korean', 'Lao', 'Latin', 'Latvian', 'Letzeburgesch', 'Lingala', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 'Maltese', 'Maori', 'Marathi', 'Moldavian', 'Moldovan', 'Mongolian', 'Myanmar', 'Nepali', 'Norwegian', 'Nynorsk', 'Occitan', 'Panjabi', 'Pashto', 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Pushto', 'Romanian', 'Russian', 'Sanskrit', 'Serbian', 'Shona', 'Sindhi', 'Sinhala', 'Sinhalese', 'Slovak', 'Slovenian', 'Somali', 'Spanish', 'Sundanese', 'Swahili', 'Swedish', 'Tagalog', 'Tajik', 'Tamil', 'Tatar', 'Telugu', 'Thai', 'Tibetan', 'Turkish', 'Turkmen', 'Ukrainian', 'Urdu', 'Uzbek', 'Valencian', 'Vietnamese', 'Welsh', 'Yiddish', 'Yoruba']
language = args.audiolanguage
# Whether to print out the progress and debug messages.
# ['Live transcription', 'Progress bar', 'None']
verbose = args.typeverbose
#  Type of file to generate to record the transcription.
# ['All', '.txt', '.vtt', '.srt']
output_type = args.outputtype
# Whether to perform X->X speech recognition (`transcribe`) or X->English translation (`translate`).
# ['transcribe', 'translate']
task = args.speechtask
# Temperature to use for sampling.
temperature = args.decodingtemperature
#  Temperature to increase when falling back when the decoding fails to meet either of the thresholds below.
temperature_increment_on_fallback = 0.2
#  Number of candidates when sampling with non-zero temperature.
best_of = 5
#  Number of beams in beam search, only applicable when temperature is zero.
beam_size = args.beamsize
# Optional patience value to use in beam decoding, as in [*Beam Decoding with Controlled Patience*](https://arxiv.org/abs/2204.05424), the default (1.0) is equivalent to conventional beam search.
patience = 1.0
# Optional token length penalty coefficient (alpha) as in [*Google's Neural Machine Translation System*](https://arxiv.org/abs/1609.08144), set to negative value to uses simple length normalization.
length_penalty = -0.05
# Comma-separated list of token ids to suppress during sampling; '-1' will suppress most special characters except common punctuations.
suppress_tokens = "-1"
# Optional text to provide as a prompt for the first window.
initial_prompt = ""
# if True, provide the previous output of the model as a prompt for the next window; disabling may make the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure loop.
condition_on_previous_text = True
#  whether to perform inference in fp16.
fp16 = True
#  If the gzip compression ratio is higher than this value, treat the decoding as failed.
compression_ratio_threshold = 2.4
# If the average log probability is lower than this value, treat the decoding as failed.
logprob_threshold = -1.0
# If the probability of the <|nospeech|> token is higher than this value AND the decoding has failed due to `logprob_threshold`, consider the segment as silence.
no_speech_threshold = 0.6

verbose_lut = {
    'Live transcription': True,
    'Progress bar': False,
    'None': None
}

args = dict(
    language=(None if language == "Auto detection" else language),
    verbose=verbose_lut[verbose],
    task=task,
    temperature=temperature,
    temperature_increment_on_fallback=temperature_increment_on_fallback,
    best_of=best_of,
    beam_size=beam_size,
    patience=patience,
    length_penalty=(length_penalty if length_penalty >= 0.0 else None),
    suppress_tokens=suppress_tokens,
    initial_prompt=(None if not initial_prompt else initial_prompt),
    condition_on_previous_text=condition_on_previous_text,
    fp16=fp16,
    compression_ratio_threshold=compression_ratio_threshold,
    logprob_threshold=logprob_threshold,
    no_speech_threshold=no_speech_threshold
)

temperature = args.pop("temperature")
temperature_increment_on_fallback = args.pop(
    "temperature_increment_on_fallback")
if temperature_increment_on_fallback is not None:
    temperature = tuple(np.arange(temperature, 1.0 + 1e-6,
                        temperature_increment_on_fallback))
else:
    temperature = [temperature]

if Model.endswith(".en") and args["language"] not in {"en", "English"}:
    warnings.warn(
        f"{Model} is an English-only model but receipted '{args['language']}'; using English instead.")
    args["language"] = "en"

video_transcription = whisper.transcribe(
    whisper_model,
    str(video_path_local),
    temperature=temperature,
    **args,
)


# Save output
writing_lut = {
    '.txt': whisper.utils.write_txt,
    '.vtt': whisper.utils.write_vtt,
    '.srt': whisper.utils.write_txt,
}

if output_type == "All":
    for suffix, write_suffix in writing_lut.items():
        transcript_local_path = os.getcwd()+output_file_path+'/' + \
            os.path.splitext(file_name)[0] + suffix
        with open(transcript_local_path, "w", encoding="utf-8") as f:
            write_suffix(video_transcription["segments"], file=f)
        try:
            transcript_drive_path = file_name
        except:
            print(f"**Transcript file created: {transcript_local_path}**")
else:
    transcript_local_path = output_file_path+'/' + \
        os.path.splitext(file_name)[0] + output_type

    with open(transcript_local_path, "w", encoding="utf-8") as f:
        writing_lut[output_type](video_transcription["segments"], file=f)