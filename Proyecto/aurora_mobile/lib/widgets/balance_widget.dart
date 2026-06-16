// lib/widgets/balance_widget.dart
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class BalanceWidget extends StatelessWidget {
  final int glims;
  const BalanceWidget({Key? key, required this.glims}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // “Píldora” con icono y brillo sutil
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.28)),
        boxShadow: [
          BoxShadow(
            color: AppColors.auroraCyan.withValues(alpha: 0.20),
            blurRadius: 14,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(Icons.stars_rounded, size: 18, color: Colors.white),
          const SizedBox(width: 6),
          Text(
            '$glims glims',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
