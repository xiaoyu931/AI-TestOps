# AI TestOps Frontend

这是根据你提供的 FastAPI 后端接口生成的可直接运行前端项目，技术栈：

- React 18
- TypeScript
- Vite
- Axios
- React Router

## 运行方式

```bash
cd ai-testops-frontend
cp .env.example .env
npm install
npm run dev
```

默认地址：

```bash
http://localhost:3000
```

后端地址默认：

```bash
http://localhost:8000
```

如果你的后端地址不同，请修改 `.env`：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 已包含模块

- Dashboard
- Case 管理
- 模板仓库
- 组件仓库
- 参数仓库
- 组件参数关系
- 模板依赖关系
- SQL 仓库
- Billing Data Pool
- Dispatcher 计划
- 测试计划
- Batch Detail 结果
- Case 执行结果
- 组件执行结果
- 前置 Case 关系
- Provision 参数

## 关于 CRUD 的重要说明

你要求前端必须包含查询、新增、修改、删除。

这份前端代码里：

- 所有页面都已经提供了查询/新增/修改/删除入口
- 但你当前后端大多数模块 **没有提供 PUT / DELETE 接口**
- 因此前端在这些模块点击“修改/删除”时，会明确提示：当前后端未提供接口

### 当前后端真正支持的写操作情况

- **支持删除**
  - `DELETE /pre-relations?pre_cfg_id=...&cfg_id=...`

- **支持更新**
  - `PUT /component-executions/{exe_id}/finish`

- **仅支持新增 + 查询，不支持更新/删除**
  - `/case-tasks`
  - `/templates`
  - `/components`
  - `/parameters`
  - `/component-parameters`
  - `/auto-sql`
  - `/billing-pool`
  - `/dispatcher`
  - `/plans`
  - `/batch-details`
  - `/executions`
  - `/provision-params`

## 建议你下一步补充的后端接口

如果你希望前端上的“修改 / 删除”真的可用，建议后端继续补这些接口：

- `PUT /case-tasks/{cfg_id}`
- `DELETE /case-tasks/{cfg_id}`
- `PUT /templates/{template_id}`
- `DELETE /templates/{template_id}`
- `PUT /components/{component_id}`
- `DELETE /components/{component_id}`
- `PUT /parameters/{parameter_id}`
- `DELETE /parameters/{parameter_id}`
- `PUT /batch-details/{id}`
- `DELETE /batch-details/{id}`
- `PUT /executions/{exe_id}`
- `DELETE /executions/{exe_id}`

## 特别说明

有几个列表接口是参数式路径，比如：

- `GET /template-rels/{template_id}`
- `GET /batch-details/batch/{batch_id}`
- `GET /executions/cfg/{cfg_id}`
- `GET /component-executions/case/{case_exe_id}`

当前前端为了“开箱即跑”，默认演示了：

- `template_id = 1`
- `batch_id = 1`
- `cfg_id = 1`
- `case_exe_id = 1`

你可以在 `src/config/resources.ts` 中改成你自己的实际 ID，或者我下一步可以继续帮你把这几个页面改成“先输入 ID 再查询”的正式版。
