import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../services/auth_service.dart';
import '../config/env.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _rutCtrl = TextEditingController();
  final _colegioCtrl = TextEditingController();
  bool _loading = false;
  final _auth = AuthService();

  late final Future<String> _mascotUrlFuture;

  @override
  void initState() {
    super.initState();
    _mascotUrlFuture = _computeMascotUrl();
  }

  @override
  void dispose() {
    _rutCtrl.dispose();
    _colegioCtrl.dispose();
    super.dispose();
  }

  Future<String> _computeMascotUrl() async {
    final base = await Env.baseUrl();
    return '$base/statics/img/aurora_login.png';
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final colegioId = int.tryParse(_colegioCtrl.text.trim());
    if (colegioId == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('El ID de colegio debe ser numérico')),
      );
      return;
    }

    setState(() => _loading = true);
    final ok = await _auth.login(_rutCtrl.text.trim(), colegioId);
    setState(() => _loading = false);

    if (!mounted) return;
    if (ok) {
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Datos inválidos')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, c) {
        final w = c.maxWidth;
        final h = c.maxHeight;
        final isWide = w >= 720; // breakpoint simple

        // Tamaños responsivos
        const panelMaxWidth = 520.0;
        final double mascotHeightWide =
            (h.clamp(500.0, 760.0)).toDouble() * 0.85; // desktop
        final double mascotHeightNarrow = ((h * 0.52).clamp(
          260.0,
          360.0,
        )).toDouble(); // móvil

        return Scaffold(
          body: Stack(
            children: [
              // —— Fondo aurora
              Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: AppColors.auroraGradient,
                    stops: [0.0, 0.55, 1.0],
                  ),
                ),
              ),

              // —— Mascota (derecha en desktop, detrás del panel en móvil)
              FutureBuilder<String>(
                future: _mascotUrlFuture,
                builder: (context, snap) {
                  final url = snap.data;
                  if (url == null) return const SizedBox.shrink();

                  if (isWide) {
                    // Derecha, cuerpo completo, sin tap events
                    return Positioned(
                      right: 16,
                      bottom: 0,
                      child: IgnorePointer(
                        ignoring: true,
                        child: Opacity(
                          opacity: 0.98,
                          child: Image.network(
                            url,
                            height: mascotHeightWide,
                            fit: BoxFit.contain,
                            semanticLabel: 'Aurora saludando',
                            errorBuilder: (_, __, ___) =>
                                const SizedBox.shrink(),
                          ),
                        ),
                      ),
                    );
                  } else {
                    // Móvil: centrada arriba y el panel tapa las piernas
                    return Positioned(
                      top: 36,
                      left: 0,
                      right: 0,
                      child: IgnorePointer(
                        ignoring: true,
                        child: SizedBox(
                          height: mascotHeightNarrow,
                          child: Center(
                            child: Stack(
                              alignment: Alignment.topCenter,
                              children: [
                                // Halo suave para integrarla con el fondo
                                Container(
                                  width: mascotHeightNarrow * 0.9,
                                  height: mascotHeightNarrow * 0.9,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: RadialGradient(
                                      colors: [
                                        Colors.white.withValues(alpha: 0.10),
                                        Colors.white.withValues(alpha: 0.00),
                                      ],
                                      radius: 0.85,
                                    ),
                                  ),
                                ),
                                Image.network(
                                  url,
                                  height: mascotHeightNarrow,
                                  fit: BoxFit.contain,
                                  semanticLabel: 'Aurora saludando',
                                  errorBuilder: (_, __, ___) =>
                                      const SizedBox.shrink(),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    );
                  }
                },
              ),

              // —— Panel “glass” con formulario
              Align(
                alignment: isWide ? Alignment.centerLeft : Alignment.center,
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: panelMaxWidth),
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: isWide ? 64 : 24),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: BackdropFilter(
                        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
                        child: Container(
                          padding: const EdgeInsets.fromLTRB(24, 28, 24, 20),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.14),
                            borderRadius: BorderRadius.circular(24),
                            border: Border.all(
                              color: Colors.white.withValues(alpha: 0.25),
                              width: 1,
                            ),
                            boxShadow: const [
                              BoxShadow(
                                color: Colors.black26,
                                blurRadius: 16,
                                offset: Offset(0, 10),
                              ),
                            ],
                          ),
                          child: Form(
                            key: _formKey,
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Text(
                                  '¡Hola! Soy Aurora ✨',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 24,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 6),
                                const Text(
                                  'Ingresa para empezar a aprender',
                                  style: TextStyle(color: Colors.white70),
                                ),
                                const SizedBox(height: 24),

                                // RUT
                                _AuroraField(
                                  controller: _rutCtrl,
                                  hint: 'RUT',
                                  icon: Icons.badge_outlined,
                                  validator: (v) =>
                                      (v == null || v.trim().isEmpty)
                                      ? 'Requerido'
                                      : null,
                                ),
                                const SizedBox(height: 12),

                                // ID Colegio
                                _AuroraField(
                                  controller: _colegioCtrl,
                                  hint: 'ID Colegio',
                                  icon: Icons.school_outlined,
                                  keyboardType: TextInputType.number,
                                  validator: (v) =>
                                      (v == null || v.trim().isEmpty)
                                      ? 'Requerido'
                                      : null,
                                ),
                                const SizedBox(height: 18),

                                // CTA
                                SizedBox(
                                  width: double.infinity,
                                  height: 48,
                                  child: ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppColors.auroraAmber,
                                      foregroundColor: Colors.white,
                                      elevation: 6,
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(14),
                                      ),
                                    ),
                                    onPressed: _loading ? null : _submit,
                                    child: _loading
                                        ? const SizedBox(
                                            width: 20,
                                            height: 20,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 3,
                                              valueColor:
                                                  AlwaysStoppedAnimation<Color>(
                                                    Colors.white,
                                                  ),
                                            ),
                                          )
                                        : const Text(
                                            'Ingresar',
                                            style: TextStyle(
                                              fontSize: 16,
                                              fontWeight: FontWeight.w700,
                                            ),
                                          ),
                                  ),
                                ),
                                const SizedBox(height: 10),

                                // Acción secundaria opcional
                                TextButton(
                                  onPressed: _loading ? null : () {},
                                  child: const Text(
                                    'Ingresar como invitado',
                                    style: TextStyle(color: Colors.white),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

// —— Campo estilo “Aurora” (pill + glass)
class _AuroraField extends StatelessWidget {
  const _AuroraField({
    required this.controller,
    required this.hint,
    required this.icon,
    this.keyboardType,
    this.validator,
  });

  final TextEditingController controller;
  final String hint;
  final IconData icon;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      validator: validator,
      keyboardType: keyboardType,
      style: const TextStyle(color: Colors.white, fontSize: 16),
      cursorColor: AppColors.auroraCyan,
      decoration: InputDecoration(
        filled: true,
        fillColor: Colors.white.withValues(alpha: 0.18),
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white70),
        prefixIcon: Icon(icon, color: Colors.white),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 14,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.35)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: AppColors.auroraCyan, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFFCA5A5)),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: Color(0xFFFCA5A5), width: 2),
        ),
      ),
    );
  }
}
