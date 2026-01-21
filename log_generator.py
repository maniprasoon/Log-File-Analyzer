"""
Log file generator for simulation
Creates realistic log data with various patterns and errors
"""
import random
import datetime
from faker import Faker
import os
from config import LOG_DIR, INPUT_LOG
from tqdm import tqdm

fake = Faker()

def generate_log_entry(timestamp=None):
    """
    Generate a single realistic log entry
    Returns formatted log string
    """
    if timestamp is None:
        timestamp = datetime.datetime.now() - datetime.timedelta(
            seconds=random.randint(0, 86400)
        )
    
    # IP address (90% real IPs, 10% potentially malicious/invalid)
    if random.random() < 0.9:
        ip = fake.ipv4()
    else:
        # Simulate some malformed/invalid IPs
        ip = random.choice([
            fake.ipv4(),
            "999.999.999.999",  # Invalid IP
            "192.168.1",  # Incomplete IP
            "localhost",  # Hostname instead of IP
        ])
    
    # HTTP methods with realistic distribution
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']
    weights = [0.7, 0.15, 0.05, 0.05, 0.05]  # GET is most common
    method = random.choices(methods, weights=weights)[0]
    
    # URLs with realistic patterns
    urls = [
        "/api/users", "/api/products", "/home", "/dashboard",
        "/login", "/logout", "/images/photo.jpg", "/css/style.css",
        "/admin", "/api/v1/data", "/search", "/profile"
    ]
    url = random.choice(urls)
    
    # Status codes with error simulation (85% success, 15% errors)
    if random.random() < 0.85:
        status = random.choice(['200', '201', '204', '301', '302', '304'])
    else:
        status = random.choice(['400', '401', '403', '404', '500', '502', '503'])
    
    # Add some malformed entries (2% of logs)
    if random.random() < 0.02:
        return f"{timestamp} {ip} {method} {url} {status} EXTRA_JUNK_DATA\n"
    
    return f"{timestamp:%Y-%m-%d %H:%M:%S} {ip} {method} {url} {status}\n"

def generate_log_file(num_entries=50000):
    """
    Generate log file with specified number of entries
    Uses progress bar for visual feedback
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print(f"Generating {num_entries} log entries...")
    
    with open(INPUT_LOG, 'w') as f:
        for i in tqdm(range(num_entries), desc="Creating log entries"):
            # Create timestamp with realistic progression
            base_time = datetime.datetime.now() - datetime.timedelta(days=1)
            timestamp = base_time + datetime.timedelta(seconds=i*2)
            
            log_entry = generate_log_entry(timestamp)
            f.write(log_entry)
    
    print(f"Log file generated: {INPUT_LOG}")
    print(f"File size: {os.path.getsize(INPUT_LOG) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    generate_log_file(50000)