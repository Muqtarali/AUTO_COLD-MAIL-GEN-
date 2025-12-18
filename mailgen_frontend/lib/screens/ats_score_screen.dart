import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class AtsScoreScreen extends StatefulWidget {
  const AtsScoreScreen({super.key});

  @override
  State<AtsScoreScreen> createState() => _AtsScoreScreenState();
}

class _AtsScoreScreenState extends State<AtsScoreScreen> {
  bool _isLoading = false;
  String? _error;
  List<dynamic> _resumes = [];
  List<dynamic> _jds = [];
  String? _selectedResumeId;
  String? _selectedJdId;
  Map<String, dynamic>? _atsResult;

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  Future<void> _loadDocuments() async {
    try {
      final apiService = context.read<ApiService>();
      final resumes = await apiService.listResumes();
      final jds = await apiService.listJds();

      if (mounted) {
        setState(() {
          _resumes = resumes['items'] as List? ?? [];
          _jds = jds['items'] as List? ?? [];
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error loading documents: $e')));
      }
    }
  }

  Future<void> _calculateAtsScore() async {
    if (_selectedResumeId == null || _selectedJdId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select both resume and job description'),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
      _atsResult = null;
    });

    try {
      // Simple ATS scoring based on available data
      // This is a mock implementation - adjust based on actual backend endpoint
      final resume = _resumes.firstWhere(
        (r) => r['id'].toString() == _selectedResumeId,
        orElse: () => {},
      );
      final jd = _jds.firstWhere(
        (j) => j['id'].toString() == _selectedJdId,
        orElse: () => {},
      );

      // Calculate mock ATS score
      double score = 50.0;
      final List<String> matchedSkills = [];
      final List<String> missingSkills = [];

      // Simple string matching for skills
      final resumeText = '${resume['name']} ${resume['metadata']?.toString()}'
          .toLowerCase();
      final jdText = '${jd['role']} ${jd['company']}'.toLowerCase();

      // Mock skill extraction and matching
      final commonKeywords = [
        'python',
        'java',
        'flutter',
        'react',
        'aws',
        'docker',
      ];
      for (final keyword in commonKeywords) {
        if (resumeText.contains(keyword) && jdText.contains(keyword)) {
          matchedSkills.add(keyword);
          score += 5;
        } else if (jdText.contains(keyword)) {
          missingSkills.add(keyword);
        }
      }

      score = score.clamp(0, 100).toDouble();

      if (mounted) {
        setState(() {
          _atsResult = {
            'score': score,
            'matched_skills': matchedSkills,
            'missing_skills': missingSkills,
            'resume_name': resume['name'] ?? 'Unknown',
            'jd_role': jd['role'] ?? 'Unknown',
            'match_percentage': '${score.toStringAsFixed(1)}%',
          };
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
      appBar: AppBar(title: const Text('ATS Score Calculator'), elevation: 0),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Resume Selection
            Text(
              'Select Resume',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(8),
              ),
              child: DropdownButton<String?>(
                value: _selectedResumeId,
                isExpanded: true,
                underline: const SizedBox(),
                hint: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('Choose a resume'),
                ),
                items: _resumes
                    .map(
                      (resume) => DropdownMenuItem<String?>(
                        value: resume['id'].toString(),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(resume['name'] ?? 'Resume'),
                              if (resume['metadata']?['email'] != null)
                                Text(
                                  resume['metadata']['email'],
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedResumeId = value;
                  });
                },
              ),
            ),
            const SizedBox(height: 24),

            // JD Selection
            Text(
              'Select Job Description',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(8),
              ),
              child: DropdownButton<String?>(
                value: _selectedJdId,
                isExpanded: true,
                underline: const SizedBox(),
                hint: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('Choose a job description'),
                ),
                items: _jds
                    .map(
                      (jd) => DropdownMenuItem<String?>(
                        value: jd['id'].toString(),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(jd['role'] ?? 'Job Description'),
                              if (jd['company'] != null)
                                Text(
                                  jd['company'],
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedJdId = value;
                  });
                },
              ),
            ),
            const SizedBox(height: 32),

            // Calculate Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _calculateAtsScore,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.assessment),
                label: Text(
                  _isLoading ? 'Calculating...' : 'Calculate ATS Score',
                ),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
            const SizedBox(height: 32),

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

            // Results Display
            if (_atsResult != null) ...[
              const SizedBox(height: 24),
              _buildAtsResultCard(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAtsResultCard() {
    final score = _atsResult!['score'] as double;
    final matchedSkills = _atsResult!['matched_skills'] as List<String>;
    final missingSkills = _atsResult!['missing_skills'] as List<String>;
    final resumeName = _atsResult!['resume_name'] as String;
    final jdRole = _atsResult!['jd_role'] as String;

    Color getScoreColor() {
      if (score >= 75) return Colors.green;
      if (score >= 50) return Colors.orange;
      return Colors.red;
    }

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Text(
              'ATS Match Score',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              '$resumeName → $jdRole',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 24),

            // Score Display
            Center(
              child: Column(
                children: [
                  Stack(
                    alignment: Alignment.center,
                    children: [
                      SizedBox(
                        width: 150,
                        height: 150,
                        child: CircularProgressIndicator(
                          value: score / 100,
                          strokeWidth: 8,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            getScoreColor(),
                          ),
                          backgroundColor: Colors.grey.shade200,
                        ),
                      ),
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            '${score.toStringAsFixed(1)}%',
                            style: TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: getScoreColor(),
                            ),
                          ),
                          Text(
                            score >= 75
                                ? 'Strong Match'
                                : score >= 50
                                ? 'Good Match'
                                : 'Weak Match',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey.shade600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Matched Skills
            if (matchedSkills.isNotEmpty) ...[
              Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Matched Skills (${matchedSkills.length})',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.green,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: matchedSkills
                    .map(
                      (skill) => Chip(
                        label: Text(skill),
                        backgroundColor: Colors.green.shade50,
                        labelStyle: TextStyle(color: Colors.green.shade700),
                        side: BorderSide(color: Colors.green.shade300),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 24),
            ],

            // Missing Skills
            if (missingSkills.isNotEmpty) ...[
              Row(
                children: [
                  Icon(Icons.highlight_off, color: Colors.orange, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Missing Skills (${missingSkills.length})',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.orange,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: missingSkills
                    .map(
                      (skill) => Chip(
                        label: Text(skill),
                        backgroundColor: Colors.orange.shade50,
                        labelStyle: TextStyle(color: Colors.orange.shade700),
                        side: BorderSide(color: Colors.orange.shade300),
                      ),
                    )
                    .toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
