import 'package:flutter/material.dart';
import 'websocket_service.dart';
import 'audio_stream_service.dart';
import 'package:provider/provider.dart';
import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class RecordingScreen extends StatelessWidget {
  final WebSocketService webSocketService;

  const RecordingScreen({
    super.key,
    required this.webSocketService,
  });

  Future<void> _playAudio(Uint8List audioBytes) async {
    final tempDir = await getTemporaryDirectory();
    final file = File('${tempDir.path}/audio_${DateTime.now().millisecondsSinceEpoch}.wav');
    await file.writeAsBytes(audioBytes);
    final player = AudioPlayer();
    await player.play(DeviceFileSource(file.path));
  }

  @override
  Widget build(BuildContext context) {
    final AudioStreamService audioStreamService = AudioStreamService(webSocketService: webSocketService);

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
                          title: Text('Session ${index + 1}'),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Transcription: ${session['transcription']}'),
                              Text('Server Processing Time: ${session['serverProcessingTime']} s'),
                              Text('Network Latency: ${session['networkLatency']} s'),
                              Text('Total Time: ${session['totalTime']} s'),
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
