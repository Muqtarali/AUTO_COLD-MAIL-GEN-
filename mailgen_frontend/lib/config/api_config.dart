/// Configuration for API connection
/// This file centralizes all API configuration for easy management

class ApiConfig {
  // Backend server configuration
  static const String apiBaseUrl = 'http://localhost:8000';
  
  // For production, change to your actual server URL
  // static const String apiBaseUrl = 'https://api.mailgen.hiresense.com';
  
  // Request timeouts (in seconds)
  static const int connectTimeout = 30;
  static const int receiveTimeout = 30;
  
  // File upload settings
  static const int maxFileSize = 16 * 1024 * 1024; // 16 MB
  static const List<String> allowedFileTypes = ['pdf'];
  
  // API endpoints
  static const String healthCheck = '/health';
  static const String pingEndpoint = '/ping';
  
  // Resume endpoints
  static const String uploadResume = '/upload/resume';
  static const String listResumes = '/list/resumes';
  static const String storeResume = '/store/resume';
  
  // Job Description endpoints
  static const String uploadJd = '/upload/jd';
  static const String listJds = '/list/jds';
  static const String storeJd = '/store/jd';
  
  // Email generation endpoints
  static const String generateEmail = '/generate';
  static const String sendEmail = '/send';
  
  // Statistics endpoint
  static const String statsEndpoint = '/stats';
  
  // Helper method to get full URL
  static String getFullUrl(String endpoint) {
    return '$apiBaseUrl$endpoint';
  }
}
