import 'package:flutter/material.dart';

class PostCard extends StatelessWidget {
  final String title;
  final String content;
  final String author;

  const PostCard({
    super.key,
    required this.title,
    required this.content,
    required this.author,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              author,
              style: TextStyle(
                color: Theme.of(context).primaryColor,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(content, style: const TextStyle(color: Colors.black87)),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.attachment, size: 16, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text(
                  "lecture_notes.pdf",
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
