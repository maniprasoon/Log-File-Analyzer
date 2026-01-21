"""
Database operations for historical analysis
Uses SQLAlchemy ORM for simplicity
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from config import DATABASE_URL
import json

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class AnalysisResult(Base):
    """Model for storing analysis results"""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    total_requests = Column(Integer)
    total_errors = Column(Integer)
    error_rate = Column(Float)
    error_distribution = Column(String)  # JSON string
    top_error_ips = Column(String)       # JSON string
    execution_time = Column(Float)
    
    def to_dict(self):
        """Convert to dictionary for easy serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'total_requests': self.total_requests,
            'total_errors': self.total_errors,
            'error_rate': self.error_rate,
            'error_distribution': json.loads(self.error_distribution) if self.error_distribution else {},
            'top_error_ips': json.loads(self.top_error_ips) if self.top_error_ips else {},
            'execution_time': self.execution_time
        }

class DatabaseManager:
    """Simple database operations manager"""
    
    def __init__(self):
        self.engine = engine
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        Base.metadata.create_all(self.engine)
    
    def save_analysis(self, results):
        """
        Save analysis results to database
        Returns the saved record ID
        """
        session = Session()
        
        # Prepare data
        error_dist = json.dumps(results.get('error_frequency', {}))
        top_ips = json.dumps(results.get('top_error_ips', {}))
        
        # Create record
        record = AnalysisResult(
            total_requests=results.get('total_requests', 0),
            total_errors=results.get('total_errors', 0),
            error_rate=results.get('error_rate', 0.0),
            error_distribution=error_dist,
            top_error_ips=top_ips,
            execution_time=results.get('execution_time', 0.0)
        )
        
        # Save to database
        session.add(record)
        session.commit()
        record_id = record.id
        session.close()
        
        return record_id
    
    def get_recent_analyses(self, limit=10):
        """Get recent analysis results"""
        session = Session()
        results = session.query(AnalysisResult)\
            .order_by(AnalysisResult.timestamp.desc())\
            .limit(limit)\
            .all()
        session.close()
        return [r.to_dict() for r in results]
    
    def get_statistics(self):
        """Get overall statistics from all analyses"""
        session = Session()
        
        # Basic stats
        total_runs = session.query(AnalysisResult).count()
        
        if total_runs == 0:
            session.close()
            return {}
        
        # Average error rate - FIXED: use func from sqlalchemy
        avg_error_rate = session.query(
            func.avg(AnalysisResult.error_rate)
        ).scalar()
        
        # Get last run for comparison
        last_run = session.query(AnalysisResult)\
            .order_by(AnalysisResult.timestamp.desc())\
            .first()
        
        session.close()
        
        return {
            'total_runs': total_runs,
            'avg_error_rate': round(avg_error_rate, 2) if avg_error_rate else 0,
            'last_run': last_run.to_dict() if last_run else None
        }
    
    def clear_old_data(self, days_to_keep=30):
        """Clean up old data (optional maintenance)"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        session = Session()
        deleted = session.query(AnalysisResult)\
            .filter(AnalysisResult.timestamp < cutoff_date)\
            .delete()
        session.commit()
        session.close()
        return deleted

# Global database instance
db_manager = DatabaseManager()