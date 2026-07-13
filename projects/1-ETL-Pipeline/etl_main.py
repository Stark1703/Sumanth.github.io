# ETL Pipeline Project - Main Orchestration
import pandas as pd
import logging
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
import psycopg2
from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DB_CONNECTION = 'postgresql://user:password@localhost:5432/etl_db'
engine = create_engine(DB_CONNECTION)

# Default DAG arguments
default_args = {
    'owner': 'data_engineer',
    'start_date': days_ago(1),
    'retries': 2,
    'retry_delay': 300
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL Pipeline for Data Processing',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False
)

# ======================== EXTRACT ========================
def extract_from_csv(file_path):
    """Extract data from CSV file"""
    try:
        logger.info(f"Extracting data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Successfully extracted {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error in extraction: {str(e)}")
        raise

def extract_from_api(api_url, params=None):
    """Extract data from REST API"""
    import requests
    try:
        logger.info(f"Extracting data from API: {api_url}")
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        logger.info(f"Successfully extracted {len(df)} rows from API")
        return df
    except Exception as e:
        logger.error(f"Error extracting from API: {str(e)}")
        raise

def extract_from_database(query):
    """Extract data from source database"""
    try:
        logger.info("Extracting data from source database")
        df = pd.read_sql(query, engine)
        logger.info(f"Successfully extracted {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error extracting from database: {str(e)}")
        raise

# ======================== TRANSFORM ========================
def clean_data(df):
    """Clean and validate data"""
    try:
        logger.info("Starting data cleaning...")
        
        # Remove duplicates
        df = df.drop_duplicates()
        logger.info(f"Removed duplicates. Current rows: {len(df)}")
        
        # Handle missing values
        df = df.fillna(df.median(numeric_only=True))
        logger.info("Filled missing numerical values")
        
        # Remove rows with critical null values
        critical_columns = ['id', 'date', 'amount']
        df = df.dropna(subset=critical_columns)
        logger.info(f"After removing null rows: {len(df)} rows")
        
        return df
    except Exception as e:
        logger.error(f"Error in data cleaning: {str(e)}")
        raise

def transform_data(df):
    """Transform data for analytics"""
    try:
        logger.info("Starting data transformation...")
        
        # Convert date columns
        df['date'] = pd.to_datetime(df['date'])
        
        # Create new features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        
        # Aggregate metrics
        df['amount_category'] = pd.cut(df['amount'], 
                                       bins=[0, 100, 500, 1000, float('inf')],
                                       labels=['Low', 'Medium', 'High', 'VeryHigh'])
        
        # Remove outliers using IQR method
        Q1 = df['amount'].quantile(0.25)
        Q3 = df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        df = df[~((df['amount'] < (Q1 - 1.5 * IQR)) | (df['amount'] > (Q3 + 1.5 * IQR)))]
        
        logger.info(f"Transformed data shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error in data transformation: {str(e)}")
        raise

# ======================== LOAD ========================
def load_to_database(df, table_name):
    """Load transformed data to database"""
    try:
        logger.info(f"Loading {len(df)} rows to table: {table_name}")
        
        # Use truncate for full refresh or append for incremental
        df.to_sql(table_name, engine, if_exists='append', index=False)
        
        logger.info(f"Successfully loaded data to {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def data_quality_check(df, table_name):
    """Validate data quality"""
    try:
        logger.info(f"Performing data quality checks for {table_name}")
        
        checks = {
            'total_rows': len(df),
            'null_count': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'columns': len(df.columns)
        }
        
        if checks['null_count'] > 0:
            logger.warning(f"Found {checks['null_count']} null values")
        
        logger.info(f"Quality checks: {checks}")
        return checks
    except Exception as e:
        logger.error(f"Error in quality check: {str(e)}")
        raise

# ======================== AIRFLOW TASKS ========================
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract_from_csv,
    op_kwargs={'file_path': '/data/raw_data.csv'},
    dag=dag
)

task_clean = PythonOperator(
    task_id='clean_data',
    python_callable=clean_data,
    dag=dag
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

task_load = PythonOperator(
    task_id='load_to_db',
    python_callable=load_to_database,
    op_kwargs={'table_name': 'processed_data'},
    dag=dag
)

task_quality = PythonOperator(
    task_id='quality_check',
    python_callable=data_quality_check,
    dag=dag
)

# Set dependencies
task_extract >> task_clean >> task_transform >> task_load >> task_quality
