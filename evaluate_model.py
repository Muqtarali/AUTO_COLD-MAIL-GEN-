"""
Model Evaluation Script for Cold Email Generation System
Calculates precision, recall, F1-score, and other metrics
Generates bar graphs for visualization
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    classification_report,
    roc_auc_score,
    roc_curve,
    auc
)
from sklearn.preprocessing import label_binarize
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Configure plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

class ModelEvaluator:
    """Evaluate model performance and generate visualizations"""
    
    def __init__(self, output_dir: str = "evaluation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metrics = {}
        
    def generate_sample_predictions(self, n_samples: int = 200) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate sample true labels and predictions for testing
        In production, replace with actual model predictions
        """
        np.random.seed(42)
        
        # Simulate binary classification (email relevant: 1, not relevant: 0)
        y_true = np.random.randint(0, 2, n_samples)
        
        # Create predictions with some error rate
        y_pred = y_true.copy()
        error_indices = np.random.choice(n_samples, size=int(0.15 * n_samples), replace=False)
        y_pred[error_indices] = 1 - y_pred[error_indices]
        
        return y_true, y_pred
    
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate all evaluation metrics"""
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred),
            'true_positives': np.sum((y_true == 1) & (y_pred == 1)),
            'true_negatives': np.sum((y_true == 0) & (y_pred == 0)),
            'false_positives': np.sum((y_true == 0) & (y_pred == 1)),
            'false_negatives': np.sum((y_true == 1) & (y_pred == 0)),
        }
        
        # Calculate additional metrics
        tn, fp, fn, tp = metrics['confusion_matrix'].ravel()
        metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
        metrics['sensitivity'] = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        self.metrics = metrics
        return metrics
    
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Plot and save confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Not Relevant', 'Relevant'],
                    yticklabels=['Not Relevant', 'Relevant'],
                    cbar_kws={'label': 'Count'})
        plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
        plt.ylabel('True Label', fontsize=12, fontweight='bold')
        plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_path = self.output_dir / 'confusion_matrix.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved confusion matrix to {output_path}")
        plt.close()
    
    def plot_metrics_bar_chart(self):
        """Plot metrics as bar chart"""
        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1', 'specificity', 'sensitivity']
        values = [self.metrics.get(m, 0) for m in metrics_to_plot]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        bars = ax.bar(metrics_to_plot, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Metrics', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = self.output_dir / 'metrics_bar_chart.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved metrics bar chart to {output_path}")
        plt.close()
    
    def plot_roc_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray = None):
        """Plot ROC curve"""
        if y_pred_proba is None:
            # Use predictions as probabilities (0 or 1)
            y_pred_proba = np.vstack([1 - y_pred_proba, y_pred_proba]).T if hasattr(y_pred_proba, '__len__') else None
        
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba if y_pred_proba is not None else y_true)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold')
        plt.ylabel('True Positive Rate', fontsize=12, fontweight='bold')
        plt.title('ROC Curve', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=10)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        output_path = self.output_dir / 'roc_curve.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved ROC curve to {output_path}")
        plt.close()
    
    def plot_confusion_metrics_breakdown(self):
        """Plot TP, TN, FP, FN breakdown"""
        metrics_data = {
            'True Positives': self.metrics['true_positives'],
            'True Negatives': self.metrics['true_negatives'],
            'False Positives': self.metrics['false_positives'],
            'False Negatives': self.metrics['false_negatives'],
        }
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
        bars = ax.bar(metrics_data.keys(), metrics_data.values(), color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix Breakdown', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = self.output_dir / 'confusion_breakdown.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved confusion breakdown to {output_path}")
        plt.close()
    
    def plot_classification_report_heatmap(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Plot classification report as heatmap"""
        report = classification_report(y_true, y_pred, 
                                      target_names=['Not Relevant', 'Relevant'],
                                      output_dict=True)
        
        # Prepare data for heatmap
        metrics_names = ['Precision', 'Recall', 'F1-Score']
        data = []
        for label in ['Not Relevant', 'Relevant']:
            row = [
                report[label]['precision'],
                report[label]['recall'],
                report[label]['f1-score']
            ]
            data.append(row)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(data, annot=True, fmt='.3f', cmap='RdYlGn', 
                   xticklabels=metrics_names,
                   yticklabels=['Not Relevant', 'Relevant'],
                   vmin=0, vmax=1, cbar_kws={'label': 'Score'})
        plt.title('Classification Report Heatmap', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_path = self.output_dir / 'classification_report.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved classification report to {output_path}")
        plt.close()
    
    def generate_metrics_report(self, y_true: np.ndarray, y_pred: np.ndarray):
        """Generate text report of all metrics"""
        report = f"""
{'='*60}
MODEL EVALUATION REPORT
{'='*60}

MAIN METRICS:
  • Accuracy:      {self.metrics['accuracy']:.4f} (overall correctness)
  • Precision:     {self.metrics['precision']:.4f} (positive prediction accuracy)
  • Recall:        {self.metrics['recall']:.4f} (sensitivity - catching positives)
  • F1-Score:      {self.metrics['f1']:.4f} (harmonic mean)
  • Specificity:   {self.metrics['specificity']:.4f} (true negative rate)
  • Sensitivity:   {self.metrics['sensitivity']:.4f} (true positive rate)

CONFUSION MATRIX BREAKDOWN:
  • True Positives (TP):   {self.metrics['true_positives']} (correctly identified relevant)
  • True Negatives (TN):   {self.metrics['true_negatives']} (correctly identified not relevant)
  • False Positives (FP):  {self.metrics['false_positives']} (incorrectly identified as relevant)
  • False Negatives (FN):  {self.metrics['false_negatives']} (missed relevant items)

INTERPRETATION:
  • Precision: {self.metrics['precision']:.1%} of predicted relevant emails are actually relevant
  • Recall: {self.metrics['recall']:.1%} of actual relevant emails are correctly identified
  • F1-Score indicates overall model quality (balance between precision and recall)

RECOMMENDATION:
  {'✅ Model is performing well!' if self.metrics['f1'] > 0.75 else '⚠️  Model needs improvement' if self.metrics['f1'] > 0.5 else '❌ Model needs significant improvement'}

{'='*60}
        """
        
        print(report)
        
        # Save report to file
        output_path = self.output_dir / 'metrics_report.txt'
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"✅ Saved detailed report to {output_path}")
    
    def run_evaluation(self):
        """Run complete evaluation pipeline"""
        print("\n🚀 Starting Model Evaluation...")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        
        # Generate sample predictions
        print("\n📊 Generating sample predictions...")
        y_true, y_pred = self.generate_sample_predictions(n_samples=200)
        
        # Calculate metrics
        print("🧮 Calculating metrics...")
        self.calculate_metrics(y_true, y_pred)
        
        # Generate visualizations
        print("📈 Generating visualizations...")
        self.plot_confusion_matrix(y_true, y_pred)
        self.plot_metrics_bar_chart()
        self.plot_confusion_metrics_breakdown()
        self.plot_classification_report_heatmap(y_true, y_pred)
        self.plot_roc_curve(y_true, y_pred)
        
        # Generate report
        print("📋 Generating detailed report...")
        self.generate_metrics_report(y_true, y_pred)
        
        print("\n✅ Evaluation complete!")
        print(f"📁 All results saved to: {self.output_dir.absolute()}\n")


def main():
    """Main entry point"""
    evaluator = ModelEvaluator(output_dir="evaluation_results")
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()
