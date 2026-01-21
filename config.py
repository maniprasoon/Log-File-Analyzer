"""
Configuration settings for Log File Analyzer
"""
import os
from datetime import datetime

# File paths
LOG_DIR = "logs"
INPUT_LOG = os.path.join(LOG_DIR, "server.log")
ANALYSIS_LOG = os.path.join(LOG_DIR, "analysis.log")
OUTPUT_REPORT = "log_analysis_report.txt"

# Database
DATABASE_PATH = "log_analysis.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Web Dashboard
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# Log patterns
LOG_PATTERN = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (?P<method>GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) (?P<url>\S+) (?P<status>\d{3})'

# Error status codes
ERROR_CODES = {'400', '401', '403', '404', '405', '408', '429', '500', '502', '503', '504'}

# Analysis parameters
TOP_IPS_COUNT = 5
CHUNK_SIZE = 10000

# Visualization
CHART_WIDTH = 12
CHART_HEIGHT = 8
COLOR_MAP = 'viridis'"""
Configuration settings for Log File Analyzer
"""
import os
from datetime import datetime

# File paths
LOG_DIR = "logs"
INPUT_LOG = os.path.join(LOG_DIR, "server.log")
ANALYSIS_LOG = os.path.join(LOG_DIR, "analysis.log")
OUTPUT_REPORT = "log_analysis_report.txt"

# Database
DATABASE_PATH = "log_analysis.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Web Dashboard
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True

# Log patterns
LOG_PATTERN = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (?P<method>GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH) (?P<url>\S+) (?P<status>\d{3})'

# Error status codes
ERROR_CODES = {'400', '401', '403', '404', '405', '408', '429', '500', '502', '503', '504'}

# Analysis parameters
TOP_IPS_COUNT = 5
CHUNK_SIZE = 10000

# Visualization
CHART_WIDTH = 12
CHART_HEIGHT = 8
COLOR_MAP = 'viridis'