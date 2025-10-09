"""
Previous Results Page for Streamlit Video Forensics Application
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from streamlit_app import load_user_analyses, init_database
    from components import StreamlitVideoComponents, VideoForensicReporting
except ImportError:
    st.error("Unable to import required modules. Please ensure all dependencies are installed.")
    st.stop()

def render_results_page():
    """Render the previous results page"""
    st.title("Previous Analysis Results")
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.warning("Please log in to view your analysis history.")
        return
    
    username = st.session_state.get('username', '')
    
    # Load user analyses
    analyses = load_user_analyses(username)
    
    if not analyses:
        st.info("No previous analyses found. Upload and analyze a video to see results here.")
        return
    
    # Summary statistics
    display_analysis_statistics(analyses)
    
    # Filters and sorting
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox(
            "Sort by:",
            ["Most Recent", "Oldest First", "Filename A-Z", "Filename Z-A", "Risk Level"]
        )
    
    with col2:
        filter_status = st.selectbox(
            "Filter by status:",
            ["All", "Clean", "Suspicious", "High Risk"]
        )
    
    with col3:
        items_per_page = st.selectbox(
            "Items per page:",
            [5, 10, 20, 50],
            index=1
        )
    
    # Apply filters and sorting
    filtered_analyses = apply_filters_sorting(analyses, sort_by, filter_status)
    
    # Pagination
    total_items = len(filtered_analyses)
    total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    if total_pages > 1:
        page = st.selectbox(f"Page (1-{total_pages}):", range(1, total_pages + 1))
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_analyses = filtered_analyses[start_idx:end_idx]
    else:
        paginated_analyses = filtered_analyses
    
    # Display results
    st.markdown(f"### Analysis Results ({len(filtered_analyses)} total)")
    
    for analysis in paginated_analyses:
        display_analysis_card(analysis)
    
    # Bulk operations
    if analyses:
        st.markdown("---")
        display_bulk_operations(analyses)

def display_analysis_statistics(analyses: list):
    """Display summary statistics of analyses"""
    st.markdown("### Summary Statistics")
    
    # Calculate statistics
    total_analyses = len(analyses)
    clean_count = sum(1 for a in analyses if a['analysis_data'].get('summary', {}).get('overall_status') == 'Clean')
    suspicious_count = total_analyses - clean_count
    
    # Risk distribution
    risk_levels = {'Low': 0, 'Medium': 0, 'High': 0}
    for analysis in analyses:
        tampering_prob = analysis['analysis_data'].get('tampering_analysis', {}).get('tampering_probability', 0)
        if tampering_prob < 0.3:
            risk_levels['Low'] += 1
        elif tampering_prob < 0.7:
            risk_levels['Medium'] += 1
        else:
            risk_levels['High'] += 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", total_analyses)
    
    with col2:
        st.metric("Clean Files", clean_count)
    
    with col3:
        st.metric("Suspicious Files", suspicious_count)
    
    with col4:
        clean_percentage = (clean_count / total_analyses * 100) if total_analyses > 0 else 0
        st.metric("Clean Rate", f"{clean_percentage:.1f}%")
    
    # Risk level distribution
    if any(risk_levels.values()):
        st.markdown("#### Risk Level Distribution")
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        
        with risk_col1:
            st.metric("Low Risk", risk_levels['Low'], delta_color="normal")
        
        with risk_col2:
            st.metric("Medium Risk", risk_levels['Medium'], delta_color="off")
        
        with risk_col3:
            st.metric("High Risk", risk_levels['High'], delta_color="inverse")

def apply_filters_sorting(analyses: list, sort_by: str, filter_status: str) -> list:
    """Apply filters and sorting to analyses list"""
    filtered = analyses[:]
    
    # Apply status filter
    if filter_status != "All":
        if filter_status == "Clean":
            filtered = [a for a in filtered if a['analysis_data'].get('summary', {}).get('overall_status') == 'Clean']
        elif filter_status == "Suspicious":
            filtered = [a for a in filtered if a['analysis_data'].get('summary', {}).get('overall_status') != 'Clean']
        elif filter_status == "High Risk":
            filtered = [a for a in filtered if a['analysis_data'].get('tampering_analysis', {}).get('tampering_probability', 0) >= 0.7]
    
    # Apply sorting
    if sort_by == "Most Recent":
        filtered.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Oldest First":
        filtered.sort(key=lambda x: x['created_at'])
    elif sort_by == "Filename A-Z":
        filtered.sort(key=lambda x: x['filename'].lower())
    elif sort_by == "Filename Z-A":
        filtered.sort(key=lambda x: x['filename'].lower(), reverse=True)
    elif sort_by == "Risk Level":
        filtered.sort(key=lambda x: x['analysis_data'].get('tampering_analysis', {}).get('tampering_probability', 0), reverse=True)
    
    return filtered

def display_analysis_card(analysis: dict):
    """Display individual analysis result card"""
    data = analysis['analysis_data']
    
    # Determine status color
    overall_status = data.get('summary', {}).get('overall_status', 'Unknown')
    tampering_prob = data.get('tampering_analysis', {}).get('tampering_probability', 0)
    
    if overall_status == 'Clean':
        status_color = "#28a745"
        status_icon = "✓"
    elif tampering_prob >= 0.7:
        status_color = "#dc3545"
        status_icon = "⚠"
    else:
        status_color = "#ffc107"
        status_icon = "⚡"
    
    # Create expandable card
    with st.expander(
        f"{status_icon} {analysis['filename']} - {analysis['created_at'][:19].replace('T', ' ')}",
        expanded=False
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**File Information**")
            st.markdown(f"Filename: `{analysis['filename']}`")
            st.markdown(f"File Hash: `{analysis['file_hash'][:16]}...`")
            st.markdown(f"Analysis ID: `{analysis['analysis_id'][:8]}...`")
            st.markdown(f"Created: {analysis['created_at'][:19].replace('T', ' ')}")
        
        with col2:
            st.markdown("**Analysis Results**")
            st.markdown(f"Status: **{overall_status}**")
            st.markdown(f"Tampering Risk: **{tampering_prob:.1%}**")
            
            confidence = data.get('tampering_analysis', {}).get('confidence', 'Unknown')
            st.markdown(f"Confidence: **{confidence}**")
            
            indicators = data.get('tampering_analysis', {}).get('indicators', [])
            st.markdown(f"Indicators: **{len(indicators)} found**")
        
        # Detailed information
        if indicators:
            st.markdown("**Detected Indicators:**")
            for indicator in indicators:
                st.markdown(f"• {indicator}")
        
        # Metadata summary
        if 'metadata' in data and 'basic_info' in data['metadata']:
            basic_info = data['metadata']['basic_info']
            
            st.markdown("**Video Properties:**")
            prop_col1, prop_col2, prop_col3 = st.columns(3)
            
            with prop_col1:
                st.markdown(f"Resolution: {basic_info.get('resolution', 'Unknown')}")
                st.markdown(f"Duration: {basic_info.get('duration_seconds', 0):.1f}s")
            
            with prop_col2:
                st.markdown(f"Frame Rate: {basic_info.get('fps', 0):.1f} fps")
                st.markdown(f"Frames: {basic_info.get('frame_count', 0):,}")
            
            with prop_col3:
                st.markdown(f"Codec: {basic_info.get('codec', 'Unknown')}")
                file_size = data.get('metadata', {}).get('file_info', {}).get('size_bytes', 0)
                st.markdown(f"Size: {file_size / (1024*1024):.1f} MB" if file_size > 0 else "Size: Unknown")
        
        # Recommendations
        recommendations = data.get('summary', {}).get('recommendations', [])
        if recommendations:
            st.markdown("**Recommendations:**")
            for rec in recommendations:
                st.markdown(f"• {rec}")
        
        # Action buttons
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            # Download report button
            report_json = json.dumps(data, indent=2)
            st.download_button(
                label="Download Report",
                data=report_json,
                file_name=f"report_{analysis['analysis_id']}.json",
                mime="application/json",
                key=f"download_{analysis['analysis_id']}"
            )
        
        with action_col2:
            # Generate executive summary
            if st.button("Executive Summary", key=f"summary_{analysis['analysis_id']}"):
                st.session_state[f"show_summary_{analysis['analysis_id']}"] = True
        
        with action_col3:
            # View detailed analysis
            if st.button("Detailed View", key=f"detailed_{analysis['analysis_id']}"):
                st.session_state[f"show_detailed_{analysis['analysis_id']}"] = True
        
        # Show executive summary if requested
        if st.session_state.get(f"show_summary_{analysis['analysis_id']}", False):
            summary = VideoForensicReporting.generate_executive_summary(data)
            st.markdown("**Executive Summary:**")
            st.info(summary)
        
        # Show detailed view if requested
        if st.session_state.get(f"show_detailed_{analysis['analysis_id']}", False):
            st.markdown("**Detailed Analysis Data:**")
            st.json(data)

def display_bulk_operations(analyses: list):
    """Display bulk operations for multiple analyses"""
    st.markdown("### Bulk Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export All Reports", use_container_width=True):
            export_all_reports(analyses)
    
    with col2:
        if st.button("Generate Summary Report", use_container_width=True):
            generate_summary_report(analyses)
    
    with col3:
        if st.button("Clear All Results", use_container_width=True, type="secondary"):
            st.warning("This feature is not yet implemented for data safety.")

def export_all_reports(analyses: list):
    """Export all analyses as a combined report"""
    combined_report = {
        "export_metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_analyses": len(analyses),
            "username": st.session_state.get('username', 'unknown')
        },
        "analyses": [a['analysis_data'] for a in analyses]
    }
    
    report_json = json.dumps(combined_report, indent=2)
    st.download_button(
        label="Download Combined Report",
        data=report_json,
        file_name=f"combined_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key="export_all"
    )

def generate_summary_report(analyses: list):
    """Generate and display summary report of all analyses"""
    st.markdown("#### Analysis Summary Report")
    
    # Statistics
    total = len(analyses)
    clean = sum(1 for a in analyses if a['analysis_data'].get('summary', {}).get('overall_status') == 'Clean')
    suspicious = total - clean
    
    avg_tampering_prob = sum(
        a['analysis_data'].get('tampering_analysis', {}).get('tampering_probability', 0) 
        for a in analyses
    ) / total if total > 0 else 0
    
    # Summary data
    summary_data = {
        "Total Files Analyzed": total,
        "Clean Files": clean,
        "Suspicious Files": suspicious,
        "Average Tampering Risk": f"{avg_tampering_prob:.1%}",
        "Clean Rate": f"{(clean/total*100):.1f}%" if total > 0 else "0%"
    }
    
    # Display as metrics
    cols = st.columns(len(summary_data))
    for i, (key, value) in enumerate(summary_data.items()):
        with cols[i]:
            st.metric(key, value)
    
    # File list with risk levels
    if analyses:
        st.markdown("#### File Risk Assessment")
        
        file_data = []
        for analysis in analyses:
            data = analysis['analysis_data']
            tampering_prob = data.get('tampering_analysis', {}).get('tampering_probability', 0)
            
            risk_level = "Low" if tampering_prob < 0.3 else "Medium" if tampering_prob < 0.7 else "High"
            
            file_data.append({
                "Filename": analysis['filename'],
                "Status": data.get('summary', {}).get('overall_status', 'Unknown'),
                "Risk Level": risk_level,
                "Tampering Probability": f"{tampering_prob:.1%}",
                "Date": analysis['created_at'][:10]
            })
        
        df = pd.DataFrame(file_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# Page configuration and main execution
if __name__ == "__main__":
    # This page should be run as part of the main Streamlit app
    st.error("This page should be accessed through the main application navigation.")
else:
    # Render the results page
    render_results_page()