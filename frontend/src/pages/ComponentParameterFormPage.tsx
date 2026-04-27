import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

export default function ComponentParameterFormPage({ id, onBack }: any) {

  const [components, setComponents] = useState<any[]>([]);
  const [parameters, setParameters] = useState<any[]>([]);

  const [form, setForm] = useState({
    component_id: "",
    parameter_id: "",
    sort: 1,
    state: 1
  });

  // ✅ 加载数据
  const loadOptions = async () => {
    try {
      const cRes = await testopsApi.getComponents({ page: 1, page_size: 999 });
      const pRes = await testopsApi.getParameters({ page: 1, page_size: 999 });

      console.log("components:", cRes.data);
      console.log("parameters:", pRes.data);

      setComponents(cRes.data?.data || []);
      setParameters(pRes.data?.data || []);

    } catch (e) {
      console.error("Load options error:", e);
      alert("Failed to load dropdown data");
    }
  };

  // ✅ 编辑
  const loadDetail = async () => {
    if (!id) return;

    const res = await testopsApi.getComponentParameterDetail(id);
    const d = res.data;

    setForm({
      component_id: String(d.component_id),
      parameter_id: String(d.parameter_id),
      sort: d.sort || 1,
      state: d.state || 1
    });
  };

  useEffect(() => {
    loadOptions();
    loadDetail();
  }, []);

  // ✅ 保存
  const handleSave = async () => {
    if (!form.component_id || !form.parameter_id) {
      alert("Please select Component and Parameter");
      return;
    }

    const payload = {
      component_id: Number(form.component_id),
      parameter_id: Number(form.parameter_id),
      sort: form.sort,
      state: form.state
    };

    try {
      if (id) {
        await testopsApi.updateComponentParameter(id, payload);
        alert("Update success");
      } else {
        await testopsApi.createComponentParameter(payload);
        alert("Create success");
      }

      onBack();
    } catch (e) {
      alert("Save failed");
    }
  };

  return (
    <div className="page-container">

      <div className="page-title">
        {id ? "Edit Mapping" : "Create Mapping"}
      </div>

      <div className="form-card">

        <div className="form-grid">

          {/* Component */}
          <div className="field">
            <label>Component</label>
            <select
              value={form.component_id}
              onChange={(e) =>
                setForm({ ...form, component_id: e.target.value })
              }
            >
              <option value="">Select Component</option>

              {components.map((c) => (
                <option key={c.component_id} value={c.component_id}>
                  {c.component_id} - {c.component_name}
                </option>
              ))}
            </select>
          </div>

          {/* Parameter */}
          <div className="field">
            <label>Parameter</label>
            <select
              value={form.parameter_id}
              onChange={(e) =>
                setForm({ ...form, parameter_id: e.target.value })
              }
            >
              <option value="">Select Parameter</option>

              {parameters.map((p) => (
                <option key={p.parameter_id} value={p.parameter_id}>
                  {p.parameter_id} - {p.parameter_name}
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div className="field">
            <label>Sort</label>
            <input
              type="number"
              value={form.sort}
              onChange={(e) =>
                setForm({ ...form, sort: Number(e.target.value) })
              }
            />
          </div>

          {/* State */}
          <div className="field">
            <label>State</label>
            <input
              type="number"
              value={form.state}
              onChange={(e) =>
                setForm({ ...form, state: Number(e.target.value) })
              }
            />
          </div>

        </div>

        <div className="form-header-actions">
          <button className="btn btn-primary" onClick={handleSave}>
            Save
          </button>
          <button className="btn btn-secondary" onClick={onBack}>
            Back
          </button>
        </div>

      </div>
    </div>
  );
}