"""Test DCS vs risk score correlation to verify separation."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.risk_scores import RiskScore


def test_dcs_risk_correlation():
    """Test correlation between DCS and risk scores to verify they are independent."""
    print("=" * 80)
    print("DCS VS RISK SCORE CORRELATION TEST")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Get all risk scores with DCS
        query = session.query(
            RiskScore.composite_score,
            RiskScore.data_confidence_score
        ).filter(
            RiskScore.composite_score.isnot(None),
            RiskScore.data_confidence_score.isnot(None)
        ).all()
        
        if not query:
            print("No risk scores with DCS found in database")
            return
        
        # Extract scores
        risk_scores = [float(r.composite_score) for r in query]
        dcs_scores = [float(r.data_confidence_score) for r in query]
        
        print(f"\nTotal records: {len(risk_scores)}")
        
        # Calculate basic statistics
        import statistics
        
        risk_mean = statistics.mean(risk_scores)
        risk_median = statistics.median(risk_scores)
        risk_std = statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0
        
        dcs_mean = statistics.mean(dcs_scores)
        dcs_median = statistics.median(dcs_scores)
        dcs_std = statistics.stdev(dcs_scores) if len(dcs_scores) > 1 else 0
        
        print(f"\nRisk Score Statistics:")
        print(f"  Mean: {risk_mean:.2f}")
        print(f"  Median: {risk_median:.2f}")
        print(f"  Std Dev: {risk_std:.2f}")
        print(f"  Min: {min(risk_scores):.2f}")
        print(f"  Max: {max(risk_scores):.2f}")
        
        print(f"\nDCS Statistics:")
        print(f"  Mean: {dcs_mean:.2f}")
        print(f"  Median: {dcs_median:.2f}")
        print(f"  Std Dev: {dcs_std:.2f}")
        print(f"  Min: {min(dcs_scores):.2f}")
        print(f"  Max: {max(dcs_scores):.2f}")
        
        # Calculate correlation
        if len(risk_scores) > 1:
            # Pearson correlation
            n = len(risk_scores)
            sum_xy = sum(r * d for r, d in zip(risk_scores, dcs_scores))
            sum_x = sum(risk_scores)
            sum_y = sum(dcs_scores)
            sum_x2 = sum(r * r for r in risk_scores)
            sum_y2 = sum(d * d for d in dcs_scores)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            if denominator != 0:
                correlation = numerator / denominator
            else:
                correlation = 0.0
            
            print(f"\nCorrelation Analysis:")
            print(f"  Pearson Correlation: {correlation:.4f}")
            print(f"  Correlation Strength: {abs(correlation):.4f}")
            
            # Interpret correlation
            if abs(correlation) < 0.1:
                interpretation = "Very weak or no correlation"
            elif abs(correlation) < 0.3:
                interpretation = "Weak correlation"
            elif abs(correlation) < 0.5:
                interpretation = "Moderate correlation"
            elif abs(correlation) < 0.7:
                interpretation = "Strong correlation"
            else:
                interpretation = "Very strong correlation"
            
            print(f"  Interpretation: {interpretation}")
            
            # Check if they are properly separated
            if abs(correlation) < 0.3:
                print(f"\n✓ DCS and risk scores are properly separated (low correlation)")
            else:
                print(f"\n⚠ WARNING: DCS and risk scores show significant correlation")
                print(f"  This may indicate they are not properly independent")
        
        # Cross-tabulation by risk category and DCS label
        print(f"\nCross-tabulation (Risk Category vs DCS Label):")
        print("-" * 80)
        
        # Get risk categories and DCS labels
        query2 = session.query(
            RiskScore.risk_category,
            RiskScore.data_confidence_score
        ).filter(
            RiskScore.risk_category.isnot(None),
            RiskScore.data_confidence_score.isnot(None)
        ).all()
        
        # Simple DCS labels
        def dcs_label(score):
            if score >= 80:
                return "HIGH"
            elif score >= 50:
                return "MODERATE"
            else:
                return "LOW"
        
        from collections import defaultdict
        crosstab = defaultdict(lambda: defaultdict(int))
        
        for risk_cat, dcs_score in query2:
            dcs_lbl = dcs_label(dcs_score)
            crosstab[risk_cat][dcs_lbl] += 1
        
        print(f"{'Risk Category':<15} {'LOW DCS':<10} {'MODERATE DCS':<15} {'HIGH DCS':<10}")
        print("-" * 80)
        for risk_cat in sorted(crosstab.keys()):
            low = crosstab[risk_cat]['LOW']
            moderate = crosstab[risk_cat]['MODERATE']
            high = crosstab[risk_cat]['HIGH']
            print(f"{risk_cat:<15} {low:<10} {moderate:<15} {high:<10}")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_dcs_risk_correlation()
