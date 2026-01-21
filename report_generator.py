"""
Report generation and visualization module
"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from typing import Dict, Any
import os

from config import OUTPUT_REPORT, CHART_WIDTH, CHART_HEIGHT, COLOR_MAP, TOP_IPS_COUNT

class ReportGenerator:
    """
    Handles report generation and visualization
    """
    
    def __init__(self):
        # Set style for better visualizations
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette(COLOR_MAP)
        self.output_dir = "reports"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_text_report(self, results: Dict[str, Any], output_file: str = None):
        """
        Generate comprehensive text report
        """
        if output_file is None:
            output_file = OUTPUT_REPORT
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("SERVER LOG ANALYSIS REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Log File: server.log\n\n")
            
            # Summary Statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Requests: {results.get('total_requests', 0):,}\n")
            f.write(f"Total Errors: {results.get('total_errors', 0):,}\n")
            f.write(f"Error Rate: {results.get('error_rate', 0):.2f}%\n\n")
            
            # Error Code Distribution
            f.write("ERROR CODE DISTRIBUTION\n")
            f.write("-"*40 + "\n")
            error_freq = results.get('error_frequency', {})
            for code, count in sorted(error_freq.items(), 
                                     key=lambda x: x[1], reverse=True):
                f.write(f"HTTP {code}: {count:,} occurrences\n")
            f.write("\n")
            
            # Top IPs with Errors
            f.write(f"TOP {TOP_IPS_COUNT} IP ADDRESSES WITH ERRORS\n")
            f.write("-"*40 + "\n")
            top_ips = results.get('top_error_ips', {})
            for ip, count in list(top_ips.items())[:TOP_IPS_COUNT]:
                f.write(f"{ip}: {count:,} errors\n")
            f.write("\n")
            
            # Request Method Distribution
            f.write("REQUEST METHOD DISTRIBUTION\n")
            f.write("-"*40 + "\n")
            method_dist = results.get('detailed_metrics', {}).get('method_distribution', {})
            for method, count in method_dist.items():
                percentage = (count / results['total_requests'] * 100) if results['total_requests'] > 0 else 0
                f.write(f"{method}: {count:,} ({percentage:.1f}%)\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")
        
        print(f"Text report saved to: {output_file}")
    
    def generate_visualizations(self, results: Dict[str, Any]):
        """
        Generate all visualizations
        """
        # Create subplot grid
        fig, axes = plt.subplots(2, 2, figsize=(CHART_WIDTH, CHART_HEIGHT))
        fig.suptitle('Server Log Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Error Code Distribution (Pie Chart)
        self._plot_error_distribution(axes[0, 0], results)
        
        # 2. Top IPs with Errors (Bar Chart)
        self._plot_top_error_ips(axes[0, 1], results)
        
        # 3. Hourly Error Pattern (Line Chart)
        self._plot_hourly_errors(axes[1, 0], results)
        
        # 4. Request Method Distribution (Bar Chart)
        self._plot_method_distribution(axes[1, 1], results)
        
        plt.tight_layout()
        chart_path = os.path.join(self.output_dir, "log_analysis_dashboard.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Visualizations saved to: {chart_path}")
    
    def _plot_error_distribution(self, ax, results: Dict[str, Any]):
        """Plot error code distribution as pie chart"""
        error_freq = results.get('error_frequency', {})
        
        if error_freq:
            labels = [f'HTTP {code}' for code in error_freq.keys()]
            sizes = list(error_freq.values())
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title('Error Code Distribution', fontweight='bold')
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No Error Data', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Error Code Distribution', fontweight='bold')
    
    def _plot_top_error_ips(self, ax, results: Dict[str, Any]):
        """Plot top IP addresses with errors"""
        top_ips = results.get('top_error_ips', {})
        
        if top_ips:
            ips = list(top_ips.keys())[:TOP_IPS_COUNT]
            counts = list(top_ips.values())[:TOP_IPS_COUNT]
            
            bars = ax.barh(ips, counts, color=sns.color_palette(COLOR_MAP, len(ips)))
            ax.set_xlabel('Error Count')
            ax.set_title(f'Top {TOP_IPS_COUNT} IPs with Errors', fontweight='bold')
            ax.invert_yaxis()
            
            # Add value labels on bars
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                       f' {int(width)}', va='center')
        else:
            ax.text(0.5, 0.5, 'No Error IP Data', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title(f'Top {TOP_IPS_COUNT} IPs with Errors', fontweight='bold')
    
    def _plot_hourly_errors(self, ax, results: Dict[str, Any]):
        """Plot hourly error pattern"""
        hourly_errors = results.get('detailed_metrics', {}).get('hourly_error_pattern', {})
        
        if hourly_errors:
            hours = list(range(24))
            error_counts = [hourly_errors.get(hour, 0) for hour in hours]
            
            ax.plot(hours, error_counts, marker='o', linewidth=2, markersize=6)
            ax.fill_between(hours, error_counts, alpha=0.3)
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Error Count')
            ax.set_title('Hourly Error Pattern', fontweight='bold')
            ax.set_xticks(range(0, 24, 3))
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No Hourly Pattern Data', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Hourly Error Pattern', fontweight='bold')
    
    def _plot_method_distribution(self, ax, results: Dict[str, Any]):
        """Plot request method distribution"""
        method_dist = results.get('detailed_metrics', {}).get('method_distribution', {})
        
        if method_dist:
            methods = list(method_dist.keys())
            counts = list(method_dist.values())
            
            bars = ax.bar(methods, counts, color=sns.color_palette(COLOR_MAP, len(methods)))
            ax.set_xlabel('HTTP Method')
            ax.set_ylabel('Request Count')
            ax.set_title('Request Method Distribution', fontweight='bold')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       f' {int(height):,}', ha='center', va='bottom')
        else:
            ax.text(0.5, 0.5, 'No Method Data', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            ax.set_title('Request Method Distribution', fontweight='bold')