# Predictive Analytics with Machine Learning - End-to-End Pipeline
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================== DATA LOADING & EXPLORATION ========================
class DataLoader:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        logger.info(f"Dataset loaded: {self.df.shape}")
    
    def exploratory_analysis(self):
        """Perform EDA"""
        logger.info("=== EXPLORATORY DATA ANALYSIS ===")
        
        # Basic statistics
        logger.info(f"Dataset shape: {self.df.shape}")
        logger.info(f"\nData types:\n{self.df.dtypes}")
        logger.info(f"\nMissing values:\n{self.df.isnull().sum()}")
        logger.info(f"\nBasic statistics:\n{self.df.describe()}")
        
        # Correlation analysis
        correlation = self.df.corr(numeric_only=True)
        logger.info(f"\nTop correlations:\n{correlation.iloc[:, 0].sort_values(ascending=False)[1:6]}")
        
        # Class distribution (for classification)
        if 'target' in self.df.columns:
            logger.info(f"\nClass distribution:\n{self.df['target'].value_counts()}")
        
        return self.df
    
    def handle_missing_values(self, strategy='mean'):
        """Handle missing values"""
        logger.info(f"Handling missing values with strategy: {strategy}")
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        # Numeric columns
        for col in numeric_cols:
            if self.df[col].isnull().sum() > 0:
                if strategy == 'mean':
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                elif strategy == 'median':
                    self.df[col].fillna(self.df[col].median(), inplace=True)
        
        # Categorical columns
        for col in categorical_cols:
            if self.df[col].isnull().sum() > 0:
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)
        
        logger.info(f"Missing values after handling: {self.df.isnull().sum().sum()}")
        return self.df

# ======================== FEATURE ENGINEERING ========================
class FeatureEngineer:
    def __init__(self, df):
        self.df = df.copy()
        self.label_encoders = {}
    
    def create_features(self):
        """Create new features"""
        logger.info("Creating new features...")
        
        # Example: Create interaction features
        if 'age' in self.df.columns and 'income' in self.df.columns:
            self.df['age_income_ratio'] = self.df['age'] / (self.df['income'] + 1)
        
        # Example: Create time-based features
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['day_of_week'] = self.df['date'].dt.dayofweek
            self.df['month'] = self.df['date'].dt.month
            self.df['quarter'] = self.df['date'].dt.quarter
        
        # Example: Binning continuous variables
        if 'amount' in self.df.columns:
            self.df['amount_category'] = pd.cut(
                self.df['amount'],
                bins=[0, 100, 500, 1000, float('inf')],
                labels=['Low', 'Medium', 'High', 'VeryHigh']
            )
        
        logger.info(f"Features created. New shape: {self.df.shape}")
        return self.df
    
    def encode_categorical(self):
        """Encode categorical variables"""
        logger.info("Encoding categorical variables...")
        
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if col != 'target':  # Don't encode target yet
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                self.label_encoders[col] = le
        
        logger.info(f"Categorical encoding complete")
        return self.df, self.label_encoders
    
    def select_features(self, method='correlation', threshold=0.1):
        """Select important features"""
        logger.info(f"Selecting features using {method} method...")
        
        if method == 'correlation':
            if 'target' in self.df.columns:
                correlations = self.df.corr()['target'].abs().sort_values(ascending=False)
                selected_features = correlations[correlations > threshold].index.tolist()
                selected_features.remove('target') if 'target' in selected_features else None
                logger.info(f"Selected {len(selected_features)} features")
                return selected_features
        
        return self.df.columns.tolist()

# ======================== MODEL TRAINING ========================
class ModelTrainer:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.models = {}
        self.results = {}
    
    def preprocess_data(self):
        """Standardize features"""
        logger.info("Preprocessing data...")
        
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)
        
        return self.X_train, self.X_test
    
    def train_random_forest(self, n_estimators=100):
        """Train Random Forest model"""
        logger.info("Training Random Forest...")
        
        rf = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        rf.fit(self.X_train, self.y_train)
        
        self.models['random_forest'] = rf
        self._evaluate_model(rf, 'Random Forest')
    
    def train_gradient_boosting(self, n_estimators=100, learning_rate=0.1):
        """Train Gradient Boosting model"""
        logger.info("Training Gradient Boosting...")
        
        gb = GradientBoostingClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42
        )
        gb.fit(self.X_train, self.y_train)
        
        self.models['gradient_boosting'] = gb
        self._evaluate_model(gb, 'Gradient Boosting')
    
    def hyperparameter_tuning(self, model_name='random_forest'):
        """Tune hyperparameters using GridSearchCV"""
        logger.info(f"Tuning hyperparameters for {model_name}...")
        
        if model_name == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10]
            }
            model = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1', n_jobs=-1)
        grid_search.fit(self.X_train, self.y_train)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
        
        self.models[f'{model_name}_tuned'] = grid_search.best_estimator_
        return grid_search.best_estimator_
    
    def _evaluate_model(self, model, model_name):
        """Evaluate model performance"""
        logger.info(f"\n=== {model_name} Evaluation ===")
        
        # Predictions
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]
        
        # Metrics
        accuracy = (y_pred == self.y_test).mean()
        f1 = f1_score(self.y_test, y_pred)
        roc_auc = roc_auc_score(self.y_test, y_pred_proba)
        
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"F1 Score: {f1:.4f}")
        logger.info(f"ROC AUC: {roc_auc:.4f}")
        logger.info(f"\nClassification Report:\n{classification_report(self.y_test, y_pred)}")
        
        self.results[model_name] = {
            'accuracy': accuracy,
            'f1': f1,
            'roc_auc': roc_auc,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
        
        return self.results[model_name]
    
    def save_model(self, model_name, filepath):
        """Save trained model"""
        joblib.dump(self.models[model_name], filepath)
        logger.info(f"Model saved to {filepath}")

# ======================== VISUALIZATION ========================
class ModelVisualizer:
    def __init__(self, results, y_test):
        self.results = results
        self.y_test = y_test
    
    def plot_confusion_matrix(self, y_pred, model_name):
        """Plot confusion matrix"""
        cm = confusion_matrix(self.y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.savefig(f'confusion_matrix_{model_name}.png')
        plt.close()
    
    def plot_roc_curve(self, y_pred_proba, model_name):
        """Plot ROC curve"""
        fpr, tpr, _ = roc_curve(self.y_test, y_pred_proba)
        roc_auc = roc_auc_score(self.y_test, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}')
        plt.legend()
        plt.savefig(f'roc_curve_{model_name}.png')
        plt.close()

# ======================== MAIN PIPELINE ========================
def main():
    # Load data
    loader = DataLoader('data.csv')
    df = loader.exploratory_analysis()
    df = loader.handle_missing_values(strategy='mean')
    
    # Feature engineering
    engineer = FeatureEngineer(df)
    df = engineer.create_features()
    df, encoders = engineer.encode_categorical()
    selected_features = engineer.select_features(method='correlation', threshold=0.1)
    
    # Prepare data
    X = df[selected_features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train models
    trainer = ModelTrainer(X_train, X_test, y_train, y_test)
    trainer.preprocess_data()
    
    trainer.train_random_forest(n_estimators=100)
    trainer.train_gradient_boosting(n_estimators=100)
    
    # Hyperparameter tuning
    best_model = trainer.hyperparameter_tuning('random_forest')
    
    # Save best model
    trainer.save_model('random_forest_tuned', 'best_model.pkl')
    
    logger.info("Pipeline completed!")

if __name__ == "__main__":
    main()
