import 'question.dart';

class StudySession {
  final int id;
  final String title;
  final String objetivo;
  final List<Question> questions;
  final int? testId; // <- útil para enviar score directo al test
  bool completed;

  StudySession({
    required this.id,
    required this.title,
    required this.objetivo,
    required this.questions,
    this.testId,
    this.completed = false,
  });

  static int _asInt(dynamic v) {
    if (v == null) return 0;
    if (v is int) return v;
    return int.tryParse(v.toString()) ?? 0;
  }

  factory StudySession.fromJson(Map<String, dynamic> j) {
    final tests = (j['tests'] as List? ?? const []);
    final List qs = tests
        .expand((t) => (t['preguntas'] as List? ?? const []))
        .toList();

    // toma el primer test si existe (común en tu backend)
    final int? testId = tests.isNotEmpty ? _asInt(tests.first['id']) : null;

    return StudySession(
      id: _asInt(j['id']),
      title: (j['bitacora'] ?? '').toString(),
      objetivo: (j['objetivo'] ?? '').toString(),
      questions: qs
          .map((e) => Question.fromJson(e as Map<String, dynamic>))
          .toList(),
      testId: testId,
      completed: (j['completed'] ?? false) == true,
    );
  }
}
