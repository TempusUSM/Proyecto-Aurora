import 'package:flutter/foundation.dart';
import '../services/challenge_service.dart';
import '../services/store_service.dart';

class GlimsProvider with ChangeNotifier {
  GlimsProvider(this.store, this.challenges);

  final StoreService store;
  final ChallengeService challenges;

  int? _glims;
  int? get glims => _glims;
  bool loading = false;
  String? error;

  Future<void> refresh(String rut) async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      _glims = await store.getBalance(rut);
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> addFromScore({
    required String rut,
    required int testId,
    required int score,
  }) async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      _glims = await challenges.sendScore(
        rut: rut,
        testId:
            testId, // si no tienes testId, manda sesionId en este campo; el backend lo resuelve
        score: score,
      );
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> buy({required String rut, required int itemId}) async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      _glims = await store.purchaseSkin(rut, itemId);
    } catch (e) {
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  void setBalance({required int newBalance}) {
    _glims = newBalance;
    notifyListeners();
  }
}
