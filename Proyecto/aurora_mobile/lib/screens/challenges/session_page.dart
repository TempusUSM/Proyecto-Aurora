import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../providers/glims_provider.dart';
import '../../providers/store_provider.dart';
import '../../widgets/emotion_dialog.dart';
import '../../models/session.dart';
import '../../providers/challenge_provider.dart';
import '../../theme/app_colors.dart';
import 'package:flutter/services.dart';

class SessionPage extends StatefulWidget {
  const SessionPage({
    super.key,
    required this.session,
    this.review = false,
    this.initialAnswers,
    this.initialCorrections,
  });

  final StudySession session;
  final bool review;
  final Map<int, String>? initialAnswers;
  final Map<int, bool>? initialCorrections;

  @override
  State<SessionPage> createState() => _SessionPageState();
}

class _SessionPageState extends State<SessionPage>
    with SingleTickerProviderStateMixin {
  late int index;
  late final Map<int, String> answers;
  late final Map<int, bool> wasCorrect;

  final Map<int, TextEditingController> _textCtrls = {};
  late final AnimationController _enterCtrl;
  final ScrollController _scrollCtrl = ScrollController();

  @override
  void initState() {
    super.initState();
    index = 0;
    answers = {...?widget.initialAnswers};
    wasCorrect = {...?widget.initialCorrections};
    _enterCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 450),
    )..forward();

    // Edge-to-edge...
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        systemNavigationBarColor: Colors.transparent,
        systemNavigationBarIconBrightness: Brightness.light,
        systemNavigationBarContrastEnforced: false,
      ),
    );
  }

  void _jumpToTop() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollCtrl.hasClients) return;
      _scrollCtrl.animateTo(
        0,
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOutCubic,
      );
    });
  }

  void _prev() {
    if (index == 0) return;
    setState(() => index--);
    _jumpToTop();
  }

  @override
  void dispose() {
    _enterCtrl.dispose();
    for (final c in _textCtrls.values) {
      c.dispose();
      _scrollCtrl.dispose();
    }
    super.dispose();
  }

  TextEditingController _controllerFor(int qId) {
    return _textCtrls.putIfAbsent(
      qId,
      () => TextEditingController(text: answers[qId] ?? ''),
    );
  }

  String? _deriveCorrectLabel({
    required Map<String, String>? options,
    required String? correctField,
  }) {
    if (options == null || options.isEmpty) return null;
    String? correctText = correctField ?? options['correcta'];

    const letras = {'A', 'B', 'C', 'D'};
    if (correctText != null &&
        letras.contains(correctText.trim().toUpperCase())) {
      return correctText.trim().toUpperCase();
    }
    if (correctText != null) {
      final entry = options.entries.firstWhere(
        (e) =>
            e.key != 'correcta' &&
            e.value.trim().toLowerCase() == correctText.trim().toLowerCase(),
        orElse: () => const MapEntry('', ''),
      );
      return entry.key.isEmpty ? null : entry.key;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final s = widget.session;
    final q = s.questions[index];
    final bool inReview = widget.review;
    final double progress = (index + 1) / s.questions.length;

    final media = MediaQuery.of(context);
    final bool keyboardOpen = media.viewInsets.bottom > 0;

    return Scaffold(
      // Dibujamos detrás del AppBar para que el gradiente sea continuo
      extendBodyBehindAppBar: true,
      backgroundColor: Colors.transparent,
      resizeToAvoidBottomInset: true,
      appBar: AppBar(
        title: Text(s.title, maxLines: 1, overflow: TextOverflow.ellipsis),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: Colors.white,
      ),
      body: Container(
        // ← el gradiente cubre TODA la ventana (no dentro de SafeArea)
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: AppColors.auroraGradient,
            stops: [0, .55, 1],
          ),
        ),
        // Usamos SafeArea solo para no chocar con status/gestos,
        // pero SIN recortar el fondo (bottom/top en false)
        child: SafeArea(
          top: false,
          bottom: false,
          child: FadeTransition(
            opacity: CurvedAnimation(parent: _enterCtrl, curve: Curves.easeOut),
            child: SingleChildScrollView(
              controller: _scrollCtrl, // ← NUEVO
              keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
              padding: EdgeInsets.fromLTRB(
                16,
                media.padding.top + kToolbarHeight + 12,
                16,
                16 + media.padding.bottom,
              ),
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: media.size.height),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _HeaderProgress(
                      current: index + 1,
                      total: s.questions.length,
                      progress: progress,
                    ),
                    const SizedBox(height: 16),
                    _AuroraCard(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 18),
                      child: Text(
                        q.prompt,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          height: 1.28,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    if (q.type == 'Alternativa')
                      _AlternativesGrid(
                        options: q.options!,
                        selectedKey: answers[q.id],
                        inReview: inReview,
                        wasCorrect: wasCorrect[q.id] ?? false,
                        onSelect: inReview
                            ? null
                            : (k) => setState(() => answers[q.id] = k),
                      ),

                    if (q.type == 'Desarrollo') ...[
                      _AuroraCard(
                        padding: const EdgeInsets.all(12),
                        child: _AuroraTextField(
                          controller: _controllerFor(q.id),
                          enabled: !inReview,
                          hint: 'Escribe tu respuesta…',
                          onChanged: (v) {
                            answers[q.id] = v;
                            setState(() {}); // actualiza contador
                          },
                        ),
                      ),
                      const SizedBox(height: 4),
                      ValueListenableBuilder<TextEditingValue>(
                        valueListenable: _controllerFor(q.id),
                        builder: (_, value, __) => Align(
                          alignment: Alignment.centerRight,
                          child: Text(
                            '${value.text.length} caracteres',
                            style: TextStyle(
                              color: Colors.white.withValues(alpha: .70),
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                    ],

                    const SizedBox(height: 16),

                    // Botones DENTRO del flujo, ocultos si el teclado está abierto
                    if (!keyboardOpen)
                      _ActionsRow(
                        showBack: index > 0,
                        nextLabel: inReview
                            ? (index < s.questions.length - 1
                                  ? 'Siguiente'
                                  : 'Cerrar')
                            : (index < s.questions.length - 1
                                  ? 'Siguiente'
                                  : 'Finalizar'),
                        onBack: _prev, // ← usar helper
                        onNext: _nextOrFinish, // ← ver punto 3
                      ),

                    const SizedBox(height: 8),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _nextOrFinish() {
    final s = widget.session;
    final q = s.questions[index];
    final ans = answers[q.id];

    if (widget.review) {
      if (index < s.questions.length - 1) {
        setState(() => index++);
      } else {
        Navigator.pop(context); // cerrar revisión
      }
      return;
    }

    if (q.type == 'Alternativa' && ans == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecciona una alternativa')),
      );
      return;
    }
    if (q.type == 'Desarrollo') {
      answers[q.id] = _controllerFor(q.id).text;
    }

    if (index < s.questions.length - 1) {
      setState(() => index++);
      _jumpToTop();
    } else {
      _finish(s);
    }
  }

  Future<void> _finish(StudySession s) async {
    final challengeApi = context.read<ChallengeProvider>().api;
    final glimsProv = context.read<GlimsProvider>();
    final storeProv = context.read<StoreProvider>();

    // Calcular aciertos
    for (final q in s.questions.where((e) => e.type == 'Alternativa')) {
      final correctLabel = _deriveCorrectLabel(
        options: q.options,
        correctField: q.correct,
      );
      wasCorrect[q.id] =
          (answers[q.id] != null && answers[q.id] == correctLabel);
    }
    final correct = wasCorrect.values.where((v) => v == true).length;
    final score = correct * 10;

    final prefs = await SharedPreferences.getInstance();
    final rut = prefs.getString('rut');
    if (rut == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se encontró el RUT. Inicia sesión.')),
      );
      return;
    }

    // Guardar puntaje
    int newBalance = 0;
    try {
      int testId;
      try {
        testId = await challengeApi.resolveTestIdForSession(s.id);
      } catch (_) {
        testId = s.id;
      }
      newBalance = await challengeApi.sendScore(
        rut: rut,
        testId: testId,
        score: score,
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('No se pudo guardar el puntaje: $e')),
        );
      }
    }

    // Actualizar glims / inventario (no bloquear UX)
    if (newBalance >= 0) {
      glimsProv.setBalance(newBalance: newBalance);
    }
    try {
      storeProv.setRut(rut);
      await storeProv.loadInventoryAndBalance();
    } catch (_) {}

    if (!mounted) return;

    // Emoción post
    try {
      await showMoodCheckDialog(context: context, sesionId: s.id, tipo: 'post');
    } catch (_) {}

    if (!mounted) return;

    // Marcar completada
    context.read<ChallengeProvider>().markSessionCompleted(s.id);

    // Pantalla de resultados → al cerrar vuelve a “Secciones”
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => _ResultPage(
          score: score,
          total: s.questions.length * 10,
          session: s,
          answers: answers,
          corrections: wasCorrect,
          newBalance: newBalance,
          onClose: (ctx) => Navigator.pop(ctx),
        ),
      ),
    );
  }
}

/* =========================  Widgets Aurora  ========================= */

class _HeaderProgress extends StatelessWidget {
  const _HeaderProgress({
    required this.current,
    required this.total,
    required this.progress,
  });
  final int current, total;
  final double progress;

  @override
  Widget build(BuildContext context) {
    return _AuroraCard(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Row(
        children: [
          Icon(Icons.auto_awesome, color: Colors.white.withValues(alpha: .95)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Pregunta $current de $total',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                ClipRRect(
                  borderRadius: BorderRadius.circular(999),
                  child: Stack(
                    children: [
                      Container(
                        height: 8,
                        color: Colors.white.withValues(alpha: .16),
                      ),
                      FractionallySizedBox(
                        widthFactor: progress.clamp(0.0, 1.0),
                        child: Container(
                          height: 8,
                          decoration: const BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                AppColors.auroraCyan,
                                AppColors.auroraViolet,
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Text(
            '${(progress * 100).round()}%',
            style: TextStyle(
              color: Colors.white.withValues(alpha: .92),
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class _AlternativesGrid extends StatelessWidget {
  const _AlternativesGrid({
    required this.options,
    required this.selectedKey,
    required this.inReview,
    required this.wasCorrect,
    required this.onSelect,
  });

  final Map<String, String> options;
  final String? selectedKey;
  final bool inReview;
  final bool wasCorrect;
  final void Function(String key)? onSelect;

  @override
  Widget build(BuildContext context) {
    final entries = options.entries.where((e) => e.key != 'correcta').toList();
    final w = MediaQuery.of(context).size.width;
    final isNarrow = w < 380;

    return GridView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      itemCount: entries.length,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: isNarrow ? 1 : 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: isNarrow ? 3.4 : 3.0,
      ),
      itemBuilder: (_, i) {
        final e = entries[i];
        final isSelected = selectedKey == e.key;
        final bool showCorrect = inReview && isSelected && wasCorrect;
        final bool showWrong = inReview && isSelected && !wasCorrect;

        return _AuroraChoice(
          letter: e.key,
          text: e.value,
          selected: isSelected,
          correct: showCorrect,
          wrong: showWrong,
          onTap: onSelect == null ? null : () => onSelect!(e.key),
        );
      },
    );
  }
}

class _AuroraChoice extends StatelessWidget {
  const _AuroraChoice({
    required this.letter,
    required this.text,
    required this.selected,
    required this.correct,
    required this.wrong,
    this.onTap,
  });

  final String letter;
  final String text;
  final bool selected;
  final bool correct;
  final bool wrong;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    Color glow;
    List<Color> gradient;
    Color border;

    if (correct) {
      glow = Colors.greenAccent.withValues(alpha: .45);
      gradient = [const Color(0xFF34D399), const Color(0xFF10B981)];
      border = Colors.white.withValues(alpha: .40);
    } else if (wrong) {
      glow = Colors.redAccent.withValues(alpha: .45);
      gradient = [const Color(0xFFFB7185), const Color(0xFFF43F5E)];
      border = Colors.white.withValues(alpha: .40);
    } else if (selected) {
      glow = AppColors.auroraViolet.withValues(alpha: .45);
      gradient = const [AppColors.auroraBlue, AppColors.auroraViolet];
      border = Colors.white.withValues(alpha: .42);
    } else {
      glow = Colors.black.withValues(alpha: .25);
      gradient = [
        Colors.white.withValues(alpha: .10),
        Colors.white.withValues(alpha: .06),
      ];
      border = Colors.white.withValues(alpha: .28);
    }

    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: gradient,
            ),
            border: Border.all(color: border, width: 1.2),
            boxShadow: [
              BoxShadow(
                color: glow,
                blurRadius: 22,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Row(
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: correct
                        ? [const Color(0xFF6EE7B7), const Color(0xFF34D399)]
                        : wrong
                        ? [const Color(0xFFFDA4AF), const Color(0xFFFB7185)]
                        : const [AppColors.auroraCyan, AppColors.auroraViolet],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: glow,
                      blurRadius: 14,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: Center(
                  child: Text(
                    letter,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  text,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15.5,
                    height: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (correct || wrong) ...[
                const SizedBox(width: 8),
                Icon(
                  correct ? Icons.check_circle_rounded : Icons.cancel_rounded,
                  color: Colors.white,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _AuroraCard extends StatelessWidget {
  const _AuroraCard({required this.child, this.padding});
  final Widget child;
  final EdgeInsetsGeometry? padding;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ?? const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: .08),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Colors.white.withValues(alpha: .28)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: .25),
            blurRadius: 14,
            offset: const Offset(0, 8),
          ),
        ],
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withValues(alpha: .12),
            Colors.white.withValues(alpha: .06),
          ],
        ),
      ),
      child: child,
    );
  }
}

class _AuroraTextField extends StatelessWidget {
  const _AuroraTextField({
    required this.controller,
    required this.enabled,
    required this.hint,
    required this.onChanged,
  });

  final TextEditingController controller;
  final bool enabled;
  final String hint;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final base = Colors.white.withValues(alpha: .85);
    return TextField(
      controller: controller,
      enabled: enabled,
      minLines: 4,
      maxLines: 8, // crece pero con límite
      keyboardType: TextInputType.multiline,
      textInputAction: TextInputAction.newline,
      scrollPadding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 80,
      ),
      onChanged: onChanged,
      style: const TextStyle(color: Colors.white, fontSize: 16),
      cursorColor: AppColors.auroraCyan,
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: TextStyle(color: base.withValues(alpha: .65)),
        filled: true,
        fillColor: Colors.white.withValues(alpha: .06),
        contentPadding: const EdgeInsets.all(14),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: .28)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.auroraCyan, width: 1.4),
        ),
        disabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: .18)),
        ),
      ),
    );
  }
}

class _GlassButton extends StatelessWidget {
  const _GlassButton({
    required this.label,
    required this.onTap,
    required this.icon,
    this.fullWidth = false, // ← NUEVO
  });
  final String label;
  final VoidCallback onTap;
  final IconData icon;
  final bool fullWidth; // ← NUEVO

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          width: fullWidth ? double.infinity : null, // ← NUEVO
          constraints: const BoxConstraints(minHeight: 48), // ← cómodo
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            color: Colors.white.withValues(alpha: .10),
            border: Border.all(color: Colors.white.withValues(alpha: .28)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center, // ← centrado
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 18, color: Colors.white),
              const SizedBox(width: 8),
              Text(
                label,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PrimaryCTA extends StatelessWidget {
  const _PrimaryCTA({
    required this.label,
    required this.onTap,
    this.fullWidth = false, // ← NUEVO
  });
  final String label;
  final VoidCallback onTap;
  final bool fullWidth; // ← NUEVO

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: fullWidth ? double.infinity : null, // ← NUEVO
        constraints: const BoxConstraints(minHeight: 48), // ← igual que el otro
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(999),
          gradient: const LinearGradient(
            colors: [AppColors.auroraAmber, AppColors.auroraPink],
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.auroraAmber.withValues(alpha: .45),
              blurRadius: 18,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center, // ← centrado
          mainAxisSize: MainAxisSize.min,
          children: [
            Flexible(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),
            const SizedBox(width: 8),
            const Icon(Icons.arrow_forward_rounded, color: Colors.white),
          ],
        ),
      ),
    );
  }
}

class _ActionsRow extends StatelessWidget {
  const _ActionsRow({
    required this.showBack,
    required this.nextLabel,
    required this.onBack,
    required this.onNext,
  });

  final bool showBack;
  final String nextLabel;
  final VoidCallback onBack;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Opacity(
            // mantiene el layout aunque no haya “Anterior”
            opacity: showBack ? 1 : 0,
            child: IgnorePointer(
              ignoring: !showBack,
              child: _GlassButton(
                label: 'Anterior',
                icon: Icons.arrow_back_rounded,
                onTap: onBack,
                fullWidth: true, // ← ocupa todo el Expanded
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _PrimaryCTA(
            label: nextLabel,
            onTap: onNext,
            fullWidth: true, // ← ocupa todo el Expanded
          ),
        ),
      ],
    );
  }
}

/* ===========================  Resultados  =========================== */

class _ResultPage extends StatelessWidget {
  const _ResultPage({
    required this.score,
    required this.total,
    required this.session,
    required this.answers,
    required this.corrections,
    required this.newBalance,
    required this.onClose,
  });

  final int score, total, newBalance;
  final StudySession session;
  final Map<int, String> answers;
  final Map<int, bool> corrections;
  final void Function(BuildContext) onClose;

  @override
  Widget build(BuildContext context) {
    final pct = total == 0 ? 0.0 : score / total;

    return PopScope(
      canPop: true,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) onClose(context);
      },
      child: Scaffold(
        extendBodyBehindAppBar: true,
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          title: const Text('Resultados'),
          backgroundColor: Colors.transparent,
          elevation: 0,
          foregroundColor: Colors.white,
        ),
        body: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: AppColors.auroraGradient,
              stops: [0, .55, 1],
            ),
          ),
          child: SafeArea(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: _AuroraCard(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 24,
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${(pct * 100).round()}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 44,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Puntaje: $score / $total',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: .90),
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Saldo actual: $newBalance glims',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: .85),
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 20),
                      Wrap(
                        alignment: WrapAlignment.center,
                        spacing: 12,
                        runSpacing:
                            12, // si no cabe a lo ancho, baja uno debajo del otro
                        children: [
                          _GlassButton(
                            label: 'Revisar desafío',
                            icon: Icons.visibility_rounded,
                            onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => SessionPage(
                                  session: session,
                                  review: true,
                                  initialAnswers: answers,
                                  initialCorrections: corrections,
                                ),
                              ),
                            ),
                          ),
                          _PrimaryCTA(
                            label: 'Volver a las secciones',
                            onTap: () {
                              final nav = Navigator.of(context);
                              if (nav.canPop()) {
                                nav.pop();
                              } else {
                                onClose(context);
                              }
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
