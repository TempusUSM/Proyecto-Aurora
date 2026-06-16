import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../config/env.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  Future<String> _mascotUrl() async {
    final base = await Env.baseUrl();
    return '$base/statics/img/aurora_login.png';
  }

  @override
  Widget build(BuildContext context) {
    // Catálogo de accesos
    const items = [
      _MenuItem('Desafíos', Icons.play_lesson, '/challenges'),
      _MenuItem('Tienda', Icons.storefront_outlined, '/shop'),
      _MenuItem('Chatbot', Icons.chat_bubble_outline, '/chatbot'),
      _MenuItem('Inventario', Icons.inventory_2_outlined, '/inventory'),
      _MenuItem('Perfil', Icons.person_outline, '/profile'),
      _MenuItem('Estadísticas', Icons.bar_chart_outlined, '/stats'),
    ];

    return LayoutBuilder(
      builder: (context, c) {
        final w = c.maxWidth;
        final h = c.maxHeight;
        final isWide = w >= 900;

        // Columnas responsivas
        final crossCount = w >= 1200 ? 4 : (w >= 900 ? 3 : 2);

        return Scaffold(
          body: Stack(
            children: [
              // —— Fondo Aurora Boreal
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

              // —— Aurora decorativa a la derecha (solo desktop/tablet anchos)
              if (isWide)
                FutureBuilder<String>(
                  future: _mascotUrl(),
                  builder: (context, snap) {
                    final url = snap.data;
                    if (url == null) return const SizedBox.shrink();
                    final double height =
                        (h.clamp(520.0, 820.0)).toDouble() * 0.9;
                    return Positioned(
                      right: 24,
                      bottom: 0,
                      child: IgnorePointer(
                        ignoring: true,
                        child: Opacity(
                          opacity: 0.95,
                          child: Image.network(
                            url,
                            height: height,
                            fit: BoxFit.contain,
                            errorBuilder: (_, __, ___) =>
                                const SizedBox.shrink(),
                          ),
                        ),
                      ),
                    );
                  },
                ),

              // —— Contenido principal
              SafeArea(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header minimal
                      const Text(
                        'Aurora',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '¿Qué quieres hacer hoy?',
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.80),
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 20),

                      // Grid de acciones
                      Expanded(
                        child: GridView.builder(
                          padding: EdgeInsets.only(
                            right: isWide ? 240 : 0, // deja “aire” a la mascota
                          ),
                          itemCount: items.length,
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: crossCount,
                                mainAxisSpacing: 16,
                                crossAxisSpacing: 16,
                                childAspectRatio: 1.15,
                              ),
                          itemBuilder: (ctx, i) => _AuroraTile(item: items[i]),
                        ),
                      ),
                    ],
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

/* ─────────────────────────  TILE “GLASS + GLOW”  ───────────────────────── */
class _AuroraTile extends StatefulWidget {
  final _MenuItem item;
  const _AuroraTile({required this.item});

  @override
  State<_AuroraTile> createState() => _AuroraTileState();
}

class _AuroraTileState extends State<_AuroraTile> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final glow = _hover ? 0.22 : 0.10;

    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: () => Navigator.pushNamed(context, widget.item.route),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          decoration: BoxDecoration(
            // “Glass” con leve brillo y borde translúcido
            color: Colors.white.withValues(alpha: 0.10),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.28),
              width: 1,
            ),
            boxShadow: [
              // Sombra base
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.25),
                blurRadius: 14,
                offset: const Offset(0, 8),
              ),
              // Glow al hover
              BoxShadow(
                color: AppColors.auroraCyan.withValues(alpha: glow),
                blurRadius: 24,
                spreadRadius: 2,
              ),
            ],
            // Ligero gradiente interno para volumen
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withValues(alpha: 0.12),
                Colors.white.withValues(alpha: 0.06),
              ],
            ),
          ),
          padding: const EdgeInsets.all(16),
          child: LayoutBuilder(
            builder: (context, c) {
              final isTight =
                  c.maxHeight < 130; // celdas más bajas: icono más chico
              final iconSize = isTight ? 56.0 : 64.0;

              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  AnimatedScale(
                    duration: const Duration(milliseconds: 180),
                    scale: _hover ? 1.06 : 1.0,
                    child: Container(
                      height: iconSize,
                      width: iconSize,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            AppColors.auroraBlue,
                            AppColors.auroraViolet,
                          ],
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.auroraBlue.withValues(alpha: 0.35),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: Icon(
                        widget.item.icon,
                        color: Colors.white,
                        size: iconSize * 0.53,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Flexible(
                    child: Text(
                      widget.item.title,
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        height: 1.1,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Flexible(
                    child: Text(
                      _subtitleFor(widget.item.title),
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.75),
                        fontSize: 12.5,
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  String _subtitleFor(String title) {
    switch (title) {
      case 'Desafíos':
        return 'Practica y gana glims';
      case 'Tienda':
        return 'Skins y más';
      case 'Chatbot':
        return 'Habla con Aurora';
      case 'Inventario':
        return 'Tus objetos';
      case 'Perfil':
        return 'Tu información';
      case 'Estadísticas':
        return 'Tu progreso';
      default:
        return '';
    }
  }
}

/* ─────────────────────────────  MODELO  ───────────────────────────── */
class _MenuItem {
  final String title;
  final IconData icon;
  final String route;
  const _MenuItem(this.title, this.icon, this.route);
}
