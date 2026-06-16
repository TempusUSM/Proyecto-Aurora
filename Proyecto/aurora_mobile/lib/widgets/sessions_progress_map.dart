import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/session.dart';
import '../theme/app_colors.dart';
import 'bubble_button.dart';

class SessionsProgressMap extends StatelessWidget {
  const SessionsProgressMap({
    super.key,
    required this.sessions,
    required this.onTapSession,
  });

  final List<StudySession> sessions;
  final void Function(StudySession) onTapSession;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    // Misma geometría que en ProgressMap (unidades)
    const bubbleSize = 96.0;
    const ringStroke = 8.0;
    const ringExtra = 6.0;
    const ringSize = bubbleSize + ringStroke + ringExtra; // 110
    const horizMargin = 32.0;
    const verticalSpacing = 160.0;

    // puntos alternando izquierda/derecha
    final points = List.generate(sessions.length, (i) {
      final dx = i.isEven
          ? horizMargin + bubbleSize / 2
          : size.width - horizMargin - bubbleSize / 2;
      final dy = i * verticalSpacing + bubbleSize / 2 + 24;
      return Offset(dx, dy);
    });

    final canvasHeight = math.max(
      size.height,
      (sessions.length - 1) * verticalSpacing + 220,
    );

    const palette = <Color>[
      AppColors.auroraCyan,
      AppColors.auroraPink,
      AppColors.auroraAmber,
      AppColors.auroraViolet,
    ];

    return SizedBox(
      height: canvasHeight,
      width: size.width,
      child: Stack(
        clipBehavior: Clip.none, // ← evita cortes de halo/anillo
        children: [
          CustomPaint(
            size: Size(size.width, canvasHeight),
            painter: _PathPainter(points),
          ),
          for (int i = 0; i < sessions.length; i++)
            _buildPositionedNode(
              context: context,
              size: size,
              center: points[i],
              ringSize: ringSize,
              color: palette[i % palette.length],
              session: sessions[i],
            ),
        ],
      ),
    );
  }

  /// Igual que en unidades: calcula un labelWidth seguro y centra por el ancho real
  Positioned _buildPositionedNode({
    required BuildContext context,
    required Size size,
    required Offset center,
    required double ringSize,
    required Color color,
    required StudySession session,
  }) {
    const double minLabel = 110.0; // no menor que el ring
    const double maxLabel = 160.0;
    const double safeSidePadding = 16.0;

    // espacio disponible a ambos lados del centro (respetando padding)
    final double leftAvail = center.dx - safeSidePadding;
    final double rightAvail = size.width - center.dx - safeSidePadding;
    final double half = math.max(0.0, math.min(leftAvail, rightAvail));

    // ancho simétrico respecto del centro
    final double labelWidth = half.isFinite && half > 0
        ? (2 * half).clamp(minLabel, maxLabel)
        : minLabel;

    final double outerWidth = math.max(labelWidth, ringSize);

    return Positioned(
      left: center.dx - outerWidth / 2, // ← centrado real
      top: center.dy - ringSize / 2,
      width: outerWidth,
      child: BubbleButton(
        label: session.title,
        bubbleColor: color,
        progress: session.completed ? 1.0 : 0.0,
        completed: session.completed,
        labelWidth: labelWidth, // ← ancho dinámico que evita cortes
        onTap: session.completed ? () {} : () => onTapSession(session),
      ),
    );
  }
}

class _PathPainter extends CustomPainter {
  _PathPainter(this.points);
  final List<Offset> points;

  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;

    final paint = Paint()
      ..color = Colors.white.withValues(alpha: .22)
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (var i = 1; i < points.length; i++) {
      final prev = points[i - 1];
      final curr = points[i];
      final ctrlY = (prev.dy + curr.dy) / 2;
      path.quadraticBezierTo(prev.dx, ctrlY, curr.dx, curr.dy);
    }

    const dash = 12.0, gap = 8.0;
    for (final metric in path.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        final next = math.min(distance + dash, metric.length);
        final segment = metric.extractPath(distance, next);
        canvas.drawPath(segment, paint);
        distance = next + gap;
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
