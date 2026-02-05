import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

// Principle: Using the correct package name ensures the compiler can locate your code
import 'package:flutter_application_frontend/main.dart';
import 'package:flutter_application_frontend/widgets/feed/post_card.dart';

void main() {
  // Principle: Behavioral Verification - Testing if the "Shell" loads
  testWidgets('We!earn app loads with correct branding and navigation', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const WeLearnApp());

    // Verify the "We!earn" branding text is present
    expect(find.text('We!earn'), findsOneWidget);

    // Verify navigation elements exist
    expect(find.byType(BottomNavigationBar), findsOneWidget);
    expect(find.byIcon(Icons.feed), findsOneWidget);
    expect(find.byIcon(Icons.assignment), findsOneWidget);
  });

  // Principle: Component Isolation - Testing the PostCard specifically
  testWidgets('PostCard displays lecture content correctly', (
    WidgetTester tester,
  ) async {
    // We wrap it in MaterialApp so it can find the Theme defined in theme.dart
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: PostCard(
            author: "Prof. Herenged",
            title: "Intro to Flutter",
            content: "Welcome to the education platform.",
          ),
        ),
      ),
    );

    // Verify rendering of passed data
    expect(find.text('Prof. Herenged'), findsOneWidget);
    expect(find.text('Intro to Flutter'), findsOneWidget);
    expect(find.text('Welcome to the education platform.'), findsOneWidget);

    // Check for the attachment icon inside the card
    expect(find.byIcon(Icons.attachment), findsOneWidget);
  });
}
