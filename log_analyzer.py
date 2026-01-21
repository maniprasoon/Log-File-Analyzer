"""
Main log analyzer module with comprehensive error handling and logging
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from tqdm import tqdm

from log_parser import LogParser
from config import INPUT_LOG, ANALYSIS_LOG, CHUNK_SIZE
from report_generator import ReportGenerator
from database import db_manager

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(ANALYSIS_LOG),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LogAnalyzer:
    """
    Main analyzer class orchestrating parsing, analysis, and reporting
    """
    
    def __init__(self, log_file: str = INPUT_LOG):
        self.log_file = log_file
        self.parser = LogParser()
        self.reporter = ReportGenerator()
        self.results = {}
        
    def analyze(self) -> Dict[str, Any]:
        """
        Main analysis pipeline with performance tracking
        """
        logger.info(f"Starting analysis of {self.log_file}")
        start_time = time.time()
        
        try:
            # Phase 1: Parse and collect data
            parsed_data = self._parse_log_file()
            
            if parsed_data.empty:
                logger.error("No valid log entries found")
                return {}
            
            # Phase 2: Analyze error distribution
            logger.info("Analyzing error distribution...")
            analysis_results = self.parser.analyze_error_distribution(parsed_data)
            
            # Phase 3: Generate detailed metrics
            detailed_metrics = self._calculate_detailed_metrics(parsed_data)
            
            # Combine results
            self.results = {
                **analysis_results,
                'detailed_metrics': detailed_metrics,
                'parsed_data': parsed_data,
                'execution_time': time.time() - start_time
            }
            
            try:
                record_id = db_manager.save_analysis(analysis_results)
                logger.info(f"Analysis saved to database with ID: {record_id}")
            except Exception as e:
                logger.error(f"Failed to save to database: {e}")
            logger.info(f"Analysis completed in {self.results['execution_time']:.2f} seconds")
            
            return self.results
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise
    
    def _parse_log_file(self) -> pd.DataFrame:
        """
        Parse log file with chunking for memory efficiency
        """
        logger.info(f"Parsing log file: {self.log_file}")
        
        parsed_chunks = []
        invalid_lines = 0
        
        # Parse file in chunks with progress bar
        for chunk_df in tqdm(
            self.parser.parse_file_chunks(self.log_file, CHUNK_SIZE),
            desc="Parsing log file",
            unit="chunk"
        ):
            if not chunk_df.empty:
                parsed_chunks.append(chunk_df)
        
        # Combine all chunks
        if parsed_chunks:
            combined_df = pd.concat(parsed_chunks, ignore_index=True)
            logger.info(f"Parsed {len(combined_df)} valid log entries")
            logger.info(f"Skipped {invalid_lines} invalid/malformed entries")
            return combined_df
        
        return pd.DataFrame()
    
    def _calculate_detailed_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate additional metrics for comprehensive analysis
        """
        metrics = {}
        
        # Request methods distribution
        metrics['method_distribution'] = df['method'].value_counts().to_dict()
        
        # Hourly error pattern
        if 'timestamp' in df.columns:
            try:
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                error_mask = df['status'].apply(self.parser.is_error)
                hourly_errors = df[error_mask].groupby('hour').size().to_dict()
                metrics['hourly_error_pattern'] = hourly_errors
            except Exception as e:
                logger.warning(f"Could not calculate hourly patterns: {e}")
        
        # IP addresses with most requests (successful and errors)
        metrics['top_request_ips'] = df['ip'].value_counts().head(10).to_dict()
        
        # Most common error paths/URLs
        error_df = df[df['status'].apply(self.parser.is_error)]
        if not error_df.empty and 'url' in error_df.columns:
            metrics['error_paths'] = error_df['url'].value_counts().head(10).to_dict()
        
        return metrics
    
    def generate_report(self, output_file: str = None):
        """
        Generate comprehensive report with visualizations
        """
        if not self.results:
            self.analyze()
        
        self.reporter.generate_text_report(self.results, output_file)
        self.reporter.generate_visualizations(self.results)
        
        logger.info(f"Reports generated successfully")

def main():
    """
    Main execution function
    """
    try:
        # Initialize analyzer
        analyzer = LogAnalyzer()
        
        # Perform analysis
        results = analyzer.analyze()
        
        # Generate reports
        analyzer.generate_report()
        
        # Print summary to console
        print("\n" + "="*60)
        print("LOG ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total Requests: {results.get('total_requests', 0):,}")
        print(f"Total Errors: {results.get('total_errors', 0):,}")
        print(f"Error Rate: {results.get('error_rate', 0):.2f}%")
        print(f"Execution Time: {results.get('execution_time', 0):.2f} seconds")
        
        if 'error_frequency' in results:
            print("\nTop Error Codes:")
            for code, count in sorted(results['error_frequency'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {code}: {count:,}")
        
        print("\n" + "="*60)
        
    except FileNotFoundError:
        logger.error(f"Log file not found: {INPUT_LOG}")
        print("ERROR: Log file not found. Run log_generator.py first.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()