import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil'),
        backgroundColor: AppColors.darkAmber,
        foregroundColor: Colors.white,
      ),
      body: const Center(child: Text('Perfil del alumno (por implementar)')),
    );
  }
}
