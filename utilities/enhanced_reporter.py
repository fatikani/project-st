"""
Enhanced Test Reporting System with Bug Categorization and Analysis
Generates comprehensive reports with AI-powered insights and exploratory testing results
"""

import json
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sqlite3
from jinja2 import Template
import base64
from io import BytesIO
import numpy as np


class EnhancedTestReporter:
    """
    Advanced test reporting system with bug taxonomy, AI analysis, and visual reports
    """
    
    def __init__(self, output_dir="test_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.test_results = []
        self.bug_taxonomy = {
            'Critical': {'color': '#FF0000', 'priority': 1},
            'High': {'color': '#FF6600', 'priority': 2},
            'Medium': {'color': '#FFCC00', 'priority': 3},
            'Low': {'color': '#00FF00', 'priority': 4}
        }
        
    def add_test_result(self, test_name, status, category, severity, duration, 
                       errors=None, screenshots=None, ai_analysis=None):
        """Add a test result to the report"""
        result = {
            'test_name': test_name,
            'status': status,  # PASS, FAIL, SKIP
            'category': category,  # Authentication, Upload, Analysis, etc.
            'severity': severity,  # Critical, High, Medium, Low
            'duration': duration,
            'timestamp': datetime.datetime.now().isoformat(),
            'errors': errors or [],
            'screenshots': screenshots or [],
            'ai_analysis': ai_analysis or {}
        }
        self.test_results.append(result)
    
    def categorize_bugs(self, bugs):
        """Categorize bugs using taxonomy"""
        categorized = {
            'Functional': [],
            'Performance': [],
            'Security': [],
            'UI/UX': [],
            'Compatibility': [],
            'Accessibility': []
        }
        
        for bug in bugs:
            bug_type = bug.get('type', '').lower()
            
            if 'javascript' in bug_type or 'function' in bug_type:
                categorized['Functional'].append(bug)
            elif 'performance' in bug_type or 'load' in bug_type:
                categorized['Performance'].append(bug)
            elif 'security' in bug_type or 'auth' in bug_type:
                categorized['Security'].append(bug)
            elif 'ui' in bug_type or 'layout' in bug_type or 'display' in bug_type:
                categorized['UI/UX'].append(bug)
            elif 'browser' in bug_type or 'compatibility' in bug_type:
                categorized['Compatibility'].append(bug)
            elif 'accessibility' in bug_type or 'alt' in bug_type or 'label' in bug_type:
                categorized['Accessibility'].append(bug)
            else:
                categorized['Functional'].append(bug)  # Default category
        
        return categorized
    
    def generate_visual_charts(self):
        """Generate visual charts for the report"""
        charts = {}
        
        # Test results distribution
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Test Status Distribution
        status_counts = {}
        for result in self.test_results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        ax1.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('Test Results Distribution')
        
        # 2. Severity Distribution
        severity_counts = {}
        for result in self.test_results:
            if result['status'] == 'FAIL':
                severity = result['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts:
            colors = [self.bug_taxonomy[sev]['color'] for sev in severity_counts.keys()]
            ax2.bar(severity_counts.keys(), severity_counts.values(), color=colors)
            ax2.set_title('Failed Tests by Severity')
            ax2.set_ylabel('Number of Tests')
        
        # 3. Category Distribution
        category_counts = {}
        for result in self.test_results:
            category = result['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        ax3.bar(category_counts.keys(), category_counts.values())
        ax3.set_title('Tests by Category')
        ax3.set_ylabel('Number of Tests')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Test Duration Distribution
        durations = [result['duration'] for result in self.test_results if result['duration']]
        if durations:
            ax4.hist(durations, bins=10, alpha=0.7)
            ax4.set_title('Test Duration Distribution')
            ax4.set_xlabel('Duration (seconds)')
            ax4.set_ylabel('Number of Tests')
        
        plt.tight_layout()
        
        # Save chart as base64 for embedding
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        chart_b64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        charts['overview'] = chart_b64
        
        return charts
    
    def analyze_test_patterns(self):
        """Analyze test patterns using AI-like algorithms"""
        analysis = {
            'total_tests': len(self.test_results),
            'pass_rate': 0,
            'most_problematic_category': '',
            'avg_test_duration': 0,
            'risk_areas': [],
            'recommendations': []
        }
        
        if not self.test_results:
            return analysis
        
        # Calculate pass rate
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        analysis['pass_rate'] = (passed_tests / len(self.test_results)) * 100
        
        # Find most problematic category
        category_failures = {}
        for result in self.test_results:
            if result['status'] == 'FAIL':
                category = result['category']
                category_failures[category] = category_failures.get(category, 0) + 1
        
        if category_failures:
            analysis['most_problematic_category'] = max(category_failures, key=category_failures.get)
        
        # Calculate average duration
        durations = [r['duration'] for r in self.test_results if r['duration']]
        if durations:
            analysis['avg_test_duration'] = sum(durations) / len(durations)
        
        # Identify risk areas
        critical_failures = [r for r in self.test_results 
                           if r['status'] == 'FAIL' and r['severity'] == 'Critical']
        high_failures = [r for r in self.test_results 
                        if r['status'] == 'FAIL' and r['severity'] == 'High']
        
        if critical_failures:
            analysis['risk_areas'].append(f"Critical failures in: {', '.join(set(r['category'] for r in critical_failures))}")
        
        if high_failures:
            analysis['risk_areas'].append(f"High severity issues in: {', '.join(set(r['category'] for r in high_failures))}")
        
        # Generate recommendations
        if analysis['pass_rate'] < 80:
            analysis['recommendations'].append("Pass rate is below 80%. Review failed test cases and improve application quality.")
        
        if analysis['avg_test_duration'] > 30:
            analysis['recommendations'].append("Average test duration is high. Consider optimizing test execution or application performance.")
        
        if len(critical_failures) > 0:
            analysis['recommendations'].append("Critical failures detected. These should be fixed immediately before release.")
        
        return analysis
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Forensic Video Analysis - Test Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <style>
        .severity-critical { color: #FF0000; font-weight: bold; }
        .severity-high { color: #FF6600; font-weight: bold; }
        .severity-medium { color: #FFCC00; font-weight: bold; }
        .severity-low { color: #00AA00; }
        .status-pass { color: #28a745; }
        .status-fail { color: #dc3545; }
        .status-skip { color: #6c757d; }
        .chart-container { text-align: center; margin: 20px 0; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .risk-alert { border-left: 4px solid #dc3545; }
        .recommendation-item { border-left: 4px solid #17a2b8; padding-left: 15px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">
                <i class="bi bi-clipboard-data"></i> Test Execution Report
            </span>
            <span class="navbar-text">
                Generated: {{ report_date }}
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Executive Summary -->
        <div class="row mb-4">
            <div class="col-12">
                <h2><i class="bi bi-graph-up"></i> Executive Summary</h2>
                <div class="row">
                    <div class="col-md-3">
                        <div class="card metric-card text-center">
                            <div class="card-body">
                                <h3>{{ analysis.total_tests }}</h3>
                                <p class="mb-0">Total Tests</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card metric-card text-center">
                            <div class="card-body">
                                <h3>{{ "%.1f"|format(analysis.pass_rate) }}%</h3>
                                <p class="mb-0">Pass Rate</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card metric-card text-center">
                            <div class="card-body">
                                <h3>{{ "%.1f"|format(analysis.avg_test_duration) }}s</h3>
                                <p class="mb-0">Avg Duration</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card metric-card text-center">
                            <div class="card-body">
                                <h3>{{ failed_count }}</h3>
                                <p class="mb-0">Failed Tests</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Visual Analytics -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="bi bi-bar-chart"></i> Test Analytics</h3>
                <div class="card">
                    <div class="card-body">
                        <div class="chart-container">
                            <img src="data:image/png;base64,{{ charts.overview }}" alt="Test Analytics Charts" class="img-fluid">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Risk Areas -->
        {% if analysis.risk_areas %}
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="bi bi-exclamation-triangle text-danger"></i> Risk Areas</h3>
                {% for risk in analysis.risk_areas %}
                <div class="alert alert-danger risk-alert">
                    <strong>⚠️ High Risk:</strong> {{ risk }}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- Recommendations -->
        {% if analysis.recommendations %}
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="bi bi-lightbulb text-info"></i> Recommendations</h3>
                {% for rec in analysis.recommendations %}
                <div class="recommendation-item">
                    <strong>💡 Recommendation:</strong> {{ rec }}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- Detailed Test Results -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="bi bi-list-check"></i> Detailed Test Results</h3>
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Test Name</th>
                                        <th>Category</th>
                                        <th>Status</th>
                                        <th>Severity</th>
                                        <th>Duration</th>
                                        <th>Timestamp</th>
                                        <th>Details</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for result in test_results %}
                                    <tr>
                                        <td>{{ result.test_name }}</td>
                                        <td>{{ result.category }}</td>
                                        <td>
                                            <span class="status-{{ result.status.lower() }}">
                                                {% if result.status == 'PASS' %}
                                                    <i class="bi bi-check-circle"></i> PASS
                                                {% elif result.status == 'FAIL' %}
                                                    <i class="bi bi-x-circle"></i> FAIL
                                                {% else %}
                                                    <i class="bi bi-dash-circle"></i> SKIP
                                                {% endif %}
                                            </span>
                                        </td>
                                        <td>
                                            <span class="severity-{{ result.severity.lower() }}">
                                                {{ result.severity }}
                                            </span>
                                        </td>
                                        <td>{{ "%.2f"|format(result.duration) }}s</td>
                                        <td>{{ result.timestamp[:19].replace('T', ' ') }}</td>
                                        <td>
                                            {% if result.errors %}
                                                <button class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" data-bs-target="#errorModal{{ loop.index }}">
                                                    View Errors
                                                </button>
                                            {% endif %}
                                            {% if result.ai_analysis %}
                                                <button class="btn btn-sm btn-outline-info" data-bs-toggle="modal" data-bs-target="#aiModal{{ loop.index }}">
                                                    AI Analysis
                                                </button>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bug Taxonomy -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="bi bi-bug"></i> Bug Taxonomy</h3>
                <div class="row">
                    {% for category, bugs in categorized_bugs.items() %}
                    {% if bugs %}
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h5>{{ category }} ({{ bugs|length }})</h5>
                            </div>
                            <div class="card-body">
                                {% for bug in bugs[:5] %}
                                <div class="mb-2">
                                    <span class="badge bg-{{ 'danger' if bug.severity == 'High' else 'warning' if bug.severity == 'Medium' else 'info' }}">
                                        {{ bug.severity }}
                                    </span>
                                    {{ bug.message[:100] }}{% if bug.message|length > 100 %}...{% endif %}
                                </div>
                                {% endfor %}
                                {% if bugs|length > 5 %}
                                <small class="text-muted">... and {{ bugs|length - 5 }} more</small>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- Error Modals -->
    {% for result in test_results %}
    {% if result.errors %}
    <div class="modal fade" id="errorModal{{ loop.index }}" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Error Details: {{ result.test_name }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    {% for error in result.errors %}
                    <div class="alert alert-danger">
                        <strong>Error:</strong> {{ error }}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    {% if result.ai_analysis %}
    <div class="modal fade" id="aiModal{{ loop.index }}" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">AI Analysis: {{ result.test_name }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <pre>{{ result.ai_analysis | tojson(indent=2) }}</pre>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
    {% endfor %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        
        # Generate data for template
        charts = self.generate_visual_charts()
        analysis = self.analyze_test_patterns()
        
        # Get all bugs from test results
        all_bugs = []
        for result in self.test_results:
            if result.get('ai_analysis', {}).get('detailed_issues'):
                all_bugs.extend(result['ai_analysis']['detailed_issues'])
        
        categorized_bugs = self.categorize_bugs(all_bugs)
        failed_count = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        template = Template(template_str)
        html_content = template.render(
            test_results=self.test_results,
            analysis=analysis,
            charts=charts,
            categorized_bugs=categorized_bugs,
            failed_count=failed_count,
            report_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save HTML report
        report_path = self.output_dir / f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def generate_json_report(self):
        """Generate JSON report for programmatic access"""
        report_data = {
            'metadata': {
                'generated_at': datetime.datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'framework_version': '2.0.0'
            },
            'summary': self.analyze_test_patterns(),
            'test_results': self.test_results,
            'bug_taxonomy': self.bug_taxonomy
        }
        
        json_path = self.output_dir / f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(json_path)
    
    def export_to_csv(self):
        """Export test results to CSV for analysis"""
        if not self.test_results:
            return None
        
        df = pd.DataFrame(self.test_results)
        csv_path = self.output_dir / f"test_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False)
        
        return str(csv_path)


# Example usage and integration
def integrate_with_pytest():
    """
    Integration function to use with pytest hooks
    """
    reporter = EnhancedTestReporter()
    
    # This would typically be called from pytest hooks
    # pytest_runtest_logreport, pytest_sessionfinish, etc.
    
    def pytest_runtest_logreport(report):
        """Pytest hook to collect test results"""
        if report.when == "call":
            status = "PASS" if report.outcome == "passed" else "FAIL" if report.outcome == "failed" else "SKIP"
            
            # Extract additional information
            test_name = report.nodeid.split("::")[-1]
            category = extract_category_from_test_name(test_name)
            severity = extract_severity_from_markers(report)
            duration = getattr(report, 'duration', 0)
            
            # Add AI analysis if available
            ai_analysis = getattr(report, 'ai_analysis', {})
            
            reporter.add_test_result(
                test_name=test_name,
                status=status,
                category=category,
                severity=severity,
                duration=duration,
                errors=[str(report.longrepr)] if report.longrepr else [],
                ai_analysis=ai_analysis
            )
    
    def pytest_sessionfinish(session, exitstatus):
        """Generate reports at the end of test session"""
        html_report = reporter.generate_html_report()
        json_report = reporter.generate_json_report()
        csv_report = reporter.export_to_csv()
        
        print(f"Test reports generated:")
        print(f"HTML: {html_report}")
        print(f"JSON: {json_report}")
        print(f"CSV: {csv_report}")
    
    return pytest_runtest_logreport, pytest_sessionfinish


def extract_category_from_test_name(test_name):
    """Extract test category from test name"""
    test_name_lower = test_name.lower()
    
    if 'login' in test_name_lower or 'auth' in test_name_lower:
        return 'Authentication'
    elif 'upload' in test_name_lower:
        return 'Video Upload'
    elif 'analysis' in test_name_lower or 'analyze' in test_name_lower:
        return 'Video Analysis'
    elif 'navigation' in test_name_lower or 'nav' in test_name_lower:
        return 'Navigation'
    elif 'performance' in test_name_lower or 'load' in test_name_lower:
        return 'Performance'
    elif 'security' in test_name_lower:
        return 'Security'
    elif 'ui' in test_name_lower or 'interface' in test_name_lower:
        return 'User Interface'
    elif 'exploratory' in test_name_lower:
        return 'Exploratory'
    else:
        return 'Functional'


def extract_severity_from_markers(report):
    """Extract severity from pytest markers"""
    try:
        for marker in report.keywords:
            if marker.startswith('severity_'):
                return marker.replace('severity_', '').title()
        return 'Medium'  # Default severity
    except:
        return 'Medium'


if __name__ == "__main__":
    # Example usage
    reporter = EnhancedTestReporter()
    
    # Simulate some test results
    reporter.add_test_result(
        test_name="test_login_valid_credentials",
        status="PASS",
        category="Authentication",
        severity="Critical",
        duration=2.5
    )
    
    reporter.add_test_result(
        test_name="test_video_upload_invalid_format",
        status="FAIL",
        category="Video Upload",
        severity="High",
        duration=1.8,
        errors=["Invalid file format error"],
        ai_analysis={
            'detected_issues': [
                {
                    'type': 'Functional Bug',
                    'severity': 'High',
                    'message': 'File validation not working properly'
                }
            ]
        }
    )
    
    # Generate reports
    html_report = reporter.generate_html_report()
    json_report = reporter.generate_json_report()
    csv_report = reporter.export_to_csv()
    
    print(f"Reports generated:")
    print(f"HTML: {html_report}")
    print(f"JSON: {json_report}") 
    print(f"CSV: {csv_report}")