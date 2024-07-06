// Path: lib/recording_screen.dart

import 'package:flutter/material.dart';
import 'websocket_service.dart';
import 'audio_stream_service.dart';
import 'package:provider/provider.dart';
import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class RecordingScreen extends StatelessWidget {
  final String serverIp;
  final int serverPort;

  const RecordingScreen({
    super.key,
    required this.serverIp,
    required this.serverPort,
  });

  Uint8List _addWavHeader(
      Uint8List pcmData, int sampleRate, int channels, int bitsPerSample) {
    final int byteRate = sampleRate * channels * bitsPerSample ~/ 8;
    final int blockAlign = channels * bitsPerSample ~/ 8;
    final int subchunk2Size = pcmData.length;
    final int chunkSize = 36 + subchunk2Size;

    final ByteData header = ByteData(44);
    header.setUint32(0, 0x52494646, Endian.big); // "RIFF"
    header.setUint32(4, chunkSize, Endian.little);
    header.setUint32(8, 0x57415645, Endian.big); // "WAVE"
    header.setUint32(12, 0x666d7420, Endian.big); // "fmt "
    header.setUint32(16, 16, Endian.little); // Subchunk1Size
    header.setUint16(20, 1, Endian.little); // AudioFormat (PCM)
    header.setUint16(22, channels, Endian.little);
    header.setUint32(24, sampleRate, Endian.little);
    header.setUint32(28, byteRate, Endian.little);
    header.setUint16(32, blockAlign, Endian.little);
    header.setUint16(34, bitsPerSample, Endian.little);
    header.setUint32(36, 0x64617461, Endian.big); // "data"
    header.setUint32(40, subchunk2Size, Endian.little);

    return Uint8List.fromList([...header.buffer.asUint8List(), ...pcmData]);
  }

  Future<void> _playAudio(Uint8List audioBytes) async {
    final tempDir = await getTemporaryDirectory();
    final file = File(
        '${tempDir.path}/audio_${DateTime.now().millisecondsSinceEpoch}.wav');

    // Add WAV header to the audio data
    final wavData = _addWavHeader(audioBytes, 16000, 1, 16);

    await file.writeAsBytes(wavData);
    print("File path: ${file.path}");
    print("File size: ${await file.length()} bytes");

    final player = AudioPlayer();
    try {
      await player.play(DeviceFileSource(file.path));
    } catch (e) {
      print("Error playing audio: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    final String url = 'ws://$serverIp:$serverPort/v1/ws/transcribe';
    final WebSocketService webSocketService = WebSocketService(url: url);
    final AudioStreamService audioStreamService =
        AudioStreamService(webSocketService: webSocketService);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Recording'),
      ),
      body: ChangeNotifierProvider(
        create: (_) => audioStreamService,
        child: Consumer<AudioStreamService>(
          builder: (context, service, child) {
            return Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    itemCount: service.sessionInfo.length,
                    itemBuilder: (context, index) {
                      final session = service.sessionInfo[index];
                      return Card(
                        child: ListTile(
                          title: Text('Transaction ${index + 1}'),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                  'Transcription: ${session['transcription']}'),
                              Text(
                                  'Server Processing Time: ${(session['serverProcessingTime'] * 1000).toStringAsFixed(2)} ms'),
                              Text(
                                  'Network Latency: ${(session['networkLatency'] * 1000).toStringAsFixed(2)} ms'),
                              Text(
                                  'Total Time: ${(session['totalTime'] * 1000).toStringAsFixed(2)} ms'),
                              ElevatedButton(
                                onPressed: () => _playAudio(session['audio']),
                                child: const Text('Play Audio'),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: ElevatedButton(
                      onPressed: () async {
                        if (service.isRecording) {
                          service.stopRecording();
                        } else {
                          await service.startRecording();
                        }
                      },
                      child: Text(service.isRecording ? 'Stop' : 'Start'),
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
