# 浏览器默认 不允许不同域名之间互相请求数据，例如前端和后端，这就是“跨域”，会被浏览器拦截
from fastapi.middleware.cors import CORSMiddleware # 导入 FastAPI 提供的 CORS 中间件
from fastapi import FastAPI
from app.api.execution_api import router as execution_router2
from app.api.case_task_api import router as case_task_router
from app.api.template_api import router as template_router
from app.api.component_api import router as component_router
from app.api.parameter_api import router as parameter_router
from app.api.component_parameter_api import router as component_parameter_router
from app.api.auto_data_sql_api import router as auto_sql_router
from app.api.provision_parameter_api import router as provision_router
from app.api.pre_cfg_relation_api import router as pre_relation_router
from app.api.billing_data_pool_api import router as billing_router
from app.api.test_dispatcher_api import router as dispatcher_router
from app.api.test_plan_api import router as plan_router
from app.api.batch_detail_api import router as batch_detail_router
from app.api.test_case_execution_api import router as execution_router
from app.api.case_ext_api import router as case_ext_router
from app.api.analysis_api import router as analysis_router
from app.api.dispatcher_ext_api import router as dispatcher_ext_router
from app.api.template_ext_api import router as template_ext_router
from app.api import template_meta_router
from app.api.component_parameter_api import router as component_parameter_api
from app.api.template_rel_api import router as template_rel_router
from app.api import test_plan_api
from app.api.test_component_execution_api import router as component_execution_router
from app.api.failure_analysis_api import router as failure_analysis_router
from app.api.test_plan_health_api import router as test_plan_health_router


# 创建一个 FastAPI 应用实例  可以理解为：app = API服务器， 所有接口都会挂在这个 app 上。
app = FastAPI()
# 给 FastAPI 应用添加一个“中间件”（middleware），中间件作用：在请求进入接口之前/之后处理一些事情（比如权限、日志、CORS）
#  CORSMiddleware,指定使用 CORS 中间件
# 允许任何网站访问你的 FastAPI 后端接口（完全开放 CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许所有网站访问 （开发环境常用）生产环境建议写具体地址，例如 ["http://localhost:3000", "https://yourdomain.com"]
    allow_credentials=True, #是否允许发送“凭证”
    allow_methods=["*"], # 允许哪些 HTTP 方法  "*" = 全部允许（GET, POST, PUT, DELETE 等）
    allow_headers=["*"],  # 允许哪些请求头（headers）  比如：Content-Type Authorization
)

# 把 case_api.py 里的接口 注册到主应用。
app.include_router(case_task_router)
app.include_router(template_rel_router)
app.include_router(template_router)
app.include_router(component_router)
app.include_router(parameter_router)
app.include_router(component_parameter_router)
app.include_router(auto_sql_router)
app.include_router(provision_router)
app.include_router(pre_relation_router)
app.include_router(billing_router)
app.include_router(dispatcher_router)
app.include_router(plan_router)
app.include_router(batch_detail_router)
app.include_router(execution_router)
# app.include_router(execution_router2)
app.include_router(component_execution_router)
app.include_router(case_ext_router)
app.include_router(analysis_router)
app.include_router(dispatcher_ext_router)
app.include_router(template_ext_router)
app.include_router(template_meta_router.router)
app.include_router(component_parameter_api)
app.include_router(template_rel_router)
app.include_router(test_plan_api.router)
app.include_router(component_execution_router)
app.include_router(failure_analysis_router)
app.include_router(test_plan_health_router)
# 定义首页接口，这是 根路径接口
# 访问：http://localhost:8000/  执行：home()
@app.get("/")
def home():
    # 用来确认 API 服务启动成功
    return {"message": "AI TestOps Platform Running"}