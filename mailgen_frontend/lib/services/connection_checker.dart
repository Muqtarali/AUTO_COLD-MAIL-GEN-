import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class ConnectionChecker {
  static Future<ConnectionStatus> checkConnection(BuildContext context) async {
    try {
      final apiService = context.read<ApiService>();
      final response = await apiService.health();

      if (response['status'] == 'ok') {
        return ConnectionStatus(
          isConnected: true,
          message: 'Backend Connected Successfully',
          statusCode: 200,
          timestamp: DateTime.now(),
        );
      } else {
        return ConnectionStatus(
          isConnected: false,
          message: 'Backend returned unexpected response',
          statusCode: 500,
          timestamp: DateTime.now(),
        );
      }
    } catch (e) {
      return ConnectionStatus(
        isConnected: false,
        message: 'Failed to connect: $e',
        statusCode: 0,
        timestamp: DateTime.now(),
      );
    }
  }

  static Future<Map<String, dynamic>> testAllEndpoints(
    BuildContext context,
  ) async {
    final apiService = context.read<ApiService>();
    final results = <String, dynamic>{};

    // Test health endpoint
    try {
      await apiService.health();
      results['health'] = {
        'status': 'success',
        'message': 'Health check passed',
      };
    } catch (e) {
      results['health'] = {'status': 'failed', 'message': e.toString()};
    }

    // Test list resumes endpoint
    try {
      await apiService.listResumes();
      results['list_resumes'] = {
        'status': 'success',
        'message': 'List resumes passed',
      };
    } catch (e) {
      results['list_resumes'] = {'status': 'failed', 'message': e.toString()};
    }

    // Test list JDs endpoint
    try {
      await apiService.listJds();
      results['list_jds'] = {'status': 'success', 'message': 'List JDs passed'};
    } catch (e) {
      results['list_jds'] = {'status': 'failed', 'message': e.toString()};
    }

    // Test stats endpoint
    try {
      await apiService.getStats();
      results['stats'] = {
        'status': 'success',
        'message': 'Stats endpoint passed',
      };
    } catch (e) {
      results['stats'] = {'status': 'failed', 'message': e.toString()};
    }

    return results;
  }
}

class ConnectionStatus {
  final bool isConnected;
  final String message;
  final int statusCode;
  final DateTime timestamp;

  ConnectionStatus({
    required this.isConnected,
    required this.message,
    required this.statusCode,
    required this.timestamp,
  });

  String get connectionIcon => isConnected ? '✓' : '✗';
  Color get connectionColor => isConnected ? Colors.green : Colors.red;

  @override
  String toString() =>
      'ConnectionStatus(connected: $isConnected, message: $message, code: $statusCode)';
}

class ConnectionTestScreen extends StatefulWidget {
  const ConnectionTestScreen({super.key});

  @override
  State<ConnectionTestScreen> createState() => _ConnectionTestScreenState();
}

class _ConnectionTestScreenState extends State<ConnectionTestScreen> {
  ConnectionStatus? _status;
  Map<String, dynamic>? _endpointResults;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _checkConnection();
  }

  Future<void> _checkConnection() async {
    setState(() => _isLoading = true);

    final status = await ConnectionChecker.checkConnection(context);
    final results = await ConnectionChecker.testAllEndpoints(context);

    if (mounted) {
      setState(() {
        _status = status;
        _endpointResults = results;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Connection Test'), centerTitle: true),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Connection Status Card
                  if (_status != null)
                    Card(
                      color: _status!.isConnected
                          ? Colors.green.shade50
                          : Colors.red.shade50,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Container(
                              width: 60,
                              height: 60,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: _status!.connectionColor,
                              ),
                              child: Center(
                                child: Text(
                                  _status!.connectionIcon,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 32,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _status!.isConnected
                                        ? 'Connected'
                                        : 'Disconnected',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: _status!.connectionColor,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    _status!.message,
                                    style: const TextStyle(
                                      fontSize: 13,
                                      color: Colors.grey,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Status Code: ${_status!.statusCode}',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Time: ${_status!.timestamp.toLocal()}',
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  const SizedBox(height: 24),

                  // Endpoint Test Results
                  Text(
                    'Endpoint Tests',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (_endpointResults != null)
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _endpointResults!.length,
                      itemBuilder: (context, index) {
                        final endpoint = _endpointResults!.keys.toList()[index];
                        final result = _endpointResults![endpoint];
                        final isSuccess = result['status'] == 'success';

                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          color: isSuccess
                              ? Colors.green.shade50
                              : Colors.red.shade50,
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              children: [
                                Icon(
                                  isSuccess ? Icons.check_circle : Icons.cancel,
                                  color: isSuccess ? Colors.green : Colors.red,
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        endpoint
                                            .replaceAll('_', ' ')
                                            .toUpperCase(),
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        result['message'],
                                        style: TextStyle(
                                          fontSize: 11,
                                          color: Colors.grey.shade700,
                                        ),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  const SizedBox(height: 24),

                  // Refresh Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _checkConnection,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Refresh Tests'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
