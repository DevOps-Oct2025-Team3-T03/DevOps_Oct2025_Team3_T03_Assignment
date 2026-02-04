import 'package:flutter/material.dart';
import 'theme.dart';
// Import your widgets as you build them

void main() => runApp(const WeLearnApp());

class WeLearnApp extends StatelessWidget {
  const WeLearnApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(theme: WeLearnTheme.lightTheme, home: const HomePage());
  }
}

// --- PAGES SECTION ---

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  // List of pages kept in the same file
  final List<Widget> _pages = [const FeedPage(), const AssignmentPage()];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.feed), label: "Feed"),
          BottomNavigationBarItem(icon: Icon(Icons.assignment), label: "Tasks"),
        ],
      ),
    );
  }
}

class FeedPage extends StatelessWidget {
  const FeedPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("We!earn")),
      body: const Center(child: Text("Lectures & Posts")),
    );
  }
}

class AssignmentPage extends StatelessWidget {
  const AssignmentPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Assignments")),
      body: const Center(child: Text("Submit your work")),
    );
  }
}
