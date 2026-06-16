class Unit {
  final int id;
  final String title;
  final bool isDone;

  Unit({required this.id, required this.title, this.isDone = false});

  factory Unit.fromJson(Map<String, dynamic> j) => Unit(
    id: j['idUnidad'] ?? j['id'],
    title: j['Descripcion'] ?? j['descripcion'] ?? '',
    isDone: j['isDone'] ?? false,
  );
}
