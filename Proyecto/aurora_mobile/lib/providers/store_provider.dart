import 'package:flutter/material.dart';
import '../models/item.dart';
import '../services/store_service.dart';

class StoreProvider extends ChangeNotifier {
  final StoreService service;

  String rut; // ahora mutable
  StoreProvider({required this.service, required this.rut});

  void setRut(String value) {
    if (value.isEmpty || value == rut) return;
    rut = value;
    notifyListeners();
  }

  List<Item> skins = [];
  List<Item> inventory = [];
  int glims = 0;

  bool loadingSkins = false;
  bool loadingInventory = false;

  // control de compras en curso (para bloquear taps dobles)
  final Set<int> _buying = {};
  bool isBuying(int itemId) => _buying.contains(itemId);

  Future<void> loadSkins() async {
    loadingSkins = true;
    notifyListeners();
    try {
      skins = await service.fetchSkins();
    } finally {
      loadingSkins = false;
      notifyListeners();
    }
  }

  Future<void> loadInventoryAndBalance() async {
    if (rut.isEmpty) return;
    loadingInventory = true;
    notifyListeners();
    try {
      inventory = await service.getInventory(rut);
      glims = await service.getBalance(rut);
    } finally {
      loadingInventory = false;
      notifyListeners();
    }
  }

  bool isOwned(int itemId) => inventory.any((i) => i.id == itemId);

  // Por ahora no usamos activación (se integrará con Aurora más adelante)
  bool isActive(int itemId) => false;

  Future<String?> purchase(int itemId) async {
    if (rut.isEmpty) return 'RUT no inicializado';
    if (isOwned(itemId)) return 'Ya comprada';
    if (_buying.contains(itemId)) return 'Compra en progreso';

    _buying.add(itemId);
    notifyListeners();

    try {
      // Devuelve balance actualizado (o lanza error)
      glims = await service.purchaseSkin(rut, itemId);

      // Refrescamos inventario y balance para bloquear la tarjeta en UI
      await loadInventoryAndBalance();
      return null;
    } catch (e) {
      return e.toString();
    } finally {
      _buying.remove(itemId);
      notifyListeners();
    }
  }

  // Mantengo activate para futuro, pero no lo usamos ahora.
  Future<String?> activate(int itemId) async {
    try {
      await service.activateSkin(rut, itemId);
      await loadInventoryAndBalance();
      return null;
    } catch (e) {
      return e.toString();
    }
  }
}
