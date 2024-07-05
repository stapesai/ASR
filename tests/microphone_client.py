# Path: tests/microphone_client.py

import pyaudio
from websockets.sync.client import connect

CHUNK_SIZE = 1024
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
            devices.append((i, device_info.get('name')))
    
    p.terminate()
    return devices

def main():
    server_ip = input("Enter server IP address (default: 192.168.0.253): ") or "192.168.0.253"
    server_port = input("Enter server port (default: 8000): ") or 8000
    server_url = f"ws://{server_ip}:{server_port}/ws/transcribe"

    devices = list_microphones()
    print("Available microphones:")
    for index, name in devices:
        print(f"{index}: {name}")

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
            print("Connection established")

            while True:
                input("Press Enter to start recording...")
                print("Recording... Press Ctrl+C to stop.")

                stream.start_stream()
                try:
                    while True:
                        data = stream.read(CHUNK_SIZE)
                        websocket.send(data)
                except KeyboardInterrupt:
                    pass

                stream.stop_stream()
                websocket.send(END_OF_SPEECH_SIGNAL)

                print("Stopped recording. Waiting for ASR response...")
                response = websocket.recv()
                print("ASR Server Response:", response)

    except KeyboardInterrupt:
        print("Exiting...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
