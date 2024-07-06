// Path: lib/audio_player.dart

import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import 'dart:typed_data';

class AudioPlayerWidget extends StatefulWidget {
  final Uint8List audioData;

  const AudioPlayerWidget({super.key, required this.audioData});

  @override
  AudioPlayerWidgetState createState() => AudioPlayerWidgetState();
}

class AudioPlayerWidgetState extends State<AudioPlayerWidget> {
  late AudioPlayer _audioPlayer;
  bool _isPlaying = false;
  Duration _duration = Duration.zero;
  Duration _position = Duration.zero;
  String _audioFilePath = '';

  @override
  void initState() {
    super.initState();
    _audioPlayer = AudioPlayer();
    _setupAudioPlayer();
  }

  Future<void> _setupAudioPlayer() async {
    await _saveAudioFile();
    _audioPlayer.onDurationChanged.listen((newDuration) {
      setState(() {
        _duration = newDuration;
      });
    });

    _audioPlayer.onPositionChanged.listen((newPosition) {
      setState(() {
        _position = newPosition;
      });
    });

    _audioPlayer.onPlayerComplete.listen((_) {
      setState(() {
        _isPlaying = false;
        _position = Duration.zero;
      });
    });
  }

  Future<void> _saveAudioFile() async {
    final tempDir = await getTemporaryDirectory();
    final file = File(
        '${tempDir.path}/audio_${DateTime.now().millisecondsSinceEpoch}.wav');
    final wavData = _addWavHeader(widget.audioData, 16000, 1, 16);
    await file.writeAsBytes(wavData);
    _audioFilePath = file.path;
  }

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

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, "0");
    String twoDigitMinutes = twoDigits(duration.inMinutes.remainder(60));
    String twoDigitSeconds = twoDigits(duration.inSeconds.remainder(60));
    return "$twoDigitMinutes:$twoDigitSeconds";
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(_formatDuration(_position)),
              Text(_formatDuration(_duration)),
            ],
          ),
          Slider(
            value: _position.inSeconds.toDouble(),
            min: 0,
            max: _duration.inSeconds.toDouble(),
            onChanged: (value) {
              final newPosition = Duration(seconds: value.toInt());
              _audioPlayer.seek(newPosition);
              setState(() {
                _position = newPosition;
              });
            },
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                iconSize: 32,
                onPressed: () {
                  if (_isPlaying) {
                    _audioPlayer.pause();
                  } else {
                    _audioPlayer.play(DeviceFileSource(_audioFilePath));
                  }
                  setState(() {
                    _isPlaying = !_isPlaying;
                  });
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }
}