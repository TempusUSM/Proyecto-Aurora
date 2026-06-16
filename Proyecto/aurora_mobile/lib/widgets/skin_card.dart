import 'package:flutter/material.dart';
import '../models/item.dart';
import '../theme/app_colors.dart';

class SkinCard extends StatefulWidget {
  final Item item;
  final bool owned;
  final bool isActive;

  final bool buying;
  final bool allowActivate;

  final VoidCallback onBuy;
  final VoidCallback onActivate;

  const SkinCard({
    Key? key,
    required this.item,
    required this.owned,
    required this.isActive,
    required this.onBuy,
    required this.onActivate,
    this.buying = false,
    this.allowActivate = true,
  }) : super(key: key);

  @override
  State<SkinCard> createState() => _SkinCardState();
}

class _SkinCardState extends State<SkinCard> {
  bool _hover = false;

  Widget _imageWidget() {
    final ref = widget.item.assetRef;
    if (ref == null || ref.isEmpty) {
      return const Icon(
        Icons.image_not_supported,
        size: 48,
        color: Colors.white,
      );
    }
    final isUrl = ref.startsWith('http://') || ref.startsWith('https://');
    if (isUrl) {
      return Image.network(
        ref,
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) =>
            const Icon(Icons.broken_image, size: 48, color: Colors.white),
      );
    }
    final assetPath = ref.startsWith('assets/') ? ref : 'assets/$ref';
    return Image.asset(
      assetPath,
      fit: BoxFit.contain,
      errorBuilder: (_, __, ___) =>
          const Icon(Icons.broken_image, size: 48, color: Colors.white),
    );
  }

  @override
  Widget build(BuildContext context) {
    final glow = _hover ? 0.22 : 0.10;

    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: Colors.white.withValues(alpha: 0.28),
            width: 1,
          ),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white.withValues(alpha: 0.12),
              Colors.white.withValues(alpha: 0.06),
            ],
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.25),
              blurRadius: 14,
              offset: const Offset(0, 8),
            ),
            BoxShadow(
              color: AppColors.auroraCyan.withValues(alpha: glow),
              blurRadius: 24,
              spreadRadius: 2,
            ),
          ],
          color: Colors.white.withValues(alpha: 0.10),
        ),
        child: Column(
          children: [
            // Imagen con fondo degradado y “glass”
            Expanded(
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(18),
                ),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            AppColors.auroraBlue,
                            AppColors.auroraViolet,
                          ],
                        ),
                      ),
                      child: Center(
                        child: Padding(
                          padding: const EdgeInsets.all(6),
                          child: _imageWidget(),
                        ),
                      ),
                    ),
                    if (widget.owned)
                      Positioned(
                        top: 8,
                        right: 8,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.85),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Text(
                            'Comprada',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),

            // Texto + precio + acciones
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    widget.item.nombre,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 6),

                  // Precio con “moneda”
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.16),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.stars_rounded,
                              size: 16,
                              color: Colors.white,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '${widget.item.costo} glims',
                              style: const TextStyle(color: Colors.white),
                            ),
                          ],
                        ),
                      ),
                      const Spacer(),
                    ],
                  ),
                  const SizedBox(height: 10),

                  // Botones
                  if (!widget.owned)
                    SizedBox(
                      height: 40,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.auroraAmber,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 4,
                        ),
                        onPressed: widget.buying ? null : widget.onBuy,
                        child: widget.buying
                            ? const SizedBox(
                                height: 18,
                                width: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text(
                                'Comprar',
                                style: TextStyle(fontWeight: FontWeight.w700),
                              ),
                      ),
                    )
                  else if (widget.allowActivate)
                    SizedBox(
                      height: 40,
                      child: widget.isActive
                          ? ElevatedButton(
                              onPressed: null,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green.withValues(
                                  alpha: 0.85,
                                ),
                                disabledForegroundColor: Colors.white,
                                disabledBackgroundColor: Colors.green
                                    .withValues(alpha: 0.85),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: const Text('Equipada'),
                            )
                          : OutlinedButton(
                              onPressed: widget.onActivate,
                              style: OutlinedButton.styleFrom(
                                side: BorderSide(
                                  color: Colors.white.withValues(alpha: 0.65),
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: const Text(
                                'Equipar',
                                style: TextStyle(color: Colors.white),
                              ),
                            ),
                    )
                  else
                    const SizedBox(height: 0),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
