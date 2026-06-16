import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../providers/store_provider.dart';
import '../widgets/skin_card.dart';
import '../theme/app_colors.dart';

class InventoryPage extends StatefulWidget {
  const InventoryPage({super.key});

  @override
  State<InventoryPage> createState() => _InventoryPageState();
}

class _InventoryPageState extends State<InventoryPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    final prov = context.read<StoreProvider>();
    final prefs = await SharedPreferences.getInstance();
    final rut = prefs.getString('rut') ?? '';
    if (!mounted) return;

    if (rut.isNotEmpty) {
      prov.setRut(rut);
      await prov.loadInventoryAndBalance();
    }
  }

  Future<void> _refresh() async {
    final prov = context.read<StoreProvider>();
    await prov.loadInventoryAndBalance();
  }

  void _safeBack(BuildContext context) {
    if (Navigator.canPop(context)) {
      Navigator.pop(context);
    } else {
      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  @override
  Widget build(BuildContext context) {
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
              child: Consumer<StoreProvider>(
                builder: (context, prov, _) {
                  // CABECERA
                  final header = Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    child: Row(
                      children: [
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
                          'Inventario',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                  );

                  if (prov.loadingInventory && prov.inventory.isEmpty) {
                    return Column(
                      children: [
                        header,
                        const Expanded(
                          child: Center(child: CircularProgressIndicator()),
                        ),
                      ],
                    );
                  }

                  if (prov.inventory.isEmpty) {
                    return Column(
                      children: [
                        header,
                        Expanded(
                          child: RefreshIndicator(
                            onRefresh: _refresh,
                            child: ListView(
                              children: const [
                                SizedBox(height: 200),
                                Center(
                                  child: Text(
                                    'No tienes skins aún',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 16,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    );
                  }

                  // GRID
                  return Column(
                    children: [
                      header,
                      Expanded(
                        child: RefreshIndicator(
                          onRefresh: _refresh,
                          child: GridView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: prov.inventory.length,
                            gridDelegate:
                                SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: crossCount,
                                  childAspectRatio: 0.78,
                                  mainAxisSpacing: 16,
                                  crossAxisSpacing: 16,
                                ),
                            itemBuilder: (ctx, i) {
                              final item = prov.inventory[i];
                              return SkinCard(
                                item: item,
                                owned: true,
                                isActive: false,
                                allowActivate:
                                    false, // (cuando haya “equipar”, cambia a true)
                                buying: false,
                                onBuy: () {},
                                onActivate: () {},
                              );
                            },
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
      },
    );
  }
}
