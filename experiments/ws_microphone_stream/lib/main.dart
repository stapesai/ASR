// Path: lib/main.dart

import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'recording_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Permission.microphone.request();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Microphone Stream',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  final TextEditingController _ipController = TextEditingController();
  final TextEditingController _portController = TextEditingController();

  HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Enter Server Details'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _ipController,
              decoration: const InputDecoration(labelText: 'Server IP'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: _portController,
              decoration: const InputDecoration(labelText: 'Server Port'),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                final status = await Permission.microphone.status;
                if (status.isGranted) {
                  final serverIp = _ipController.text;
                  final serverPort = int.tryParse(_portController.text);
                  if (serverIp.isNotEmpty && serverPort != null) {
                    Navigator.push(
                      // ignore: use_build_context_synchronously
                      context,
                      MaterialPageRoute(
                        builder: (context) => RecordingScreen(
                          serverIp: serverIp,
                          serverPort: serverPort,
                        ),
                      ),
                    );
                  } else {
                    // ignore: use_build_context_synchronously
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text('Please enter valid IP and Port')),
                    );
                  }
                } else {
                  // ignore: use_build_context_synchronously
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                        content: Text('Microphone permission is required')),
                  );
                }
              },
              child: const Text('Connect'),
            ),
          ],
        ),
      ),
    );
  }
}
