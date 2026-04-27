import React, { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";
import JsonEditor from "../components/JsonEditor";

const initialForm = {
  case_name: "",
  template_id: 0,
  verify_template_id: 0,
  environment: "stage3",
  machine: "",
  tenant_id: "21",
  uipath_entry: "",

  test_data: {},
  order_test_data: {},
  verify_test_data: {}
};

export default function CaseConfigPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [form, setForm] = useState(initialForm);

  useEffect(() => {
    loadTemplates();
    loadCases();
  }, []);

  const loadTemplates = async () => {
    const res = await testopsApi.getTemplates();

    console.log("模板接口返回：", res.data);

    // 兼容不同后端结构
    const list = Array.isArray(res.data)
      ? res.data
      : res.data?.data || res.data?.templates || [];

    setTemplates(list);
  };

  const loadCases = async () => {
    const res = await testopsApi.getCases();

    const list = Array.isArray(res.data)
      ? res.data
      : res.data?.data || res.data?.cases || [];

    setCases(list);
  };

  const createCase = async () => {
    try {
      await testopsApi.createCase(form);
      alert("创建成功 ✅");
      setForm(initialForm);
      loadCases();
    } catch (e) {
      alert("创建失败 ❌");
      console.error(e);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Case配置</h2>

      {/* 基础信息 */}
      <div>
        <input
          placeholder="Case Name"
          value={form.case_name}
          onChange={(e) =>
            setForm({ ...form, case_name: e.target.value })
          }
        />
      </div>

      <br />

      {/* 模板选择 */}
      <div>
        <label>执行模板：</label>
        <select
          value={form.template_id}
          onChange={(e) =>
            setForm({ ...form, template_id: Number(e.target.value) })
          }
        >
          <option value={0}>请选择模板</option>
          {templates.map((t) => (
            <option key={t.template_id} value={t.template_id}>
              {t.template_name}
            </option>
          ))}
        </select>
      </div>

      <br />

      <div>
        <label>校验模板：</label>
        <select
          value={form.verify_template_id}
          onChange={(e) =>
            setForm({
              ...form,
              verify_template_id: Number(e.target.value)
            })
          }
        >
          <option value={0}>请选择校验模板</option>
          {templates.map((t) => (
            <option key={t.template_id} value={t.template_id}>
              {t.template_name}
            </option>
          ))}
        </select>
      </div>

      <br />

      {/* 环境信息 */}
      <div>
        <input
          placeholder="Environment (stage3)"
          value={form.environment}
          onChange={(e) =>
            setForm({ ...form, environment: e.target.value })
          }
        />
      </div>

      <br />

      <div>
        <input
          placeholder="Machine"
          value={form.machine}
          onChange={(e) =>
            setForm({ ...form, machine: e.target.value })
          }
        />
      </div>

      <br />

      <div>
        <input
          placeholder="UiPath Entry"
          value={form.uipath_entry}
          onChange={(e) =>
            setForm({ ...form, uipath_entry: e.target.value })
          }
        />
      </div>

      <br />

      {/* JSON 参数 */}
      <h3>Test Data</h3>
      <JsonEditor
        value={form.test_data}
        onChange={(val: any) =>
          setForm({ ...form, test_data: val })
        }
      />

      <h3>Order Test Data</h3>
      <JsonEditor
        value={form.order_test_data}
        onChange={(val: any) =>
          setForm({ ...form, order_test_data: val })
        }
      />

      <h3>Verify Test Data</h3>
      <JsonEditor
        value={form.verify_test_data}
        onChange={(val: any) =>
          setForm({ ...form, verify_test_data: val })
        }
      />

      <br />

      <button onClick={createCase}>🚀 创建Case</button>

      <hr />

      <h3>Case列表</h3>
      {cases.map((c) => (
        <div key={c.cfg_id}>
          {c.case_name} - {c.cfg_id}
        </div>
      ))}
    </div>
  );
}