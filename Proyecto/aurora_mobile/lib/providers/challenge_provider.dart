import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/subject.dart';
import '../models/unit.dart';
import '../models/session.dart';
import '../services/challenge_service.dart';

class ChallengeProvider with ChangeNotifier {
  ChallengeProvider(this.api);

  final ChallengeService api;

  // Estado en memoria
  List<Subject>? _subjects;
  final Map<int, List<Unit>> _unitsBySubject = {};
  final Map<int, List<StudySession>> _sessionsByUnit = {};
  final Map<int, StudySession> _sessionById = {};

  bool loading = false;
  String? error;

  String? _currentRut; // estudiante en sesión

  List<Subject>? get subjects => _subjects;
  List<Unit>? units(int subjId) => _unitsBySubject[subjId];
  List<StudySession>? sessions(int unitId) => _sessionsByUnit[unitId];
  StudySession? session(int sessionId) => _sessionById[sessionId];

  // Persistencia local por RUT (rápida y offline)
  static const String _prefsKeyPrefix = 'aurora_done_sessions_v3_';
  String get _prefsKey => _prefsKeyPrefix + (_currentRut ?? 'anonymous');
  bool _restored = false;
  final Set<int> _doneSessions = {}; // IDs de sesiones completadas

  // ======= Sesión de usuario =======
  /// LLAMA a esto tras login para fijar el RUT del estudiante.
  Future<void> setCurrentStudent(String rut) async {
    if (_currentRut == rut && _restored) return;
    _currentRut = rut;
    _restored = false;
    _doneSessions.clear();

    // 1) Cache local por RUT
    await _restoreDoneSessions();

    // 2) Merge con servidor (autoridad)
    try {
      final server = await api.completedSessionIds(rut: rut);
      if (server.isNotEmpty) {
        _doneSessions.addAll(server);
        await _persistDoneSessions();
      }
    } catch (_) {
      // si el backend no estuviese disponible, seguimos con cache local
    }

    // 3) Reflejar en listas ya cargadas
    for (final list in _sessionsByUnit.values) {
      for (final s in list) {
        s.completed = _doneSessions.contains(s.id);
      }
    }
    notifyListeners();
  }

  // ======= Carga de catálogos =======
  Future<void> loadSubjects() async {
    if (loading) return;
    await _wrapAsync(() async {
      _subjects = await api.subjects();
    });
  }

  Future<void> loadUnits(int subjectId) async {
    if (loading) return;
    await _wrapAsync(() async {
      _unitsBySubject.putIfAbsent(subjectId, () => []);
      if (_unitsBySubject[subjectId]!.isEmpty) {
        _unitsBySubject[subjectId] = await api.units(subjectId);
      }
    });
  }

  Future<void> loadSessions(int unitId) async {
    await _restoreDoneSessions(); // asegura cache cargada

    if (loading) return;
    await _wrapAsync(() async {
      _sessionsByUnit.putIfAbsent(unitId, () => []);
      if (_sessionsByUnit[unitId]!.isEmpty) {
        final list = await api.sessions(unitId);

        // marca según cache local
        for (final s in list) {
          if (_doneSessions.contains(s.id)) s.completed = true;
        }
        _sessionsByUnit[unitId] = list;

        // refuerzo desde servidor (si hay RUT)
        if (_currentRut != null) {
          try {
            final server = await api.completedSessionIds(
              rut: _currentRut!,
              unitId: unitId,
            );
            if (server.isNotEmpty) {
              _doneSessions.addAll(server);
              await _persistDoneSessions();
              for (final s in _sessionsByUnit[unitId]!) {
                if (_doneSessions.contains(s.id)) s.completed = true;
              }
            }
          } catch (_) {}
        }
      } else {
        // ya había sesiones; alinear con cache local
        for (final s in _sessionsByUnit[unitId]!) {
          if (_doneSessions.contains(s.id)) s.completed = true;
        }
      }
    });
  }

  Future<void> loadSession(int sessionId) async {
    await _restoreDoneSessions();
    if (loading) return;
    if (_sessionById.containsKey(sessionId)) return;

    await _wrapAsync(() async {
      final s = await api.session(sessionId);
      if (_doneSessions.contains(s.id)) s.completed = true;
      _sessionById[sessionId] = s;
    });
  }

  // ======= Marcar progreso =======
  void markSessionCompleted(int sessionId) {
    _doneSessions.add(sessionId);

    _sessionsByUnit.values
        .expand((l) => l)
        .where((s) => s.id == sessionId)
        .forEach((s) => s.completed = true);

    if (_sessionById.containsKey(sessionId)) {
      _sessionById[sessionId]!.completed = true;
    }

    _persistDoneSessions(); // no bloquea UI
    notifyListeners();
  }

  bool isSessionCompleted(int id) => _doneSessions.contains(id);

  // ======= Helpers de persistencia local =======
  Future<void> _restoreDoneSessions() async {
    if (_restored) return;
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_prefsKey) ?? const <String>[];

    // migración simple desde clave antigua global (si existía)
    if (raw.isEmpty) {
      final oldRaw =
          prefs.getStringList('aurora_done_sessions_v2') ?? const <String>[];
      if (oldRaw.isNotEmpty) {
        await prefs.remove('aurora_done_sessions_v2');
        await prefs.setStringList(_prefsKey, oldRaw);
      }
    }

    _doneSessions.addAll(raw.map((e) => int.tryParse(e)).whereType<int>());
    _restored = true;
  }

  Future<void> _persistDoneSessions() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(
      _prefsKey,
      _doneSessions.map((e) => e.toString()).toList(),
    );
  }

  // ======= Wrapper de estado =======
  Future<void> _wrapAsync(Future<void> Function() body) async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      await body();
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }
}
