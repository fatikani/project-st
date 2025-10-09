"""
System Status Page for Streamlit Video Forensics Application
"""

import streamlit as st
import sqlite3
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import psutil
import time

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from streamlit_app import init_database
except ImportError:
    st.error("Unable to import required modules. Please ensure all dependencies are installed.")
    st.stop()

def render_system_status_page():
    """Render the system status and monitoring page"""
    st.title("System Status & Monitoring")
    
    # Real-time system metrics
    display_system_metrics()
    
    # Database status
    display_database_status()
    
    # Application status
    display_application_status()
    
    # User activity
    if st.session_state.get('authenticated', False):
        display_user_activity()
    
    # System information
    display_system_information()

def display_system_metrics():
    """Display real-time system performance metrics"""
    st.markdown("### System Performance")
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="CPU Usage",
            value=f"{cpu_percent:.1f}%",
            delta=None
        )
    
    with col2:
        memory_percent = memory.percent
        st.metric(
            label="Memory Usage",
            value=f"{memory_percent:.1f}%",
            delta=None
        )
    
    with col3:
        disk_percent = (disk.used / disk.total) * 100
        st.metric(
            label="Disk Usage",
            value=f"{disk_percent:.1f}%",
            delta=None
        )
    
    with col4:
        memory_gb = memory.available / (1024**3)
        st.metric(
            label="Available Memory",
            value=f"{memory_gb:.1f} GB",
            delta=None
        )
    
    # Progress bars for visual representation
    st.markdown("#### Resource Utilization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**CPU Usage**")
        st.progress(cpu_percent / 100)
        
        st.markdown("**Memory Usage**")
        st.progress(memory_percent / 100)
    
    with col2:
        st.markdown("**Disk Usage**")
        st.progress(disk_percent / 100)
        
        # Network information if available
        try:
            network = psutil.net_io_counters()
            st.markdown(f"**Network:** {network.bytes_sent / (1024**2):.1f} MB sent, {network.bytes_recv / (1024**2):.1f} MB received")
        except:
            st.markdown("**Network:** Information unavailable")

def display_database_status():
    """Display database status and statistics"""
    st.markdown("### Database Status")
    
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        # Check database connectivity
        cursor.execute("SELECT 1")
        db_status = "Connected"
        db_status_color = "green"
        
        # Get table statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        analysis_count = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM analysis_results 
            WHERE created_at > datetime('now', '-24 hours')
        """)
        recent_analyses = cursor.fetchone()[0]
        
        conn.close()
        
    except Exception as e:
        db_status = f"Error: {str(e)}"
        db_status_color = "red"
        user_count = analysis_count = recent_analyses = 0
    
    # Display database metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="padding: 1rem; border-left: 4px solid {db_status_color}; background-color: rgba(255,255,255,0.1);">
            <strong>Database Status:</strong> {db_status}
        </div>
        """, unsafe_allow_html=True)
        
        # Database file information
        db_path = "forensic_db.sqlite"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024**2)  # MB
            db_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
            
            st.markdown("**Database File Information:**")
            st.markdown(f"• Size: {db_size:.2f} MB")
            st.markdown(f"• Last Modified: {db_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        st.markdown("**Database Statistics:**")
        
        stats_data = [
            ["Metric", "Count"],
            ["Total Users", f"{user_count:,}"],
            ["Total Analyses", f"{analysis_count:,}"],
            ["Recent Analyses (24h)", f"{recent_analyses:,}"]
        ]
        
        st.table(stats_data)

def display_application_status():
    """Display application status and health checks"""
    st.markdown("### Application Status")
    
    # Health check results
    health_checks = perform_health_checks()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Service Status:**")
        
        for service, status in health_checks.items():
            status_icon = "✅" if status["status"] == "OK" else "❌"
            st.markdown(f"{status_icon} **{service}:** {status['message']}")
    
    with col2:
        st.markdown("**Application Information:**")
        
        app_info = [
            ["Component", "Status"],
            ["Streamlit Version", st.__version__],
            ["Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"],
            ["Platform", sys.platform],
            ["Working Directory", str(Path.cwd())],
        ]
        
        st.table(app_info)
    
    # Feature availability
    st.markdown("#### Feature Availability")
    
    features = check_feature_availability()
    
    feature_cols = st.columns(3)
    
    for i, (feature, available) in enumerate(features.items()):
        with feature_cols[i % 3]:
            status_icon = "✅" if available else "❌"
            st.markdown(f"{status_icon} {feature}")

def perform_health_checks():
    """Perform various health checks"""
    checks = {}
    
    # Database connectivity
    try:
        conn = init_database()
        conn.execute("SELECT 1")
        conn.close()
        checks["Database"] = {"status": "OK", "message": "Connected"}
    except Exception as e:
        checks["Database"] = {"status": "ERROR", "message": f"Connection failed: {str(e)[:50]}"}
    
    # File system access
    try:
        test_file = "test_write_access.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        checks["File System"] = {"status": "OK", "message": "Read/Write access available"}
    except Exception as e:
        checks["File System"] = {"status": "ERROR", "message": f"Access error: {str(e)[:50]}"}
    
    # Memory availability
    memory = psutil.virtual_memory()
    if memory.available > 500 * 1024 * 1024:  # 500MB
        checks["Memory"] = {"status": "OK", "message": f"{memory.available / (1024**3):.1f} GB available"}
    else:
        checks["Memory"] = {"status": "WARNING", "message": "Low memory available"}
    
    return checks

def check_feature_availability():
    """Check availability of optional features"""
    features = {}
    
    # OpenCV
    try:
        import cv2
        features["Video Processing (OpenCV)"] = True
    except ImportError:
        features["Video Processing (OpenCV)"] = False
    
    # TensorFlow
    try:
        import tensorflow as tf
        features["AI Analysis (TensorFlow)"] = True
    except ImportError:
        features["AI Analysis (TensorFlow)"] = False
    
    # Plotly
    try:
        import plotly
        features["Advanced Charts (Plotly)"] = True
    except ImportError:
        features["Advanced Charts (Plotly)"] = False
    
    # Pandas
    try:
        import pandas as pd
        features["Data Processing (Pandas)"] = True
    except ImportError:
        features["Data Processing (Pandas)"] = False
    
    # NumPy
    try:
        import numpy as np
        features["Numerical Computing (NumPy)"] = True
    except ImportError:
        features["Numerical Computing (NumPy)"] = False
    
    # PIL/Pillow
    try:
        from PIL import Image
        features["Image Processing (Pillow)"] = True
    except ImportError:
        features["Image Processing (Pillow)"] = False
    
    return features

def display_user_activity():
    """Display user activity and session information"""
    st.markdown("### User Activity")
    
    username = st.session_state.get('username', 'Unknown')
    user_role = st.session_state.get('user_role', 'analyst')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Session:**")
        st.markdown(f"• **Username:** {username}")
        st.markdown(f"• **Role:** {user_role.title()}")
        st.markdown(f"• **Session Active:** Yes")
        
        # Session duration (approximate)
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        
        session_duration = datetime.now() - st.session_state.session_start
        st.markdown(f"• **Session Duration:** {str(session_duration).split('.')[0]}")
    
    with col2:
        # User statistics from database
        try:
            conn = init_database()
            cursor = conn.cursor()
            
            # User's analysis count
            cursor.execute("SELECT COUNT(*) FROM analysis_results WHERE username = ?", (username,))
            user_analyses = cursor.fetchone()[0]
            
            # User's recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM analysis_results 
                WHERE username = ? AND created_at > datetime('now', '-7 days')
            """, (username,))
            recent_user_analyses = cursor.fetchone()[0]
            
            conn.close()
            
            st.markdown("**Activity Statistics:**")
            st.markdown(f"• **Total Analyses:** {user_analyses:,}")
            st.markdown(f"• **This Week:** {recent_user_analyses:,}")
            st.markdown(f"• **Average per Week:** {user_analyses / 4:.1f}" if user_analyses > 0 else "• **Average per Week:** 0")
            
        except Exception as e:
            st.markdown("**Activity Statistics:** Error loading data")

def display_system_information():
    """Display detailed system information"""
    st.markdown("### System Information")
    
    with st.expander("Detailed System Information", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Python Environment:**")
            
            python_info = [
                ["Property", "Value"],
                ["Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"],
                ["Python Executable", sys.executable],
                ["Platform", sys.platform],
                ["Architecture", str(sys.maxsize > 2**32 and "64-bit" or "32-bit")],
            ]
            
            st.table(python_info)
        
        with col2:
            st.markdown("**Hardware Information:**")
            
            try:
                # CPU information
                cpu_count = psutil.cpu_count()
                cpu_count_logical = psutil.cpu_count(logical=True)
                
                # Memory information
                memory = psutil.virtual_memory()
                memory_total_gb = memory.total / (1024**3)
                
                hardware_info = [
                    ["Component", "Details"],
                    ["CPU Cores", f"{cpu_count} physical, {cpu_count_logical} logical"],
                    ["Total Memory", f"{memory_total_gb:.1f} GB"],
                    ["Available Memory", f"{memory.available / (1024**3):.1f} GB"],
                    ["Boot Time", datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')],
                ]
                
                st.table(hardware_info)
                
            except Exception as e:
                st.markdown(f"Hardware information unavailable: {str(e)}")
    
    # Supported formats
    with st.expander("Supported Video Formats", expanded=False):
        formats_data = [
            ["Format", "Extension", "Support Level", "Analysis Features"],
            ["MP4", ".mp4", "Full", "All features"],
            ["AVI", ".avi", "Full", "All features"],
            ["MOV", ".mov", "Full", "All features"],
            ["MKV", ".mkv", "Full", "All features"],
            ["WMV", ".wmv", "Basic", "Limited metadata"],
            ["FLV", ".flv", "Basic", "Limited metadata"],
            ["WEBM", ".webm", "Full", "All features"],
        ]
        
        st.table(formats_data)
    
    # Refresh button
    if st.button("Refresh Status", type="primary"):
        st.rerun()

# Page configuration and main execution
if __name__ == "__main__":
    # This page should be run as part of the main Streamlit app
    st.error("This page should be accessed through the main application navigation.")
else:
    # Render the system status page
    render_system_status_page()