import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class GenerateEmailScreen extends StatefulWidget {
  const GenerateEmailScreen({super.key});

  @override
  State<GenerateEmailScreen> createState() => _GenerateEmailScreenState();
}

class _GenerateEmailScreenState extends State<GenerateEmailScreen> {
  String? _selectedResumeId;
  String? _selectedJdId;
  List<dynamic> _resumes = [];
  List<dynamic> _jds = [];
  bool _isLoading = false;
  bool _isGenerating = false;
  bool _isSending = false;
  String? _generatedSubject;
  String? _generatedBody;
  String? _error;
  String? _successMessage;
  final _receiverEmailController = TextEditingController();
  bool _enableAutoReply = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _receiverEmailController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final apiService = context.read<ApiService>();
      final resumes = await apiService.listResumes();
      final jds = await apiService.listJds();

      if (mounted) {
        setState(() {
          _resumes = resumes['items'] ?? [];
          _jds = jds['items'] ?? [];
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to load data: $e';
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _generateEmail() async {
    if (_selectedResumeId == null || _selectedJdId == null) {
      setState(() => _error = 'Please select both resume and job description');
      return;
    }

    setState(() {
      _isGenerating = true;
      _error = null;
      _successMessage = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final result = await apiService.generateEmail(
        _selectedResumeId!,
        _selectedJdId!,
      );

      if (mounted) {
        setState(() {
          _generatedSubject = result['subject'];
          _generatedBody = result['body'];
          _isGenerating = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Generation failed: $e';
          _isGenerating = false;
        });
      }
    }
  }

  Future<void> _sendEmail() async {
    final receiverEmail = _receiverEmailController.text.trim();

    if (receiverEmail.isEmpty) {
      setState(() => _error = 'Please enter receiver email');
      return;
    }

    if (!_isValidEmail(receiverEmail)) {
      setState(() => _error = 'Please enter a valid email address');
      return;
    }

    if (_generatedSubject == null || _generatedBody == null) {
      setState(() => _error = 'No email to send. Generate one first.');
      return;
    }

    setState(() {
      _isSending = true;
      _error = null;
      _successMessage = null;
    });

    try {
      final apiService = context.read<ApiService>();
      await apiService.sendEmail(
        to: receiverEmail,
        subject: _generatedSubject!,
        body: _generatedBody!,
        autoReplyEnabled: _enableAutoReply,
      );

      if (mounted) {
        setState(() {
          final autoReplyMsg = _enableAutoReply
              ? ' (Auto-reply enabled - monitoring for responses)'
              : '';
          _successMessage =
              'Email sent successfully to $receiverEmail$autoReplyMsg';
          _isSending = false;
          _receiverEmailController.clear();
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to send email: $e';
          _isSending = false;
        });
      }
    }
  }

  bool _isValidEmail(String email) {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
  }

  void _copyToClipboard() {
    if (_generatedSubject != null && _generatedBody != null) {
      Clipboard.setData(
        ClipboardData(text: 'Subject: $_generatedSubject\n\n$_generatedBody'),
      );
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Email copied to clipboard')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Generate Cold Email')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_successMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  border: Border.all(color: Colors.green),
                  borderRadius: BorderRadius.circular(8),
                ),
                margin: const EdgeInsets.only(bottom: 16),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, color: Colors.green),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _successMessage!,
                        style: const TextStyle(color: Colors.green),
                      ),
                    ),
                  ],
                ),
              ),
            if (_error != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.red),
                  borderRadius: BorderRadius.circular(8),
                ),
                margin: const EdgeInsets.only(bottom: 16),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  ],
                ),
              ),
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else ...[
              // Resume Selection
              const Text(
                'Select Resume',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
              ),
              const SizedBox(height: 8),
              DropdownButton<String?>(
                isExpanded: true,
                value: _selectedResumeId,
                hint: const Text('Choose a resume...'),
                items: _resumes.map<DropdownMenuItem<String?>>((resume) {
                  return DropdownMenuItem<String?>(
                    value: resume['id'] as String,
                    child: Text(resume['name'] ?? resume['id']),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() => _selectedResumeId = value);
                },
              ),
              const SizedBox(height: 20),

              // JD Selection
              const Text(
                'Select Job Description',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
              ),
              const SizedBox(height: 8),
              DropdownButton<String?>(
                isExpanded: true,
                value: _selectedJdId,
                hint: const Text('Choose a job description...'),
                items: _jds.map<DropdownMenuItem<String?>>((jd) {
                  return DropdownMenuItem<String?>(
                    value: jd['id'] as String,
                    child: Text('${jd['role']} - ${jd['company']}'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() => _selectedJdId = value);
                },
              ),
              const SizedBox(height: 32),

              // Generate Button
              ElevatedButton(
                onPressed: _isGenerating ? null : _generateEmail,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isGenerating
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Generate Email'),
              ),
              if (_generatedSubject != null) ...[
                const SizedBox(height: 32),
                // Generated Email Display
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.green.shade300),
                    borderRadius: BorderRadius.circular(8),
                    color: Colors.green.shade50,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Generated Email',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Subject:',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(_generatedSubject!),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Body:',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(_generatedBody!),
                      ),
                      const SizedBox(height: 16),
                      // Receiver Email Input
                      const Text(
                        'Send to Receiver:',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _receiverEmailController,
                        enabled: !_isSending,
                        decoration: InputDecoration(
                          hintText: 'recipient@example.com',
                          prefixIcon: const Icon(Icons.email),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(6),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                        ),
                        keyboardType: TextInputType.emailAddress,
                      ),
                      const SizedBox(height: 16),
                      // Auto-Reply Toggle
                      Row(
                        children: [
                          Checkbox(
                            value: _enableAutoReply,
                            onChanged: (value) {
                              setState(() => _enableAutoReply = value ?? false);
                            },
                          ),
                          const Text('Enable Auto-Reply'),
                          const SizedBox(width: 8),
                          Tooltip(
                            message:
                                'When enabled, the system will monitor for replies and automatically respond using AI',
                            child: Icon(
                              Icons.info_outline,
                              size: 18,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: _copyToClipboard,
                              icon: const Icon(Icons.copy),
                              label: const Text('Copy'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _isSending ? null : _sendEmail,
                              icon: _isSending
                                  ? const SizedBox(
                                      height: 16,
                                      width: 16,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : const Icon(Icons.send),
                              label: Text(_isSending ? 'Sending...' : 'Send'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}
