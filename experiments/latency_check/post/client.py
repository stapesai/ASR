"""
Client-Side Application for Audio File Upload and Latency Measurement

This script generates random audio data, simulating audio input from a
microphone, and sends the audio data to a FastAPI server via POST request.
It measures the network latency for each upload and plots the latency
against different audio durations using matplotlib.

Dependencies:
- requests
- numpy
- matplotlib

To run the client-side application, execute the following command:
    python client.py

Ensure that the FastAPI server is running before executing this script.
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import io

# Function to generate random audio data
def generate_audio(duration_seconds, sample_rate=16000):
    samples = duration_seconds * sample_rate
    audio_data = np.random.randn(samples).astype(np.float32)
    return audio_data

# Function to send audio data to the server and measure latency
def send_audio(audio_data, sample_rate=16000):
    byte_io = io.BytesIO(audio_data.tobytes())
    files = {'file': ('audio.raw', byte_io, 'audio/x-raw')}
    start_time = time.time()
    response = requests.post("http://127.0.0.1:8000/upload-audio/", files=files)
    end_time = time.time()
    latency = end_time - start_time
    return latency, response.json()

# Benchmarking function
def benchmark():
    durations = [2, 5, 10, 20, 30, 40, 50, 60]  # durations in seconds
    latencies = []
    
    for duration in durations:
        audio_data = generate_audio(duration)
        latency, response = send_audio(audio_data)
        print(f"Duration: {duration}s, Latency: {latency:.4f}s, Response: {response}")
        latencies.append(latency)
    
    plt.plot(durations, latencies, marker='o')
    plt.xlabel("Audio Duration (seconds)")
    plt.ylabel("Latency (seconds)")
    plt.title("Network Latency for Different Audio Durations")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    benchmark()
