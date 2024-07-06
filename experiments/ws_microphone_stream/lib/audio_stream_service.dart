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
  List<Map<String, dynamic>> sessionInfo = [];
  List<int> _recordedData = [];
  DateTime? _startTime;

  AudioStreamService({required this.webSocketService});

  Future<void> startRecording() async {
    if (isRecording) {
      print("Recording is already in progress.");
      return;
    }

    try {
      Stream<List<int>> audioStream = MicStream.microphone(
        sampleRate: 16000,
        audioFormat: AudioFormat.ENCODING_PCM_16BIT,
        channelConfig: ChannelConfig.CHANNEL_IN_MONO,
      ).handleError((error) {
        print("Error: $error");
      }).asBroadcastStream();

      await _audioSubscription?.cancel();

      isRecording = true;
      _recordedData = [];
      notifyListeners();

      _audioSubscription = audioStream.listen((data) {
        _recordedData.addAll(data);
        webSocketService.sendData(Uint8List.fromList(data));
      });

      _startTime = DateTime.now();

      webSocketService.stream.listen((data) {
        final serverProcessingTime = (data['process_time'] * 1000).toInt();
        final transcription = data['transcription'];
        final endTime = DateTime.now();

        final totalLatency = endTime.difference(_startTime!).inMilliseconds;
        final networkLatency = totalLatency - serverProcessingTime;

        sessionInfo.add({
          'audio': Uint8List.fromList(_recordedData),
          'transcription': transcription,
          'serverProcessingTime': serverProcessingTime,
          'networkLatency': networkLatency,
          'totalLatency': totalLatency,
        });

        _recordedData = [];
        _startTime = DateTime.now();

        notifyListeners();
      });
    } catch (e) {
      print("Error starting recording: $e");
    }
  }

  Future<void> stopRecording() async {
    isRecording = false;
    await _audioSubscription?.cancel();
    _audioSubscription = null; // Reset the subscription
    notifyListeners();
    webSocketService.sendData([0, 0, 0, 0]); // Send end-of-speech signal
  }

  void clearSessionInfo() {
    sessionInfo.clear();
    notifyListeners();
  }
}
