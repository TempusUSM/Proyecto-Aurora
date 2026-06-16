import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:device_info_plus/device_info_plus.dart';

class Env {
  // Permite inyectar por --dart-define (ideal para equipo/CI)
  static const _fromDefine = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  static Future<String> baseUrl() async {
    if (_fromDefine.isNotEmpty) return _fromDefine;

    // Fallbacks inteligentes para dev local:
    if (kIsWeb) return 'http://localhost:8000';

    if (Platform.isAndroid) {
      final android = await DeviceInfoPlugin().androidInfo;
      final isEmu = !android.isPhysicalDevice;

      // Si usas "adb reverse", apunta a loopback del dispositivo
      // adb reverse tcp:8000 tcp:8000  ->  http://127.0.0.1:8000
      const preferReverse = bool.fromEnvironment(
        'USE_ADB_REVERSE',
        defaultValue: true,
      );
      if (preferReverse) return 'http://127.0.0.1:8000';

      // Emulador
      if (isEmu) return 'http://10.0.2.2:8000';

      // Dispositivo físico por LAN (último recurso)
      return 'http://192.168.18.47:8000';
    }

    // iOS/desktop dev LAN
    return 'http://192.168.18.47:8000';
  }
}
