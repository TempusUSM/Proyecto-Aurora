import 'package:flutter/material.dart';

class AppColors {
  // —— Paleta actual (se mantiene para no romper otras pantallas) ——
  static const blue = Color(0xFF1565C0); // Azul principal
  static const amber = Color(0xFFFF9800); // Naranja / ámbar
  static const blueDark = Color(0xFF0D47A1); // Azul oscuro
  static const amberDark = Color(0xFFF57C00); // Naranja oscuro

  static const primaryBlue = blue;
  static const primaryAmber = amber;
  static const darkBlue = blueDark;
  static const darkAmber = amberDark;

  // Preguntas
  static const correct = Color(0xFF4CAF50); // verde
  static const incorrect = Color(0xFFF44336); // rojo

  // —— Gradiente antiguo (dejado por compatibilidad) ——
  static const backgroundGradient = [blueDark, blue];

  // ─────────────────────────────────────────────────────────────────
  //        NUEVA PALETA “AURORA BOREAL” (para el login)
  // ─────────────────────────────────────────────────────────────────
  static const auroraNavy = Color(0xFF0B1021); // fondo muy oscuro (calma)
  static const auroraBlue = Color(0xFF1F5EFF); // azul vivo (enfoque)
  static const auroraCyan = Color(0xFF22D3EE); // cian (energía sutil)
  static const auroraViolet = Color(0xFFA78BFA); // violeta (creatividad)
  static const auroraPink = Color(0xFFF472B6); // rosa (cercanía)
  static const auroraAmber = Color(0xFFF59E0B); // CTA cálido

  /// Degradado recomendado para login (oscuro→azul→violeta)
  static const auroraGradient = [auroraNavy, auroraBlue, auroraViolet];
}
