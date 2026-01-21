"""
Flask web dashboard for log analysis results
Minimal but functional web interface
"""
from flask import Flask, render_template, jsonify
from database import db_manager
from config import HOST, PORT, DEBUG
import matplotlib
matplotlib.use('Agg')  # Required for headless environments
import matplotlib.pyplot as plt
import io
import base64
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    # Get recent analyses
    recent_analyses = db_manager.get_recent_analyses(limit=5)
    
    # Get overall statistics
    stats = db_manager.get_statistics()
    
    # Generate trend chart
    trend_chart = generate_trend_chart(recent_analyses)
    
    return render_template('dashboard.html',
                         recent_analyses=recent_analyses,
                         stats=stats,
                         trend_chart=trend_chart)

@app.route('/api/analyses')
def get_analyses():
    """API endpoint for analysis data (for AJAX calls)"""
    analyses = db_manager.get_recent_analyses(limit=20)
    return jsonify(analyses)

@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    stats = db_manager.get_statistics()
    return jsonify(stats)

def generate_trend_chart(analyses):
    """Generate a simple trend chart as base64 image"""
    if not analyses:
        return None
    
    # Extract data for chart
    timestamps = [a['timestamp'][:16] for a in analyses]  # Shorten timestamp
    error_rates = [a['error_rate'] for a in analyses]
    
    # Create figure
    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, error_rates, marker='o', linewidth=2)
    plt.fill_between(timestamps, error_rates, alpha=0.3)
    plt.title('Error Rate Trend (Recent Analyses)')
    plt.xlabel('Timestamp')
    plt.ylabel('Error Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert to base64 for HTML
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'log_analyzer_dashboard'})

if __name__ == '__main__':
    print(f"Starting Flask dashboard on http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop")
    app.run(host=HOST, port=PORT, debug=DEBUG)