"""
Digital Forensic Video Analysis Platform - Streamlit Application
Minimalist and responsive web interface for video forensic analysis
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import hashlib
import json
import datetime
import os
import sqlite3
import uuid
from pathlib import Path
import time
import tempfile
import threading
from typing import Dict, List, Tuple, Optional

# Page configuration
st.set_page_config(
    page_title="Digital Forensic Video Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalist responsive design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #374151;
        margin-bottom: 1rem;
    }
    
    .info-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .status-success {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .status-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .status-error {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .compact-metric {
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .sub-header {
            font-size: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Database functions
@st.cache_resource
def init_database():
    """Initialize SQLite database for user management and analysis storage"""
    db_path = os.path.join(os.path.dirname(__file__), 'forensic_db.sqlite')
    if not os.path.exists(db_path):
        open(db_path, 'a').close()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'analyst',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            analysis_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user
    admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role) 
        VALUES (?, ?, ?)
    ''', ('admin', admin_hash, 'admin'))
    
    conn.commit()
    return conn

class VideoForensicAnalyzer:
    """Core video analysis functionality"""
    
    def __init__(self):
        self.supported_formats = ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm']
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def extract_metadata(self, video_path: str) -> Dict:
        """Extract comprehensive video metadata"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {"error": "Cannot open video file"}
            
            # Basic video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Codec information
            fourcc = cap.get(cv2.CAP_PROP_FOURCC)
            codec = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
            
            cap.release()
            
            metadata = {
                "basic_info": {
                    "width": width,
                    "height": height,
                    "frame_count": frame_count,
                    "fps": fps,
                    "duration_seconds": duration,
                    "codec": codec,
                    "resolution": f"{width}x{height}"
                },
                "file_info": {
                    "size_bytes": os.path.getsize(video_path),
                    "format": os.path.splitext(video_path)[1].lower()
                }
            }
            
            return metadata
            
        except Exception as e:
            return {"error": f"Metadata extraction failed: {str(e)}"}
    
    def detect_tampering_indicators(self, video_path: str) -> Dict:
        """Analyze video for potential tampering indicators"""
        try:
            cap = cv2.VideoCapture(video_path)
            tampering_score = 0.0
            indicators = []
            
            # Sample frames for analysis
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(100, frame_count)
            frame_indices = np.linspace(0, frame_count-1, sample_frames, dtype=int)
            
            prev_frame = None
            motion_values = []
            
            for i, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(gray, prev_frame)
                    motion = np.mean(diff)
                    motion_values.append(motion)
                
                prev_frame = gray
                
                # Update progress
                if i % 20 == 0:
                    progress = i / len(frame_indices)
                    st.session_state.analysis_progress = progress
            
            cap.release()
            
            # Analyze motion patterns
            if motion_values:
                motion_std = np.std(motion_values)
                motion_mean = np.mean(motion_values)
                
                # Check for unusual motion patterns
                if motion_std > 50:
                    tampering_score += 0.3
                    indicators.append("High motion variation detected")
                
                # Check for abrupt changes
                motion_diff = np.diff(motion_values)
                if np.max(np.abs(motion_diff)) > 100:
                    tampering_score += 0.4
                    indicators.append("Abrupt motion changes detected")
            
            # Additional checks would go here (frequency analysis, etc.)
            
            result = {
                "tampering_probability": min(tampering_score, 1.0),
                "indicators": indicators,
                "confidence": "Medium" if tampering_score > 0.5 else "Low",
                "analysis_complete": True
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Tampering analysis failed: {str(e)}"}
    
    def generate_analysis_report(self, metadata: Dict, tampering_analysis: Dict, file_hash: str) -> Dict:
        """Generate comprehensive analysis report"""
        report = {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "file_hash": file_hash,
            "metadata": metadata,
            "tampering_analysis": tampering_analysis,
            "summary": {
                "overall_status": "Clean" if tampering_analysis.get("tampering_probability", 0) < 0.3 else "Suspicious",
                "confidence_level": tampering_analysis.get("confidence", "Unknown"),
                "recommendations": []
            }
        }
        
        # Generate recommendations
        if tampering_analysis.get("tampering_probability", 0) > 0.5:
            report["summary"]["recommendations"].append("Further manual inspection recommended")
            report["summary"]["recommendations"].append("Consider additional verification methods")
        else:
            report["summary"]["recommendations"].append("File appears to be authentic")
        
        return report

# Authentication functions
def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""
    conn = init_database()
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        'SELECT username, role FROM users WHERE username = ? AND password_hash = ?',
        (username, password_hash)
    )
    
    result = cursor.fetchone()
    if result:
        st.session_state.authenticated = True
        st.session_state.username = result[0]
        st.session_state.user_role = result[1]
        return True
    return False

def save_analysis_result(analysis_data: Dict, username: str, filename: str, file_hash: str):
    """Save analysis results to database"""
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analysis_results (analysis_id, username, filename, file_hash, analysis_data)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        analysis_data['analysis_id'],
        username,
        filename,
        file_hash,
        json.dumps(analysis_data)
    ))
    
    conn.commit()

def load_user_analyses(username: str) -> List[Dict]:
    """Load user's previous analyses"""
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT analysis_id, filename, file_hash, analysis_data, created_at
        FROM analysis_results 
        WHERE username = ? 
        ORDER BY created_at DESC
    ''', (username,))
    
    results = []
    for row in cursor.fetchall():
        try:
            analysis_data = json.loads(row[3])
            results.append({
                'analysis_id': row[0],
                'filename': row[1],
                'file_hash': row[2],
                'analysis_data': analysis_data,
                'created_at': row[4]
            })
        except json.JSONDecodeError:
            continue
    
    return results

# Main application functions
def render_login_page():
    """Render login interface"""
    st.markdown('<div class="main-header">Digital Forensic Video Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("### Authentication Required")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username and password:
                    if authenticate_user(username, password):
                        st.success("Authentication successful")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.info("Default credentials: admin / admin123")

def render_sidebar():
    """Render application sidebar"""
    with st.sidebar:
        st.markdown(f"**User:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.get('user_role', 'analyst').title()}")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate",
            ["Upload & Analysis", "Previous Results", "System Status"],
            key="navigation"
        )
        
        return page

def render_upload_analysis_page():
    """Render video upload and analysis interface"""
    st.markdown('<div class="main-header">Video Forensic Analysis</div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### Upload Video File")
    uploaded_file = st.file_uploader(
        "Select video file for analysis",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'],
        help="Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM"
    )
    
    if uploaded_file is not None:
        # Display file information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**File Information**")
            st.markdown(f"Name: {uploaded_file.name}")
            st.markdown(f"Size: {uploaded_file.size / (1024*1024):.2f} MB")
            st.markdown(f"Type: {uploaded_file.type}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis options
        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**Analysis Options**")
            full_analysis = st.checkbox("Full forensic analysis", value=True)
            metadata_only = st.checkbox("Metadata extraction only", value=False)
            quick_scan = st.checkbox("Quick tampering scan", value=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("**Actions**")
            if st.button("Start Analysis", type="primary", use_container_width=True):
                perform_analysis(uploaded_file, full_analysis, metadata_only, quick_scan)
            st.markdown('</div>', unsafe_allow_html=True)

def perform_analysis(uploaded_file, full_analysis: bool, metadata_only: bool, quick_scan: bool):
    """Perform video analysis"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        
        # Initialize analyzer
        analyzer = VideoForensicAnalyzer()
        
        # Calculate file hash
        uploaded_file.seek(0)
        file_hash = analyzer.calculate_file_hash(uploaded_file.read())
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Extract metadata
        status_text.text("Extracting metadata...")
        progress_bar.progress(20)
        metadata = analyzer.extract_metadata(temp_path)
        
        # Perform tampering analysis if requested
        tampering_analysis = {}
        if full_analysis or quick_scan:
            status_text.text("Analyzing for tampering indicators...")
            progress_bar.progress(50)
            tampering_analysis = analyzer.detect_tampering_indicators(temp_path)
        
        # Generate report
        status_text.text("Generating analysis report...")
        progress_bar.progress(90)
        
        report = analyzer.generate_analysis_report(metadata, tampering_analysis, file_hash)
        
        # Save results
        save_analysis_result(report, st.session_state.username, uploaded_file.name, file_hash)
        
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        # Display results
        display_analysis_results(report, uploaded_file.name)
        
        # Cleanup
        os.unlink(temp_path)
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")

def display_analysis_results(report: Dict, filename: str):
    """Display analysis results"""
    st.markdown("---")
    st.markdown("### Analysis Results")
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Overall Status", report['summary']['overall_status'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Confidence", report['summary']['confidence_level'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        tampering_prob = report.get('tampering_analysis', {}).get('tampering_probability', 0)
        st.metric("Tampering Risk", f"{tampering_prob:.1%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("File Hash", report['file_hash'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Video Metadata")
        if 'metadata' in report and 'basic_info' in report['metadata']:
            metadata_df = pd.DataFrame([
                {"Property": k.replace('_', ' ').title(), "Value": v}
                for k, v in report['metadata']['basic_info'].items()
            ])
            st.dataframe(metadata_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Analysis Findings")
        if 'tampering_analysis' in report and 'indicators' in report['tampering_analysis']:
            indicators = report['tampering_analysis']['indicators']
            if indicators:
                for indicator in indicators:
                    st.markdown(f"• {indicator}")
            else:
                st.success("No tampering indicators detected")
    
    # Complete Analysis Details
    with st.expander("🔍 Complete Analysis Details", expanded=False):
        st.markdown("### Full Analysis Report")
        
        # File Information Section
        st.markdown("#### 📄 File Information")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Filename:** `{filename}`")
            st.markdown(f"**Analysis ID:** `{report.get('analysis_id', 'N/A')}`")
            st.markdown(f"**Analysis Date:** `{report.get('timestamp', 'N/A')}`")
        with col2:
            st.markdown(f"**File Hash (SHA256):** `{report.get('file_hash', 'N/A')}`")
            st.markdown(f"**File Size:** {report.get('metadata', {}).get('basic_info', {}).get('file_size', 'N/A')} bytes")
            st.markdown(f"**Format:** {report.get('metadata', {}).get('basic_info', {}).get('format', 'N/A')}")
        
        # Technical Metadata
        if 'metadata' in report and 'basic_info' in report['metadata']:
            st.markdown("#### 🔧 Technical Metadata")
            metadata_info = report['metadata']['basic_info']
            tech_details = []
            for key, value in metadata_info.items():
                tech_details.append({
                    "Property": key.replace('_', ' ').title(),
                    "Value": str(value)
                })
            st.dataframe(pd.DataFrame(tech_details), use_container_width=True, hide_index=True)
        
        # Tampering Analysis
        if 'tampering_analysis' in report:
            st.markdown("#### 🛡️ Tampering Analysis")
            tampering = report['tampering_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Tampering Probability:** {tampering.get('tampering_probability', 0):.1%}")
                st.markdown(f"**Confidence Level:** {tampering.get('confidence', 'N/A')}")
                st.markdown(f"**Risk Assessment:** {tampering.get('risk_level', 'N/A')}")
            
            with col2:
                indicators = tampering.get('indicators', [])
                st.markdown(f"**Indicators Found:** {len(indicators)}")
                if indicators:
                    st.markdown("**Detailed Indicators:**")
                    for i, indicator in enumerate(indicators, 1):
                        st.markdown(f"{i}. {indicator}")
                else:
                    st.success("✓ No tampering indicators detected")
        
        # Complete JSON Report
        st.markdown("#### 📋 Complete JSON Report")
        st.json(report)
    
    # Recommendations
    st.markdown("#### Recommendations")
    for rec in report['summary'].get('recommendations', []):
        st.info(rec)
    
    # Download report
    if st.button("Download Report", type="secondary"):
        report_json = json.dumps(report, indent=2)
        st.download_button(
            label="Download JSON Report",
            data=report_json,
            file_name=f"forensic_report_{report['analysis_id']}.json",
            mime="application/json"
        )

def render_previous_results_page():
    """Render previous analysis results"""
    st.markdown('<div class="main-header">Previous Analysis Results</div>', unsafe_allow_html=True)
    
    analyses = load_user_analyses(st.session_state.username)
    
    if not analyses:
        st.info("No previous analyses found")
        return
    
    # Results table
    st.markdown("### Your Analysis History")
    
    for analysis in analyses:
        with st.expander(f"{analysis['filename']} - {analysis['created_at']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**File Information**")
                st.markdown(f"Filename: {analysis['filename']}")
                st.markdown(f"Hash: `{analysis['file_hash']}`")
                st.markdown(f"Analysis ID: `{analysis['analysis_id']}`")
            
            with col2:
                st.markdown("**Results Summary**")
                data = analysis['analysis_data']
                st.markdown(f"Status: {data['summary']['overall_status']}")
                st.markdown(f"Confidence: {data['summary']['confidence_level']}")
                
                if 'tampering_analysis' in data:
                    prob = data['tampering_analysis'].get('tampering_probability', 0)
                    st.markdown(f"Tampering Risk: {prob:.1%}")
            
            # Download option
            report_json = json.dumps(analysis['analysis_data'], indent=2)
            st.download_button(
                label="Download Report",
                data=report_json,
                file_name=f"report_{analysis['analysis_id']}.json",
                mime="application/json",
                key=f"download_{analysis['analysis_id']}"
            )

def render_system_status_page():
    """Render system status and information"""
    st.markdown('<div class="main-header">System Status</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### System Information")
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("**Application Status:** Online")
        st.markdown("**Database:** Connected")
        st.markdown("**Video Processing:** Available")
        st.markdown("**AI Analysis:** Available")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # User statistics
        conn = init_database()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE username = ?', (st.session_state.username,))
        user_analyses = cursor.fetchone()[0]
        
        st.markdown("### Your Statistics")
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown(f"**Total Analyses:** {user_analyses}")
        st.markdown(f"**Account Type:** {st.session_state.get('user_role', 'analyst').title()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Supported Formats")
        formats_df = pd.DataFrame([
            {"Format": "MP4", "Support": "Full"},
            {"Format": "AVI", "Support": "Full"},
            {"Format": "MOV", "Support": "Full"},
            {"Format": "MKV", "Support": "Full"},
            {"Format": "WMV", "Support": "Basic"},
            {"Format": "FLV", "Support": "Basic"},
            {"Format": "WEBM", "Support": "Full"}
        ])
        st.dataframe(formats_df, use_container_width=True, hide_index=True)

# Main application
def main():
    """Main application entry point"""
    # Initialize database
    init_database()
    
    if not st.session_state.authenticated:
        render_login_page()
    else:
        # Render sidebar and get selected page
        selected_page = render_sidebar()
        
        # Render selected page
        if selected_page == "Upload & Analysis":
            render_upload_analysis_page()
        elif selected_page == "Previous Results":
            render_previous_results_page()
        elif selected_page == "System Status":
            render_system_status_page()

if __name__ == "__main__":
    main()