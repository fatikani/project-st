"""
Digital Forensic Video Analysis Web Application
A Flask-based web application for video forensic analysis with AI integration
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import hashlib
import json
import datetime
from pathlib import Path
import sqlite3
import uuid
from functools import wraps
import tensorflow as tf
from PIL import Image, ExifTags
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ANALYSIS_FOLDER'] = 'analysis_results'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['ANALYSIS_FOLDER'], 'templates', 'static']:
    os.makedirs(folder, exist_ok=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('forensic_db.sqlite')
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
    
    # Cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'open',
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Evidence table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            file_size INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analysis_status TEXT DEFAULT 'pending',
            FOREIGN KEY (case_id) REFERENCES cases (id)
        )
    ''')
    
    # Analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER,
            analysis_type TEXT NOT NULL,
            results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evidence_id) REFERENCES evidence (id)
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_hash = generate_password_hash('admin123')
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('admin', admin_hash, 'admin'))
    
    conn.commit()
    conn.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class VideoForensicAnalyzer:
    """Main class for video forensic analysis"""
    
    def __init__(self):
        self.analysis_results = {}
    
    def extract_metadata(self, video_path):
        """Extract video metadata"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            metadata = {
                'filename': os.path.basename(video_path),
                'file_size': os.path.getsize(video_path),
                'file_hash': self.calculate_file_hash(video_path),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
                'analysis_timestamp': datetime.datetime.now().isoformat()
            }
            
            cap.release()
            return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of the file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def detect_motion(self, video_path, sensitivity=25):
        """Detect motion in video"""
        cap = cv2.VideoCapture(video_path)
        motion_data = []
        
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()
        
        frame_number = 0
        
        while cap.isOpened():
            if not ret:
                break
                
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, sensitivity, 255, cv2.THRESH_BINARY)
            
            motion_pixels = cv2.countNonZero(thresh)
            motion_percentage = (motion_pixels / (thresh.shape[0] * thresh.shape[1])) * 100
            
            motion_data.append({
                'frame': frame_number,
                'motion_percentage': motion_percentage,
                'timestamp': frame_number / cap.get(cv2.CAP_PROP_FPS)
            })
            
            frame1 = frame2
            ret, frame2 = cap.read()
            frame_number += 1
        
        cap.release()
        return motion_data
    
    def analyze_frames(self, video_path, frame_interval=30):
        """Analyze specific frames for anomalies"""
        cap = cv2.VideoCapture(video_path)
        frame_analysis = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                # Analyze frame quality
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur_measure = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                # Detect edges
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.count_nonzero(edges) / (edges.shape[0] * edges.shape[1])
                
                frame_analysis.append({
                    'frame_number': frame_count,
                    'timestamp': frame_count / cap.get(cv2.CAP_PROP_FPS),
                    'blur_measure': blur_measure,
                    'edge_density': edge_density,
                    'frame_quality': 'good' if blur_measure > 100 else 'poor'
                })
            
            frame_count += 1
        
        cap.release()
        return frame_analysis

# Initialize the analyzer
analyzer = VideoForensicAnalyzer()

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('forensic_db.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        file = request.files['video']
        case_number = request.form.get('case_number', '')
        
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Save to database
            conn = sqlite3.connect('forensic_db.sqlite')
            cursor = conn.cursor()
            
            # Create case if it doesn't exist
            cursor.execute('SELECT id FROM cases WHERE case_number = ?', (case_number,))
            case = cursor.fetchone()
            if not case:
                cursor.execute('INSERT INTO cases (case_number, title, created_by) VALUES (?, ?, ?)',
                              (case_number, f"Case {case_number}", session['user_id']))
                case_id = cursor.lastrowid
            else:
                case_id = case[0]
            
            # Calculate file hash
            file_hash = analyzer.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)
            
            cursor.execute('''INSERT INTO evidence (case_id, filename, original_name, file_hash, file_size) 
                             VALUES (?, ?, ?, ?, ?)''',
                          (case_id, unique_filename, filename, file_hash, file_size))
            evidence_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('analyze_video', evidence_id=evidence_id))
        else:
            flash('Invalid file type! Please upload a video file.', 'error')
    
    return render_template('upload.html')

@app.route('/analyze/<int:evidence_id>')
@login_required
def analyze_video(evidence_id):
    conn = sqlite3.connect('forensic_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT filename, original_name FROM evidence WHERE id = ?', (evidence_id,))
    evidence = cursor.fetchone()
    conn.close()
    
    if not evidence:
        flash('Evidence not found!', 'error')
        return redirect(url_for('index'))
    
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], evidence[0])
    
    # Start analysis in background
    def run_analysis():
        try:
            # Extract metadata
            metadata = analyzer.extract_metadata(video_path)
            
            # Detect motion
            motion_data = analyzer.detect_motion(video_path)
            
            # Analyze frames
            frame_analysis = analyzer.analyze_frames(video_path)
            
            # Save results to database
            conn = sqlite3.connect('forensic_db.sqlite')
            cursor = conn.cursor()
            
            cursor.execute('INSERT INTO analysis_results (evidence_id, analysis_type, results) VALUES (?, ?, ?)',
                          (evidence_id, 'metadata', json.dumps(metadata)))
            cursor.execute('INSERT INTO analysis_results (evidence_id, analysis_type, results) VALUES (?, ?, ?)',
                          (evidence_id, 'motion_detection', json.dumps(motion_data)))
            cursor.execute('INSERT INTO analysis_results (evidence_id, analysis_type, results) VALUES (?, ?, ?)',
                          (evidence_id, 'frame_analysis', json.dumps(frame_analysis)))
            
            cursor.execute('UPDATE evidence SET analysis_status = ? WHERE id = ?',
                          ('completed', evidence_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            conn = sqlite3.connect('forensic_db.sqlite')
            cursor = conn.cursor()
            cursor.execute('UPDATE evidence SET analysis_status = ? WHERE id = ?',
                          ('failed', evidence_id))
            conn.commit()
            conn.close()
    
    threading.Thread(target=run_analysis).start()
    
    return render_template('analysis.html', evidence_id=evidence_id, filename=evidence[1])

@app.route('/results/<int:evidence_id>')
@login_required
def view_results(evidence_id):
    conn = sqlite3.connect('forensic_db.sqlite')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT ar.analysis_type, ar.results, ar.created_at 
                     FROM analysis_results ar 
                     WHERE ar.evidence_id = ?''', (evidence_id,))
    results = cursor.fetchall()
    
    cursor.execute('SELECT original_name, analysis_status FROM evidence WHERE id = ?', (evidence_id,))
    evidence = cursor.fetchone()
    
    conn.close()
    
    if not evidence:
        flash('Evidence not found!', 'error')
        return redirect(url_for('index'))
    
    analysis_data = {}
    for result in results:
        analysis_data[result[0]] = json.loads(result[1])
    
    return render_template('results.html', 
                         evidence_id=evidence_id, 
                         filename=evidence[0],
                         status=evidence[1],
                         analysis_data=analysis_data)

@app.route('/api/analysis_status/<int:evidence_id>')
@login_required
def analysis_status(evidence_id):
    conn = sqlite3.connect('forensic_db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT analysis_status FROM evidence WHERE id = ?', (evidence_id,))
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'status': result[0] if result else 'not_found'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)