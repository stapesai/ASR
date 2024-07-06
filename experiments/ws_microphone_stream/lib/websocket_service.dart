// Path: lib/websocket_service.dart

import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
// import 'package:web_socket_channel/status.dart' as status;

class WebSocketService {
  final String url;
  late WebSocketChannel _channel;

  WebSocketService({required this.url}) {
    _channel = WebSocketChannel.connect(Uri.parse(url));
  }

  void sendData(List<int> data) {
    _channel.sink.add(data);
  }

  Stream get stream => _channel.stream.map((data) {
        final decodedData = jsonDecode(data);
        // decodedData['process_time'] = decodedData['process_time'] * 1000;
        return decodedData;
      });

  void close() {
    _channel.sink.close();
  }
}
