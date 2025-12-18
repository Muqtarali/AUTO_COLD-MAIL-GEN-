import 'dart:convert';
import 'dart:typed_data'; // Required for Uint8List
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart'; // Required for MediaType

class ApiService {
  // Use '10.0.2.2' for Android Emulator or your local IP for physical devices
  static const String baseUrl = 'http://localhost:8000';

  /// Basic health check to verify backend connectivity
  Future<Map<String, dynamic>> health() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      throw Exception(
        'Failed to connect to backend: Status ${response.statusCode}',
      );
    } catch (e) {
      throw Exception('Backend connection error: $e');
    }
  }

  /// Universal Upload Method
  /// Uses bytes to avoid "dart:io" (_Namespace) errors on Web
  Future<Map<String, dynamic>> _uploadFile(
    Uint8List fileBytes,
    String fileName,
    String endpoint,
  ) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/$endpoint'),
      );

      // Explicitly setting the MediaType 'application/pdf' fixes the 400 Parse Error
      // by helping the backend library identify the file structure correctly.
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: fileName,
          contentType: MediaType('application', 'pdf'),
        ),
      );

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(responseBody);
      } else {
        // Displays exact server error (e.g., "Expected metadata to be a non-empty dict")
        throw Exception(
          'Server returned ${response.statusCode}: $responseBody',
        );
      }
    } catch (e) {
      throw Exception('Upload error: $e');
    }
  }

  /// Uploads a Resume and returns parsed data/ID
  Future<Map<String, dynamic>> uploadResume(Uint8List bytes, String name) =>
      _uploadFile(bytes, name, 'upload/resume');

  /// Uploads a Job Description and returns parsed data/ID
  Future<Map<String, dynamic>> uploadJd(Uint8List bytes, String name) =>
      _uploadFile(bytes, name, 'upload/jd');

  /// Fetches the list of all uploaded resumes
  Future<Map<String, dynamic>> listResumes() async {
    final response = await http.get(Uri.parse('$baseUrl/list/resumes'));
    return response.statusCode == 200
        ? jsonDecode(response.body)
        : throw Exception('Failed to list resumes');
  }

  /// Fetches the list of all uploaded JDs
  Future<Map<String, dynamic>> listJds() async {
    final response = await http.get(Uri.parse('$baseUrl/list/jds'));
    return response.statusCode == 200
        ? jsonDecode(response.body)
        : throw Exception('Failed to list JDs');
  }

  /// Triggers AI to generate a cold email based on IDs
  Future<Map<String, dynamic>> generateEmail(
    String resumeId,
    String jdId,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/generate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'resume_id': resumeId, 'jd_id': jdId}),
    );
    return response.statusCode == 200
        ? jsonDecode(response.body)
        : throw Exception('Generation failed: ${response.body}');
  }

  /// Sends the generated email via SMTP
  Future<Map<String, dynamic>> sendEmail({
    required String to,
    required String subject,
    required String body,
    String? from,
    String? password,
    bool autoReplyEnabled = false,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/send'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'to': to,
        'subject': subject,
        'body': body,
        if (from != null) 'from': from,
        if (password != null) 'password': password,
        'auto_reply_enabled': autoReplyEnabled,
      }),
    );
    return response.statusCode == 200
        ? jsonDecode(response.body)
        : throw Exception('Email failed to send');
  }

  /// Lists all conversations with auto-reply enabled
  Future<List<dynamic>> listConversations() async {
    final response = await http.get(Uri.parse('$baseUrl/conversations'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      // Handle both wrapped and unwrapped responses
      if (data is Map && data.containsKey('conversations')) {
        final conversations = data['conversations'];
        return conversations is List ? conversations : [];
      } else if (data is List) {
        return data;
      }
      return [];
    }
    throw Exception('Failed to list conversations');
  }

  /// Gets detailed conversation thread by ID
  Future<Map<String, dynamic>> getConversation(String conversationId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/conversations/$conversationId'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['conversation'] ?? {};
    }
    throw Exception('Failed to get conversation');
  }

  /// Toggles auto-reply for a specific conversation
  Future<Map<String, dynamic>> toggleAutoReply(
    String conversationId,
    bool enabled,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/conversations/$conversationId/toggle'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'enabled': enabled}),
    );
    return response.statusCode == 200
        ? jsonDecode(response.body)
        : throw Exception('Failed to toggle auto-reply');
  }

  /// Fetches current usage statistics
  Future<Map<String, dynamic>> getStats() async {
    final response = await http.get(Uri.parse('$baseUrl/stats'));
    return response.statusCode == 200
        ? jsonDecode(response.body)
        : throw Exception('Stats failed');
  }
}
