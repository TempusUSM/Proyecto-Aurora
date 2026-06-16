import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class RankingPage extends StatelessWidget {
  const RankingPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ranking'),
        backgroundColor: AppColors.primaryAmber,
        foregroundColor: Colors.white,
      ),
      body: const Center(child: Text('Ranking (por implementar)')),
    );
  }
}
