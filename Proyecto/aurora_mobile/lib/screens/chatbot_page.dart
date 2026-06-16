import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class ChatbotPage extends StatelessWidget {
  const ChatbotPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chatbot'),
        backgroundColor: AppColors.primaryAmber,
        foregroundColor: Colors.white,
      ),
      body: const Center(child: Text('Chatbot IA (por implementar)')),
    );
  }
}
