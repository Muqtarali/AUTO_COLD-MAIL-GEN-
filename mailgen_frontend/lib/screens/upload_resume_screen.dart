import 'dart:typed_data'; // Mandatory for Uint8List
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
// REMOVED: import 'dart:io'; (This causes the _Namespace error on Web)
import '../services/api_service.dart';

class UploadResumeScreen extends StatefulWidget {
  const UploadResumeScreen({super.key});

  @override
  State<UploadResumeScreen> createState() => _UploadResumeScreenState();
}

class _UploadResumeScreenState extends State<UploadResumeScreen> {
  Uint8List? _fileBytes;      // Store the file content as bytes
  String? _fileName;          // Store the file name
  bool _isUploading = false;
  String? _uploadResult;
  String? _error;

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'],
        withData: true, // REQUIRED: This ensures bytes are available on Web and Mobile
      );

      if (result != null) {
        setState(() {
          // Accessing the file content directly as bytes rather than via a file path
          _fileBytes = result.files.first.bytes;
          _fileName = result.files.first.name;
          _uploadResult = null;
          _error = null;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error picking file: $e';
      });
    }
  }

  Future<void> _uploadResume() async {
    if (_fileBytes == null) {
      setState(() => _error = 'Please select a file first');
      return;
    }

    setState(() {
      _isUploading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      
      // Sending raw bytes and the filename to your updated ApiService
      await apiService.uploadResume(_fileBytes!, _fileName!);

      if (mounted) {
        setState(() {
          _uploadResult = 'Resume uploaded successfully!';
          _isUploading = false;
          _fileBytes = null;
          _fileName = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Upload failed: $e';
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Resume')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Modern Upload Area Box
            GestureDetector(
              onTap: _isUploading ? null : _pickFile,
              child: Container(
                padding: const EdgeInsets.all(32),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  border: Border.all(
                    color: Colors.indigo.withOpacity(0.2),
                    width: 2,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.description,
                      size: 64,
                      color: Colors.indigo.shade400,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Select Resume PDF',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _fileName ?? 'No file selected',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Click to browse files',
                      style: TextStyle(color: Colors.indigo, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Error Display
            if (_error != null)
              _buildFeedbackCard(_error!, Colors.red),

            // Success Display
            if (_uploadResult != null)
              _buildFeedbackCard(_uploadResult!, Colors.green),

            const SizedBox(height: 24),

            // Responsive Upload Button
            SizedBox(
              height: 50,
              child: ElevatedButton(
                onPressed: _isUploading || _fileBytes == null ? null : _uploadResume,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  disabledBackgroundColor: Colors.grey.shade300,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isUploading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('Upload Resume', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeedbackCard(String text, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        border: Border.all(color: color),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(color == Colors.red ? Icons.error : Icons.check_circle, color: color),
          const SizedBox(width: 12),
          Expanded(child: Text(text, style: TextStyle(color: color))),
        ],
      ),
    );
  }
}