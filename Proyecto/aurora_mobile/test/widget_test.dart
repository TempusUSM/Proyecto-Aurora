import 'package:flutter_test/flutter_test.dart';
import 'package:aurora_mobile/main.dart';

void main() {
  testWidgets('App builds smoke test', (tester) async {
    // Usa un RUT dummy válido para tus flujos.
    await tester.pumpWidget(AuroraApp(initialRut: '11111111-1'));

    expect(find.byType(AuroraApp), findsOneWidget);
  });
}
