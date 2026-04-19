from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models.test_plan_model import TestPlan
from app.models.batch_detail_model import BatchDetail

# 创建一个 API 路由组
router = APIRouter()

# 定义API接口 创建一个 GET接口
@router.get("/executions")
def get_executions():

    # 数据库会话,用来执行 SQL 查询
    db= SessionLocal()
    try:
        # 查询最近10个执行批次
        # plans = db.query(TestPlan).order_by(TestPlan.CREATE_DATE.desc()).limit(10).all()
        regression_list = [
            "Regression 1 Mobile Automation",
            "Regression 2 OpennetNewOM Automation",
            "Regression 3 WS Automation",
            "Regression 4 NewOmMobile Automation"
        ]

        plans = db.query(TestPlan).filter(
            TestPlan.BATCH_NAME.in_(regression_list)
        ).order_by(
            TestPlan.CREATE_DATE.desc()
        ).limit(10).all()

        result = []

        for p in plans:
            # 统计总测试用例
            total = db.query(BatchDetail).filter(
                BatchDetail.BATCH_ID == p.BATCH_ID
            ).count()
            # 统计成功用例
            passed = db.query(BatchDetail).filter(
                BatchDetail.BATCH_ID == p.BATCH_ID,
                BatchDetail.STATUS.in_([5,13,14])
            ).count()
            # 统计失败用例
            failed = db.query(BatchDetail).filter(
                BatchDetail.BATCH_ID == p.BATCH_ID,
                BatchDetail.STATUS.in_([3,6,11])
            ).count()

            success_rate = 0
            # 计算成功率
            if total > 0:
                success_rate = round(passed / total * 100, 2)
            # 组装结果，生成一个 JSON 对象
            result.append({
                "batch_id": p.BATCH_ID,
                "time": p.CREATE_DATE,
                "batch_name": p.BATCH_NAME,
                "total_cases": total,
                "passed": passed,
                "failed": failed,
                "success_rate": f"{success_rate}%"
            })

        return result
    finally:
        db.close()