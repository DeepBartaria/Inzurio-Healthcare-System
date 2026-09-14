import json
import logging
from sqlalchemy.orm import Session
from models import Report, TestResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_result(db: Session, test_name: str) -> str:
    """Gets the latest result for a specific lab test."""
    logger.info(f"[AUDIT] Tool 'get_latest_result' called with args: test_name='{test_name}'")
    
    result = db.query(TestResult).join(Report).filter(
        TestResult.test_name.ilike(f"%{test_name}%")
    ).order_by(Report.report_date.desc()).first()
    
    if not result:
        return json.dumps({"error": f"No result found for test: {test_name}"})
        
    return json.dumps({
        "test_name": result.test_name,
        "date": result.report.report_date,
        "value": result.value,
        "unit": result.unit,
        "reference_range": result.reference_range,
        "is_flagged": result.is_flagged
    })

def get_test_history(db: Session, test_name: str) -> str:
    """Gets the history of all results for a specific lab test across all reports."""
    logger.info(f"[AUDIT] Tool 'get_test_history' called with args: test_name='{test_name}'")
    
    results = db.query(TestResult).join(Report).filter(
        TestResult.test_name.ilike(f"%{test_name}%")
    ).order_by(Report.report_date.asc()).all()
    
    if not results:
        return json.dumps({"error": f"No history found for test: {test_name}"})
        
    history = []
    prev_value = None
    prev_unit = None
    
    for r in results:
        trend = None
        try:
            curr_val = float(r.value.replace("<", "").replace(">", "").strip())
            if prev_value is not None and prev_unit == r.unit:
                diff = curr_val - prev_value
                trend = f"Increased by {diff:.2f}" if diff > 0 else (f"Decreased by {abs(diff):.2f}" if diff < 0 else "Unchanged")
            prev_value = curr_val
            prev_unit = r.unit
        except ValueError:
            # Not a numeric value
            prev_value = None
            prev_unit = None
            
        history.append({
            "date": r.report.report_date,
            "value": r.value,
            "unit": r.unit,
            "reference_range": r.reference_range,
            "is_flagged": r.is_flagged,
            "numeric_trend_from_previous": trend
        })
        
    return json.dumps({
        "test_name": test_name,
        "history": history
    })

def list_out_of_range_results(db: Session, report_date: str = None) -> str:
    """Lists all tests that are flagged as high, low, or critical. Optionally filters by report date (YYYY-MM-DD)."""
    logger.info(f"[AUDIT] Tool 'list_out_of_range_results' called with args: report_date='{report_date}'")
    
    query = db.query(TestResult).filter(
        TestResult.is_flagged.in_(["high", "low", "critical"])
    )
    
    if report_date:
        query = query.join(Report).filter(Report.report_date == report_date)
        
    results = query.all()
    
    if not results:
        msg = "No out-of-range results found."
        if report_date:
            msg += f" for date {report_date}"
        return json.dumps({"message": msg})
        
    out_of_range = []
    for r in results:
        date = r.report.report_date if hasattr(r, 'report') and r.report else report_date
        out_of_range.append({
            "test_name": r.test_name,
            "date": date,
            "value": r.value,
            "unit": r.unit,
            "is_flagged": r.is_flagged,
            "reference_range": r.reference_range
        })
        
        
    return json.dumps({"out_of_range_results": out_of_range})

def get_all_results(db: Session, report_date: str=None) -> str:
    """Gets all lab results, optionally filtered by a specific report date (YYYY-MM-DD). Useful for summarizing or answering general queries."""
    logger.info(f"[AUDIT] Tool 'get_all_results' called with args: report_date='{report_date}'")
    
    query = db.query(TestResult)
    if report_date:
        query = query.join(Report).filter(Report.report_date==report_date)
        
    results = query.all()
    
    if not results:
        msg = "No results found."
        if report_date:
            msg += f" for date {report_date}"
        return json.dumps({"message": msg})
        
    all_res = []
    for r in results:
        date = r.report.report_date if hasattr(r, 'report') and r.report else report_date
        all_res.append({
            "test_name": r.test_name,
            "date": date,
            "value": r.value,
            "unit": r.unit,
            "is_flagged": r.is_flagged,
            "reference_range": r.reference_range
        })
        
    return json.dumps({"all_results": all_res})

