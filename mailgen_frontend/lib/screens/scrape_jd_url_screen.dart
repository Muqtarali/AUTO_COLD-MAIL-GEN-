import 'package:flutter/material.dart';

class ScrapeJdUrlScreen extends StatefulWidget {
  const ScrapeJdUrlScreen({super.key});

  @override
  State<ScrapeJdUrlScreen> createState() => _ScrapeJdUrlScreenState();
}

class _ScrapeJdUrlScreenState extends State<ScrapeJdUrlScreen> {
  final _urlController = TextEditingController();
  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _scrapedData;

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _scrapeJdUrl() async {
    final url = _urlController.text.trim();

    if (url.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Please enter a URL')));
      return;
    }

    // Basic URL validation
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('URL must start with http:// or https://'),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
      _scrapedData = null;
    });

    try {
      // This is a mock implementation - adjust based on actual backend endpoint
      // For now, we'll simulate scraping by making a request
      // In real scenario, this would call an actual backend scraping endpoint

      // Simulated scraped data
      final scrapedData = {
        'url': url,
        'title': 'Senior Flutter Developer',
        'company': 'Tech Company Inc.',
        'location': 'Remote',
        'role': 'Senior Flutter Developer',
        'level': 'Senior',
        'salary': '\$120,000 - \$160,000',
        'employment_type': 'Full-time',
        'description': '''
We are looking for an experienced Flutter Developer to join our team.

Key Responsibilities:
- Develop and maintain Flutter applications
- Collaborate with product and design teams
- Implement best practices and design patterns
- Optimize app performance
- Write unit and integration tests

Required Skills:
- 5+ years of mobile development experience
- Strong Flutter and Dart knowledge
- Experience with state management (Provider, Riverpod)
- Knowledge of REST APIs and JSON
- Git and version control
- Strong communication skills

Nice to Have:
- Experience with Firebase
- Knowledge of CI/CD pipelines
- Cross-platform development experience
- Open source contributions
        ''',
        'requirements': [
          'Flutter',
          'Dart',
          'REST APIs',
          'State Management',
          'Mobile Development',
          'Unit Testing',
        ],
        'nice_to_have': ['Firebase', 'CI/CD', 'Web Development', 'Open Source'],
        'posted_date': DateTime.now()
            .subtract(const Duration(days: 3))
            .toString(),
        'deadline': DateTime.now().add(const Duration(days: 30)).toString(),
      };

      if (mounted) {
        setState(() {
          _scrapedData = scrapedData;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scrape Job Description from URL'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // URL Input
            Text(
              'Enter Job Posting URL',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _urlController,
              enabled: !_isLoading,
              decoration: InputDecoration(
                hintText: 'https://linkedin.com/jobs/...',
                prefixIcon: const Icon(Icons.link),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                suffixIcon: _urlController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _urlController.clear();
                          setState(() {});
                        },
                      )
                    : null,
              ),
              onChanged: (value) {
                setState(() {});
              },
            ),
            const SizedBox(height: 12),

            // Supported URLs Info
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue.shade300),
              ),
              child: Row(
                children: [
                  Icon(Icons.info, color: Colors.blue.shade700, size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Supported: LinkedIn, Indeed, Glassdoor, company websites',
                      style: TextStyle(
                        color: Colors.blue.shade700,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Scrape Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _scrapeJdUrl,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.web_asset),
                label: Text(_isLoading ? 'Scraping...' : 'Scrape Job Posting'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Error Display
            if (_error != null)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade300),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error, color: Colors.red.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _error!,
                        style: TextStyle(color: Colors.red.shade700),
                      ),
                    ),
                  ],
                ),
              ),

            // Scraped Data Display
            if (_scrapedData != null) ...[
              const SizedBox(height: 24),
              _buildScrapedDataCard(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildScrapedDataCard() {
    final data = _scrapedData!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header Section
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  data['title'] ?? 'Job Title',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.business, size: 16, color: Colors.grey.shade600),
                    const SizedBox(width: 6),
                    Text(
                      data['company'] ?? 'Company Name',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(
                      Icons.location_on,
                      size: 16,
                      color: Colors.grey.shade600,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      data['location'] ?? 'Location',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade700,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    if (data['salary'] != null)
                      Chip(
                        label: Text(data['salary']),
                        backgroundColor: Colors.green.shade50,
                      ),
                    if (data['employment_type'] != null)
                      Chip(
                        label: Text(data['employment_type']),
                        backgroundColor: Colors.blue.shade50,
                      ),
                    if (data['level'] != null)
                      Chip(
                        label: Text(data['level']),
                        backgroundColor: Colors.purple.shade50,
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Description Section
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Job Description',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  data['description'] ?? 'No description available',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade700,
                    height: 1.6,
                  ),
                  maxLines: 10,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Requirements Section
        if (data['requirements'] != null &&
            (data['requirements'] as List).isNotEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Key Requirements',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: (data['requirements'] as List)
                        .map(
                          (req) => Chip(
                            label: Text(req),
                            backgroundColor: Colors.red.shade50,
                            labelStyle: TextStyle(color: Colors.red.shade700),
                          ),
                        )
                        .toList(),
                  ),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),

        // Nice to Have Section
        if (data['nice_to_have'] != null &&
            (data['nice_to_have'] as List).isNotEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Nice to Have',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: (data['nice_to_have'] as List)
                        .map(
                          (item) => Chip(
                            label: Text(item),
                            backgroundColor: Colors.yellow.shade50,
                            labelStyle: TextStyle(
                              color: Colors.yellow.shade700,
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),

        // Action Buttons
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                icon: const Icon(Icons.share),
                label: const Text('Share'),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Share functionality - Coming soon'),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                icon: const Icon(Icons.save),
                label: const Text('Save as JD'),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Saved successfully')),
                  );
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}
