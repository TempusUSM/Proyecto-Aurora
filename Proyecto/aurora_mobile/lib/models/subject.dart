class Subject {
  final int id;
  final String name;
  Subject({required this.id, required this.name});

  factory Subject.fromJson(Map<String, dynamic> j) => Subject(
    id: j['id'] ?? j['idAsignatura'],
    name: j['nombre'] ?? j['Nombre'],
  );
}
