from collections import Counter
from typing import Dict, List


def build_summary(total: int, failed: int, success: int) -> dict:
    return {
        "total": total,
        "failed": failed,
        "success": success,
        "success_rate": round((success / total) * 100, 2) if total > 0 else 0,
    }


def build_empty_failure_analysis_response() -> dict:
    return {
        "summary": {
            "total": 0,
            "failed": 0,
            "success": 0,
            "success_rate": 0,
        },
        "stage_distribution": [],
        "error_type_distribution": [],
        "error_pattern_distribution": [],
        "top_issue": None,
        "failure_details": [],
    }


def build_failure_analysis_response(summary: dict, failure_details: List[dict]) -> dict:
    distribution = aggregate_failure_details(
        failure_details=failure_details,
        failed_count=summary["failed"],
    )

    return {
        "summary": summary,
        "stage_distribution": distribution["stage_distribution"],
        "error_type_distribution": distribution["error_type_distribution"],
        "error_pattern_distribution": distribution["error_pattern_distribution"],
        "top_issue": distribution["top_issue"],
        "failure_details": distribution["failure_details"],
    }


def aggregate_failure_details(failure_details: List[dict], failed_count: int) -> dict:
    stage_counter = Counter()
    error_type_counter = Counter()
    pattern_counter = Counter()
    pattern_display_map: Dict[str, dict] = {}

    cleaned_details = []

    for detail in failure_details:
        stage_counter[detail["stage"]] += 1
        error_type_counter[detail["error_type"]] += 1
        pattern_counter[detail["error_pattern"]] += 1

        pattern_display_map[detail["error_pattern"]] = {
            "title": detail.get("error_pattern_title") or detail["error_pattern"],
            "suggestion": detail.get("error_pattern_suggestion") or detail.get("solution") or "",
            # "suggestion": detail.get("error_pattern_suggestion") or detail.get("solution") or detail.get("suggestion") or "",
        }

        cleaned_detail = dict(detail)
        cleaned_detail.pop("error_pattern_title", None)
        cleaned_detail.pop("error_pattern_suggestion", None)
        cleaned_details.append(cleaned_detail)

    stage_distribution = [
        {"stage": k, "count": v}
        for k, v in sorted(stage_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    error_type_distribution = [
        {"error_type": k, "count": v}
        for k, v in sorted(error_type_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    error_pattern_distribution = []
    for pattern, count in sorted(pattern_counter.items(), key=lambda x: x[1], reverse=True):
        display = pattern_display_map.get(pattern, {})
        percent = round((count / failed_count) * 100, 1) if failed_count > 0 else 0

        error_pattern_distribution.append({
            "pattern": pattern,
            "title": display.get("title") or pattern,
            "suggestion": display.get("suggestion") or "",
            "count": count,
            "percent": percent,
        })

    return {
        "stage_distribution": stage_distribution,
        "error_type_distribution": error_type_distribution,
        "error_pattern_distribution": error_pattern_distribution,
        "top_issue": error_pattern_distribution[0] if error_pattern_distribution else None,
        "failure_details": cleaned_details,
    }
