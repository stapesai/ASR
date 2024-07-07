// Path: lib/websocket_service.dart

import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

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
        return decodedData;
      });

  void close() {
    _channel.sink.close();
  }
}
