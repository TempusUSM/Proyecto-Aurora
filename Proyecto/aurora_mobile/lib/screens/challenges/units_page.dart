import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/challenge_provider.dart';
import '../../models/subject.dart';
import '../../models/unit.dart';
import '../../theme/app_colors.dart';
import '../../widgets/progress_map.dart';
import 'sessions_page.dart';

/// Lista de unidades de una asignatura.
/// Cada unidad se muestra como burbuja con un anillo de progreso
/// que se llena según las **sesiones** (secciones) completadas.
class UnitsPage extends StatefulWidget {
  const UnitsPage({super.key, required this.subject});
  final Subject subject;

  @override
  State<UnitsPage> createState() => _UnitsPageState();
}

class _UnitsPageState extends State<UnitsPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      context.read<ChallengeProvider>().loadUnits(widget.subject.id);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChallengeProvider>(
      builder: (_, prov, __) {
        final units = prov.units(widget.subject.id) ?? <Unit>[];

        // Resolvedor de progreso [0..1] para cada unidad.
        double _progressFor(Unit u) {
          final ss = prov.sessions(u.id);

          // Si aún no hay sesiones, disparamos una carga perezosa para esa unidad.
          if (ss == null) {
            // Evitamos disparar múltiples cargas cuando el provider ya está ocupado.
            if (!prov.loading) {
              WidgetsBinding.instance.addPostFrameCallback((_) {
                prov.loadSessions(u.id);
              });
            }
            return 0.0; // mientras carga, mostramos 0%
          }

          if (ss.isEmpty) return 0.0;

          final done = ss
              .where((s) => s.completed || prov.isSessionCompleted(s.id))
              .length;

          return done / ss.length;
        }

        return Scaffold(
          extendBodyBehindAppBar: true,
          backgroundColor: Colors.transparent,
          appBar: AppBar(
            title: Text(widget.subject.name),
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
            // Fondo aurora consistente con el resto de la app.
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: AppColors.auroraGradient,
                stops: [0, .55, 1],
              ),
            ),
            child: SafeArea(
              child: units.isEmpty
                  ? const Center(child: CircularProgressIndicator())
                  : SingleChildScrollView(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: ProgressMap(
                          units: units,
                          progressResolver: _progressFor,
                          onTapUnit: (u) => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => SessionsPage(unit: u),
                            ),
                          ),
                        ),
                      ),
                    ),
            ),
          ),
        );
      },
    );
  }
}
