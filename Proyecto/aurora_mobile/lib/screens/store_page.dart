// lib/screens/store_page.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../providers/store_provider.dart';
import '../providers/glims_provider.dart';
import '../widgets/skin_card.dart';
import '../widgets/balance_widget.dart';
import '../theme/app_colors.dart';

class StorePage extends StatefulWidget {
  const StorePage({super.key});
  @override
  State<StorePage> createState() => _StorePageState();
}

class _StorePageState extends State<StorePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    final store = context.read<StoreProvider>();
    final glims = context.read<GlimsProvider>();

    await store.loadSkins();

    final prefs = await SharedPreferences.getInstance();
    final rut = prefs.getString('rut') ?? '';
    if (!mounted) return;

    if (rut.isNotEmpty) {
      store.setRut(rut);
      await Future.wait([store.loadInventoryAndBalance(), glims.refresh(rut)]);
    }
  }

  void _safeBack(BuildContext context) {
    // Navegación defensiva
    if (Navigator.canPop(context)) {
      Navigator.pop(context);
    } else {
      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final glimsGlobal = context.watch<GlimsProvider>().glims;
    final glimsProv = context.read<GlimsProvider>();

    return LayoutBuilder(
      builder: (context, c) {
        final w = c.maxWidth;
        final crossCount = w >= 1200 ? 4 : (w >= 900 ? 3 : 2);

        return Scaffold(
          body: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: AppColors.auroraGradient,
                stops: [0.0, 0.55, 1.0],
              ),
            ),
            child: SafeArea(
              child: Column(
                children: [
                  // Cabecera
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    child: Row(
                      children: [
                        // Botón volver (seguro)
                        IconButton(
                          tooltip: 'Volver',
                          onPressed: () => _safeBack(context),
                          icon: const Icon(
                            Icons.arrow_back_rounded,
                            color: Colors.white,
                          ),
                          splashRadius: 22,
                          // sutil en web/desktop, casi imperceptible en móvil
                          style: IconButton.styleFrom(
                            backgroundColor: Colors.transparent,
                            hoverColor: Colors.white.withValues(alpha: 0.06),
                            highlightColor: Colors.white.withValues(
                              alpha: 0.10,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          'Tienda',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const Spacer(),
                        Consumer<StoreProvider>(
                          builder: (_, prov, __) =>
                              BalanceWidget(glims: glimsGlobal ?? prov.glims),
                        ),
                      ],
                    ),
                  ),

                  // Grid de skins
                  Expanded(
                    child: Consumer<StoreProvider>(
                      builder: (context, prov, _) {
                        if (prov.loadingSkins && prov.skins.isEmpty) {
                          return const Center(
                            child: CircularProgressIndicator(),
                          );
                        }

                        final saldo = glimsGlobal ?? prov.glims;

                        return GridView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: prov.skins.length,
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: crossCount,
                                mainAxisSpacing: 16,
                                crossAxisSpacing: 16,
                                childAspectRatio: 0.78,
                              ),
                          itemBuilder: (ctx, i) {
                            final item = prov.skins[i];
                            final owned = prov.isOwned(item.id);

                            return SkinCard(
                              item: item,
                              owned: owned,
                              isActive: false,
                              allowActivate: false,
                              buying: prov.isBuying(item.id),
                              onBuy: () async {
                                if (saldo < item.costo) {
                                  if (!mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Saldo insuficiente'),
                                    ),
                                  );
                                  return;
                                }

                                final err = await prov.purchase(item.id);
                                if (!mounted) return;

                                if (err == null) {
                                  glimsProv.setBalance(newBalance: prov.glims);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Compra exitosa'),
                                    ),
                                  );
                                } else {
                                  final msg = err.contains('Saldo insuficiente')
                                      ? 'Saldo insuficiente'
                                      : 'Error: $err';
                                  ScaffoldMessenger.of(
                                    context,
                                  ).showSnackBar(SnackBar(content: Text(msg)));
                                }
                              },
                              onActivate: () {},
                            );
                          },
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
