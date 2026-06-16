import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config/env.dart';
import '../models/item.dart';

class StoreService {
  /* ───────── host unificado ───────── */
  Future<String> _baseUrl() => Env.baseUrl();

  int? _tryParsePoints(dynamic body) {
    try {
      final j = body is String
          ? jsonDecode(body)
          : body as Map<String, dynamic>;
      final keys = ['points', 'glims', 'Puntos', 'puntos'];
      for (final k in keys) {
        if (j[k] != null) {
          final v = j[k];
          if (v is int) return v;
          return int.tryParse(v.toString());
        }
      }
    } catch (_) {}
    return null;
  }

  Future<List<Item>> fetchSkins() async {
    final url = Uri.parse('${await _baseUrl()}/store/skins');
    final res = await http.get(url);
    if (res.statusCode == 200) {
      final List parsed = jsonDecode(res.body) as List;
      return parsed
          .map((e) => Item.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Error al obtener skins (${res.statusCode})');
  }

  Future<int> getBalance(String rut) async {
    final url = Uri.parse('${await _baseUrl()}/store/balance/$rut');
    final res = await http.get(url);
    if (res.statusCode == 200) {
      final p = _tryParsePoints(res.body);
      if (p != null) return p;
    }
    throw Exception('Error al obtener balance (${res.statusCode})');
  }

  /// Compra un item y devuelve el **balance** posterior
  Future<int> purchaseSkin(String rut, int itemId) async {
    final url = Uri.parse('${await _baseUrl()}/store/purchase');
    final res = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'rut': rut, 'item_id': itemId}),
    );

    if (res.statusCode == 201 || res.statusCode == 200) {
      final p = _tryParsePoints(res.body);
      if (p != null) return p;

      // fallback: consultar el balance
      return getBalance(rut);
    }

    final body = res.body.isNotEmpty ? res.body : 'status ${res.statusCode}';
    throw Exception('Compra fallida: $body');
  }

  Future<List<Item>> getInventory(String rut) async {
    final url = Uri.parse('${await _baseUrl()}/store/inventory/$rut');
    final res = await http.get(url);
    if (res.statusCode == 200) {
      final List parsed = jsonDecode(res.body) as List;
      return parsed
          .map((e) => Item.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Error al obtener inventario (${res.statusCode})');
  }

  Future<void> activateSkin(String rut, int itemId) async {
    final url = Uri.parse('${await _baseUrl()}/store/activate');
    final res = await http.patch(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'rut': rut, 'item_id': itemId}),
    );
    if (res.statusCode == 200) return;
    throw Exception('No se pudo activar skin (${res.statusCode})');
  }
}
