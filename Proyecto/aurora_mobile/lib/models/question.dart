class Question {
  final int id;
  final String type; // "Alternativa" | "Desarrollo"
  final String prompt;
  final Map<String, String>? options; // null si es desarrollo
  final String? correct;

  Question({
    required this.id,
    required this.type,
    required this.prompt,
    this.options,
    this.correct,
  });

  static int _asInt(dynamic v) {
    if (v == null) return 0;
    if (v is int) return v;
    return int.tryParse(v.toString()) ?? 0;
  }

  factory Question.fromJson(Map<String, dynamic> j) {
    final rawAlt = j['alternativas'] as Map<String, dynamic>?;
    Map<String, String>? onlyOptions;
    String? correct;

    if (rawAlt != null) {
      // Copia y filtra "correcta" fuera de las opciones
      final map = <String, String>{};
      rawAlt.forEach((k, v) {
        if (k.toString().toLowerCase() != 'correcta') {
          map[k.toString()] = v?.toString() ?? '';
        }
      });
      onlyOptions = map;
      final corr = rawAlt['correcta'];
      if (corr != null) correct = corr.toString();
    }

    return Question(
      id: _asInt(j['id'] ?? j['idPregunta']),
      type: (j['tipo'] ?? j['Tipo'] ?? '').toString(),
      prompt: (j['enunciado'] ?? j['Enunciado'] ?? '').toString(),
      options: onlyOptions,
      correct: correct,
    );
  }
}
