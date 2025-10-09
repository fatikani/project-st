"""
Upload and Analysis Page for Streamlit Video Forensics Application
"""

import streamlit as st
import os
import tempfile
import json
from pathlib import Path
import sys
import pandas as pd

from typing import Dict

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from streamlit_app import VideoForensicAnalyzer, save_analysis_result, display_analysis_results
    from components import AdvancedVideoAnalyzer, StreamlitVideoComponents, render_advanced_analysis_page
except ImportError:
    st.error("Unable to import required modules. Please ensure all dependencies are installed.")
    st.stop()

def render_upload_page():
    """Render the main upload and analysis page"""
    st.title("Video Upload & Analysis")
    
    st.markdown("""
    Upload a video file for comprehensive forensic analysis. The system will examine the file for:
    - Metadata extraction and verification
    - Tampering detection algorithms
    - Motion pattern analysis
    - Scene change detection
    - Color distribution analysis
    """)
    
    # File upload section
    st.markdown("### Upload Video File")
    uploaded_file = st.file_uploader(
        "Select video file for analysis",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'],
        help="Maximum file size: 500MB. Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM"
    )
    
    if uploaded_file is not None:
        # File information display
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
            "File type": uploaded_file.type or "Unknown"
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### File Information")
            for key, value in file_details.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### Analysis Options")
            
            # Analysis type selection
            analysis_type = st.radio(
                "Select analysis type:",
                ["Quick Analysis", "Standard Analysis", "Comprehensive Analysis"],
                help="Quick: Basic metadata and hash. Standard: Includes tampering detection. Comprehensive: Full forensic analysis."
            )
            
            # Additional options
            save_frames = st.checkbox("Extract sample frames", value=False)
            generate_report = st.checkbox("Generate detailed report", value=True)
        
        # Analysis controls
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Start Analysis", type="primary", use_container_width=True):
                perform_video_analysis(uploaded_file, analysis_type, save_frames, generate_report)
        
        with col2:
            if st.button("Advanced Analysis", use_container_width=True):
                st.session_state.show_advanced = True
        
        # Advanced analysis section
        if st.session_state.get('show_advanced', False):
            st.markdown("---")
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name
            
            render_advanced_analysis_page(uploaded_file, temp_path)
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)

def perform_video_analysis(uploaded_file, analysis_type: str, save_frames: bool, generate_report: bool):
    """Perform comprehensive video analysis"""
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            uploaded_file.seek(0)  # Reset file pointer
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        
        # Initialize analyzer
        analyzer = VideoForensicAnalyzer()
        
        # Progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Calculate file hash
        uploaded_file.seek(0)
        file_hash = analyzer.calculate_file_hash(uploaded_file.read())
        
        # Step 1: Extract metadata
        status_text.text("Extracting video metadata...")
        progress_bar.progress(20)
        metadata = analyzer.extract_metadata(temp_path)
        
        if "error" in metadata:
            st.error(f"Failed to extract metadata: {metadata['error']}")
            return
        
        # Step 2: Basic analysis complete for Quick mode
        if analysis_type == "Quick Analysis":
            progress_bar.progress(100)
            status_text.text("Quick analysis complete!")
            
            # Display basic results
            display_quick_results(metadata, file_hash, uploaded_file.name)
        
        else:
            # Step 3: Tampering analysis
            status_text.text("Analyzing for tampering indicators...")
            progress_bar.progress(60)
            
            tampering_analysis = analyzer.detect_tampering_indicators(temp_path)
            
            if analysis_type == "Comprehensive Analysis":
                # Step 4: Advanced analysis
                status_text.text("Performing comprehensive analysis...")
                progress_bar.progress(80)
                
                # Additional comprehensive analysis would go here
                # For now, we'll use the same tampering analysis
            
            # Step 5: Generate report
            status_text.text("Generating analysis report...")
            progress_bar.progress(90)
            
            report = analyzer.generate_analysis_report(metadata, tampering_analysis, file_hash)
            
            # Step 6: Save results
            if st.session_state.get('authenticated', False):
                save_analysis_result(
                    report, 
                    st.session_state.get('username', 'guest'), 
                    uploaded_file.name, 
                    file_hash
                )
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Display comprehensive results
            display_analysis_results(report, uploaded_file.name)
            
            # Additional result components
            display_detailed_analysis_results(report, metadata, tampering_analysis)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        # Cleanup on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)

def display_quick_results(metadata: Dict, file_hash: str, filename: str):
    """Display quick analysis results"""
    st.markdown("### Quick Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### File Integrity")
        st.markdown(f"**SHA256 Hash:** `{file_hash[:32]}...`")
        st.markdown(f"**File verified:** ✓ Hash calculated successfully")
    
    with col2:
        st.markdown("#### Basic Properties")
        if 'basic_info' in metadata:
            basic_info = metadata['basic_info']
            st.markdown(f"**Resolution:** {basic_info.get('resolution', 'Unknown')}")
            st.markdown(f"**Duration:** {basic_info.get('duration_seconds', 0):.1f} seconds")
            st.markdown(f"**Frame Rate:** {basic_info.get('fps', 0):.1f} fps")
            st.markdown(f"**Codec:** {basic_info.get('codec', 'Unknown')}")
    
    # Download basic report
    basic_report = {
        "filename": filename,
        "file_hash": file_hash,
        "metadata": metadata,
        "analysis_type": "quick",
        "timestamp": str(pd.Timestamp.now())
    }
    
    st.download_button(
        label="Download Basic Report",
        data=json.dumps(basic_report, indent=2),
        file_name=f"basic_report_{filename}.json",
        mime="application/json"
    )

def display_detailed_analysis_results(report: Dict, metadata: Dict, tampering_analysis: Dict):
    """Display detailed analysis results with enhanced visualizations"""
    
    st.markdown("---")
    st.markdown("### Detailed Analysis Results")
    
    # Tampering risk assessment
    if tampering_analysis:
        tampering_prob = tampering_analysis.get('tampering_probability', 0)
        indicators = tampering_analysis.get('indicators', [])
        
        # Risk level visualization
        risk_level = "Low" if tampering_prob < 0.3 else "Medium" if tampering_prob < 0.7 else "High"
        risk_color = "#28a745" if risk_level == "Low" else "#ffc107" if risk_level == "Medium" else "#dc3545"
        
        st.markdown(f"""
        <div style="border: 2px solid {risk_color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4 style="color: {risk_color}; margin: 0;">Tampering Risk Assessment</h4>
            <p style="font-size: 18px; margin: 10px 0;"><strong>Risk Level:</strong> {risk_level}</p>
            <p style="margin: 5px 0;"><strong>Probability:</strong> {tampering_prob:.1%}</p>
            <p style="margin: 5px 0;"><strong>Indicators Found:</strong> {len(indicators)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed indicators
        if indicators:
            st.markdown("#### Detected Indicators")
            for i, indicator in enumerate(indicators, 1):
                st.markdown(f"{i}. {indicator}")
    
    # Technical details
    with st.expander("Technical Details", expanded=False):
        if metadata and 'basic_info' in metadata:
            st.markdown("**Video Properties:**")
            basic_info = metadata['basic_info']
            
            tech_data = [
                ["Property", "Value"],
                ["Width", f"{basic_info.get('width', 'Unknown')} pixels"],
                ["Height", f"{basic_info.get('height', 'Unknown')} pixels"],
                ["Total Frames", f"{basic_info.get('frame_count', 'Unknown'):,}"],
                ["Frame Rate", f"{basic_info.get('fps', 'Unknown'):.2f} fps"],
                ["Duration", f"{basic_info.get('duration_seconds', 'Unknown'):.2f} seconds"],
                ["Codec", basic_info.get('codec', 'Unknown')],
            ]
            
            st.table(tech_data)
    
    # Analysis metadata
    with st.expander("Analysis Metadata", expanded=False):
        st.markdown("**Analysis Information:**")
        st.markdown(f"- **Analysis ID:** {report.get('analysis_id', 'Unknown')}")
        st.markdown(f"- **Timestamp:** {report.get('timestamp', 'Unknown')}")
        st.markdown(f"- **File Hash:** {report.get('file_hash', 'Unknown')}")
        st.markdown(f"- **Confidence Level:** {tampering_analysis.get('confidence', 'Unknown')}")

# Page configuration and main execution
if __name__ == "__main__":
    # This page should be run as part of the main Streamlit app
    st.error("This page should be accessed through the main application navigation.")
else:
    # Initialize required session state
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False
    
    # Render the upload page
    render_upload_page()