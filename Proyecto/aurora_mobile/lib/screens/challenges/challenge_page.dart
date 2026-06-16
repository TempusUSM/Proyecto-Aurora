import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/challenge_provider.dart';
import '../../models/subject.dart';
import '../../theme/app_colors.dart';
import 'units_page.dart';

// NEW: helper modular
import '../../shared/subjects/subject_matcher.dart';

/// Pantalla principal del catálogo de Desafíos (lista de asignaturas).
class ChallengePage extends StatefulWidget {
  const ChallengePage({super.key});

  @override
  State<ChallengePage> createState() => _ChallengePageState();
}

class _ChallengePageState extends State<ChallengePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final prov = context.read<ChallengeProvider>();
      if (prov.subjects == null && !prov.loading) {
        prov.loadSubjects();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChallengeProvider>(
      builder: (_, prov, __) {
        if (prov.loading && prov.subjects == null) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (prov.error != null && prov.subjects == null) {
          return Scaffold(body: Center(child: Text(prov.error!)));
        }
        if ((prov.subjects ?? const <Subject>[]).isEmpty) {
          return const Scaffold(
            body: Center(child: Text('No hay asignaturas disponibles')),
          );
        }
        final subjects = prov.subjects ?? [];

        return Scaffold(
          extendBodyBehindAppBar: true,
          backgroundColor: Colors.transparent,
          appBar: AppBar(
            title: const Text('Desafíos'),
            centerTitle: false,
            backgroundColor: Colors.transparent,
            elevation: 0,
            foregroundColor: Colors.white,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back_rounded),
              onPressed: () => Navigator.maybePop(context),
              tooltip: 'Volver',
            ),
          ),
          body: Container(
            // Fondo aurora consistente con la Home.
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: AppColors.auroraGradient,
                stops: [0, .55, 1],
              ),
            ),
            child: SafeArea(
              child: LayoutBuilder(
                builder: (context, c) {
                  // Grid responsivo — 2/3/4 columnas según ancho.
                  final cross = c.maxWidth >= 1200
                      ? 4
                      : (c.maxWidth >= 900 ? 3 : 2);
                  return Padding(
                    padding: const EdgeInsets.all(16),
                    child: GridView.builder(
                      itemCount: subjects.length,
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: cross,
                        mainAxisSpacing: 16,
                        crossAxisSpacing: 16,
                        childAspectRatio: 1.05,
                      ),
                      itemBuilder: (_, i) =>
                          _SubjectCard(subject: subjects[i], index: i),
                    ),
                  );
                },
              ),
            ),
          ),
        );
      },
    );
  }
}

/* ──────────────────────────────────────────────────────────────────────
   TARJETA DE ASIGNATURA – “Vibrant Aurora”
   ───────────────────────────────────────────────────────────────────── */

class _SubjectCard extends StatefulWidget {
  const _SubjectCard({required this.subject, required this.index});
  final Subject subject;
  final int index;

  @override
  State<_SubjectCard> createState() => _SubjectCardState();
}

class _SubjectCardState extends State<_SubjectCard> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    final name = widget.subject.name;

    // Paleta dinámica (evita camuflarse con el fondo)
    final palette = _SubjectPalette.fromName(name, salt: widget.index);

    void go() {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => UnitsPage(subject: widget.subject)),
      );
    }

    return AnimatedScale(
      duration: const Duration(milliseconds: 140),
      curve: Curves.easeOut,
      scale: _pressed ? 0.98 : 1.0,
      child: InkWell(
        onTap: go,
        onHighlightChanged: (v) => setState(() => _pressed = v),
        borderRadius: BorderRadius.circular(24),
        splashColor: palette.primary.withValues(alpha: .15),
        highlightColor: palette.primary.withValues(alpha: .10),
        child: Ink(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [palette.primary, palette.secondary],
            ),
            border: Border.all(
              color: Colors.white.withValues(alpha: .16),
              width: 1.2,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: .28),
                blurRadius: 14,
                offset: const Offset(0, 8),
              ),
              BoxShadow(
                color: palette.glow.withValues(alpha: .45),
                blurRadius: 26,
                spreadRadius: 2,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Stack(
            children: [
              Positioned(
                top: 18,
                right: 18,
                child: _Bubble(color: palette.bubble1, size: 86),
              ),
              Positioned(
                bottom: -12,
                left: -12,
                child: _Bubble(color: palette.bubble2, size: 120),
              ),
              Positioned.fill(
                child: IgnorePointer(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Colors.white.withValues(alpha: .10),
                          Colors.white.withValues(alpha: .02),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Container(
                      height: 56,
                      width: 56,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [palette.iconBgStart, palette.iconBgEnd],
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: palette.iconBgStart.withValues(alpha: .35),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: Icon(
                        iconForSubject(name), // ← del helper modular
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      name,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 18,
                        height: 1.08,
                        shadows: [
                          Shadow(
                            color: Colors.black54,
                            blurRadius: 6,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/* ──────────────────────────── Helpers visuales ─────────────────────────── */

class _Bubble extends StatelessWidget {
  const _Bubble({required this.color, required this.size});
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(shape: BoxShape.circle, color: color),
    );
  }
}

/// Paleta generada desde el nombre de la asignatura.
class _SubjectPalette {
  final Color primary;
  final Color secondary;
  final Color glow;
  final Color bubble1;
  final Color bubble2;
  final Color iconBgStart;
  final Color iconBgEnd;

  const _SubjectPalette({
    required this.primary,
    required this.secondary,
    required this.glow,
    required this.bubble1,
    required this.bubble2,
    required this.iconBgStart,
    required this.iconBgEnd,
  });

  factory _SubjectPalette.fromName(String name, {int salt = 0}) {
    final hue = _stableHue(name, salt: salt);
    const s1 = 0.78;
    const s2 = 0.82;
    const v1 = 0.98;
    const v2 = 0.86;

    final c1 = HSVColor.fromAHSV(1, hue.toDouble(), s1, v1).toColor();
    final c2 = HSVColor.fromAHSV(
      1,
      ((hue + 22) % 360).toDouble(),
      s2,
      v2,
    ).toColor();
    final glow = HSVColor.fromAHSV(1, hue.toDouble(), .85, .60).toColor();
    final bubble1 = HSVColor.fromAHSV(.16, hue.toDouble(), .25, 1.0).toColor();
    final bubble2 = HSVColor.fromAHSV(
      .12,
      (hue + 10).toDouble(),
      .20,
      1.0,
    ).toColor();
    final iconA = HSVColor.fromAHSV(1, hue.toDouble(), .70, .92).toColor();
    final iconB = HSVColor.fromAHSV(
      1,
      (hue + 18).toDouble(),
      .80,
      .80,
    ).toColor();

    return _SubjectPalette(
      primary: c1,
      secondary: c2,
      glow: glow,
      bubble1: bubble1,
      bubble2: bubble2,
      iconBgStart: iconA,
      iconBgEnd: iconB,
    );
  }

  /// Hash → Hue en [0, 360), evitando 210°–280° (zona del fondo).
  static int _stableHue(String input, {int salt = 0}) {
    int h = salt;
    for (final code in input.codeUnits) {
      h = (h * 31 + code) & 0x7fffffff;
    }
    int hue = h % 360;
    const badStart = 210;
    const badEnd = 280;
    if (hue >= badStart && hue <= badEnd) {
      hue = (hue + 100) % 360;
    }
    return hue;
  }
}
