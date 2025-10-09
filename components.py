"""
Enhanced Video Forensic Analysis Components for Streamlit
Modular components for advanced video analysis functionality
"""

import cv2
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional
import hashlib
import tempfile
import os
from pathlib import Path
import json

class AdvancedVideoAnalyzer:
    """Advanced video analysis capabilities"""
    
    def __init__(self):
        self.frame_cache = {}
        self.analysis_cache = {}
    
    def extract_frames_sample(self, video_path: str, num_frames: int = 10) -> List[np.ndarray]:
        """Extract sample frames from video for analysis"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            return []
        
        frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
        frames = []
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        cap.release()
        return frames
    
    def analyze_motion_patterns(self, video_path: str) -> Dict:
        """Analyze motion patterns in video"""
        cap = cv2.VideoCapture(video_path)
        
        # Motion analysis parameters
        motion_data = []
        frame_count = 0
        prev_gray = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is not None:
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_gray, gray, 
                    cv2.goodFeaturesToTrack(prev_gray, maxCorners=100, qualityLevel=0.3, minDistance=7),
                    None
                )
                
                if flow[0] is not None:
                    motion_magnitude = np.mean(np.sqrt(np.sum(flow[0]**2, axis=2)))
                    motion_data.append({
                        'frame': frame_count,
                        'motion_magnitude': motion_magnitude
                    })
            
            prev_gray = gray
            frame_count += 1
            
            # Limit analysis for performance
            if frame_count > 500:
                break
        
        cap.release()
        
        return {
            'motion_data': motion_data,
            'avg_motion': np.mean([d['motion_magnitude'] for d in motion_data]) if motion_data else 0,
            'motion_variance': np.var([d['motion_magnitude'] for d in motion_data]) if motion_data else 0
        }
    
    def detect_scene_changes(self, video_path: str) -> Dict:
        """Detect scene changes and cuts"""
        cap = cv2.VideoCapture(video_path)
        
        scene_changes = []
        prev_hist = None
        frame_count = 0
        threshold = 0.7  # Scene change threshold
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Calculate histogram
            hist = cv2.calcHist([frame], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            if prev_hist is not None:
                # Compare histograms
                correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                
                if correlation < threshold:
                    scene_changes.append({
                        'frame': frame_count,
                        'timestamp': frame_count / cap.get(cv2.CAP_PROP_FPS),
                        'correlation': correlation
                    })
            
            prev_hist = hist
            frame_count += 1
            
            # Limit analysis
            if frame_count > 1000:
                break
        
        cap.release()
        
        return {
            'scene_changes': scene_changes,
            'total_scenes': len(scene_changes) + 1,
            'avg_scene_length': frame_count / (len(scene_changes) + 1) if scene_changes else frame_count
        }
    
    def analyze_color_distribution(self, frames: List[np.ndarray]) -> Dict:
        """Analyze color distribution across frames"""
        color_stats = {
            'mean_rgb': [],
            'std_rgb': [],
            'dominant_colors': []
        }
        
        for frame in frames:
            # RGB statistics
            mean_color = np.mean(frame, axis=(0, 1))
            std_color = np.std(frame, axis=(0, 1))
            
            color_stats['mean_rgb'].append(mean_color)
            color_stats['std_rgb'].append(std_color)
            
            # Dominant color (simplified)
            pixels = frame.reshape(-1, 3)
            dominant = np.mean(pixels, axis=0)
            color_stats['dominant_colors'].append(dominant)
        
        return {
            'avg_brightness': np.mean([np.mean(color) for color in color_stats['mean_rgb']]),
            'color_variance': np.mean([np.mean(std) for std in color_stats['std_rgb']]),
            'color_consistency': np.std([np.mean(color) for color in color_stats['mean_rgb']])
        }

class StreamlitVideoComponents:
    """Streamlit-specific video display and interaction components"""
    
    @staticmethod
    def display_video_info_cards(metadata: Dict):
        """Display video information in card format"""
        if 'basic_info' not in metadata:
            st.error("Metadata not available")
            return
        
        basic_info = metadata['basic_info']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Resolution", basic_info.get('resolution', 'Unknown'))
        
        with col2:
            duration = basic_info.get('duration_seconds', 0)
            duration_str = f"{int(duration//60)}:{int(duration%60):02d}"
            st.metric("Duration", duration_str)
        
        with col3:
            st.metric("Frame Rate", f"{basic_info.get('fps', 0):.1f} fps")
        
        with col4:
            st.metric("Total Frames", f"{basic_info.get('frame_count', 0):,}")
    
    @staticmethod
    def display_motion_analysis_chart(motion_data: List[Dict]):
        """Display motion analysis as interactive chart"""
        if not motion_data:
            st.warning("No motion data available")
            return
        
        df = pd.DataFrame(motion_data)
        
        fig = px.line(
            df, 
            x='frame', 
            y='motion_magnitude',
            title='Motion Analysis Over Time',
            labels={'frame': 'Frame Number', 'motion_magnitude': 'Motion Magnitude'}
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Frame Number",
            yaxis_title="Motion Magnitude"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_scene_changes_timeline(scene_changes: List[Dict]):
        """Display scene changes as timeline"""
        if not scene_changes:
            st.info("No scene changes detected")
            return
        
        df = pd.DataFrame(scene_changes)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=[1] * len(df),
            mode='markers+text',
            marker=dict(size=12, color='red'),
            text=[f"Scene {i+1}" for i in range(len(df))],
            textposition="top center",
            name="Scene Changes"
        ))
        
        fig.update_layout(
            title="Scene Changes Timeline",
            xaxis_title="Time (seconds)",
            yaxis=dict(showticklabels=False, range=[0.5, 1.5]),
            height=200,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_tampering_indicators(indicators: List[str], probability: float):
        """Display tampering analysis results"""
        st.markdown("#### Tampering Analysis")
        
        # Risk level indicator
        if probability < 0.3:
            risk_color = "green"
            risk_level = "Low Risk"
        elif probability < 0.7:
            risk_color = "orange"
            risk_level = "Medium Risk"
        else:
            risk_color = "red"
            risk_level = "High Risk"
        
        st.markdown(f"""
        <div style="padding: 1rem; border-left: 4px solid {risk_color}; background-color: rgba(255,255,255,0.1);">
            <strong>Risk Level:</strong> {risk_level} ({probability:.1%} probability)
        </div>
        """, unsafe_allow_html=True)
        
        # Indicators
        if indicators:
            st.markdown("**Detected Indicators:**")
            for indicator in indicators:
                st.markdown(f"• {indicator}")
        else:
            st.success("No tampering indicators detected")
    
    @staticmethod
    def display_analysis_summary_table(report: Dict):
        """Display comprehensive analysis summary"""
        summary_data = []
        
        # Basic metadata
        if 'metadata' in report and 'basic_info' in report['metadata']:
            basic_info = report['metadata']['basic_info']
            summary_data.extend([
                {"Category": "Video Properties", "Item": "Resolution", "Value": basic_info.get('resolution', 'Unknown')},
                {"Category": "Video Properties", "Item": "Duration", "Value": f"{basic_info.get('duration_seconds', 0):.1f}s"},
                {"Category": "Video Properties", "Item": "Frame Rate", "Value": f"{basic_info.get('fps', 0):.1f} fps"},
                {"Category": "Video Properties", "Item": "Codec", "Value": basic_info.get('codec', 'Unknown')},
            ])
        
        # File properties
        if 'file_hash' in report:
            summary_data.append({
                "Category": "File Integrity", 
                "Item": "SHA256 Hash", 
                "Value": report['file_hash']
            })
        
        # Analysis results
        if 'tampering_analysis' in report:
            tampering = report['tampering_analysis']
            summary_data.extend([
                {"Category": "Forensic Analysis", "Item": "Tampering Probability", "Value": f"{tampering.get('tampering_probability', 0):.1%}"},
                {"Category": "Forensic Analysis", "Item": "Confidence Level", "Value": tampering.get('confidence', 'Unknown')},
                {"Category": "Forensic Analysis", "Item": "Indicators Found", "Value": str(len(tampering.get('indicators', [])))},
            ])
        
        # Summary
        if 'summary' in report:
            summary = report['summary']
            summary_data.extend([
                {"Category": "Overall Assessment", "Item": "Status", "Value": summary.get('overall_status', 'Unknown')},
                {"Category": "Overall Assessment", "Item": "Recommendations", "Value": str(len(summary.get('recommendations', [])))},
            ])
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

class VideoForensicReporting:
    """Enhanced reporting capabilities for video forensic analysis"""
    
    @staticmethod
    def generate_executive_summary(report: Dict) -> str:
        """Generate executive summary of analysis"""
        summary_parts = []
        
        # File information
        if 'metadata' in report and 'basic_info' in report['metadata']:
            basic_info = report['metadata']['basic_info']
            summary_parts.append(
                f"Video Analysis Summary: {basic_info.get('resolution', 'Unknown')} resolution, "
                f"{basic_info.get('duration_seconds', 0):.1f} seconds duration, "
                f"{basic_info.get('fps', 0):.1f} fps frame rate."
            )
        
        # Tampering assessment
        if 'tampering_analysis' in report:
            tampering = report['tampering_analysis']
            prob = tampering.get('tampering_probability', 0)
            indicators_count = len(tampering.get('indicators', []))
            
            if prob < 0.3:
                summary_parts.append(
                    f"Forensic Assessment: Low tampering risk ({prob:.1%} probability). "
                    f"Analysis detected {indicators_count} potential indicators."
                )
            elif prob < 0.7:
                summary_parts.append(
                    f"Forensic Assessment: Medium tampering risk ({prob:.1%} probability). "
                    f"Analysis detected {indicators_count} indicators requiring attention."
                )
            else:
                summary_parts.append(
                    f"Forensic Assessment: High tampering risk ({prob:.1%} probability). "
                    f"Analysis detected {indicators_count} significant indicators."
                )
        
        # Recommendations
        if 'summary' in report and 'recommendations' in report['summary']:
            recommendations = report['summary']['recommendations']
            if recommendations:
                summary_parts.append(f"Recommendations: {len(recommendations)} action items identified.")
        
        return " ".join(summary_parts)
    
    @staticmethod
    def export_detailed_report(report: Dict, filename: str) -> str:
        """Export detailed analysis report"""
        report_content = {
            "report_metadata": {
                "generated_at": report.get('timestamp', ''),
                "analysis_id": report.get('analysis_id', ''),
                "file_hash": report.get('file_hash', '')
            },
            "executive_summary": VideoForensicReporting.generate_executive_summary(report),
            "detailed_analysis": report,
            "conclusions": report.get('summary', {}),
            "technical_details": {
                "metadata": report.get('metadata', {}),
                "tampering_analysis": report.get('tampering_analysis', {})
            }
        }
        
        return json.dumps(report_content, indent=2)

def render_advanced_analysis_page(uploaded_file, video_path: str):
    """Render advanced analysis interface"""
    st.markdown("### Advanced Video Analysis")
    
    # Initialize analyzer
    analyzer = AdvancedVideoAnalyzer()
    components = StreamlitVideoComponents()
    
    # Analysis options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Analysis Options**")
        motion_analysis = st.checkbox("Motion Pattern Analysis", value=True)
        scene_analysis = st.checkbox("Scene Change Detection", value=True)
        color_analysis = st.checkbox("Color Distribution Analysis", value=True)
    
    with col2:
        st.markdown("**Processing Options**")
        frame_limit = st.slider("Frame Analysis Limit", 100, 1000, 500)
        detail_level = st.selectbox("Detail Level", ["Basic", "Standard", "Comprehensive"])
    
    if st.button("Run Advanced Analysis", type="primary"):
        with st.spinner("Performing advanced analysis..."):
            results = {}
            
            # Motion analysis
            if motion_analysis:
                st.info("Analyzing motion patterns...")
                motion_results = analyzer.analyze_motion_patterns(video_path)
                results['motion'] = motion_results
                
                if motion_results['motion_data']:
                    components.display_motion_analysis_chart(motion_results['motion_data'])
            
            # Scene analysis
            if scene_analysis:
                st.info("Detecting scene changes...")
                scene_results = analyzer.detect_scene_changes(video_path)
                results['scenes'] = scene_results
                
                if scene_results['scene_changes']:
                    components.display_scene_changes_timeline(scene_results['scene_changes'])
                
                st.metric("Total Scenes Detected", scene_results['total_scenes'])
            
            # Color analysis
            if color_analysis:
                st.info("Analyzing color distribution...")
                frames = analyzer.extract_frames_sample(video_path, 20)
                if frames:
                    color_results = analyzer.analyze_color_distribution(frames)
                    results['color'] = color_results
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Avg Brightness", f"{color_results['avg_brightness']:.1f}")
                    with col2:
                        st.metric("Color Variance", f"{color_results['color_variance']:.1f}")
                    with col3:
                        st.metric("Color Consistency", f"{color_results['color_consistency']:.1f}")
            
            st.success("Advanced analysis complete!")
            
            # Store results in session state
            st.session_state.advanced_results = results
    
    # Display stored results if available
    if hasattr(st.session_state, 'advanced_results') and st.session_state.advanced_results:
        st.markdown("### Previous Advanced Analysis Results")
        
        results = st.session_state.advanced_results
        
        # Export option
        if st.button("Export Advanced Results"):
            export_data = json.dumps(results, indent=2)
            st.download_button(
                label="Download Advanced Analysis",
                data=export_data,
                file_name=f"advanced_analysis_{uploaded_file.name}.json",
                mime="application/json"
            )