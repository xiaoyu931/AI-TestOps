import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

const initialForm = {
  template_name: "",
  module: "",
  test_case_type: "1",
  is_browser: 0,
  tenant_id: "21",
  state: 1,
  remark: "",
  components: [] as any[]
};

export default function TemplateFormPage({ mode, templateId, onBack, onSaved }: any) {
  const [form, setForm] = useState<any>(initialForm);
  const [componentOptions, setComponentOptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadComponents = async () => {
    try {
      let page = 1;
      const pageSize = 100;
      let all: any[] = [];

      while (true) {
        const res = await testopsApi.getComponents({
          page,
          page_size: pageSize
        });

        const list = res.data?.data || [];

        all = [...all, ...list];

        // 如果这一页不满，说明结束
        if (list.length < pageSize) break;

        page++;
      }

      // 排序
      all.sort((a: any, b: any) => a.component_id - b.component_id);

      setComponentOptions(all);
    } catch (e) {
      console.error("Load components error:", e);
    }
  };

  const loadDetail = async () => {
    if (!templateId) return;
    const res = await testopsApi.getTemplateDetail(templateId);
    const d = res.data;
    setForm({
      template_name: d.template_name || "",
      module: d.module || "",
      test_case_type: d.test_case_type || "1",
      is_browser: d.is_browser ?? 0,
      tenant_id: d.tenant_id || "21",
      state: d.state ?? 1,
      remark: d.remark || "",
      components: d.components || []
    });
  };

  useEffect(() => {
    loadComponents();
    if (mode === "edit") loadDetail();
  }, [mode, templateId]);

  const addComponentRow = () => {
    setForm({
      ...form,
      components: [
        ...form.components,
        {
          component_id: "",
          sort: form.components.length + 1,
          wait_time: 5,
          loop_num: 1,
          is_suspend: "Y",
          remark: ""
        }
      ]
    });
  };

  const updateRow = (index: number, key: string, value: any) => {
    const next = [...form.components];
    next[index][key] = value;
    setForm({ ...form, components: next });
  };

  const removeRow = (index: number) => {
    const next = form.components.filter((_: any, i: number) => i !== index);
    setForm({ ...form, components: next });
  };

  const handleSubmit = async () => {
    const payload = {
      ...form,
      is_browser: Number(form.is_browser),
      state: Number(form.state),
      components: form.components.map((c: any) => ({
        component_id: Number(c.component_id),
        sort: Number(c.sort),
        wait_time: Number(c.wait_time),
        loop_num: Number(c.loop_num),
        is_suspend: c.is_suspend,
        remark: c.remark || ""
      }))
    };

    setLoading(true);
    try {
      if (mode === "create") {
        await testopsApi.createTemplate(payload);
        alert("创建成功");
      } else {
        await testopsApi.updateTemplate(templateId, payload);
        alert("更新成功");
      }
      onSaved();
    } catch (e: any) {
      alert(e?.response?.data?.detail || "保存失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="form-header">
        <div className="page-title">{mode === "create" ? "Create Template" : `Edit Template - ${templateId}`}</div>
        <div className="form-header-actions">
          <button className="btn btn-secondary" onClick={onBack}>Back</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">Template Basic Information</div>
        <div className="form-grid">
          <div className="field">
            <label>Template Name</label>
            <input value={form.template_name} onChange={(e) => setForm({ ...form, template_name: e.target.value })} />
          </div>
          <div className="field">
            <label>Module</label>
            <input value={form.module} onChange={(e) => setForm({ ...form, module: e.target.value })} />
          </div>
          <div className="field">
            <label>Case Type</label>
            <input value={form.test_case_type} onChange={(e) => setForm({ ...form, test_case_type: e.target.value })} />
          </div>
          <div className="field">
            <label>Is Browser</label>
            <input type="number" value={form.is_browser} onChange={(e) => setForm({ ...form, is_browser: Number(e.target.value) })} />
          </div>
          <div className="field">
            <label>Tenant ID</label>
            <input value={form.tenant_id} onChange={(e) => setForm({ ...form, tenant_id: e.target.value })} />
          </div>
          <div className="field">
            <label>State</label>
            <input type="number" value={form.state} onChange={(e) => setForm({ ...form, state: Number(e.target.value) })} />
          </div>
          <div className="field" style={{ gridColumn: "1 / span 3" }}>
            <label>Remark</label>
            <input value={form.remark} onChange={(e) => setForm({ ...form, remark: e.target.value })} />
          </div>
        </div>
      </div>

      <div className="form-card">
        <div className="form-header">
          <div className="section-title">Template Components</div>
          <button className="btn btn-success" onClick={addComponentRow}>Add Step</button>
        </div>

        <table className="case-table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Sort</th>
              <th>Wait Time</th>
              <th>Loop Num</th>
              <th>Is Suspend</th>
              <th>Remark</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {form.components.map((row: any, index: number) => (
              <tr key={index}>
                <td>
                  <select
                    value={row.component_id}
                    onChange={(e) => updateRow(index, "component_id", e.target.value)}
                  >
                    <option value="">Please select components</option>
                    {componentOptions.map((c) => (
                      <option key={c.component_id} value={c.component_id}>
                        {c.component_id} - {c.component_name}
                      </option>
                    ))}
                  </select>
                </td>
                <td><input type="number" value={row.sort} onChange={(e) => updateRow(index, "sort", e.target.value)} /></td>
                <td><input type="number" value={row.wait_time} onChange={(e) => updateRow(index, "wait_time", e.target.value)} /></td>
                <td><input type="number" value={row.loop_num} onChange={(e) => updateRow(index, "loop_num", e.target.value)} /></td>
                <td>
                  <select value={row.is_suspend} onChange={(e) => updateRow(index, "is_suspend", e.target.value)}>
                    <option value="Y">Y</option>
                    <option value="N">N</option>
                  </select>
                </td>
                <td><input value={row.remark} onChange={(e) => updateRow(index, "remark", e.target.value)} /></td>
                <td>
                  <button className="btn btn-link danger" onClick={() => removeRow(index)}>Delete</button>
                </td>
              </tr>
            ))}

            {form.components.length === 0 && (
              <tr>
                <td colSpan={7} className="empty-row">No Components</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}