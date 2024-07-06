// Path: lib/audio_stream_service.dart

import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'websocket_service.dart';
import 'package:mic_stream/mic_stream.dart';

class AudioStreamService extends ChangeNotifier {
  final WebSocketService webSocketService;
  StreamSubscription<List<int>>? _audioSubscription;
  bool isRecording = false;
  String? transcription;

  AudioStreamService({
    required this.webSocketService,
  });

  Future<void> startRecording() async {
    try {
      Stream<List<int>> audioStream = MicStream.microphone(
        sampleRate: 16000,
        audioFormat: AudioFormat.ENCODING_PCM_16BIT,
        channelConfig: ChannelConfig.CHANNEL_IN_MONO,
      ).handleError((error) {
        print("Error: $error");
      }).map((buffer) => buffer as List<int>);

      isRecording = true;
      notifyListeners();

      _audioSubscription = audioStream.listen((data) {
        webSocketService.sendData(Uint8List.fromList(data));
      });

      webSocketService.stream.listen((data) {
        transcription = String.fromCharCodes(data);
        notifyListeners();
      });
    } catch (e) {
      print("Error starting recording: $e");
    }
  }

  void stopRecording() {
    isRecording = false;
    _audioSubscription?.cancel();
    notifyListeners();
    webSocketService.sendData([0, 0, 0, 0]);
    webSocketService.close();
  }
}
