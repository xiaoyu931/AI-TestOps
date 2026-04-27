import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

const initialForm = {
  parameter_name: "",
  parameter_path: "",
  parameter_type: "",
  default_value: "",
  remark: "",
  tenant_id: "21",
  state: 1
};

export default function ParameterFormPage({ mode, parameterId, onBack, onSaved }: any) {
  const [form, setForm] = useState<any>(initialForm);
  const [loading, setLoading] = useState(false);

  const loadDetail = async () => {
    if (!parameterId) return;
    const res = await testopsApi.getParameterDetail(parameterId);
    setForm({
      parameter_name: res.data.parameter_name || "",
      parameter_path: res.data.parameter_path || "",
      parameter_type: res.data.parameter_type || "",
      default_value: res.data.default_value || "",
      remark: res.data.remark || "",
      tenant_id: res.data.tenant_id || "21",
      state: res.data.state ?? 1
    });
  };

  useEffect(() => {
    if (mode === "edit") loadDetail();
  }, [mode, parameterId]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (mode === "create") {
        await testopsApi.createParameter(form);
        alert("创建成功");
      } else {
        await testopsApi.updateParameter(parameterId, form);
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
        <div className="page-title">{mode === "create" ? "Create Parameter" : `Edit Parameter - ${parameterId}`}</div>
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
            <label>Parameter Name</label>
            <input value={form.parameter_name} onChange={(e) => setForm({ ...form, parameter_name: e.target.value })} />
          </div>
          <div className="field">
            <label>Parameter Path</label>
            <input value={form.parameter_path} onChange={(e) => setForm({ ...form, parameter_path: e.target.value })} />
          </div>
          <div className="field">
            <label>Parameter Type</label>
            <input value={form.parameter_type} onChange={(e) => setForm({ ...form, parameter_type: e.target.value })} />
          </div>
          <div className="field">
            <label>Default Value</label>
            <input value={form.default_value} onChange={(e) => setForm({ ...form, default_value: e.target.value })} />
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