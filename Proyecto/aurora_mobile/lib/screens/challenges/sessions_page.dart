import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/challenge_provider.dart';
import '../../models/unit.dart';
import '../../widgets/sessions_progress_map.dart';
import '../../widgets/emotion_dialog.dart';
import '../../theme/app_colors.dart';
import 'session_page.dart';

class SessionsPage extends StatefulWidget {
  const SessionsPage({super.key, required this.unit});
  final Unit unit;

  @override
  State<SessionsPage> createState() => _SessionsPageState();
}

class _SessionsPageState extends State<SessionsPage> {
  @override
  void initState() {
    super.initState();
    // Dispara la carga una sola vez, fuera del build.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      context.read<ChallengeProvider>().loadSessions(widget.unit.id);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChallengeProvider>(
      builder: (_, prov, __) {
        final sessionsOrNull = prov.sessions(widget.unit.id);

        return Scaffold(
          extendBodyBehindAppBar: true,
          backgroundColor: Colors.transparent,
          appBar: AppBar(
            toolbarHeight: 72,
            titleSpacing: 0,
            title: SizedBox(
              width: double.infinity,
              child: Text(
                widget.unit.title,
                maxLines: 2,
                softWrap: true,
                overflow: TextOverflow.ellipsis,
              ),
            ),
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
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: AppColors.auroraGradient,
                stops: [0, .55, 1],
              ),
            ),
            child: SafeArea(
              child: (sessionsOrNull == null)
                  ? const Center(
                      child: CircularProgressIndicator(),
                    ) // todavía cargando
                  : (sessionsOrNull.isEmpty)
                  ? const Center(child: Text('No hay sesiones disponibles'))
                  : SingleChildScrollView(
                      child: SessionsProgressMap(
                        sessions: sessionsOrNull,
                        onTapSession: (s) async {
                          final ok = await showMoodCheckDialog(
                            // ← aquí
                            context: context,
                            sesionId: s.id,
                            tipo: 'pre',
                          );
                          if (!ok) return;

                          await prov.loadSession(s.id);
                          if (!context.mounted) return;

                          final full = prov.session(s.id)!;
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => SessionPage(session: full),
                            ),
                          );
                        },
                      ),
                    ),
            ),
          ),
        );
      },
    );
  }
}
