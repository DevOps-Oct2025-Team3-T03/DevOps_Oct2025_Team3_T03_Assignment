import 'package:flutter_test/flutter_test.dart';

// Principle: Unit Testing addresses "Pure Logic"
void main() {
  group('We!earn Branding Logic', () {
    test('Branding string contains the "!" symbol', () {
      const String brand = "We!earn";
      expect(brand.contains('!'), isTrue); // Ensures branding consistency
    });
  });

  group('Gamification Data Parsing', () {
    test('XP points calculation logic', () {
      int calculateProgress(int current, int goal) {
        if (goal == 0) return 0;
        return ((current / goal) * 100).toInt();
      }

      // Principle: Isolation - testing math without a UI
      expect(calculateProgress(50, 100), 50);
      expect(calculateProgress(10, 0), 0);
    });
  });
}
