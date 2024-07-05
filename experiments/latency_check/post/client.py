"""
Client-Side Application for Audio File Upload and Latency Measurement

This script generates random audio data, simulating audio input from a
microphone, and sends the audio data to a FastAPI server via POST request.
It measures the network latency for each upload and plots the latency
against different audio durations using matplotlib.

To run the client-side application, execute the following command:
    python client.py

Ensure that the FastAPI server is running before executing this script.
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import io

SERVER_URL = "http://127.0.0.1:8000/upload-audio/"    # Local server
# SERVER_URL = "http://20.ip.gl.ply.gg:57813/upload-audio/"   # using playit.gg
# SERVER_URL = "http://213.173.105.83:6679/upload-audio/"   # runpod server
# SERVER_URL = "https://devel-8000.devasheeshmishra.com/upload-audio/"   # using cloudflare tunnel

SAMPLE_RATE = 16000
D_TYPE = np.float32

# Function to generate random audio data
def generate_audio(duration_seconds):
    samples = duration_seconds * SAMPLE_RATE
    audio_data = np.random.randn(samples).astype(D_TYPE)
    return audio_data

# Function to send audio data to the server and measure latency
def send_audio(audio_data):
    byte_io = io.BytesIO(audio_data.tobytes())
    files = {'file': ('audio.raw', byte_io, 'audio/x-raw')}
    start_time = time.perf_counter()
    response = requests.post(SERVER_URL, files=files)
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # in milliseconds
    return latency, response.json()

# Function to plot latency vs. audio duration
def plot_latency(durations, latencies):
    plt.figure(figsize=(12, 6))
    
    # Plot the data points
    plt.scatter(durations, latencies, color='blue', alpha=0.6, label='Data points')
    
    # Plot the trend line
    z = np.polyfit(durations, latencies, 1)
    p = np.poly1d(z)
    plt.plot(durations, p(durations), "r--", label='Trend line')
    
    # Calculate and display correlation coefficient
    correlation = np.corrcoef(durations, latencies)[0, 1]
    plt.text(0.05, 0.95, f'Correlation: {correlation:.2f}', transform=plt.gca().transAxes,
             verticalalignment='top')
    
    # Styling
    plt.xlabel("Audio Duration (seconds)")
    plt.ylabel("Latency (ms)")
    plt.title("Network Latency for Different Audio Durations")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Add horizontal lines for mean and median latency
    mean_latency = np.mean(latencies)
    median_latency = np.median(latencies)
    plt.axhline(y=mean_latency, color='g', linestyle='-.', label=f'Mean: {mean_latency:.2f} ms')
    plt.axhline(y=median_latency, color='m', linestyle=':', label=f'Median: {median_latency:.2f} ms')
    
    # Update legend
    # plt.legend(loc='upper left')
    plt.legend(loc='lower right')
    
    # Improve tick marks
    plt.xticks(np.arange(0, max(durations)+1, 5))
    plt.yticks(np.arange(min(latencies), max(latencies), (max(latencies)-min(latencies))/10))
    
    # Adjust layout and save
    plt.tight_layout()
    
    test_name = input("Enter the test name: ")
    plt.savefig(f'results/latency_{test_name}_{SAMPLE_RATE}Hz.png', dpi=600)
    print(f"Saved latency plot to `results/latency_{test_name}_{SAMPLE_RATE}Hz`")
    # plt.show()

# Benchmarking function
def benchmark():
    durations = [i for i in range(1, 61)] # Audio durations from 1s to 60s
    latencies = []
    
    for duration in durations:
        audio_data = generate_audio(duration)
        latency, response = send_audio(audio_data)
        print(f"Audio Duration: {duration}s, Latency: {latency:.2f}ms, Response: {response}")
        latencies.append(latency)
    
    # Using threading to send audio data concurrently
    # import threading as th
    # def send_audio_concurrent(duration):
    #     print(f"Sending audio data for {duration}s...")
    #     audio_data = generate_audio(duration)
    #     latency, response = send_audio(audio_data)
    #     print(f"Duration: {duration}s, Latency: {latency:.4f}s, Response: {response}")
    #     latencies.append(latency)
        
    # threads = [th.Thread(target=send_audio_concurrent, args=(duration,)) for duration in durations]
    # for thread in threads:
    #     thread.start()
        
    # for thread in threads:
    #     thread.join()
        
    plot_latency(durations, latencies)

if __name__ == "__main__":
    start_time = time.perf_counter()
    benchmark()
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.2f} seconds")
