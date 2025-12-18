"""
Model Evaluation Script - Simplified Version
Calculates precision, recall, F1-score and plots bar graphs
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score, 
    f1_score, accuracy_score
)
import seaborn as sns
from pathlib import Path

# Configure plotting
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

class ModelEvaluator:
    def __init__(self, output_dir="evaluation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_sample_data(self, n=200):
        """Generate sample predictions"""
        np.random.seed(42)
        y_true = np.random.randint(0, 2, n)
        y_pred = y_true.copy()
        error_idx = np.random.choice(n, size=int(0.15*n), replace=False)
        y_pred[error_idx] = 1 - y_pred[error_idx]
        return y_true, y_pred
    
    def calculate_metrics(self, y_true, y_pred):
        """Calculate evaluation metrics"""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        metrics = {
            'Accuracy': accuracy_score(y_true, y_pred),
            'Precision': precision_score(y_true, y_pred),
            'Recall': recall_score(y_true, y_pred),
            'F1-Score': f1_score(y_true, y_pred),
            'Specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'Sensitivity': tp / (tp + fn) if (tp + fn) > 0 else 0,
        }
        
        counts = {
            'True Positives': tp,
            'True Negatives': tn,
            'False Positives': fp,
            'False Negatives': fn,
        }
        
        return metrics, counts, confusion_matrix(y_true, y_pred)
    
    def plot_metrics_bar(self, metrics):
        """Plot metrics as bar chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        names = list(metrics.keys())
        values = list(metrics.values())
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        bars = ax.bar(names, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Metrics', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path = self.output_dir / 'metrics_bar_chart.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {path}")
        plt.close()
    
    def plot_confusion_matrix(self, cm):
        """Plot confusion matrix"""
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Not Relevant', 'Relevant'],
                   yticklabels=['Not Relevant', 'Relevant'],
                   cbar_kws={'label': 'Count'}, ax=ax)
        ax.set_xlabel('Predicted', fontsize=12, fontweight='bold')
        ax.set_ylabel('True', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        path = self.output_dir / 'confusion_matrix.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {path}")
        plt.close()
    
    def plot_confusion_breakdown(self, counts):
        """Plot TP/TN/FP/FN breakdown"""
        fig, ax = plt.subplots(figsize=(10, 6))
        names = list(counts.keys())
        values = list(counts.values())
        colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
        
        bars = ax.bar(names, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=12)
        
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix Breakdown', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path = self.output_dir / 'confusion_breakdown.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {path}")
        plt.close()
    
    def print_report(self, metrics, counts):
        """Print metrics report"""
        report = f"""
{'='*70}
MODEL EVALUATION REPORT
{'='*70}

📊 MAIN METRICS:
  • Accuracy:      {metrics['Accuracy']:.4f}  (overall correctness)
  • Precision:     {metrics['Precision']:.4f}  (positive prediction accuracy)
  • Recall:        {metrics['Recall']:.4f}  (catch all positives)
  • F1-Score:      {metrics['F1-Score']:.4f}  (balance precision & recall)
  • Specificity:   {metrics['Specificity']:.4f}  (true negative rate)
  • Sensitivity:   {metrics['Sensitivity']:.4f}  (true positive rate)

🎯 CONFUSION MATRIX:
  • True Positives (TP):   {counts['True Positives']:>3}  ✅ Correctly identified relevant
  • True Negatives (TN):   {counts['True Negatives']:>3}  ✅ Correctly identified not relevant
  • False Positives (FP):  {counts['False Positives']:>3}  ❌ Incorrectly marked as relevant
  • False Negatives (FN):  {counts['False Negatives']:>3}  ❌ Missed relevant items

📈 INTERPRETATION:
  • Precision: {metrics['Precision']:.1%} of predicted emails are actually relevant
  • Recall: {metrics['Recall']:.1%} of actual relevant emails are found
  • F1-Score balances precision and recall

{'='*70}
"""
        print(report)
        
        # Save report
        path = self.output_dir / 'report.txt'
        with open(path, 'w') as f:
            f.write(report)
        print(f"\n✅ Report saved to: {path}")
    
    def run(self):
        """Run complete evaluation"""
        print("\n🚀 Starting Model Evaluation...\n")
        
        # Generate data
        y_true, y_pred = self.generate_sample_data()
        
        # Calculate metrics
        metrics, counts, cm = self.calculate_metrics(y_true, y_pred)
        
        # Print report
        self.print_report(metrics, counts)
        
        # Generate plots
        print("\n📊 Generating visualizations...")
        self.plot_metrics_bar(metrics)
        self.plot_confusion_matrix(cm)
        self.plot_confusion_breakdown(counts)
        
        print(f"\n✅ All files saved to: {self.output_dir.absolute()}\n")

if __name__ == "__main__":
    evaluator = ModelEvaluator()
    evaluator.run()
