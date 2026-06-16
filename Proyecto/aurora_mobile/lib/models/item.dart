class Item {
  final int id;
  final String nombre;
  final String? descripcion;
  final int costo;
  final String? tipo;
  final String? assetRef;

  Item({
    required this.id,
    required this.nombre,
    this.descripcion,
    required this.costo,
    this.tipo,
    this.assetRef,
  });

  static int _asInt(dynamic v) {
    if (v == null) return 0;
    if (v is int) return v;
    return int.tryParse(v.toString()) ?? 0;
  }

  factory Item.fromJson(Map<String, dynamic> json) {
    return Item(
      id: json['id'] is int
          ? json['id']
          : (json['id'] != null
                ? int.tryParse(json['id'].toString()) ?? _asInt(json['idItem'])
                : _asInt(json['idItem'])),
      nombre: (json['nombre'] ?? json['Nombre'] ?? '').toString(),
      descripcion: (json['descripcion'] ?? json['Descripcion'])?.toString(),
      costo: json['costo'] is int
          ? json['costo']
          : _asInt(json['costo'] ?? json['Costo']),
      tipo: (json['tipo'] ?? json['Tipo'])?.toString(),
      assetRef: (json['asset_ref'] ?? json['assetRef'] ?? json['AssetRef'])
          ?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'descripcion': descripcion,
      'costo': costo,
      'tipo': tipo,
      'asset_ref': assetRef,
    };
  }
}
