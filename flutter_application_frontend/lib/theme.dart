import 'package:flutter/material.dart';

class WeLearnTheme {
  // Brand Colors
  static const Color primaryPurple = Color(0xFF6C63FF);
  static const Color accentCyan = Color(0xFF00D2FF);
  static const Color darkText = Color(0xFF2D2D2D);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryPurple,
        primary: primaryPurple,
        secondary: accentCyan,
      ),
      scaffoldBackgroundColor: const Color(0xFFF5F7FA),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        backgroundColor: Colors.white,
        foregroundColor: primaryPurple,
        elevation: 0,
      ),
      cardTheme: const CardThemeData(
        // Changed from CardTheme to CardThemeData
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(16)),
          side: BorderSide(color: Color(0xFFEEEEEE)),
        ),
      ),
    );
  }
}
