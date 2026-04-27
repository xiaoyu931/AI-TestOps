import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

const initialForm = {
  component_name: "",
  component_type: "",
  component_file: "",
  remark: "",
  tenant_id: "21",
  state: 1
};

export default function ComponentFormPage({ mode, componentId, onBack, onSaved }: any) {
  const [form, setForm] = useState<any>(initialForm);
  const [loading, setLoading] = useState(false);

  const loadDetail = async () => {
    if (!componentId) return;
    const res = await testopsApi.getComponentDetail(componentId);
    setForm({
      component_name: res.data.component_name || "",
      component_type: res.data.component_type || "",
      component_file: res.data.component_file || "",
      remark: res.data.remark || "",
      tenant_id: res.data.tenant_id || "21",
      state: res.data.state ?? 1
    });
  };

  useEffect(() => {
    if (mode === "edit") loadDetail();
  }, [mode, componentId]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (mode === "create") {
        await testopsApi.createComponent(form);
        alert("创建成功");
      } else {
        await testopsApi.updateComponent(componentId, form);
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
        <div className="page-title">{mode === "create" ? "Create Component" : `Edit Component - ${componentId}`}</div>
        <div className="form-header-actions">
          <button className="btn btn-secondary" onClick={onBack}>Back</button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      <div className="form-card">
        <div className="form-grid">
          <div className="field">
            <label>Component Name</label>
            <input value={form.component_name} onChange={(e) => setForm({ ...form, component_name: e.target.value })} />
          </div>
          <div className="field">
            <label>Component Type</label>
            <input value={form.component_type} onChange={(e) => setForm({ ...form, component_type: e.target.value })} />
          </div>
          <div className="field">
            <label>Component File</label>
            <input value={form.component_file} onChange={(e) => setForm({ ...form, component_file: e.target.value })} />
          </div>
          <div className="field">
            <label>Remark</label>
            <input value={form.remark} onChange={(e) => setForm({ ...form, remark: e.target.value })} />
          </div>
          <div className="field">
            <label>Tenant ID</label>
            <input value={form.tenant_id} onChange={(e) => setForm({ ...form, tenant_id: e.target.value })} />
          </div>
          <div className="field">
            <label>State</label>
            <input type="number" value={form.state} onChange={(e) => setForm({ ...form, state: Number(e.target.value) })} />
          </div>
        </div>
      </div>
    </div>
  );
}