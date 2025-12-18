import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _resumes = [];
  List<dynamic> _jds = [];
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final resumesData = await apiService.listResumes();
      final jdsData = await apiService.listJds();

      if (mounted) {
        setState(() {
          _resumes = resumesData['items'] ?? [];
          _jds = jdsData['items'] ?? [];
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
        title: const Text('Dashboard'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Resumes', icon: Icon(Icons.description)),
            Tab(text: 'Job Descriptions', icon: Icon(Icons.work)),
          ],
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: TabBarView(
          controller: _tabController,
          children: [_buildResumesList(), _buildJdsList()],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _loadData,
        tooltip: 'Refresh',
        child: const Icon(Icons.refresh),
      ),
    );
  }

  Widget _buildResumesList() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text('Error: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _loadData, child: const Text('Retry')),
          ],
        ),
      );
    }

    if (_resumes.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.description_outlined,
              size: 48,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            const Text('No resumes uploaded yet'),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to upload resume
              },
              icon: const Icon(Icons.upload),
              label: const Text('Upload Resume'),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: _resumes.length,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        final resume = _resumes[index];
        return _buildDocumentCard(
          id: resume['id'],
          name: resume['name'] ?? 'Resume',
          metadata: resume['metadata'] ?? {},
          onDelete: () => _deleteResume(resume['id']),
        );
      },
    );
  }

  Widget _buildJdsList() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text('Error: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _loadData, child: const Text('Retry')),
          ],
        ),
      );
    }

    if (_jds.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.work_outline, size: 48, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('No job descriptions uploaded yet'),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to upload JD
              },
              icon: const Icon(Icons.upload),
              label: const Text('Upload JD'),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: _jds.length,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        final jd = _jds[index];
        return _buildDocumentCard(
          id: jd['id'],
          name: jd['role'] ?? 'Job Description',
          company: jd['company'],
          metadata: jd['metadata'] ?? {},
          onDelete: () => _deleteJd(jd['id']),
        );
      },
    );
  }

  Widget _buildDocumentCard({
    required String id,
    required String name,
    String? company,
    required Map<String, dynamic> metadata,
    required VoidCallback onDelete,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(
          company != null ? Icons.description : Icons.person,
          color: const Color(0xFF6366F1),
        ),
        title: Text(name),
        subtitle: company != null ? Text(company) : null,
        trailing: PopupMenuButton(
          itemBuilder: (context) => [
            PopupMenuItem(child: const Text('Delete'), onTap: onDelete),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteResume(String id) async {
    // Implement delete functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Resume deleted (not implemented yet)')),
    );
  }

  Future<void> _deleteJd(String id) async {
    // Implement delete functionality
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('JD deleted (not implemented yet)')),
    );
  }
}
