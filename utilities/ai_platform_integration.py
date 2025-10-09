"""
AI Platform Integration for Automated Bug Detection and Analysis
Integrates with various AI services for intelligent test analysis and bug prediction
"""

import numpy as np
import pandas as pd
import json
import requests
import cv2
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow import keras
import joblib
import os
from datetime import datetime
import logging
from pathlib import Path
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import base64


class AIBugPredictor:
    """
    AI-powered bug prediction and analysis system
    """
    
    def __init__(self, model_dir="ai_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logging()
        
        # Load or create models
        self.bug_classifier = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        
        self._load_or_create_models()
    
    def _setup_logging(self):
        """Setup logging for AI operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        try:
            # Try to load existing models
            self.bug_classifier = joblib.load(self.model_dir / "bug_classifier.pkl")
            self.anomaly_detector = joblib.load(self.model_dir / "anomaly_detector.pkl")
            self.scaler = joblib.load(self.model_dir / "scaler.pkl")
            self.logger.info("Loaded existing AI models")
        except FileNotFoundError:
            # Create and train new models
            self._create_and_train_models()
            self.logger.info("Created and trained new AI models")
    
    def _create_and_train_models(self):
        """Create and train AI models with synthetic data"""
        # Generate synthetic training data for bug classification
        training_data = self._generate_synthetic_training_data()
        
        X = training_data.drop(['bug_type', 'is_bug'], axis=1)
        y_classification = training_data['is_bug']
        y_bug_type = training_data['bug_type']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train bug classifier (predicts if something is a bug)
        self.bug_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.bug_classifier.fit(X_scaled, y_classification)
        
        # Train anomaly detector
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.anomaly_detector.fit(X_scaled)
        
        # Save models
        joblib.dump(self.bug_classifier, self.model_dir / "bug_classifier.pkl")
        joblib.dump(self.anomaly_detector, self.model_dir / "anomaly_detector.pkl")
        joblib.dump(self.scaler, self.model_dir / "scaler.pkl")
    
    def _generate_synthetic_training_data(self):
        """Generate synthetic training data for model training"""
        np.random.seed(42)
        n_samples = 5000
        
        data = {
            # Performance metrics
            'response_time': np.random.lognormal(1, 0.5, n_samples),
            'memory_usage': np.random.normal(70, 20, n_samples),
            'cpu_usage': np.random.normal(60, 25, n_samples),
            'error_count': np.random.poisson(2, n_samples),
            
            # UI metrics
            'element_load_time': np.random.lognormal(0.5, 0.3, n_samples),
            'click_response_time': np.random.lognormal(0.2, 0.2, n_samples),
            'page_size_mb': np.random.lognormal(1, 0.4, n_samples),
            
            # Code quality metrics
            'cyclomatic_complexity': np.random.poisson(5, n_samples),
            'code_coverage': np.random.beta(8, 2, n_samples) * 100,
            'duplicate_code_percentage': np.random.beta(2, 8, n_samples) * 30,
            
            # Test metrics
            'test_duration': np.random.lognormal(1.5, 0.6, n_samples),
            'assertion_count': np.random.poisson(3, n_samples),
            'mock_usage': np.random.binomial(1, 0.3, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Create labels based on realistic rules
        bug_conditions = [
            (df['response_time'] > 5) & (df['error_count'] > 5),  # Performance bugs
            (df['memory_usage'] > 90) & (df['cpu_usage'] > 85),   # Resource bugs
            (df['element_load_time'] > 2) & (df['click_response_time'] > 1),  # UI bugs
            (df['cyclomatic_complexity'] > 10) & (df['code_coverage'] < 50),  # Quality bugs
            df['error_count'] > 10,  # Error-prone code
        ]
        
        df['is_bug'] = 0
        for condition in bug_conditions:
            df.loc[condition, 'is_bug'] = 1
        
        # Add some noise
        noise_indices = np.random.choice(len(df), size=int(0.1 * len(df)), replace=False)
        df.loc[noise_indices, 'is_bug'] = 1 - df.loc[noise_indices, 'is_bug']
        
        # Assign bug types
        bug_types = ['performance', 'ui', 'functional', 'security', 'compatibility']
        df['bug_type'] = np.random.choice(bug_types, n_samples)
        
        return df
    
    def extract_features_from_test_result(self, test_result: Dict) -> np.array:
        """Extract features from a test result for AI analysis"""
        features = {
            'response_time': test_result.get('duration', 0),
            'memory_usage': test_result.get('memory_usage', 50),
            'cpu_usage': test_result.get('cpu_usage', 40),
            'error_count': len(test_result.get('errors', [])),
            'element_load_time': test_result.get('element_load_time', 0.5),
            'click_response_time': test_result.get('click_response_time', 0.2),
            'page_size_mb': test_result.get('page_size_mb', 1.0),
            'cyclomatic_complexity': test_result.get('complexity', 3),
            'code_coverage': test_result.get('coverage', 80),
            'duplicate_code_percentage': test_result.get('duplication', 5),
            'test_duration': test_result.get('duration', 0),
            'assertion_count': test_result.get('assertions', 1),
            'mock_usage': 1 if test_result.get('uses_mocks', False) else 0,
        }
        
        return np.array(list(features.values())).reshape(1, -1)
    
    def predict_bug_probability(self, test_result: Dict) -> Dict[str, Any]:
        """Predict the probability that a test result indicates a bug"""
        features = self.extract_features_from_test_result(test_result)
        features_scaled = self.scaler.transform(features)
        
        # Get prediction probability
        bug_probability = self.bug_classifier.predict_proba(features_scaled)[0]
        is_bug_prob = bug_probability[1] if len(bug_probability) > 1 else bug_probability[0]
        
        # Get anomaly score
        anomaly_score = self.anomaly_detector.score_samples(features_scaled)[0]
        is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
        
        return {
            'bug_probability': float(is_bug_prob),
            'anomaly_score': float(anomaly_score),
            'is_anomaly': is_anomaly,
            'confidence': float(max(bug_probability)),
            'prediction': 'BUG' if is_bug_prob > 0.5 else 'NORMAL',
            'risk_level': self._calculate_risk_level(is_bug_prob, anomaly_score)
        }
    
    def _calculate_risk_level(self, bug_prob: float, anomaly_score: float) -> str:
        """Calculate risk level based on predictions"""
        if bug_prob > 0.8 or anomaly_score < -0.5:
            return 'CRITICAL'
        elif bug_prob > 0.6 or anomaly_score < -0.3:
            return 'HIGH'
        elif bug_prob > 0.4 or anomaly_score < -0.1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def analyze_test_patterns(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns across multiple test results"""
        if not test_results:
            return {'error': 'No test results provided'}
        
        predictions = []
        for result in test_results:
            pred = self.predict_bug_probability(result)
            predictions.append(pred)
        
        # Aggregate analysis
        bug_probabilities = [p['bug_probability'] for p in predictions]
        anomaly_scores = [p['anomaly_score'] for p in predictions]
        
        analysis = {
            'total_tests': len(test_results),
            'high_risk_tests': len([p for p in predictions if p['risk_level'] in ['CRITICAL', 'HIGH']]),
            'average_bug_probability': np.mean(bug_probabilities),
            'max_bug_probability': np.max(bug_probabilities),
            'anomaly_detection_rate': len([p for p in predictions if p['is_anomaly']]) / len(predictions),
            'risk_distribution': {
                'CRITICAL': len([p for p in predictions if p['risk_level'] == 'CRITICAL']),
                'HIGH': len([p for p in predictions if p['risk_level'] == 'HIGH']),
                'MEDIUM': len([p for p in predictions if p['risk_level'] == 'MEDIUM']),
                'LOW': len([p for p in predictions if p['risk_level'] == 'LOW'])
            },
            'recommendations': self._generate_recommendations(predictions)
        }
        
        return analysis
    
    def _generate_recommendations(self, predictions: List[Dict]) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        critical_count = len([p for p in predictions if p['risk_level'] == 'CRITICAL'])
        high_count = len([p for p in predictions if p['risk_level'] == 'HIGH'])
        avg_bug_prob = np.mean([p['bug_probability'] for p in predictions])
        
        if critical_count > 0:
            recommendations.append(f"🔴 URGENT: {critical_count} tests show critical risk levels. Immediate investigation required.")
        
        if high_count > len(predictions) * 0.2:
            recommendations.append(f"⚠️ HIGH ALERT: {high_count} tests show high risk. Consider code review and additional testing.")
        
        if avg_bug_prob > 0.6:
            recommendations.append("📈 TREND ALERT: Average bug probability is high. Consider improving code quality and test coverage.")
        
        anomaly_rate = len([p for p in predictions if p['is_anomaly']]) / len(predictions)
        if anomaly_rate > 0.15:
            recommendations.append(f"🔍 ANOMALY DETECTED: {anomaly_rate:.1%} of tests show anomalous behavior. Investigate unusual patterns.")
        
        if not recommendations:
            recommendations.append("✅ GOOD: Test results show normal patterns with low risk levels.")
        
        return recommendations


class VideoAnalysisAI:
    """
    AI-powered video analysis for forensic applications
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load pre-trained models or create simple ones
        self.motion_analyzer = self._create_motion_analyzer()
        self.quality_assessor = self._create_quality_assessor()
        self.tampering_detector = self._create_tampering_detector()
    
    def _create_motion_analyzer(self):
        """Create motion analysis model"""
        # Simple CNN for motion analysis
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
    def _create_quality_assessor(self):
        """Create video quality assessment model"""
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(10,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
    
    def _create_tampering_detector(self):
        """Create video tampering detection model"""
        # Random Forest for tampering detection
        return RandomForestClassifier(n_estimators=100, random_state=42)
    
    def analyze_video_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze a single video frame"""
        try:
            # Resize frame for analysis
            frame_resized = cv2.resize(frame, (64, 64))
            frame_normalized = frame_resized / 255.0
            
            # Motion analysis (simplified)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            motion_score = np.std(gray)  # Simple motion indicator
            
            # Quality assessment
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Extract features for tampering detection
            features = self._extract_frame_features(frame)
            
            return {
                'motion_score': float(motion_score),
                'blur_score': float(blur_score),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'quality_score': float(blur_score / 1000),  # Normalized
                'tampering_probability': self._detect_tampering(features),
                'features': features.tolist()
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing frame: {str(e)}")
            return {'error': str(e)}
    
    def _extract_frame_features(self, frame: np.ndarray) -> np.ndarray:
        """Extract features from frame for tampering detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Statistical features
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        skewness = self._calculate_skewness(gray)
        kurtosis = self._calculate_kurtosis(gray)
        
        # Texture features
        glcm_contrast = self._calculate_glcm_contrast(gray)
        glcm_energy = self._calculate_glcm_energy(gray)
        
        # Edge features
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Frequency domain features
        f_transform = np.fft.fft2(gray)
        f_magnitude = np.abs(f_transform)
        high_freq_energy = np.sum(f_magnitude[gray.shape[0]//4:, gray.shape[1]//4:])
        
        return np.array([
            mean_val, std_val, skewness, kurtosis,
            glcm_contrast, glcm_energy, edge_density, high_freq_energy
        ])
    
    def _calculate_skewness(self, image: np.ndarray) -> float:
        """Calculate skewness of image intensity distribution"""
        flat = image.flatten()
        mean_val = np.mean(flat)
        std_val = np.std(flat)
        if std_val == 0:
            return 0
        return np.mean(((flat - mean_val) / std_val) ** 3)
    
    def _calculate_kurtosis(self, image: np.ndarray) -> float:
        """Calculate kurtosis of image intensity distribution"""
        flat = image.flatten()
        mean_val = np.mean(flat)
        std_val = np.std(flat)
        if std_val == 0:
            return 0
        return np.mean(((flat - mean_val) / std_val) ** 4) - 3
    
    def _calculate_glcm_contrast(self, image: np.ndarray) -> float:
        """Calculate GLCM contrast (simplified)"""
        # Simplified GLCM contrast calculation
        dx = np.diff(image, axis=1)
        dy = np.diff(image, axis=0)
        return np.mean(dx**2) + np.mean(dy**2)
    
    def _calculate_glcm_energy(self, image: np.ndarray) -> float:
        """Calculate GLCM energy (simplified)"""
        # Simplified energy calculation
        hist, _ = np.histogram(image, bins=256, range=(0, 255))
        hist_norm = hist / np.sum(hist)
        return np.sum(hist_norm**2)
    
    def _detect_tampering(self, features: np.ndarray) -> float:
        """Detect tampering probability (simplified)"""
        # Simplified tampering detection based on feature thresholds
        # In practice, this would use the trained model
        
        # Normalize features
        normalized_features = (features - np.mean(features)) / (np.std(features) + 1e-8)
        
        # Simple rule-based detection
        tampering_indicators = 0
        
        if normalized_features[0] > 2:  # Unusual mean
            tampering_indicators += 1
        if normalized_features[1] > 2:  # Unusual std
            tampering_indicators += 1
        if abs(normalized_features[2]) > 2:  # Unusual skewness
            tampering_indicators += 1
        if abs(normalized_features[3]) > 2:  # Unusual kurtosis
            tampering_indicators += 1
        
        return min(tampering_indicators / 4.0, 1.0)


class CloudAIIntegration:
    """
    Integration with cloud AI services for advanced analysis
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.logger = logging.getLogger(__name__)
    
    def analyze_with_openai(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Analyze test results using OpenAI GPT (simulation)"""
        try:
            # Simulate OpenAI API call
            # In practice, you would use the actual OpenAI API
            
            summary = {
                'total_tests': len(test_results),
                'failed_tests': len([r for r in test_results if r.get('status') == 'FAIL']),
                'critical_issues': []
            }
            
            # Simulate AI insights
            insights = [
                "Authentication module shows consistent failures - investigate user session management",
                "Video upload functionality has intermittent issues with large files",
                "Performance degradation detected in analysis pipeline - consider optimization",
                "UI responsiveness issues on mobile devices detected"
            ]
            
            return {
                'provider': 'OpenAI GPT',
                'summary': summary,
                'insights': insights,
                'confidence': 0.85,
                'recommendations': [
                    "Focus testing efforts on authentication and file upload modules",
                    "Implement performance monitoring for video analysis pipeline",
                    "Add mobile-specific test cases for UI validation"
                ]
            }
        
        except Exception as e:
            self.logger.error(f"Error with OpenAI analysis: {str(e)}")
            return {'error': str(e)}
    
    def analyze_with_azure_ai(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze images using Azure Computer Vision (simulation)"""
        try:
            # Simulate Azure Computer Vision API
            return {
                'provider': 'Azure Computer Vision',
                'detected_objects': [
                    {'object': 'person', 'confidence': 0.95, 'bounding_box': [100, 100, 200, 300]},
                    {'object': 'vehicle', 'confidence': 0.87, 'bounding_box': [300, 150, 450, 250]}
                ],
                'scene_analysis': {
                    'is_outdoor': True,
                    'lighting_conditions': 'daylight',
                    'weather': 'clear'
                },
                'quality_metrics': {
                    'blur_level': 'low',
                    'noise_level': 'medium',
                    'overall_quality': 'good'
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error with Azure AI analysis: {str(e)}")
            return {'error': str(e)}


# Integration class that combines all AI capabilities
class ComprehensiveAIAnalyzer:
    """
    Comprehensive AI analyzer that combines all AI capabilities
    """
    
    def __init__(self, model_dir="ai_models", api_keys=None):
        self.bug_predictor = AIBugPredictor(model_dir)
        self.video_analyzer = VideoAnalysisAI()
        self.cloud_ai = CloudAIIntegration(api_keys)
        self.logger = logging.getLogger(__name__)
    
    def comprehensive_analysis(self, test_results: List[Dict], 
                             video_path: str = None) -> Dict[str, Any]:
        """Perform comprehensive AI analysis"""
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'bug_prediction': {},
            'pattern_analysis': {},
            'video_analysis': {},
            'cloud_insights': {},
            'overall_assessment': {}
        }
        
        try:
            # Bug prediction analysis
            if test_results:
                analysis_results['bug_prediction'] = self.bug_predictor.analyze_test_patterns(test_results)
                
                # Cloud AI analysis
                analysis_results['cloud_insights'] = self.cloud_ai.analyze_with_openai(test_results)
            
            # Video analysis (if video provided)
            if video_path and os.path.exists(video_path):
                video_results = self._analyze_video_comprehensive(video_path)
                analysis_results['video_analysis'] = video_results
            
            # Generate overall assessment
            analysis_results['overall_assessment'] = self._generate_overall_assessment(analysis_results)
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {str(e)}")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def _analyze_video_comprehensive(self, video_path: str) -> Dict[str, Any]:
        """Comprehensive video analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {'error': 'Could not open video file'}
            
            frame_analyses = []
            frame_count = 0
            max_frames = 100  # Analyze first 100 frames
            
            while cap.isOpened() and frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 10 == 0:  # Analyze every 10th frame
                    frame_analysis = self.video_analyzer.analyze_video_frame(frame)
                    frame_analysis['frame_number'] = frame_count
                    frame_analyses.append(frame_analysis)
                
                frame_count += 1
            
            cap.release()
            
            # Aggregate results
            if frame_analyses:
                avg_quality = np.mean([f.get('quality_score', 0) for f in frame_analyses])
                avg_tampering_prob = np.mean([f.get('tampering_probability', 0) for f in frame_analyses])
                
                return {
                    'total_frames_analyzed': len(frame_analyses),
                    'average_quality_score': float(avg_quality),
                    'average_tampering_probability': float(avg_tampering_prob),
                    'frame_details': frame_analyses,
                    'quality_assessment': 'high' if avg_quality > 0.7 else 'medium' if avg_quality > 0.4 else 'low',
                    'tampering_risk': 'high' if avg_tampering_prob > 0.6 else 'medium' if avg_tampering_prob > 0.3 else 'low'
                }
            else:
                return {'error': 'No frames could be analyzed'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_overall_assessment(self, analysis_results: Dict) -> Dict[str, Any]:
        """Generate overall assessment based on all analyses"""
        assessment = {
            'risk_level': 'LOW',
            'confidence': 0.5,
            'key_findings': [],
            'priority_actions': [],
            'quality_score': 0.0
        }
        
        try:
            # Assess bug prediction results
            bug_analysis = analysis_results.get('bug_prediction', {})
            if bug_analysis.get('high_risk_tests', 0) > 0:
                assessment['risk_level'] = 'HIGH'
                assessment['key_findings'].append(f"High risk detected in {bug_analysis['high_risk_tests']} tests")
            
            # Assess video analysis results
            video_analysis = analysis_results.get('video_analysis', {})
            if video_analysis.get('tampering_risk') == 'high':
                assessment['risk_level'] = 'CRITICAL'
                assessment['key_findings'].append("High tampering risk detected in video evidence")
            
            # Calculate quality score
            quality_factors = []
            
            if bug_analysis.get('average_bug_probability'):
                quality_factors.append(1 - bug_analysis['average_bug_probability'])
            
            if video_analysis.get('average_quality_score'):
                quality_factors.append(video_analysis['average_quality_score'])
            
            if quality_factors:
                assessment['quality_score'] = np.mean(quality_factors)
            
            # Generate priority actions
            if assessment['risk_level'] in ['HIGH', 'CRITICAL']:
                assessment['priority_actions'].append("Immediate review and remediation required")
            
            if bug_analysis.get('recommendations'):
                assessment['priority_actions'].extend(bug_analysis['recommendations'][:3])
            
            assessment['confidence'] = min(0.9, 0.5 + len(assessment['key_findings']) * 0.1)
            
        except Exception as e:
            assessment['error'] = str(e)
        
        return assessment


# Example usage
if __name__ == "__main__":
    # Initialize comprehensive AI analyzer
    ai_analyzer = ComprehensiveAIAnalyzer()
    
    # Example test results
    sample_test_results = [
        {
            'test_name': 'test_login',
            'duration': 2.5,
            'status': 'PASS',
            'errors': [],
            'memory_usage': 65,
            'cpu_usage': 45
        },
        {
            'test_name': 'test_upload_large_file',
            'duration': 15.2,
            'status': 'FAIL',
            'errors': ['Timeout error', 'Memory exceeded'],
            'memory_usage': 95,
            'cpu_usage': 85
        }
    ]
    
    # Perform comprehensive analysis
    results = ai_analyzer.comprehensive_analysis(sample_test_results)
    print(json.dumps(results, indent=2))