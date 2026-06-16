📱 Aurora Mobile — App Flutter

Aplicación móvil de Aurora (Flutter + Provider) que consume el backend FastAPI/MySQL. Incluye catálogo de desafíos por asignatura → unidad → sesión, rendición de preguntas (alternativas y desarrollo), registro de emociones pre/post, y gamificación con Glims (puntos/tienda).

🚀 Stack & versión

Flutter 3.24+ / Dart 3.8 (según environment del pubspec.yaml)

State management: provider

Storage local: shared_preferences

HTTP: http

Plataformas: Android, iOS, Web (dev)

🗂 Estructura principal
aurora_mobile/
├─ pubspec.yaml
├─ lib/
│  ├─ main.dart
│  ├─ theme/
│  │  └─ app_colors.dart
│  ├─ models/
│  │  ├─ emotion.dart
│  │  ├─ item.dart
│  │  ├─ question.dart
│  │  ├─ session.dart
│  │  ├─ subject.dart
│  │  └─ unit.dart
│  ├─ services/
│  │  ├─ auth_service.dart
│  │  ├─ challenge_service.dart
│  │  └─ store_service.dart
│  ├─ providers/
│  │  ├─ challenge_provider.dart
│  │  ├─ glims_provider.dart
│  │  └─ store_provider.dart
│  ├─ screens/
│  │  ├─ home_page.dart
│  │  ├─ login_page.dart
│  │  ├─ inventory_page.dart
│  │  ├─ store_page.dart
│  │  ├─ chatbot_page.dart
│  │  ├─ ranking_page.dart
│  │  ├─ statistics_page.dart
│  │  └─ challenges/
│  │     ├─ challenge_page.dart
│  │     ├─ units_page.dart
│  │     ├─ sessions_page.dart
│  │     └─ session_page.dart
│  └─ widgets/
│     ├─ balance_widget.dart
│     ├─ bubble_button.dart
│     ├─ emotion_dialog.dart
│     ├─ progress_map.dart
│     ├─ sessions_progress_map.dart
│     └─ skin_card.dart

Endpoints consumidos (resumen):

GET /asignaturas/ → asignaturas

GET /asignaturas/{id}/unidades → unidades por asignatura

GET /unidades/{id}/sesiones → sesiones por unidad

GET /sesiones/{id}/detalle → preguntas de la sesión

POST /desempenos/ → upsert de puntaje (móvil)

GET /store/balance/{rut} → balance de Glims

GET /emociones/ → catálogo de emociones (id, tipo, escala_max)

POST /registrosemocionales/ → registro emoción pre/post

POST /mobile/login → login por rut + colegio_id

CORS está habilitado en backend (ver README del backend para restringir orígenes si hace falta).


🧑‍💻 Cómo ejecutar localmente
0) Requisitos previos

    Instalar Git (última versión).

    Instalar Visual Studio Code.

    (Android) Instalar Android Studio (provee Android SDK, AVD y JDK).

    (iOS) Requiere macOS con Xcode + CocoaPods.

1) Instalar Flutter con VS Code

    Abre VS Code.

    En Extensions, instala Flutter (esto instala también Dart).

    Abre la Command Palette (View → Command Palette o Ctrl+Shift+P).

    Escribe “flutter” y ejecuta Flutter: New Project → Download SDK.

    Elige la carpeta donde se instalará el SDK y confirma Add SDK to PATH.

    Cierra y reabre VS Code y cualquier terminal para actualizar el PATH.

Verifica en terminal:
flutter --version
flutter doctor

Si doctor marca temas de Android, acepta licencias:
flutter doctor --android-licenses

2) Clonar el repositorio
En una terminal (PowerShell/CMD/Bash), clona tu repo y entra a la carpeta del app móvil:

git clone https://github.com/feriasw/2025repequipo05.git
cd Proyecto/aurora_mobile

*Asegúrate de estar exactamente en la carpeta aurora_mobile/ antes de correr comandos Flutter.

3) Instalar dependencias del proyecto
flutter pub get

*En caso de fallar, borra la carpeta Proyecto\aurora_mobile\build y luego ejecuta:
flutter clean

4. Ejecutar la app
El programa se puede correr en multiples plataformas
Para web:
flutter run -d web-server
*Para mantener la sesion (desafios completados) en el desarrollo, se recomienda ejecutar el comando, especificando el puerto:
flutter run -d web-server --web-hostname localhost --web-port 56881 <--- se puede colocar cualquier puerto.

Para móvil:
Se debe tener conectado el móvil, tener activo el modo opciones para desarrolladores -> tener activo la depuración por USB.
*opcional pero necesario en ciertos casos; tener activo en las opciones de desarrolladores -> Instalar vía USB

Para efectos

Una vez conectado y detectado el móvil, ejecutar este comando:
flutter run

