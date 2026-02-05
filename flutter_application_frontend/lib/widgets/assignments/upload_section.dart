// lib/widgets/assignments/upload_section.dart
import 'package:flutter/material.dart';

class UploadSection extends StatelessWidget {
  final String title;
  const UploadSection({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.all(30),
          decoration: BoxDecoration(
            border: Border.all(
              color: Colors.grey.shade300,
              style: BorderStyle.solid,
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Center(
            child: Column(
              children: [
                Icon(Icons.upload_file, size: 40, color: Colors.grey),
                Text("Tap to select assignment file"),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: () {
              // Future: call your Python API here
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Submitting to backend...")),
              );
            },
            child: const Text("Submit Assignment"),
          ),
        ),
      ],
    );
  }
}
