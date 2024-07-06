// Path: lib/recording_screen.dart

import 'package:flutter/material.dart';
import 'websocket_service.dart';
import 'audio_stream_service.dart';
import 'package:provider/provider.dart';

class RecordingScreen extends StatelessWidget {
  final String serverIp;
  final int serverPort;

  const RecordingScreen({
    super.key,
    required this.serverIp,
    required this.serverPort,
  });

  @override
  Widget build(BuildContext context) {
    final WebSocketService webSocketService = WebSocketService(
      url: 'ws://$serverIp:$serverPort/v1/ws/transcribe',
    );
    final AudioStreamService audioStreamService = AudioStreamService(
      webSocketService: webSocketService,
    );

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
                  child: Center(
                    child: service.isRecording
                        ? const Text('Recording... Press Stop to finish.')
                        : const Text('Press Start to begin recording.'),
                  ),
                ),
                ElevatedButton(
                  onPressed: service.isRecording
                      ? service.stopRecording
                      : service.startRecording,
                  child: Text(service.isRecording ? 'Stop' : 'Start'),
                ),
                const SizedBox(height: 16),
                service.transcription != null
                    ? Text(
                        'Transcription: ${service.transcription}',
                        textAlign: TextAlign.center,
                      )
                    : Container(),
              ],
            );
          },
        ),
      ),
    );
  }
}
