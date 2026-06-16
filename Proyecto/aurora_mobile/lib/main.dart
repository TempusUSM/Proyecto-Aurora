import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'theme/app_colors.dart';
import 'screens/login_page.dart';
import 'screens/home_page.dart';
import 'screens/challenges/challenge_page.dart';
import 'screens/store_page.dart';
import 'screens/inventory_page.dart';

import 'providers/challenge_provider.dart';
import 'providers/store_provider.dart';
import 'providers/glims_provider.dart';

import 'services/challenge_service.dart';
import 'services/store_service.dart';
import 'services/auth_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final prefs = await SharedPreferences.getInstance();
  final initialRut = prefs.getString('rut') ?? '';

  runApp(MyApp(initialRut: initialRut));
}

class MyApp extends StatelessWidget {
  final String initialRut;
  const MyApp({Key? key, required this.initialRut}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ChallengeService>(
          create: (_) => ChallengeService(),
          lazy: false,
        ),
        Provider<StoreService>(create: (_) => StoreService(), lazy: false),

        ChangeNotifierProvider<ChallengeProvider>(
          create: (ctx) => ChallengeProvider(ctx.read<ChallengeService>()),
        ),
        ChangeNotifierProvider<StoreProvider>(
          create: (ctx) =>
              StoreProvider(service: ctx.read<StoreService>(), rut: initialRut),
        ),
        ChangeNotifierProvider<GlimsProvider>(
          create: (ctx) {
            final gp = GlimsProvider(
              ctx.read<StoreService>(),
              ctx.read<ChallengeService>(),
            );
            if (initialRut.isNotEmpty) {
              gp.refresh(initialRut); // fire-and-forget
            }
            return gp;
          },
        ),
      ],
      child: const AuroraApp(),
    );
  }
}

class AuroraApp extends StatelessWidget {
  const AuroraApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Aurora Mobile',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: AppColors.blue,
        scaffoldBackgroundColor: Colors.white,
      ),
      debugShowCheckedModeBanner: false,

      // Usamos el gate asíncrono (con home:)
      home: const _SplashGate(),
      routes: {
        '/login': (_) => const LoginPage(),
        '/home': (_) => const HomePage(),
        '/challenges': (_) => const ChallengePage(),
        '/shop': (_) => const StorePage(),
        '/inventory': (_) => const InventoryPage(),
      },
    );
  }
}

class _SplashGate extends StatefulWidget {
  const _SplashGate();

  @override
  State<_SplashGate> createState() => _SplashGateState();
}

class _SplashGateState extends State<_SplashGate> {
  final _auth = AuthService();

  @override
  void initState() {
    super.initState();
    _decide();
  }

  Future<void> _decide() async {
    final ok = await _auth.isAuthenticated();
    if (!mounted) return;
    Navigator.pushReplacementNamed(context, ok ? '/home' : '/login');
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
