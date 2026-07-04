"""
Goldmine ML - Script 03: Model Training
Train XGBoost classifier for entry signals
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, classification_report, confusion_matrix)
import joblib
import json
import warnings
import os

warnings.filterwarnings('ignore')
print('✅ Imports complete!')

# ============================================================================
# 1. LOAD FEATURE DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING FEATURE DATA')
print('='*60)

train = pd.read_parquet('data/features/train.parquet')
val = pd.read_parquet('data/features/val.parquet')
test = pd.read_parquet('data/features/test.parquet')

print(f'Train: {train.shape}')
print(f'Val:   {val.shape}')
print(f'Test:  {test.shape}')

# ============================================================================
# 2. PREPARE FEATURES & LABELS
# ============================================================================
print('\n' + '='*60)
print('PREPARING FEATURES & LABELS')
print('='*60)

# Define feature columns (exclude non-predictive columns)
exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 'date', 'time']
feature_cols = [c for c in train.columns if c not in exclude_cols]

print(f'Total features: {len(feature_cols)}')
print(f'First 10 features: {feature_cols[:10]}')

# Separate features and labels
X_train = train[feature_cols]
y_train = train['label']

X_val = val[feature_cols]
y_val = val['label']

X_test = test[feature_cols]
y_test = test['label']

# Filter out NO_TRADE (-1) for training
train_mask = y_train != -1
X_train_filtered = X_train[train_mask]
y_train_filtered = y_train[train_mask]

val_mask = y_val != -1
X_val_filtered = X_val[val_mask]
y_val_filtered = y_val[val_mask]

print(f'\nAfter filtering NO_TRADE:')
print(f'Train: {len(X_train_filtered):,} samples')
print(f'  SELL: {sum(y_train_filtered==0):,}, BUY: {sum(y_train_filtered==1):,}')
print(f'Val:   {len(X_val_filtered):,} samples')
print(f'  SELL: {sum(y_val_filtered==0):,}, BUY: {sum(y_val_filtered==1):,}')

# ============================================================================
# 3. BASELINE MODEL: RANDOM FOREST
# ============================================================================
print('\n' + '='*60)
print('TRAINING BASELINE: RANDOM FOREST')
print('='*60)

rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

print('Training Random Forest...')
rf.fit(X_train_filtered, y_train_filtered)

# Evaluate
y_val_pred_rf = rf.predict(X_val_filtered)

print('\n📊 RANDOM FOREST RESULTS (Validation Set):')
print(f'Accuracy:  {accuracy_score(y_val_filtered, y_val_pred_rf):.4f}')
print(f'Precision: {precision_score(y_val_filtered, y_val_pred_rf, average="weighted"):.4f}')
print(f'Recall:    {recall_score(y_val_filtered, y_val_pred_rf, average="weighted"):.4f}')
print(f'F1-Score:  {f1_score(y_val_filtered, y_val_pred_rf, average="weighted"):.4f}')

# ============================================================================
# 4. PRIMARY MODEL: XGBOOST
# ============================================================================
print('\n' + '='*60)
print('TRAINING PRIMARY MODEL: XGBOOST')
print('='*60)

# Initial hyperparameters
xgb_params = {
    'objective': 'binary:logistic',
    'max_depth': 6,
    'learning_rate': 0.01,
    'n_estimators': 500,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'gamma': 0.1,
    'reg_alpha': 0.01,
    'reg_lambda': 1.0,
    'random_state': 42,
    'n_jobs': -1,
    'eval_metric': 'logloss'
}

print('Training XGBoost...')
xgb_model = xgb.XGBClassifier(**xgb_params)

xgb_model.fit(
    X_train_filtered, 
    y_train_filtered,
    eval_set=[(X_val_filtered, y_val_filtered)],
    verbose=50
)

# Evaluate
y_val_pred_xgb = xgb_model.predict(X_val_filtered)
y_val_prob_xgb = xgb_model.predict_proba(X_val_filtered)

print('\n📊 XGBOOST RESULTS (Validation Set):')
print(f'Accuracy:  {accuracy_score(y_val_filtered, y_val_pred_xgb):.4f}')
print(f'Precision: {precision_score(y_val_filtered, y_val_pred_xgb, average="weighted"):.4f}')
print(f'Recall:    {recall_score(y_val_filtered, y_val_pred_xgb, average="weighted"):.4f}')
print(f'F1-Score:  {f1_score(y_val_filtered, y_val_pred_xgb, average="weighted"):.4f}')

print('\n📋 DETAILED CLASSIFICATION REPORT:')
print(classification_report(y_val_filtered, y_val_pred_xgb, 
                           target_names=['SELL', 'BUY']))

# ============================================================================
# 5. FEATURE IMPORTANCE
# ============================================================================
print('\n' + '='*60)
print('FEATURE IMPORTANCE')
print('='*60)

# Get feature importance
importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': xgb_model.feature_importances_
}).sort_values('importance', ascending=False)

print('\nTop 20 Most Important Features:')
print(importance.head(20).to_string(index=False))

# Plot
plt.figure(figsize=(10, 8))
importance.head(20).plot(x='feature', y='importance', kind='barh', figsize=(10, 8))
plt.title('Top 20 Feature Importance', fontsize=14, fontweight='bold')
plt.xlabel('Importance')
plt.tight_layout()
plt.savefig('results/visualizations/feature_importance.png', dpi=150)
plt.close()

print('\n✅ Feature importance chart saved')

# ============================================================================
# 6. CONFUSION MATRIX
# ============================================================================
print('\n' + '='*60)
print('CONFUSION MATRIX')
print('='*60)

cm = confusion_matrix(y_val_filtered, y_val_pred_xgb)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['SELL', 'BUY'],
            yticklabels=['SELL', 'BUY'])
plt.title('Confusion Matrix - XGBoost', fontsize=14, fontweight='bold')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('results/visualizations/confusion_matrix.png', dpi=150)
plt.close()

print('✅ Confusion matrix saved')

# ============================================================================
# 7. SAVE MODEL
# ============================================================================
print('\n' + '='*60)
print('SAVING MODEL')
print('='*60)

os.makedirs('models/final', exist_ok=True)

# Save XGBoost model
model_path = 'models/final/xgboost_model.pkl'
joblib.dump(xgb_model, model_path)
print(f'✅ Model saved: {model_path}')

# Save hyperparameters
params_path = 'models/final/model_params.json'
with open(params_path, 'w') as f:
    json.dump(xgb_params, f, indent=2)
print(f'✅ Parameters saved: {params_path}')

# Save feature importance
importance.to_csv('results/metrics/feature_importance.csv', index=False)
print('✅ Feature importance saved')

# Save metrics
metrics = {
    'model': 'XGBoost',
    'validation_metrics': {
        'accuracy': float(accuracy_score(y_val_filtered, y_val_pred_xgb)),
        'precision': float(precision_score(y_val_filtered, y_val_pred_xgb, average='weighted')),
        'recall': float(recall_score(y_val_filtered, y_val_pred_xgb, average='weighted')),
        'f1_score': float(f1_score(y_val_filtered, y_val_pred_xgb, average='weighted'))
    },
    'n_features': len(feature_cols),
    'training_samples': len(X_train_filtered),
    'validation_samples': len(X_val_filtered)
}

with open('results/metrics/training_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print('✅ Metrics saved')

print('\n🎉 SCRIPT 03 COMPLETE!')
print('Next: Run 04_model_evaluation.py')


