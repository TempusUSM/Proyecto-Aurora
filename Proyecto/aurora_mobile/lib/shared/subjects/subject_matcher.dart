import 'package:flutter/material.dart';

/// Normaliza strings (minúsculas, sin tildes ni espacios raros) para matching.
extension Normalize on String {
  String norm() {
    final s = trim().toLowerCase();
    const map = {
      'á': 'a',
      'à': 'a',
      'ä': 'a',
      'â': 'a',
      'ã': 'a',
      'é': 'e',
      'è': 'e',
      'ë': 'e',
      'ê': 'e',
      'í': 'i',
      'ì': 'i',
      'ï': 'i',
      'î': 'i',
      'ó': 'o',
      'ò': 'o',
      'ö': 'o',
      'ô': 'o',
      'õ': 'o',
      'ú': 'u',
      'ù': 'u',
      'ü': 'u',
      'û': 'u',
      'ñ': 'n',
    };
    final buf = StringBuffer();
    for (final cp in s.runes) {
      final ch = String.fromCharCode(cp);
      buf.write(map[ch] ?? ch);
    }
    return buf.toString().replaceAll(RegExp(r'\s+'), ' ');
  }
}

/// Tipo de asignatura: patrones + ícono.
class SubjectKind {
  final String id;
  final List<RegExp> patterns;
  final IconData icon;
  SubjectKind(this.id, this.patterns, this.icon);
  bool matches(String nameNorm) => patterns.any((p) => p.hasMatch(nameNorm));
}

/// Asignaturas típicas de básica (Chile) + sinónimos.
// OJO: Historia va ANTES que Ciencias Naturales.
final List<SubjectKind> kPrimarySubjects = [
  SubjectKind('lenguaje', [
    RegExp(r'\bleng\b'),
    RegExp(r'comunic'),
    RegExp(r'castellano'),
    RegExp(r'lenguaje( y)? comunicacion'),
  ], Icons.menu_book_rounded),

  SubjectKind('matematica', [
    RegExp(r'\bmate\b'),
    RegExp(r'matematica?s?'),
  ], Icons.calculate_outlined),

  // ← prioridad para “Historia, Geografía y Ciencias Sociales”
  SubjectKind('historia_geografia_cs', [
    RegExp(r'historia'),
    RegExp(r'geografia'),
    RegExp(r'ciencias?\s+social(?:es)?'), // “ciencias sociales”
    RegExp(r'historia.*geografia'), // combinadas
    RegExp(r'hgcs'), // sigla
  ], Icons.history_edu_outlined),

  // Ciencias Naturales (evitamos capturar “ciencias sociales”)
  SubjectKind('ciencias_naturales', [
    RegExp(r'ciencias?\s+naturales?'), // nomencla oficial
    RegExp(r'ciencias?\s+de\s+la\s+naturaleza'), // variante
    RegExp(r'biologia|fisica|quimica'), // subramas
    RegExp(
      r'\bciencias?(?!\s+social(?:es)?)\b',
    ), // “ciencias” NO seguido de “social(es)”
  ], Icons.science_outlined),

  SubjectKind('ingles', [
    RegExp(r'ingles?'),
    RegExp(r'english'),
  ], Icons.translate),

  SubjectKind('artes_visuales', [
    RegExp(r'artes?\s+visuales?'),
    RegExp(r'artes?\s+plasticas?'),
    RegExp(r'\barte?s?\b'),
  ], Icons.brush_outlined),

  SubjectKind('musica', [RegExp(r'musica')], Icons.music_note),

  SubjectKind('tecnologia_informatica', [
    RegExp(r'tecnologia'),
    RegExp(r'informatica'),
    RegExp(r'computacion'),
    RegExp(r'\btic?s?\b'),
  ], Icons.memory_outlined),

  SubjectKind('educacion_fisica_y_salud', [
    RegExp(r'educacion\s+fisica'),
    RegExp(r'\bef\b'),
    RegExp(r'educacion\s+fisica\s+y\s+salud'),
    RegExp(r'fisica\s+y\s+salud'),
  ], Icons.sports_handball),

  SubjectKind('orientacion_convivencia', [
    RegExp(r'orientacion'),
    RegExp(r'consejo\s+de\s+curso'),
    RegExp(r'tutori?a'),
    RegExp(r'convivencia\s+escolar'),
  ], Icons.emoji_people),

  SubjectKind('religion', [
    RegExp(r'religion'),
    RegExp(r'educacion\s+religiosa'),
    RegExp(r'catequesis'),
  ], Icons.self_improvement),
];

/// Ícono robusto (tolerante a nombres raros). Fallback seguro.
IconData iconForSubject(String rawName) {
  final key = (rawName.isEmpty ? 'asignatura' : rawName).norm();

  for (final kind in kPrimarySubjects) {
    if (kind.matches(key)) return kind.icon;
  }
  // Heurísticas suaves:
  if (key.contains('program') || key.contains('robot')) {
    return Icons.memory_outlined;
  }
  if (key.contains('lect') || key.contains('escrit')) {
    return Icons.menu_book_rounded;
  }
  return Icons.menu_book_rounded;
}
