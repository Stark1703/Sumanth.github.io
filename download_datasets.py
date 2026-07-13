#!/usr/bin/env python3
"""
Download real-world datasets for all portfolio projects
This script fetches datasets from various sources for demonstration purposes
"""

import os
import pandas as pd
import requests
import json
from pathlib import Path

# Create data directories
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

print("🔄 Downloading real-world datasets for portfolio projects...\n")

# ======================== PROJECT 1: ETL Pipeline ========================
print("📥 1. ETL Pipeline Project - Sample Transaction Data")
try:
    # Create sample transaction data for ETL pipeline demonstration
    etl_data = {
        'transaction_id': range(1, 1001),
        'customer_id': [f'CUST{i%100:03d}' for i in range(1, 1001)],
        'amount': [round(__import__('random').uniform(10, 5000), 2) for _ in range(1000)],
        'transaction_date': pd.date_range('2024-01-01', periods=1000, freq='H'),
        'product_id': [f'PROD{i%50:03d}' for i in range(1, 1001)],
        'status': [__import__('random').choice(['completed', 'pending', 'failed']) for _ in range(1000)]
    }
    etl_df = pd.DataFrame(etl_data)
    etl_df.to_csv('data/raw/transactions_sample.csv', index=False)
    print("   ✓ transactions_sample.csv (1000 rows)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# ======================== PROJECT 2: Data Quality Framework ========================
print("\n📥 2. Data Quality Framework - Customer Dataset")
try:
    quality_data = {
        'customer_id': range(1, 501),
        'customer_name': [f'Customer_{i}' for i in range(1, 501)],
        'email': [f'customer{i}@example.com' for i in range(1, 501)],
        'signup_date': pd.date_range('2023-01-01', periods=500, freq='D'),
        'city': [__import__('random').choice(['NYC', 'LA', 'Chicago', 'Houston', 'Phoenix']) for _ in range(500)],
        'status': [__import__('random').choice(['active', 'inactive', 'suspended']) for _ in range(500)],
        'lifetime_value': [round(__import__('random').uniform(100, 10000), 2) for _ in range(500)]
    }
    quality_df = pd.DataFrame(quality_data)
    quality_df.to_csv('data/raw/customers.csv', index=False)
    print("   ✓ customers.csv (500 rows)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# ======================== PROJECT 3: SQL Optimization ========================
print("\n📥 3. Advanced SQL Optimization - Sales Orders")
try:
    orders_data = {
        'order_id': range(1, 5001),
        'customer_id': [f'CUST{i%500:04d}' for i in range(1, 5001)],
        'order_date': pd.date_range('2023-01-01', periods=5000, freq='6H'),
        'amount': [round(__import__('random').uniform(50, 5000), 2) for _ in range(5000)],
        'order_status': [__import__('random').choice(['completed', 'pending', 'cancelled', 'shipped']) for _ in range(5000)],
        'product_category': [__import__('random').choice(['Electronics', 'Clothing', 'Books', 'Food', 'Sports']) for _ in range(5000)]
    }
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_csv('data/raw/orders.csv', index=False)
    print("   ✓ orders.csv (5000 rows)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# ======================== PROJECT 4: Predictive Analytics ML ========================
print("\n📥 4. Predictive Analytics - Customer Churn Dataset")
try:
    import random
    ml_data = {
        'customer_id': range(1, 1001),
        'age': [random.randint(18, 80) for _ in range(1000)],
        'tenure_months': [random.randint(1, 72) for _ in range(1000)],
        'monthly_charges': [round(random.uniform(20, 150), 2) for _ in range(1000)],
        'total_charges': [round(random.uniform(100, 10000), 2) for _ in range(1000)],
        'internet_service': [random.choice(['Fiber optic', 'DSL', 'No']) for _ in range(1000)],
        'contract_type': [random.choice(['Month-to-month', 'One year', 'Two year']) for _ in range(1000)],
        'churn': [random.choice([0, 1]) for _ in range(1000)]
    }
    ml_df = pd.DataFrame(ml_data)
    ml_df.to_csv('data/raw/customer_churn.csv', index=False)
    print("   ✓ customer_churn.csv (1000 rows)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# ======================== PROJECT 5: Real-Time Dashboard ========================
print("\n📥 5. Real-Time Dashboard - Time Series Data")
try:
    import numpy as np
    dashboard_data = {
        'timestamp': pd.date_range('2024-01-01', periods=2880, freq='5min'),
        'transactions': np.random.poisson(50, 2880),
        'revenue': np.random.uniform(1000, 5000, 2880),
        'active_users': np.random.poisson(200, 2880),
        'page_views': np.random.poisson(500, 2880),
        'bounce_rate': np.random.uniform(20, 80, 2880)
    }
    dashboard_df = pd.DataFrame(dashboard_data)
    dashboard_df.to_csv('data/raw/real_time_metrics.csv', index=False)
    print("   ✓ real_time_metrics.csv (2880 rows)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# ======================== Download External Datasets ========================
print("\n📥 6. Downloading External Datasets...")

# UCI Machine Learning Repository - Iris Dataset
try:
    print("   Fetching: Iris Dataset (Kaggle)")
    iris_url = "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv"
    iris_df = pd.read_csv(iris_url)
    iris_df.to_csv('data/raw/iris.csv', index=False)
    print("   ✓ iris.csv")
except Exception as e:
    print(f"   ✗ Iris Dataset: {e}")

# Wine Quality Dataset
try:
    print("   Fetching: Wine Quality Dataset")
    wine_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    wine_df = pd.read_csv(wine_url, sep=';')
    wine_df.to_csv('data/raw/wine_quality.csv', index=False)
    print("   ✓ wine_quality.csv")
except Exception as e:
    print(f"   ✗ Wine Quality Dataset: {e}")

# Titanic Dataset
try:
    print("   Fetching: Titanic Dataset")
    titanic_url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    titanic_df = pd.read_csv(titanic_url)
    titanic_df.to_csv('data/raw/titanic.csv', index=False)
    print("   ✓ titanic.csv")
except Exception as e:
    print(f"   ✗ Titanic Dataset: {e}")

# ======================== Create Data Dictionary ========================
print("\n📋 Creating Data Dictionary...")
data_dictionary = {
    "datasets": {
        "transactions_sample.csv": {
            "description": "Sample transaction data for ETL Pipeline project",
            "rows": 1000,
            "columns": ["transaction_id", "customer_id", "amount", "transaction_date", "product_id", "status"],
            "use_case": "ETL Pipeline demonstration"
        },
        "customers.csv": {
            "description": "Customer data for Data Quality Framework",
            "rows": 500,
            "columns": ["customer_id", "customer_name", "email", "signup_date", "city", "status", "lifetime_value"],
            "use_case": "Data quality checks and validation"
        },
        "orders.csv": {
            "description": "Sales orders for SQL Optimization",
            "rows": 5000,
            "columns": ["order_id", "customer_id", "order_date", "amount", "order_status", "product_category"],
            "use_case": "Query optimization and performance tuning"
        },
        "customer_churn.csv": {
            "description": "Customer churn data for Predictive Analytics",
            "rows": 1000,
            "columns": ["customer_id", "age", "tenure_months", "monthly_charges", "total_charges", "internet_service", "contract_type", "churn"],
            "use_case": "Machine learning and churn prediction"
        },
        "real_time_metrics.csv": {
            "description": "Real-time website metrics for Dashboard",
            "rows": 2880,
            "columns": ["timestamp", "transactions", "revenue", "active_users", "page_views", "bounce_rate"],
            "use_case": "Real-time analytics dashboard"
        },
        "iris.csv": {
            "description": "Classic Iris flower classification dataset",
            "rows": 150,
            "use_case": "Classification and EDA demonstrations"
        },
        "wine_quality.csv": {
            "description": "Wine quality dataset with physicochemical properties",
            "rows": 1599,
            "use_case": "Regression and quality prediction"
        },
        "titanic.csv": {
            "description": "Titanic passenger survival data",
            "rows": 891,
            "use_case": "Classification and feature engineering"
        }
    }
}

with open('data/DATA_DICTIONARY.json', 'w') as f:
    json.dump(data_dictionary, f, indent=2)
print("   ✓ DATA_DICTIONARY.json")

# ======================== Create README for datasets ========================
readme_content = """# Portfolio Project Datasets

This directory contains datasets for the portfolio projects. All datasets are for educational and demonstration purposes.

## Dataset Sources

### Generated Datasets (Synthetic)
- `transactions_sample.csv` - Sample transaction data (ETL Pipeline)
- `customers.csv` - Customer information (Data Quality Framework)
- `orders.csv` - Sales orders (SQL Optimization)
- `customer_churn.csv` - Customer churn data (Predictive Analytics)
- `real_time_metrics.csv` - Real-time website metrics (Dashboard)

### External Datasets (Open Source)
- `iris.csv` - Iris flower dataset (UCI ML Repository)
- `wine_quality.csv` - Wine quality dataset (UCI ML Repository)
- `titanic.csv` - Titanic survivor data (Public Domain)

## How to Use

### For ETL Pipeline Project
```python
import pandas as pd
df = pd.read_csv('data/raw/transactions_sample.csv')
```

### For Data Quality Framework
```python
from quality_checks import DataQualityChecker
df = pd.read_csv('data/raw/customers.csv')
checker = DataQualityChecker(df)
```

### For SQL Optimization
```sql
-- Import to your database
COPY orders FROM 'data/raw/orders.csv' WITH (FORMAT csv, HEADER);
```

### For Predictive Analytics
```python
from sklearn.model_selection import train_test_split
df = pd.read_csv('data/raw/customer_churn.csv')
X_train, X_test, y_train, y_test = train_test_split(df.drop('churn', axis=1), df['churn'])
```

### For Dashboard
```python
df = pd.read_csv('data/raw/real_time_metrics.csv')
# Use for real-time visualization
```

## Data Statistics

| Dataset | Rows | Columns | Size | Use Case |
|---------|------|---------|------|----------|
| transactions_sample | 1,000 | 6 | ~45 KB | ETL Pipeline |
| customers | 500 | 7 | ~25 KB | Data Quality |
| orders | 5,000 | 6 | ~250 KB | SQL Optimization |
| customer_churn | 1,000 | 8 | ~50 KB | ML/Churn Prediction |
| real_time_metrics | 2,880 | 6 | ~150 KB | Real-time Dashboard |
| iris | 150 | 5 | ~5 KB | Classification |
| wine_quality | 1,599 | 12 | ~90 KB | Regression |
| titanic | 891 | 12 | ~60 KB | Classification |

## Data Privacy

- All synthetic datasets are randomly generated
- External datasets are from public repositories
- No sensitive personal information is included
- All datasets are free for educational use

## Preprocessing Notes

Before using datasets in your projects:

1. **Check for missing values**
   ```python
   df.isnull().sum()
   ```

2. **Validate data types**
   ```python
   df.dtypes
   ```

3. **Handle outliers**
   ```python
   df.describe()
   ```

4. **Normalize/Scale if needed**
   ```python
   from sklearn.preprocessing import StandardScaler
   ```

## Additional Resources

- [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/)
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Data.gov](https://www.data.gov/)

---
Last Updated: July 2024
"""

with open('data/README.md', 'w') as f:
    f.write(readme_content)
print("   ✓ README.md")

# ======================== Summary ========================
print("\n" + "="*50)
print("✅ Dataset Download Complete!")
print("="*50)
print("\n📊 Summary:")
print("   Total datasets created/downloaded: 8")
print("   Location: data/raw/")
print("   Formats: CSV, JSON")
print("\n📁 Next Steps:")
print("   1. Load data using pandas: pd.read_csv('data/raw/<filename>.csv')")
print("   2. Review DATA_DICTIONARY.json for column descriptions")
print("   3. Check README.md for usage examples")
print("   4. Start implementing projects!")
print("\n💡 Tips:")
print("   - Use data/raw/ for raw data")
print("   - Use data/processed/ for cleaned/processed data")
print("   - Version control your data pipelines")
print("   - Document data transformations")

