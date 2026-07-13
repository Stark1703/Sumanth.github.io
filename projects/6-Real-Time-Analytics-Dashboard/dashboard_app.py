# Real-Time Analytics Dashboard - Flask Application
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from sqlalchemy import create_engine
import logging
import json
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database connection
DB_URL = 'postgresql://user:password@localhost:5432/analytics_db'
engine = create_engine(DB_URL)

# ======================== DATA LAYER ========================
class DataService:
    def __init__(self, engine):
        self.engine = engine
    
    @lru_cache(maxsize=128)
    def get_kpi_metrics(self, days=30):
        """Fetch KPI metrics"""
        query = f"""
        SELECT 
            DATE_TRUNC('day', transaction_date) as date,
            COUNT(*) as transaction_count,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_transaction,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM transactions
        WHERE transaction_date >= NOW() - INTERVAL '{days} days'
        GROUP BY DATE_TRUNC('day', transaction_date)
        ORDER BY date DESC;
        """
        try:
            df = pd.read_sql(query, self.engine)
            logger.info(f"Fetched KPI metrics for {days} days")
            return df
        except Exception as e:
            logger.error(f"Error fetching KPI metrics: {str(e)}")
            return None
    
    def get_sales_by_category(self, limit=10):
        """Get sales breakdown by category"""
        query = f"""
        SELECT 
            p.category,
            COUNT(*) as sale_count,
            SUM(t.amount) as total_sales,
            AVG(t.amount) as avg_sale
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        WHERE t.transaction_date >= NOW() - INTERVAL '30 days'
        GROUP BY p.category
        ORDER BY total_sales DESC
        LIMIT {limit};
        """
        try:
            df = pd.read_sql(query, self.engine)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching sales by category: {str(e)}")
            return []
    
    def get_customer_segments(self):
        """Get customer segmentation"""
        query = """
        SELECT 
            CASE 
                WHEN lifetime_value > 1000 THEN 'VIP'
                WHEN lifetime_value > 500 THEN 'Premium'
                WHEN lifetime_value > 100 THEN 'Regular'
                ELSE 'New'
            END as segment,
            COUNT(*) as customer_count,
            AVG(lifetime_value) as avg_value,
            AVG(purchase_frequency) as avg_frequency
        FROM customer_metrics
        GROUP BY segment;
        """
        try:
            df = pd.read_sql(query, self.engine)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching customer segments: {str(e)}")
            return []
    
    def get_real_time_stats(self):
        """Get real-time statistics"""
        query = """
        SELECT 
            (SELECT COUNT(*) FROM transactions WHERE transaction_date >= NOW() - INTERVAL '1 hour') as transactions_last_hour,
            (SELECT COUNT(DISTINCT customer_id) FROM transactions WHERE transaction_date >= NOW() - INTERVAL '1 hour') as active_customers,
            (SELECT SUM(amount) FROM transactions WHERE transaction_date >= NOW() - INTERVAL '1 hour') as revenue_last_hour,
            (SELECT AVG(amount) FROM transactions WHERE transaction_date >= NOW() - INTERVAL '1 hour') as avg_transaction_size
        """
        try:
            df = pd.read_sql(query, self.engine)
            return df.to_dict('records')[0]
        except Exception as e:
            logger.error(f"Error fetching real-time stats: {str(e)}")
            return {}

# ======================== API ENDPOINTS ========================
@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    """Get KPI metrics"""
    days = request.args.get('days', 30, type=int)
    service = DataService(engine)
    data = service.get_kpi_metrics(days)
    
    if data is not None:
        return jsonify({
            'status': 'success',
            'data': data.to_dict('records')
        })
    return jsonify({'status': 'error'}), 500

@app.route('/api/sales-by-category', methods=['GET'])
def get_sales_by_category():
    """Get sales by category"""
    service = DataService(engine)
    data = service.get_sales_by_category(limit=10)
    
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/customer-segments', methods=['GET'])
def get_customer_segments():
    """Get customer segments"""
    service = DataService(engine)
    data = service.get_customer_segments()
    
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/real-time-stats', methods=['GET'])
def get_real_time_stats():
    """Get real-time statistics"""
    service = DataService(engine)
    data = service.get_real_time_stats()
    
    return jsonify({
        'status': 'success',
        'data': data
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """Serve dashboard homepage"""
    return render_template('dashboard.html')

# ======================== ERROR HANDLING ========================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
