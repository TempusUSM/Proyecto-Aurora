import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../providers/challenge_provider.dart';
import '../theme/app_colors.dart';

/// Moods fijos para quedar igual que web (1..5)
class _Mood {
  final int value;
  final String label;
  final String emoji;
  const _Mood(this.value, this.label, this.emoji);
}

const List<_Mood> _webMoods = <_Mood>[
  _Mood(1, 'Muy mal', '😱'),
  _Mood(2, 'Mal', '😟'),
  _Mood(3, 'Regular', '😐'),
  _Mood(4, 'Bien', '😊'),
  _Mood(5, 'Excelente', '😁'),
];

/// Diálogo de check emocional alineado con la web.
/// - tipo: 'pre' o 'post'
/// Devuelve true si se envió, false si canceló.
Future<bool> showMoodCheckDialog({
  required BuildContext context,
  required int sesionId,
  required String tipo, // 'pre' | 'post'
}) async {
  int? selected; // 1..5
  final TextEditingController commentCtrl = TextEditingController();

  return await showDialog<bool>(
        context: context,
        barrierDismissible: false,
        builder: (ctx) {
          final size = MediaQuery.of(ctx).size;
          return Dialog(
            backgroundColor: Colors.transparent,
            // mueve el diálogo hacia arriba cuando aparece el teclado
            insetPadding: const EdgeInsets.symmetric(
              horizontal: 20,
              vertical: 24,
            ),
            child: ConstrainedBox(
              // limita la altura total para que pueda scrollear
              constraints: BoxConstraints(maxHeight: size.height * 0.90),
              child: Container(
                padding: const EdgeInsets.fromLTRB(16, 14, 16, 12),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: .08),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: .28),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: .35),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
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
                child: StatefulBuilder(
                  builder: (inner, setState) {
                    final kOpen = MediaQuery.of(inner).viewInsets.bottom > 0;
                    final nav = Navigator.of(inner);
                    final messenger = ScaffoldMessenger.of(inner);
                    final api = Provider.of<ChallengeProvider>(
                      inner,
                      listen: false,
                    ).api;

                    return SingleChildScrollView(
                      physics: const ClampingScrollPhysics(),
                      keyboardDismissBehavior:
                          ScrollViewKeyboardDismissBehavior.onDrag,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            tipo == 'pre'
                                ? '¿Cómo te sientes antes de comenzar?'
                                : 'Cuéntanos cómo te sientes ahora',
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Moods (1..5)
                          Wrap(
                            spacing: 12,
                            runSpacing: 12,
                            alignment: WrapAlignment.center,
                            children: _webMoods.map((m) {
                              final bool sel = selected == m.value;
                              return GestureDetector(
                                onTap: () => setState(() => selected = m.value),
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    _EmojiChip(
                                      emoji: m.emoji,
                                      selected: sel,
                                      onTap: () =>
                                          setState(() => selected = m.value),
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      m.label,
                                      style: TextStyle(
                                        color: Colors.white.withValues(
                                          alpha: .90,
                                        ),
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ),

                          if (tipo == 'post') ...[
                            const SizedBox(height: 16),
                            Align(
                              alignment: Alignment.centerLeft,
                              child: Text(
                                'Coméntanos brevemente',
                                style: TextStyle(
                                  color: Colors.white.withValues(alpha: .90),
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            const SizedBox(height: 8),
                            _AuroraTextField(
                              controller: commentCtrl,
                              enabled: true,
                              hint: 'Comparte tu experiencia (opcional)',
                              onChanged: (_) {},
                            ),
                          ],

                          const SizedBox(height: 14),

                          // ⬇️ Botones ocultos cuando el teclado está abierto
                          if (!kOpen)
                            Row(
                              children: [
                                Expanded(
                                  child: _GlassButton(
                                    label: 'Cancelar',
                                    onTap: () => Navigator.pop(inner, false),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: _PrimaryCTA(
                                    label: 'Enviar',
                                    enabled: selected != null,
                                    onTap: () async {
                                      if (selected == null) return;
                                      try {
                                        final prefs =
                                            await SharedPreferences.getInstance();
                                        final rut =
                                            prefs.getString('rut') ?? '';

                                        await api.sendMoodCheck(
                                          rut: rut,
                                          sesionId: sesionId,
                                          tipo: tipo,
                                          value: selected!,
                                          comment: tipo == 'post'
                                              ? (commentCtrl.text.trim().isEmpty
                                                    ? null
                                                    : commentCtrl.text.trim())
                                              : null,
                                        );

                                        if (!nav.mounted) return;
                                        nav.pop(true);
                                      } catch (e) {
                                        if (!nav.mounted) return;
                                        messenger.showSnackBar(
                                          SnackBar(
                                            content: Text(
                                              'No se pudo registrar: $e',
                                            ),
                                          ),
                                        );
                                      }
                                    },
                                  ),
                                ),
                              ],
                            ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
          );
        },
      ) ??
      false;
}

/* ─────────────────────────  Widgets básicos  ───────────────────────── */

class _EmojiChip extends StatelessWidget {
  const _EmojiChip({
    required this.emoji,
    required this.selected,
    required this.onTap,
  });
  final String emoji;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        width: 60,
        height: 60,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: selected
              ? const LinearGradient(
                  colors: [AppColors.auroraBlue, AppColors.auroraViolet],
                )
              : LinearGradient(
                  colors: [
                    Colors.white.withValues(alpha: .10),
                    Colors.white.withValues(alpha: .06),
                  ],
                ),
          border: Border.all(
            color: Colors.white.withValues(alpha: selected ? .6 : .28),
            width: 1.2,
          ),
          boxShadow: [
            BoxShadow(
              color: (selected ? AppColors.auroraViolet : Colors.black)
                  .withValues(alpha: .35),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Center(child: Text(emoji, style: const TextStyle(fontSize: 26))),
      ),
    );
  }
}

/// Campo de texto con estilo Aurora (reutilizado aquí para el comentario post)
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
      maxLines: 6,
      keyboardType: TextInputType.multiline,
      textInputAction: TextInputAction.newline,
      style: const TextStyle(color: Colors.white, fontSize: 16),
      cursorColor: AppColors.auroraCyan,
      onChanged: onChanged,
      scrollPadding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 120,
      ),
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
  const _GlassButton({required this.label, required this.onTap});
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white.withValues(alpha: .10),
      borderRadius: BorderRadius.circular(999),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: Colors.white.withValues(alpha: .28)),
          ),
          child: Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w700,
            ),
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
    this.enabled = true,
  });
  final String label;
  final VoidCallback onTap;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: enabled ? 1 : .6,
      child: IgnorePointer(
        ignoring: !enabled,
        child: GestureDetector(
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 12),
            alignment: Alignment.center,
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
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
