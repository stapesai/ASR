# Path: m4a_2_wav.py
# Description: Convert m4a to wav

from pydub import AudioSegment

def convert_m4a_to_wav(m4a_file_path, wav_file_path):
    # Load the M4A file
    audio = AudioSegment.from_file(m4a_file_path, format="m4a")
    
    # Export the audio in WAV format
    audio.export(wav_file_path, format="wav")

if __name__ == "__main__":
    # Take a folder of m4a files and convert them to wav
    import os

    m4a_folder = "dev_raw"
    wav_folder = "dev_wav"

    for m4a_file in os.listdir(m4a_folder):
        m4a_file_path = os.path.join(m4a_folder, m4a_file)
        wav_file_path = os.path.join(wav_folder, m4a_file.replace(".m4a", ".wav"))
        
        convert_m4a_to_wav(m4a_file_path, wav_file_path)
        print(f"Converted {m4a_file_path} to {wav_file_path}")
        
    print("Conversion complete!")
