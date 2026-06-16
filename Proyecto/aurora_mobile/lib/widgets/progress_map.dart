import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/unit.dart';
import '../theme/app_colors.dart';
import 'bubble_button.dart';

class ProgressMap extends StatelessWidget {
  const ProgressMap({
    super.key,
    required this.units,
    required this.onTapUnit,
    this.progressResolver,
  });

  final List<Unit> units;
  final void Function(Unit) onTapUnit;

  /// Devuelve el progreso [0..1] de una unidad. Si no se provee, usa isDone.
  final double Function(Unit)? progressResolver;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    // Geometría consistente con BubbleButton
    const bubbleSize = 96.0;
    const ringStroke = 8.0;
    const ringExtra = 6.0;
    const ringSize = bubbleSize + ringStroke + ringExtra; // = 110
    const nodeDiameter = bubbleSize;

    const horizMargin = 32.0;
    const verticalSpacing = 160.0;

    final points = List.generate(units.length, (i) {
      final dx = i.isEven
          ? horizMargin + nodeDiameter / 2
          : size.width - horizMargin - nodeDiameter / 2;
      final dy = i * verticalSpacing + nodeDiameter / 2 + 24;
      return Offset(dx, dy);
    });

    final canvasHeight = math.max(
      size.height,
      (units.length - 1) * verticalSpacing + 220,
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
        clipBehavior: Clip.none, // permite halo suave sin cortes
        children: [
          CustomPaint(
            size: Size(size.width, canvasHeight),
            painter: _PathPainter(points),
          ),

          // Nodos
          for (int i = 0; i < units.length; i++)
            _buildPositionedNode(
              context: context,
              size: size,
              center: points[i],
              ringSize: ringSize,
              color: palette[i % palette.length],
              unit: units[i],
            ),
        ],
      ),
    );
  }

  /// Calcula el ancho máximo del label para que NO se salga de la pantalla
  Positioned _buildPositionedNode({
    required BuildContext context,
    required Size size,
    required Offset center,
    required double ringSize,
    required Color color,
    required Unit unit,
  }) {
    const double minLabel = 110.0; // no menor que el ring
    const double maxLabel = 160.0;
    const double safeSidePadding = 16.0;

    // Espacio disponible a ambos lados del centro (respetando padding)
    final double leftAvail = center.dx - safeSidePadding;
    final double rightAvail = size.width - center.dx - safeSidePadding;
    final double half = math.max(0.0, math.min(leftAvail, rightAvail));

    // El label debe ser simétrico respecto del centro
    final double labelWidth = half.isFinite && half > 0
        ? (2 * half).clamp(minLabel, maxLabel)
        : minLabel;

    // Ancho externo real del widget (coincide con BubbleButton)
    final double outerWidth = math.max(labelWidth, ringSize);

    return Positioned(
      // 🔧 Colocamos el widget CENTRADO en 'center.dx'
      left: center.dx - outerWidth / 2,
      // 🔧 Verticalmente, el centro del ring coincide con 'center.dy'
      top: center.dy - ringSize / 2,
      width: outerWidth, // ayuda a evitar re-layouts
      child: BubbleButton(
        label: unit.title,
        bubbleColor: color,
        // progreso seguro 0..1
        progress: (progressResolver?.call(unit) ?? (unit.isDone ? 1.0 : 0.0))
            .clamp(0.0, 1.0),
        completed: unit.isDone,
        onTap: () => onTapUnit(unit),
        labelWidth: labelWidth, // << ancho dinámico que no se sale
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
