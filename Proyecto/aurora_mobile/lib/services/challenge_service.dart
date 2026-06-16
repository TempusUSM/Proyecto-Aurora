import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config/env.dart';
import '../models/emotion.dart';
import '../models/subject.dart';
import '../models/unit.dart';
import '../models/session.dart';

class ChallengeService {
  /* ───────── host unificado ───────── */
  Future<String> _baseUrl() => Env.baseUrl();

  /* ───────── helpers ───────── */
  int? _tryParsePoints(dynamic body) {
    try {
      final j = body is String
          ? jsonDecode(body)
          : body as Map<String, dynamic>;
      final candidates = ['points', 'glims', 'Puntos', 'puntos'];
      for (final k in candidates) {
        if (j[k] != null) {
          final v = j[k];
          if (v is int) return v;
          return int.tryParse(v.toString());
        }
      }
    } catch (_) {}
    return null;
  }

  /* ───────── EMOCIONES ───────── */
  List<Emotion>? _memEmos;

  Future<List<Emotion>> emotions() async {
    if (_memEmos != null) return _memEmos!;
    final r = await http.get(Uri.parse('${await _baseUrl()}/emociones/'));
    _memEmos = (jsonDecode(r.body) as List)
        .map((e) => Emotion.fromJson(e))
        .toList();
    return _memEmos!;
  }

  Future<void> sendEmotion({
    required String rut,
    required int sesionId,
    required int emocionId,
    required String tipo, // 'pre' | 'post'
    required int escala, // 1-4
  }) async {
    await http.post(
      Uri.parse('${await _baseUrl()}/registrosemocionales/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'estudiante_rut': rut,
        'sesion_id': sesionId,
        'emocion_id': emocionId,
        'tipo': tipo,
        'escala': escala,
      }),
    );
  }

  /* ───────── CATÁLOGO DE DESAFÍOS ───────── */
  Future<List<Subject>> subjects() async {
    final r = await http.get(Uri.parse('${await _baseUrl()}/asignaturas/'));
    return (jsonDecode(r.body) as List)
        .map((e) => Subject.fromJson(e))
        .toList();
  }

  Future<List<Unit>> units(int subjectId) async {
    final r = await http.get(
      Uri.parse('${await _baseUrl()}/asignaturas/$subjectId/unidades'),
    );
    return (jsonDecode(r.body) as List).map((e) => Unit.fromJson(e)).toList();
  }

  Future<List<StudySession>> sessions(int unitId) async {
    final r = await http.get(
      Uri.parse('${await _baseUrl()}/unidades/$unitId/sesiones'),
    );
    final List data = jsonDecode(r.body);
    return data
        .map(
          (e) => StudySession(
            id: e['id'],
            title: e['bitacora'],
            objetivo: e['objetivo'],
            questions: const [],
          ),
        )
        .toList();
  }

  Future<StudySession> session(int sessionId) async {
    final r = await http.get(
      Uri.parse('${await _baseUrl()}/sesiones/$sessionId/detalle'),
    );
    return StudySession.fromJson(jsonDecode(r.body));
  }

  /* ───────── resolver testId por sessionId (cache) ───────── */
  final Map<int, int> _session2testId = {};

  Future<int> resolveTestIdForSession(int sessionId) async {
    if (_session2testId.containsKey(sessionId)) {
      return _session2testId[sessionId]!;
    }
    final r = await http.get(
      Uri.parse('${await _baseUrl()}/sesiones/$sessionId/detalle'),
    );
    if (r.statusCode < 200 || r.statusCode >= 300) {
      throw Exception('No se pudo obtener detalle de la sesión ($sessionId)');
    }
    final body = jsonDecode(r.body) as Map<String, dynamic>;
    final tests = (body['tests'] as List?) ?? [];
    if (tests.isEmpty || tests.first['id'] == null) {
      throw Exception('La sesión $sessionId no tiene tests definidos');
    }
    final testId = tests.first['id'] as int;
    _session2testId[sessionId] = testId;
    return testId;
  }

  /* ───────── PUNTAJE (devuelve nuevo balance) ───────── */
  Future<int> sendScore({
    required String rut,
    required int testId,
    required int score,
  }) async {
    final url = Uri.parse('${await _baseUrl()}/desempenos/');
    final res = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'rut': rut,
        'test_id': testId,
        'nota_test': score,
        'desempenio': 'OK',
      }),
    );
    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw Exception('Error al guardar puntaje (${res.statusCode})');
    }

    // 1) intentar leer el balance desde el propio POST
    final fromPost = _tryParsePoints(res.body);
    if (fromPost != null) return fromPost;

    // 2) fallback: consultar el balance a la ruta de tienda
    final bal = await http.get(
      Uri.parse('${await _baseUrl()}/store/balance/$rut'),
    );
    if (bal.statusCode == 200) {
      final p = _tryParsePoints(bal.body);
      if (p != null) return p;
    }

    // Si no podemos obtenerlo, devolvemos 0 para no romper la UI
    // (puedes cambiar esto por un throw si prefieres obligar a tener balance)
    return 0;
  }

  /// IDs de sesiones completadas para un estudiante (opcionalmente por unidad).
  Future<Set<int>> completedSessionIds({
    required String rut,
    int? unitId,
  }) async {
    final base = await _baseUrl();
    final uri = unitId == null
        ? Uri.parse('$base/desempenos/completadas/$rut')
        : Uri.parse('$base/desempenos/completadas/$rut/unidad/$unitId');

    final r = await http.get(uri);
    if (r.statusCode != 200) return <int>{};

    final body = jsonDecode(r.body);
    if (body is List) {
      return body
          .map((e) => e is int ? e : int.tryParse(e.toString()))
          .whereType<int>()
          .toSet();
    }
    return <int>{};
  }

  // En ChallengeService
  Future<void> sendMoodCheck({
    required String rut,
    required int sesionId,
    required String tipo, // 'pre' | 'post'
    required int value, // 1..5
    String? comment, // opcional (post)
  }) async {
    final base = await _baseUrl();

    // Intento 1: endpoints "nuevos" (si existen en tu FastAPI)
    final payload = {
      'rut': rut,
      'session_id': sesionId,
      'type': tipo,
      'value': value,
      if (comment != null && comment.trim().isNotEmpty)
        'comment': comment.trim(),
    };

    final candidates = <Uri>[
      Uri.parse('$base/sessions/$sesionId/mood'),
      Uri.parse('$base/mood-checks/'),
    ];

    for (final u in candidates) {
      try {
        final res = await http.post(
          u,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(payload),
        );
        if (res.statusCode >= 200 && res.statusCode < 300) {
          return; // OK con el endpoint nuevo
        }
        if (res.statusCode == 404 || res.statusCode == 405) {
          // endpoint no existe → probamos el siguiente
          continue;
        }
      } catch (_) {
        // seguimos al siguiente candidato / fallback
      }
    }

    // Fallback: usar el endpoint existente de tu app móvil.
    // Mapeamos value→emocionId y escala=value (comentario se ignora aquí).
    await sendEmotion(
      rut: rut,
      sesionId: sesionId,
      emocionId: value,
      tipo: tipo,
      escala: value,
    );

    // Intento opcional de guardar comentario si el backend tiene algo para eso
    if (comment != null && comment.trim().isNotEmpty) {
      try {
        await http.post(
          Uri.parse('$base/registrosemocionales/comentarios'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'estudiante_rut': rut,
            'sesion_id': sesionId,
            'tipo': tipo,
            'comentario': comment.trim(),
          }),
        );
        // Si no existe esta ruta no pasa nada; lo ignoramos
      } catch (_) {}
    }
  }
}
