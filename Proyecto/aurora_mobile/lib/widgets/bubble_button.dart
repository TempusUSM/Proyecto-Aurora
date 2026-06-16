import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class BubbleButton extends StatefulWidget {
  const BubbleButton({
    super.key,
    required this.label,
    required this.onTap,
    this.completed = false,
    this.bubbleColor,
    this.progress,
    this.labelWidth,
  });

  final String label;
  final VoidCallback onTap;
  final bool completed;
  final Color? bubbleColor;
  final double? progress;
  final double? labelWidth;

  @override
  State<BubbleButton> createState() => _BubbleButtonState();
}

class _BubbleButtonState extends State<BubbleButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
      lowerBound: 0,
      upperBound: 1,
    )..forward();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final Color base = widget.bubbleColor ?? AppColors.auroraBlue;
    final Color fill = widget.completed ? _darken(base, .22) : base;
    final double progress = (widget.progress ?? (widget.completed ? 1.0 : 0.0))
        .clamp(0.0, 1.0);

    // Dimensiones coherentes con el ProgressMap
    const bubbleSize = 96.0;
    const ringStroke = 8.0;
    const ringExtra = 6.0;
    const ringSize = bubbleSize + ringStroke + ringExtra; // = 110
    final double labelW = widget.labelWidth ?? 140.0;

    // 🔧 Ancho "externo" estable: el padre puede posicionar centrado
    final double outerWidth = math.max(labelW, ringSize);

    return ScaleTransition(
      scale: CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut),
      child: SizedBox(
        width: outerWidth,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            GestureDetector(
              onTap: widget.onTap,
              child: SizedBox(
                width: ringSize,
                height: ringSize,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // Halo suave
                    IgnorePointer(
                      child: Container(
                        width: ringSize,
                        height: ringSize,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: RadialGradient(
                            colors: [
                              base.withValues(alpha: .28),
                              Colors.transparent,
                            ],
                            stops: const [.55, 1.0],
                          ),
                        ),
                      ),
                    ),

                    // Anillo de progreso (sin cambios funcionales)
                    TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0, end: progress),
                      duration: const Duration(milliseconds: 500),
                      curve: Curves.easeOutCubic,
                      builder: (_, value, __) {
                        return ClipOval(
                          clipBehavior: Clip.antiAlias,
                          child: CustomPaint(
                            size: const Size(ringSize, ringSize),
                            painter: _RingPainter(
                              progress: value,
                              color: base,
                              strokeWidth: ringStroke,
                            ),
                          ),
                        );
                      },
                    ),

                    // Cuerpo
                    Container(
                      width: bubbleSize,
                      height: bubbleSize,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: RadialGradient(
                          colors: [fill, fill.withValues(alpha: .75)],
                          radius: .9,
                        ),
                        border: Border.all(
                          color: Colors.white.withValues(alpha: .18),
                          width: 1.2,
                        ),
                      ),
                      child: Center(
                        child: AnimatedSwitcher(
                          duration: const Duration(milliseconds: 250),
                          child: widget.completed
                              ? const Icon(
                                  Icons.check_rounded,
                                  key: ValueKey('done'),
                                  size: 38,
                                  color: Colors.white,
                                )
                              : const Icon(
                                  Icons.star_border_rounded,
                                  key: ValueKey('todo'),
                                  size: 38,
                                  color: Colors.white,
                                ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 8),

            // Etiqueta con ancho controlado desde afuera
            SizedBox(
              width: labelW,
              child: Text(
                widget.label,
                textAlign: TextAlign.center,
                maxLines: 2,
                softWrap: true,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  height: 1.15,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _darken(Color c, double amount) {
    final hsl = HSLColor.fromColor(c);
    final h = hsl.withLightness((hsl.lightness - amount).clamp(0.0, 1.0));
    return h.toColor();
  }
}

class _RingPainter extends CustomPainter {
  _RingPainter({
    required this.progress,
    required this.color,
    this.strokeWidth = 8.0,
  });

  final double progress; // 0..1
  final Color color;
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (math.min(size.width, size.height) / 2) - strokeWidth / 2;

    final track = Paint()
      ..color = Colors.white.withValues(alpha: .18)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;
    canvas.drawCircle(center, radius, track);

    final arc = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round
      ..shader = SweepGradient(
        startAngle: -math.pi / 2,
        endAngle: 3 * math.pi / 2,
        colors: [color, Color.lerp(color, Colors.white, .2)!, color],
        stops: const [0.0, .5, 1.0],
      ).createShader(Rect.fromCircle(center: center, radius: radius));

    final sweep = 2 * math.pi * progress;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      sweep,
      false,
      arc,
    );
  }

  @override
  bool shouldRepaint(covariant _RingPainter old) =>
      old.progress != progress ||
      old.color != color ||
      old.strokeWidth != strokeWidth;
}
