import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class SearchMatchScreen extends StatefulWidget {
  const SearchMatchScreen({super.key});

  @override
  State<SearchMatchScreen> createState() => _SearchMatchScreenState();
}

class _SearchMatchScreenState extends State<SearchMatchScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  List<dynamic> _resumeResults = [];
  List<dynamic> _jdResults = [];
  bool _isSearching = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _searchResumes(String query) async {
    if (query.isEmpty) {
      setState(() {
        _resumeResults = [];
        _error = null;
      });
      return;
    }

    setState(() {
      _isSearching = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final results = await apiService.listResumes();

      final filtered =
          (results['items'] as List?)?.where((resume) {
            final name = (resume['name'] ?? '').toString().toLowerCase();
            final query_ = query.toLowerCase();
            return name.contains(query_);
          }).toList() ??
          [];

      if (mounted) {
        setState(() {
          _resumeResults = filtered;
          _isSearching = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Search failed: $e';
          _isSearching = false;
        });
      }
    }
  }

  Future<void> _searchJds(String query) async {
    if (query.isEmpty) {
      setState(() {
        _jdResults = [];
        _error = null;
      });
      return;
    }

    setState(() {
      _isSearching = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final results = await apiService.listJds();

      final filtered =
          (results['items'] as List?)?.where((jd) {
            final role = (jd['role'] ?? '').toString().toLowerCase();
            final company = (jd['company'] ?? '').toString().toLowerCase();
            final query_ = query.toLowerCase();
            return role.contains(query_) || company.contains(query_);
          }).toList() ??
          [];

      if (mounted) {
        setState(() {
          _jdResults = filtered;
          _isSearching = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Search failed: $e';
          _isSearching = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Search & Match'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Find Resume', icon: Icon(Icons.description)),
            Tab(text: 'Find JD', icon: Icon(Icons.work)),
          ],
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: _tabController.index == 0
                    ? 'Search by name, email, skills...'
                    : 'Search by role, company...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          setState(() {
                            _resumeResults = [];
                            _jdResults = [];
                          });
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              onChanged: (value) {
                setState(() {});
                if (_tabController.index == 0) {
                  _searchResumes(value);
                } else {
                  _searchJds(value);
                }
              },
            ),
          ),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.red),
                  borderRadius: BorderRadius.circular(8),
                ),
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
            ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [_buildResumeResults(), _buildJdResults()],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResumeResults() {
    if (_isSearching) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_searchController.text.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text('Start typing to search resumes'),
          ],
        ),
      );
    }

    if (_resumeResults.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.description_outlined,
              size: 64,
              color: Colors.grey.shade300,
            ),
            const SizedBox(height: 16),
            const Text('No resumes found'),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: _resumeResults.length,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        final resume = _resumeResults[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: const Icon(Icons.person, color: Color(0xFF6366F1)),
            title: Text(resume['name'] ?? 'Resume'),
            subtitle: Text(resume['metadata']?['email'] ?? 'No email'),
            trailing: Chip(
              label: Text(resume['id'].toString().substring(0, 8)),
              backgroundColor: Colors.blue.shade100,
            ),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Resume ID: ${resume['id']}'),
                  duration: const Duration(seconds: 2),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Widget _buildJdResults() {
    if (_isSearching) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_searchController.text.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text('Start typing to search job descriptions'),
          ],
        ),
      );
    }

    if (_jdResults.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.work_outline, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            const Text('No job descriptions found'),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: _jdResults.length,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        final jd = _jdResults[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: const Icon(Icons.business, color: Color(0xFF8B5CF6)),
            title: Text(jd['role'] ?? 'Job Description'),
            subtitle: Text(jd['company'] ?? 'No company'),
            trailing: Chip(
              label: Text(jd['id'].toString().substring(0, 8)),
              backgroundColor: Colors.purple.shade100,
            ),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('JD ID: ${jd['id']}'),
                  duration: const Duration(seconds: 2),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
