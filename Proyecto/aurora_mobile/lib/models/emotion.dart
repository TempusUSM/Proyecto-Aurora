class Emotion {
  final int id;
  final String tipo;
  final int escalaMax;

  Emotion({required this.id, required this.tipo, required this.escalaMax});

  factory Emotion.fromJson(Map<String, dynamic> j) => Emotion(
    id: j['id'] ?? j['idEmocion'],
    tipo: j['tipo'] ?? j['Tipo'],
    escalaMax: j['escala_max'] ?? j['EscalaMax'],
  );
}
