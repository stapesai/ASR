# Path: tests/microphone_client.py

import pyaudio
import asyncio
import websockets

CHUNK_SIZE = 1024
#TODO: Change the FORMAT to pyaudio.paInt16
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000
END_OF_STREAM_SIGNAL = b'\x00\x00\x00\x00'

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

async def record_audio(stream, websocket):
    while stream.is_active():
        data = stream.read(CHUNK_SIZE)
        await websocket.send(data)
        await asyncio.sleep(0.01)  # small delay to simulate real-time streaming

async def send_end_of_stream_signal(websocket):
    await websocket.send(END_OF_STREAM_SIGNAL)

async def main():
    server_ip = input("Enter server IP address: ") or "localhost"
    server_port = input("Enter server port: ") or 8000
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

    async with websockets.connect(server_url) as websocket:
        print("Connection established")
        print("Press Enter to stop recording and send the stream to the ASR server")

        record_task = asyncio.create_task(record_audio(stream, websocket))

        await asyncio.get_event_loop().run_in_executor(None, input)

        stream.stop_stream()
        stream.close()
        p.terminate()

        await send_end_of_stream_signal(websocket)
        await record_task

        response = await websocket.recv()
        print("ASR Server Response:", response)

if __name__ == "__main__":
    asyncio.run(main())
