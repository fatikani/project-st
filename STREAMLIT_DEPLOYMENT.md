# Streamlit Video Forensics - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Streamlit Video Forensics application to various hosting platforms. The application is designed for fast deployment with minimal configuration.

## Quick Start

### Local Development

1. **Clone or prepare your project directory**
   ```bash
   cd /path/to/your/project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Login with default credentials: `admin` / `admin123`

## Cloud Deployment Options

### 1. Streamlit Cloud (Recommended for Demos)

**Advantages:**
- Free hosting for public repositories
- Automatic deployment from GitHub
- Built-in secrets management
- Zero configuration required

**Steps:**

1. **Push code to GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/video-forensics.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Configure secrets (if needed)**
   - In Streamlit Cloud dashboard, go to app settings
   - Add secrets from `.streamlit/secrets.toml`

**Live URL:** Your app will be available at `https://share.streamlit.io/yourusername/video-forensics/streamlit_app.py`

### 2. Heroku Deployment

**Advantages:**
- Professional hosting
- Custom domains
- Scalable
- Database add-ons available

**Steps:**

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create additional files for Heroku**

   Create `Procfile`:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

   Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [general]\n\
   email = \"your-email@domain.com\"\n\
   " > ~/.streamlit/credentials.toml
   echo "\
   [server]\n\
   headless = true\n\
   enableCORS=false\n\
   port = $PORT\n\
   " > ~/.streamlit/config.toml
   ```

3. **Deploy to Heroku**
   ```bash
   heroku login
   heroku create your-app-name
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

4. **Configure environment variables**
   ```bash
   heroku config:set STREAMLIT_SERVER_HEADLESS=true
   heroku config:set STREAMLIT_SERVER_PORT=$PORT
   ```

**Live URL:** `https://your-app-name.herokuapp.com`

### 3. Railway Deployment

**Advantages:**
- Simple deployment
- Automatic HTTPS
- Good performance
- Affordable pricing

**Steps:**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Configure start command**
   - In Railway dashboard, set start command:
   - `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

### 4. Docker Deployment

**Advantages:**
- Consistent environment
- Easy scaling
- Works on any Docker-compatible platform

**Local Docker Testing:**
```bash
# Build image
docker build -t video-forensics .

# Run container
docker run -p 8501:8501 video-forensics
```

**Docker Compose Deployment:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 5. AWS EC2 Deployment

**Advantages:**
- Full control over environment
- Scalable infrastructure
- Professional hosting

**Steps:**

1. **Launch EC2 instance**
   - Choose Ubuntu 20.04 LTS
   - Select instance type (t3.medium recommended)
   - Configure security group (allow port 8501)

2. **Connect and setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install python3 python3-pip -y
   
   # Clone your repository
   git clone https://github.com/yourusername/video-forensics.git
   cd video-forensics
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Run application
   streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
   ```

3. **Setup as service (optional)**
   Create `/etc/systemd/system/video-forensics.service`:
   ```ini
   [Unit]
   Description=Video Forensics Streamlit App
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/video-forensics
   Environment=PATH=/home/ubuntu/.local/bin
   ExecStart=/home/ubuntu/.local/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

   Enable service:
   ```bash
   sudo systemctl enable video-forensics
   sudo systemctl start video-forensics
   ```

## Environment Configuration

### Production Settings

Update `.streamlit/config.toml` for production:

```toml
[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 500

[browser]
gatherUsageStats = false
showErrorDetails = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### Security Configuration

1. **Change default credentials**
   - Update admin password in database
   - Use strong passwords

2. **Configure secrets**
   - Set unique secret keys
   - Use environment variables for sensitive data

3. **Enable HTTPS**
   - Use reverse proxy (nginx/Apache)
   - Configure SSL certificates

### Database Configuration

For production, consider upgrading from SQLite:

**PostgreSQL Setup:**
```python
# Update database connection in streamlit_app.py
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///forensic_db.sqlite')

def init_database():
    if DATABASE_URL.startswith('postgres'):
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect('forensic_db.sqlite')
    return conn
```

## Performance Optimization

### Caching Configuration

```python
import streamlit as st

# Cache database connections
@st.cache_resource
def init_database():
    return sqlite3.connect('forensic_db.sqlite', check_same_thread=False)

# Cache analysis results
@st.cache_data
def analyze_video(video_hash):
    # Your analysis logic here
    pass
```

### Resource Limits

Set appropriate limits in production:

```toml
[server]
maxUploadSize = 500  # MB
maxMessageSize = 200  # MB

[runner]
magicEnabled = false  # Disable magic commands in production
```

## Monitoring and Maintenance

### Health Checks

The application includes built-in health monitoring:

- **System Status:** Available at `/System_Status` page
- **Database Status:** Automatic connection testing
- **Resource Monitoring:** CPU, memory, disk usage

### Logging

Configure logging for production:

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Backup Strategy

1. **Database Backups**
   ```bash
   # SQLite backup
   cp forensic_db.sqlite forensic_db.backup.$(date +%Y%m%d)
   
   # PostgreSQL backup
   pg_dump DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

2. **File Storage Backups**
   ```bash
   # Backup uploaded files
   tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
   tar -czf analysis_backup_$(date +%Y%m%d).tar.gz analysis_results/
   ```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8501
   lsof -ti:8501
   kill -9 $(lsof -ti:8501)
   ```

2. **Memory Issues**
   - Increase server memory
   - Optimize video processing
   - Implement file size limits

3. **Upload Failures**
   - Check file permissions
   - Verify disk space
   - Review file size limits

### Debug Mode

Enable debug mode for development:

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Log Analysis

Monitor application logs:

```bash
# View real-time logs
tail -f app.log

# Search for errors
grep -i error app.log

# Analyze access patterns
grep -i "analysis" app.log | wc -l
```

## Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer Setup**
   - Use nginx or AWS ALB
   - Distribute traffic across multiple instances

2. **Database Scaling**
   - Move to PostgreSQL
   - Implement connection pooling
   - Consider read replicas

3. **File Storage**
   - Use object storage (AWS S3, Google Cloud Storage)
   - Implement CDN for static assets

### Vertical Scaling

Optimize single instance performance:

1. **Resource Allocation**
   - Increase RAM for large video processing
   - Use SSD storage for better I/O
   - Optimize CPU usage

2. **Application Optimization**
   - Implement lazy loading
   - Use background processing
   - Cache frequently accessed data

## Security Best Practices

1. **Authentication**
   - Use strong passwords
   - Implement session timeout
   - Consider multi-factor authentication

2. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement proper access controls

3. **Input Validation**
   - Validate all uploaded files
   - Sanitize user inputs
   - Implement rate limiting

## Support and Maintenance

For ongoing support:

1. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Test updates in staging environment

2. **Performance Monitoring**
   - Track response times
   - Monitor resource usage
   - Set up alerts for issues

3. **User Feedback**
   - Collect user feedback
   - Monitor error rates
   - Implement feature requests

## Conclusion

This deployment guide provides multiple options for hosting your Streamlit Video Forensics application. Choose the option that best fits your requirements:

- **Streamlit Cloud:** Best for demos and prototypes
- **Heroku/Railway:** Good for small to medium applications
- **Docker:** Best for consistent deployments
- **EC2/VPS:** Best for full control and customization

For production use, always implement proper security measures, monitoring, and backup strategies.