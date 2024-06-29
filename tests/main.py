import requests
from pathlib import Path
from termcolor import colored
from time import perf_counter
from tabulate import tabulate

BASE_URL = "http://192.168.0.253:8000"

def main():
    table_data = []
    
    for audio_file_path in Path("samples").glob("*"):
        start_time = perf_counter()
        
        with open(audio_file_path, "rb") as audio_file:
            files = {"audio_file": (audio_file_path.name, audio_file, "audio/mpeg")}
            response = requests.post(f"{BASE_URL}/transcribe", files=files)
        
        end_time = perf_counter()
        total_process_time_ms = (end_time - start_time) * 1000

        if response.status_code == 200:
            data = response.json()
            process_time_ms = data["process_time"] * 1000
            
            table_data.append([
                colored(audio_file_path.name, "cyan"),
                colored(data['transcription'], "green"),
                colored(f"{process_time_ms:.2f} ms", "yellow"),
                colored(f"{total_process_time_ms:.2f} ms", "magenta")
            ])
        else:
            table_data.append([
                colored(audio_file_path.name, "cyan"),
                colored("Failed to transcribe", "red"),
                "N/A",
                "N/A"
            ])
    
    headers = ["File", "Transcription", "X-Server-Process-Time", "X-Total-Process-Time"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

if __name__ == "__main__":
    main()
