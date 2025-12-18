import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class UploadJdScreen extends StatefulWidget {
  const UploadJdScreen({super.key});

  @override
  State<UploadJdScreen> createState() => _UploadJdScreenState();
}

class _UploadJdScreenState extends State<UploadJdScreen> {
  Uint8List? _fileBytes;
  String? _fileName;
  bool _isUploading = false;
  String? _error;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: true, // IMPORTANT: Required for Web to get file bytes
    );

    if (result != null) {
      setState(() {
        _fileBytes = result.files.first.bytes;
        _fileName = result.files.first.name;
        _error = null;
      });
    }
  }

  Future<void> _handleUpload() async {
    if (_fileBytes == null) return;

    setState(() {
      _isUploading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      await apiService.uploadJd(_fileBytes!, _fileName!);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Upload Successful!'), backgroundColor: Colors.green),
        );
        setState(() {
          _fileBytes = null;
          _fileName = null;
        });
      }
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _isUploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Upload Job Description")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            GestureDetector(
              onTap: _pickFile,
              child: Container(
                width: double.infinity,
                height: 200,
                decoration: BoxDecoration(
                  color: Colors.indigo.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.indigo.withOpacity(0.2), width: 2),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.cloud_upload_outlined, size: 64, color: Colors.indigo),
                    const SizedBox(height: 16),
                    Text(_fileName ?? "Tap to select JD (PDF)", 
                      style: const TextStyle(fontWeight: FontWeight.w600, color: Colors.indigo)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            if (_error != null) 
              Text(_error!, style: const TextStyle(color: Colors.red), textAlign: TextAlign.center),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: (_fileBytes == null || _isUploading) ? null : _handleUpload,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isUploading 
                  ? const CircularProgressIndicator(color: Colors.white) 
                  : const Text("Confirm Upload", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}