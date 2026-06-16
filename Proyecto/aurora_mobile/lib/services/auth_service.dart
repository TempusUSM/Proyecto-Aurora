import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/env.dart';

class AuthService {
  Future<http.Client> _client() async {
    // Puedes envolver con timeouts si quieres un cliente custom
    return http.Client();
  }

  Future<Uri> _uri(String path) async {
    final base = await Env.baseUrl();
    return Uri.parse('$base$path');
  }

  // Login “ligero” (tu backend hoy solo verifica existencia)
  Future<bool> login(String rut, int colegioId) async {
    final client = await _client();
    final uri = await _uri('/mobile/login');

    try {
      final res = await client
          .post(
            uri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'rut': rut, 'colegio_id': colegioId}),
          )
          .timeout(const Duration(seconds: 10));

      if (res.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('rut', rut);
        await prefs.setInt('colegio_id', colegioId);
        // Si en el futuro hay token, guárdalo aquí
        return true;
      } else {
        debugPrint('Login error ${res.statusCode}: ${res.body}');
        return false;
      }
    } catch (e) {
      debugPrint('Login exception: $e');
      return false;
    } finally {
      client.close();
    }
  }

  // Validación real de sesión (si tu backend expone algo como /auth/me)
  // Si no existe, al menos verifica que existan las prefs.
  Future<bool> isAuthenticated() async {
    final prefs = await SharedPreferences.getInstance();
    final rut = prefs.getString('rut');
    final colegioId = prefs.getInt('colegio_id');

    if (rut == null || colegioId == null) return false;

    // Intento de validación con backend (opcional si tienes endpoint)
    try {
      final client = await _client();
      final uri = await _uri('/auth/me'); // <- cámbialo si tu backend usa otro
      final res = await client.get(uri).timeout(const Duration(seconds: 5));
      client.close();

      // Si el endpoint no existe (404) o no hay auth, cae al fallback
      if (res.statusCode == 200) return true;
    } catch (_) {
      // Ignora y usa fallback
    }

    // Fallback: si hay datos, considera “autenticado” (comportamiento actual)
    return true;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
