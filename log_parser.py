"""
Log parsing utilities with optimized regex and error handling
Handles malformed entries gracefully
"""
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from collections import defaultdict
from config import LOG_PATTERN, ERROR_CODES

class LogParser:
    """
    Efficient log parser with compiled regex for performance
    """
    
    def __init__(self):
        # Compile regex once for reuse (performance optimization)
        self.log_pattern = re.compile(LOG_PATTERN)
        self.error_codes = ERROR_CODES
        
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse single log line with error handling
        Returns parsed data or None for invalid lines
        """
        try:
            # Clean the line
            line = line.strip()
            if not line:
                return None
            
            # Try regex pattern first (fastest for valid lines)
            match = self.log_pattern.match(line)
            if match:
                return match.groupdict()
            
            # Fallback parsing for malformed entries
            return self._fallback_parse(line)
            
        except Exception as e:
            logging.warning(f"Failed to parse line: {line[:100]}... Error: {e}")
            return None
    
    def _fallback_parse(self, line: str) -> Optional[Dict]:
        """
        Fallback parsing for lines that don't match the regex
        More tolerant but less precise
        """
        try:
            parts = line.split()
            if len(parts) >= 5:
                # Extract likely components based on position
                timestamp = parts[0] + " " + parts[1] if len(parts) > 5 else parts[0]
                ip = parts[2] if len(parts) > 5 else parts[1]
                method = parts[3] if len(parts) > 5 else parts[2]
                status = parts[-1]  # Status code is usually last
                
                # Validate extracted data
                if re.match(r'\d{3}', status) and re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip):
                    return {
                        'timestamp': timestamp,
                        'ip': ip,
                        'method': method,
                        'status': status
                    }
        except Exception:
            pass
        
        return None
    
    def is_error(self, status_code: str) -> bool:
        """
        Check if status code represents an error
        """
        return status_code in self.error_codes
    
    def parse_file_chunks(self, filepath: str, chunk_size: int = 10000):
        """
        Parse large files in chunks to conserve memory
        Generator yields chunks of parsed data
        """
        chunk = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                parsed = self.parse_line(line)
                if parsed:
                    chunk.append(parsed)
                    
                    if len(chunk) >= chunk_size:
                        yield pd.DataFrame(chunk)
                        chunk = []
            
            # Yield remaining data
            if chunk:
                yield pd.DataFrame(chunk)
    
    def analyze_error_distribution(self, df: pd.DataFrame) -> Dict:
        """
        Calculate error statistics from parsed data
        """
        # Filter error rows
        error_mask = df['status'].apply(self.is_error)
        error_df = df[error_mask]
        
        # Calculate statistics
        total_requests = len(df)
        total_errors = len(error_df)
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Error code frequency
        error_freq = error_df['status'].value_counts().to_dict()
        
        # Top IPs with errors
        top_error_ips = error_df['ip'].value_counts().head(10).to_dict()
        
        return {
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': error_rate,
            'error_frequency': error_freq,
            'top_error_ips': top_error_ips,
            'error_df': error_df
        }