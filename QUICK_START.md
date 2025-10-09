# Quick Start Guide - Streamlit Video Forensics

## Immediate Deployment (5 minutes)

### Option 1: Streamlit Cloud (Fastest - No Setup Required)

1. **Upload your code to GitHub:**
   - Create new repository on GitHub
   - Upload all files from this project
   - Make repository public (for free hosting)

2. **Deploy instantly:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select `streamlit_app.py` as main file
   - Click "Deploy"

3. **Your app is live!**
   - Access URL: `https://share.streamlit.io/yourusername/yourrepo`
   - Default login: `admin` / `admin123`

### Option 2: Local Hosting (2 minutes)

```bash
# Install requirements
pip install streamlit opencv-python-headless numpy pandas plotly

# Run application
streamlit run streamlit_app.py

# Access at: http://localhost:8501
```

### Option 3: Heroku (10 minutes)

1. **Create these files:**

   `Procfile`:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy:**
   ```bash
   heroku create your-app-name
   git add .
   git commit -m "Deploy app"
   git push heroku main
   ```

## Features Ready to Use

- **Video Upload:** Drag & drop MP4, AVI, MOV files
- **Forensic Analysis:** Automated tampering detection
- **Interactive Results:** Charts and detailed reports
- **Multi-user Support:** Authentication system
- **Responsive Design:** Works on mobile and desktop
- **Export Reports:** JSON and PDF downloads

## Default Credentials

- **Username:** admin
- **Password:** admin123

## Troubleshooting

**Application won't start?**
- Check Python version (3.8+ required)
- Install missing dependencies: `pip install -r requirements.txt`

**Upload fails?**
- File size limit: 500MB max
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM

**Analysis stuck?**
- Large files take longer to process
- Check system resources (RAM/CPU)

## Production Deployment

For production use:
1. Change default password in database
2. Update secret keys in `.streamlit/secrets.toml`
3. Enable HTTPS
4. Configure backup strategy

See `STREAMLIT_DEPLOYMENT.md` for detailed production setup.

## Support

- **Documentation:** See all `.md` files in project
- **Test Suite:** Run `pytest streamlit_test_suite.py`
- **Issues:** Check system status page in application

Your video forensics platform is now ready for deployment and client demonstration!