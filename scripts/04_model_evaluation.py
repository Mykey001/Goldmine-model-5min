"""
Goldmine ML - Script 04: Model Evaluation
Evaluate trained model on test set
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, classification_report, confusion_matrix,
                             roc_auc_score, roc_curve)
import json
import warnings

warnings.filterwarnings('ignore')
print('✅ Imports complete!')

# ============================================================================
# 1. LOAD MODEL & DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING MODEL & TEST DATA')
print('='*60)

# Load model
model = joblib.load('models/final/xgboost_model.pkl')
print('✅ Model loaded')

# Load test data
test = pd.read_parquet('data/features/test.parquet')
print(f'✅ Test data loaded: {test.shape}')

# Prepare features
exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 'date', 'time']
feature_cols = [c for c in test.columns if c not in exclude_cols]

X_test = test[feature_cols]
y_test = test['label']

# Filter NO_TRADE
test_mask = y_test != -1
X_test_filtered = X_test[test_mask]
y_test_filtered = y_test[test_mask]

print(f'\nTest set (filtered):')
print(f'Samples: {len(X_test_filtered):,}')
print(f'SELL: {sum(y_test_filtered==0):,}, BUY: {sum(y_test_filtered==1):,}')

# ============================================================================
# 2. GENERATE PREDICTIONS
# ============================================================================
print('\n' + '='*60)
print('GENERATING PREDICTIONS')
print('='*60)

y_pred = model.predict(X_test_filtered)
y_prob = model.predict_proba(X_test_filtered)

print('✅ Predictions generated')

# ============================================================================
# 3. CLASSIFICATION METRICS
# ============================================================================
print('\n' + '='*60)
print('CLASSIFICATION METRICS (TEST SET)')
print('='*60)

accuracy = accuracy_score(y_test_filtered, y_pred)
precision = precision_score(y_test_filtered, y_pred, average='weighted')
recall = recall_score(y_test_filtered, y_pred, average='weighted')
f1 = f1_score(y_test_filtered, y_pred, average='weighted')

print(f'\n📊 OVERALL METRICS:')
print(f'Accuracy:  {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'Recall:    {recall:.4f}')
print(f'F1-Score:  {f1:.4f}')

print(f'\n📋 DETAILED REPORT:')
print(classification_report(y_test_filtered, y_pred, 
                           target_names=['SELL', 'BUY']))

# ============================================================================
# 4. CONFUSION MATRIX
# ============================================================================
print('\n' + '='*60)
print('CONFUSION MATRIX')
print('='*60)

cm = confusion_matrix(y_test_filtered, y_pred)
print(f'\n{cm}')

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['SELL', 'BUY'],
            yticklabels=['SELL', 'BUY'])
plt.title('Confusion Matrix - Test Set', fontsize=14, fontweight='bold')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('results/visualizations/confusion_matrix_test.png', dpi=150)
plt.close()

print('✅ Confusion matrix saved')

# ============================================================================
# 5. ROC CURVE
# ============================================================================
print('\n' + '='*60)
print('ROC CURVE')
print('='*60)

# ROC for BUY class
fpr, tpr, thresholds = roc_curve(y_test_filtered, y_prob[:, 1])
roc_auc = roc_auc_score(y_test_filtered, y_prob[:, 1])

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, linewidth=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - BUY Signal', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/visualizations/roc_curve.png', dpi=150)
plt.close()

print(f'ROC-AUC: {roc_auc:.4f}')
print('✅ ROC curve saved')

# ============================================================================
# 6. PREDICTION CONFIDENCE ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('PREDICTION CONFIDENCE ANALYSIS')
print('='*60)

# Confidence scores
confidence = np.max(y_prob, axis=1)

print(f'\nConfidence statistics:')
print(f'Mean: {confidence.mean():.3f}')
print(f'Median: {np.median(confidence):.3f}')
print(f'Min: {confidence.min():.3f}')
print(f'Max: {confidence.max():.3f}')

# Plot confidence distribution
plt.figure(figsize=(10, 5))
plt.hist(confidence, bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('Prediction Confidence')
plt.ylabel('Frequency')
plt.title('Prediction Confidence Distribution', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/visualizations/confidence_distribution.png', dpi=150)
plt.close()

print('✅ Confidence distribution saved')

# ============================================================================
# 7. ERROR ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('ERROR ANALYSIS')
print('='*60)

# Identify errors
errors = (y_test_filtered != y_pred)
print(f'\nTotal errors: {errors.sum():,} ({errors.sum()/len(y_test_filtered)*100:.2f}%)')

# High confidence errors
high_conf_errors = (errors) & (confidence > 0.8)
print(f'High confidence errors (>0.8): {high_conf_errors.sum()}')

# ============================================================================
# 8. SAVE RESULTS
# ============================================================================
print('\n' + '='*60)
print('SAVING RESULTS')
print('='*60)

# Save predictions
results_df = pd.DataFrame({
    'actual': y_test_filtered.values,
    'predicted': y_pred,
    'confidence': confidence,
    'correct': ~errors
})

results_df.to_csv('results/predictions/test_predictions.csv', index=False)
print('✅ Predictions saved')

# Save metrics
test_metrics = {
    'test_set_size': len(X_test_filtered),
    'metrics': {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc)
    },
    'confusion_matrix': cm.tolist(),
    'confidence_stats': {
        'mean': float(confidence.mean()),
        'median': float(np.median(confidence)),
        'min': float(confidence.min()),
        'max': float(confidence.max())
    }
}

with open('results/metrics/test_metrics.json', 'w') as f:
    json.dump(test_metrics, f, indent=2)
print('✅ Test metrics saved')

print('\n🎉 SCRIPT 04 COMPLETE!')
print(f'\n📊 FINAL RESULTS:')
print(f'Accuracy:  {accuracy:.4f}')
print(f'Precision: {precision:.4f}')
print(f'F1-Score:  {f1:.4f}')
print(f'ROC-AUC:   {roc_auc:.4f}')
print('\nNext: Run 05_backtesting.py')


