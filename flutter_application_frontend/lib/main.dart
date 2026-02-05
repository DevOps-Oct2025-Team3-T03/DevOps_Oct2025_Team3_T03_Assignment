import 'package:flutter/material.dart';
import 'package:flutter_application_frontend/theme.dart';
import 'package:flutter_application_frontend/widgets/feed/post_card.dart';

void main() => runApp(const WeLearnApp());

class WeLearnApp extends StatelessWidget {
  const WeLearnApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: WeLearnTheme.lightTheme,
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const FeedPage(),
    const AssignmentPage(),
    const DashboardPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Desktop Layout (Width > 600px)
        if (constraints.maxWidth > 600) {
          return Scaffold(
            body: Row(
              children: [
                NavigationRail(
                  selectedIndex: _currentIndex,
                  onDestinationSelected: (int index) {
                    setState(() => _currentIndex = index);
                  },
                  labelType: NavigationRailLabelType.all,
                  leading: const Padding(
                    padding: EdgeInsets.symmetric(vertical: 20),
                    child: Text(
                      "We!earn",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.deepPurple,
                      ),
                    ),
                  ),
                  destinations: const [
                    NavigationRailDestination(
                      icon: Icon(Icons.feed),
                      label: Text('Feed'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.assignment),
                      label: Text('Tasks'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.dashboard),
                      label: Text('Me'),
                    ),
                  ],
                  trailing: Expanded(
                    child: Align(
                      alignment: Alignment.bottomCenter,
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 20.0),
                        child: IconButton(
                          onPressed: () {},
                          icon: const Icon(Icons.settings),
                        ),
                      ),
                    ),
                  ),
                ),
                const VerticalDivider(thickness: 1, width: 1),
                Expanded(child: _pages[_currentIndex]),
              ],
            ),
          );
        }

        // Mobile Layout (Current implementation)
        return Scaffold(
          body: _pages[_currentIndex],
          bottomNavigationBar: BottomNavigationBar(
            currentIndex: _currentIndex,
            onTap: (index) => setState(() => _currentIndex = index),
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.feed), label: "Feed"),
              BottomNavigationBarItem(
                icon: Icon(Icons.assignment),
                label: "Tasks",
              ),
              BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: "Me"),
            ],
          ),
        );
      },
    );
  }
}

// --- KEEP OTHER PAGES (FeedPage, AssignmentPage, DashboardPage) AS IS ---

// --- FEED PAGE ---
class FeedPage extends StatelessWidget {
  const FeedPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("We!earn")),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          PostCard(
            author: "Prof. Tanaka",
            title: "Lesson 04: Flutter Layouts",
            content: "Please check the attached PDF for today's briefing.",
          ),
          PostCard(
            author: "System",
            title: "New Assignment Posted",
            content: "Assignment 02 is now live in the Tasks tab.",
          ),
        ],
      ),
    );
  }
}

// --- ASSIGNMENT & SUBMISSION PAGE ---
class AssignmentPage extends StatelessWidget {
  const AssignmentPage({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Assignments")),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            "Active Homework",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          Card(
            child: ListTile(
              title: const Text("Build a Dashboard UI"),
              subtitle: const Text("Due: Feb 12th"),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // Future: Navigate to detail/upload screen
              },
            ),
          ),
        ],
      ),
    );
  }
}

// --- STUDENT DASHBOARD ---
class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Student Dashboard")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          // Add this Column widget!
          crossAxisAlignment:
              CrossAxisAlignment.start, // Align text to the left
          children: [
            const Center(
              child: CircleAvatar(
                radius: 40,
                child: Icon(Icons.person, size: 40),
              ),
            ),
            const SizedBox(height: 10),
            const Center(
              child: Text(
                "Jonathan",
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
            ),
            const Divider(height: 40),
            const Text(
              "Statistics",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _statItem("Submissions", "12"),
                _statItem("XP", "1.2k"),
                _statItem("Streak", "5 Days"),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Ensure this helper method is defined at the bottom of the class
  Widget _statItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.deepPurple,
          ),
        ),
        Text(label, style: const TextStyle(color: Colors.grey)),
      ],
    );
  }
}
