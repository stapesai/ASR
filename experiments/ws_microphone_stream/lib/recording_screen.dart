// Path: lib/recording_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'websocket_service.dart';
import 'audio_stream_service.dart';
import 'audio_player.dart';

class RecordingScreen extends StatefulWidget {
  final String serverIp;
  final int serverPort;

  const RecordingScreen({
    super.key,
    required this.serverIp,
    required this.serverPort,
  });

  @override
  RecordingScreenState createState() => RecordingScreenState();
}

class RecordingScreenState extends State<RecordingScreen> {
  late ScrollController _scrollController;
  late AudioStreamService audioStreamService;

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController(initialScrollOffset: 0.0);
    final String url =
        'ws://${widget.serverIp}:${widget.serverPort}/v1/ws/transcribe';
    final WebSocketService webSocketService = WebSocketService(url: url);
    audioStreamService = AudioStreamService(webSocketService: webSocketService);

    audioStreamService.addListener(_scrollToBottom);
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    audioStreamService.removeListener(_scrollToBottom);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Recording'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete, color: Colors.red),
            onPressed: () {
              audioStreamService.clearSessionInfo();
            },
          ),
        ],
      ),
      body: ChangeNotifierProvider.value(
        value: audioStreamService,
        child: Consumer<AudioStreamService>(
          builder: (context, service, child) {
            return Column(
              children: [
                Expanded(
                  child: ListView.separated(
                    controller: _scrollController,
                    // reverse: true,
                    itemCount: service.sessionInfo.length,
                    separatorBuilder: (context, index) => const Divider(height: 1),
                    itemBuilder: (context, index) {
                      final session = service
                          .sessionInfo[service.sessionInfo.length - 1 - index];
                      return Card(
                        margin: const EdgeInsets.symmetric(
                            vertical: 8, horizontal: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Transaction ${index + 1}'),
                                  Text(
                                      'Transcription: ${session['transcription']}'),
                                  Text(
                                      'Server Processing Time: ${(session['serverProcessingTime']).toStringAsFixed(2)} ms'),
                                  Text(
                                      'Network Latency: ${(session['networkLatency']).toStringAsFixed(2)} ms'),
                                  Text(
                                      'Total Latency: ${(session['totalLatency']).toStringAsFixed(2)} ms'),
                                ],
                              ),
                            ),
                            AudioPlayerWidget(audioData: session['audio']),
                          ],
                        ),
                      );
                    },
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: ElevatedButton(
                    onPressed: () async {
                      if (service.isRecording) {
                        service.stopRecording();
                      } else {
                        await service.startRecording();
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(200, 50),
                      elevation: 5,
                    ),
                    child: Text(
                      service.isRecording ? 'Stop' : 'Start',
                      style: TextStyle(
                        color: service.isRecording ? Colors.red : Colors.green,
                      ),
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
