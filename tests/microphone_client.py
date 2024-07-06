# File: tests/microphone_client.py
"""
This script implements a client for real-time speech recognition using a microphone.
It connects to a WebSocket server, streams audio data, and receives transcriptions.
Features include microphone selection, colored output, and timing measurements for transcriptions.

playit.gg public ip (devel-container):
    - IP: 20.ip.gl.ply.gg
    - Port: 57813
    - URL: ws://20.ip.gl.ply.gg:57813/ws/transcribe
"""

import pyaudio
from websockets.sync.client import connect
import json
from termcolor import colored
import time

CHUNK_SIZE = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
END_OF_SPEECH_SIGNAL = b'\x00\x00\x00\x00'

def list_microphones():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []

    for i in range(num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            devices.append({
                'index': i,
                'name': device_info.get('name'),
                'defaultSampleRate': device_info.get('defaultSampleRate'),
                'maxInputChannels': device_info.get('maxInputChannels'),
                'maxOutputChannels': device_info.get('maxOutputChannels')
            })
    
    p.terminate()
    return devices

def print_beautified_output(server_output, total_time):
    data = json.loads(server_output)
    transcription = data['transcription']
    process_time = data['process_time']

    # print(colored("ASR Server Response:", "cyan"))
    print(colored(f"Transcription: {transcription}", "green"))
    print(colored(f"Server process time: {process_time*1000:.2f}ms", "yellow"))
    print(colored(f"Network latency: {(total_time - process_time)*1000:.2f}ms", "blue"))
    print(colored(f"Total response time: {total_time*1000:.2f}ms", "magenta"))
    print()

def main():
    server_ip = input("Enter server IP address (default: 192.168.0.253): ") or "192.168.0.253"
    server_port = input("Enter server port (default: 8000): ") or 8000
    server_url = f"ws://{server_ip}:{server_port}/v1/ws/transcribe"

    devices = list_microphones()
    print(colored("Available microphones:", "cyan"))
    # for index, name in devices:
    #     print(colored(f"{index}: {name}", "yellow"))
        
    for device in list_microphones():
        print(colored(f"Index: {device['index']}", "white"))
        print(colored(f"Name: {device['name']}", "yellow"))
        print(colored(f"Default Sample Rate: {device['defaultSampleRate']}", "yellow"))
        print(colored(f"Max Input Channels: {device['maxInputChannels']}", "yellow"))
        print(colored(f"Max Output Channels: {device['maxOutputChannels']}", "yellow"))
        print()

    mic_index = int(input("Select a microphone by index: "))

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=mic_index,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        with connect(server_url) as websocket:
            print(colored("Connection established", "green"))

            while True:
                input(colored("Press Enter to start recording...", "yellow"))
                print(colored("Recording... Press Ctrl+C to stop.", "red"))

                stream.start_stream()
                
                try:
                    while True:
                        data = stream.read(CHUNK_SIZE)
                        websocket.send(data)
                except KeyboardInterrupt:
                    pass
                
                if stream.is_active():
                    stream.stop_stream()
                    print(colored("Stopped recording. Sending end-of-speech signal...", "yellow"))
                else:
                    print(colored("Some unknown error occured. Exiting...", "red"))
                    break
                
                start_time = time.time()
                websocket.send(END_OF_SPEECH_SIGNAL)

                # print(colored("Waiting for ASR response...", "yellow"))
                response = websocket.recv()
                end_time = time.time()

                total_time = end_time - start_time
                print_beautified_output(response, total_time)

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))
        
    except Exception as e:
        print(colored(f"An error occurred: {e}", "red"))
    
    finally:
        if stream is not None:
            if stream.is_active():
                stream.stop_stream()
            stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
