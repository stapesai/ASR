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
      _recordedData = [];
      _startTime = DateTime.now();
      notifyListeners();

      _audioSubscription = audioStream.listen((data) {
        _recordedData.addAll(data);
        webSocketService.sendData(Uint8List.fromList(data));
      });

      webSocketService.stream.listen((data) {
        final totalTime = DateTime.now().difference(_startTime!).inMilliseconds / 1000;
        final serverData = String.fromCharCodes(data).split(',');
        final serverProcessingTime = double.parse(serverData[0]);
        final transcription = serverData.sublist(1).join(',');

        sessionInfo.add({
          'audio': Uint8List.fromList(_recordedData),
          'transcription': transcription,
          'serverProcessingTime': serverProcessingTime,
          'totalTime': totalTime,
          'networkLatency': totalTime - serverProcessingTime,
        });
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
  }
}
