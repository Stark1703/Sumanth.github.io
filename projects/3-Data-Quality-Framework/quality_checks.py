# Data Quality Framework - Quality Checks Implementation
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================== ENUMS ========================
class CheckType(Enum):
    SCHEMA = 'schema'
    COMPLETENESS = 'completeness'
    UNIQUENESS = 'uniqueness'
    VALIDITY = 'validity'
    CONSISTENCY = 'consistency'
    ACCURACY = 'accuracy'
    TIMELINESS = 'timeliness'

class CheckStatus(Enum):
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    WARNING = 'WARNING'

# ======================== DATA CLASSES ========================
@dataclass
class CheckResult:
    check_name: str
    check_type: CheckType
    status: CheckStatus
    rows_passed: int
    rows_failed: int
    percentage_passed: float
    error_message: str = None
    timestamp: datetime = None
    
    def to_dict(self):
        return {
            'check_name': self.check_name,
            'check_type': self.check_type.value,
            'status': self.status.value,
            'rows_passed': self.rows_passed,
            'rows_failed': self.rows_failed,
            'percentage_passed': self.percentage_passed,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# ======================== QUALITY CHECKS ========================
class DataQualityChecker:
    def __init__(self, df, threshold=0.95):
        self.df = df
        self.threshold = threshold  # 95% pass rate required
        self.results = []
        
    def check_schema(self, schema_dict):
        """Validate data types match expected schema"""
        logger.info("Running schema validation...")
        failed_count = 0
        
        try:
            for column, expected_type in schema_dict.items():
                if column not in self.df.columns:
                    logger.error(f"Missing column: {column}")
                    failed_count += 1
                elif str(self.df[column].dtype) != expected_type:
                    logger.warning(f"Type mismatch for {column}: expected {expected_type}, got {self.df[column].dtype}")
                    failed_count += 1
            
            passed = len(self.df.columns) - failed_count
            result = CheckResult(
                check_name='Schema Validation',
                check_type=CheckType.SCHEMA,
                status=CheckStatus.PASSED if failed_count == 0 else CheckStatus.FAILED,
                rows_passed=passed,
                rows_failed=failed_count,
                percentage_passed=(passed / len(self.df.columns)) * 100,
                timestamp=datetime.now()
            )
            self.results.append(result)
            return result
        except Exception as e:
            logger.error(f"Error in schema check: {str(e)}")
            return None
    
    def check_completeness(self, required_columns):
        """Check for missing values in critical columns"""
        logger.info("Running completeness check...")
        
        null_counts = self.df[required_columns].isnull().sum()
        total_nulls = null_counts.sum()
        total_cells = len(self.df) * len(required_columns)
        
        result = CheckResult(
            check_name='Completeness Check',
            check_type=CheckType.COMPLETENESS,
            status=CheckStatus.PASSED if total_nulls == 0 else CheckStatus.FAILED,
            rows_passed=total_cells - total_nulls,
            rows_failed=total_nulls,
            percentage_passed=((total_cells - total_nulls) / total_cells) * 100,
            error_message=f"Null values by column: {null_counts.to_dict()}",
            timestamp=datetime.now()
        )
        self.results.append(result)
        return result
    
    def check_uniqueness(self, columns):
        """Check for duplicate values"""
        logger.info(f"Running uniqueness check on {columns}...")
        
        duplicates = self.df.duplicated(subset=columns, keep=False).sum()
        unique_rows = len(self.df) - duplicates
        
        result = CheckResult(
            check_name=f'Uniqueness Check ({columns})',
            check_type=CheckType.UNIQUENESS,
            status=CheckStatus.PASSED if duplicates == 0 else CheckStatus.FAILED,
            rows_passed=unique_rows,
            rows_failed=duplicates,
            percentage_passed=(unique_rows / len(self.df)) * 100,
            timestamp=datetime.now()
        )
        self.results.append(result)
        return result
    
    def check_validity(self, column, valid_values):
        """Check if values are within valid set"""
        logger.info(f"Running validity check on {column}...")
        
        valid_mask = self.df[column].isin(valid_values)
        invalid_count = (~valid_mask).sum()
        
        result = CheckResult(
            check_name=f'Validity Check ({column})',
            check_type=CheckType.VALIDITY,
            status=CheckStatus.PASSED if invalid_count == 0 else CheckStatus.FAILED,
            rows_passed=valid_mask.sum(),
            rows_failed=invalid_count,
            percentage_passed=(valid_mask.sum() / len(self.df)) * 100,
            error_message=f"Invalid values: {self.df[~valid_mask][column].unique().tolist()}",
            timestamp=datetime.now()
        )
        self.results.append(result)
        return result
    
    def check_consistency(self, column1, column2, condition):
        """Check logical consistency between columns"""
        logger.info(f"Running consistency check between {column1} and {column2}...")
        
        # Example: if column1 > 0, then column2 should not be null
        inconsistent = ~condition(self.df)
        inconsistent_count = inconsistent.sum()
        
        result = CheckResult(
            check_name=f'Consistency Check ({column1} vs {column2})',
            check_type=CheckType.CONSISTENCY,
            status=CheckStatus.PASSED if inconsistent_count == 0 else CheckStatus.FAILED,
            rows_passed=len(self.df) - inconsistent_count,
            rows_failed=inconsistent_count,
            percentage_passed=((len(self.df) - inconsistent_count) / len(self.df)) * 100,
            timestamp=datetime.now()
        )
        self.results.append(result)
        return result
    
    def check_range(self, column, min_val, max_val):
        """Check if values are within acceptable range"""
        logger.info(f"Running range check on {column}: [{min_val}, {max_val}]...")
        
        in_range = (self.df[column] >= min_val) & (self.df[column] <= max_val)
        out_of_range = (~in_range).sum()
        
        result = CheckResult(
            check_name=f'Range Check ({column})',
            check_type=CheckType.VALIDITY,
            status=CheckStatus.PASSED if out_of_range == 0 else CheckStatus.FAILED,
            rows_passed=in_range.sum(),
            rows_failed=out_of_range,
            percentage_passed=(in_range.sum() / len(self.df)) * 100,
            error_message=f"Min: {self.df[column].min()}, Max: {self.df[column].max()}",
            timestamp=datetime.now()
        )
        self.results.append(result)
        return result
    
    def check_anomalies(self, column, method='zscore', threshold=3):
        """Detect anomalies using statistical methods"""
        logger.info(f"Running anomaly detection on {column} using {method}...")
        
        if method == 'zscore':
            z_scores = np.abs((self.df[column] - self.df[column].mean()) / self.df[column].std())
            anomalies = (z_scores > threshold).sum()
        elif method == 'iqr':
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            anomalies = ((self.df[column] < Q1 - 1.5 * IQR) | (self.df[column] > Q3 + 1.5 * IQR)).sum()
        
        result = CheckResult(
            check_name=f'Anomaly Detection ({column})',
            check_type=CheckType.ACCURACY,
            status=CheckStatus.WARNING if anomalies > 0 else CheckStatus.PASSED,
            rows_passed=len(self.df) - anomalies,
            rows_failed=anomalies,
            percentage_passed=((len(self.df) - anomalies) / len(self.df)) * 100,
            error_message=f"Found {anomalies} anomalies using {method}",
            timestamp=datetime.now()
        )
        self.results.append(result)
        return result
    
    def generate_report(self):
        """Generate quality report"""
        logger.info("Generating quality report...")
        
        report = {
            'total_checks': len(self.results),
            'passed_checks': sum(1 for r in self.results if r.status == CheckStatus.PASSED),
            'failed_checks': sum(1 for r in self.results if r.status == CheckStatus.FAILED),
            'warning_checks': sum(1 for r in self.results if r.status == CheckStatus.WARNING),
            'overall_status': 'PASSED' if all(r.status != CheckStatus.FAILED for r in self.results) else 'FAILED',
            'timestamp': datetime.now().isoformat(),
            'checks': [r.to_dict() for r in self.results]
        }
        
        return report

# ======================== EXAMPLE USAGE ========================
if __name__ == "__main__":
    # Create sample data
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['John', 'Jane', None, 'Bob', 'Alice'],
        'amount': [100, 200, 150, 2000, 75],
        'status': ['active', 'inactive', 'active', 'active', 'pending']
    })
    
    # Initialize checker
    checker = DataQualityChecker(df)
    
    # Run checks
    checker.check_schema({'id': 'int64', 'name': 'object', 'amount': 'int64'})
    checker.check_completeness(['id', 'name', 'amount'])
    checker.check_uniqueness(['id'])
    checker.check_validity('status', ['active', 'inactive', 'pending'])
    checker.check_range('amount', 0, 1000)
    checker.check_anomalies('amount', method='iqr')
    
    # Generate report
    report = checker.generate_report()
    print(json.dumps(report, indent=2))
