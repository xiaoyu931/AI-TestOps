import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

export default function TemplateRelationFormPage({ relId, onBack, onSaved }: any) {
  const [form, setForm] = useState({
    test_case_template_id: "",
    pre_test_case_template_id: "",
    tenant_id: "21",
    state: 1
  });

  const loadDetail = async () => {
    if (!relId) return;

    const res = await testopsApi.getTemplateRelationDetail(relId);
    const d = res.data;

    setForm({
      test_case_template_id: String(d.test_case_template_id || ""),
      pre_test_case_template_id: String(d.pre_test_case_template_id || ""),
      tenant_id: String(d.tenant_id || "21"),
      state: d.state ?? 1
    });
  };

  useEffect(() => {
    loadDetail();
  }, [relId]);

  const handleSave = async () => {
    if (!form.test_case_template_id || !form.pre_test_case_template_id) {
      alert("Please input Template ID and Pre Template ID");
      return;
    }

    const payload = {
      test_case_template_id: Number(form.test_case_template_id),
      pre_test_case_template_id: Number(form.pre_test_case_template_id),
      tenant_id: Number(form.tenant_id),
      state: Number(form.state)
    };

    if (relId) {
      await testopsApi.updateTemplateRelation(relId, payload);
      alert("Update success");
    } else {
      await testopsApi.createTemplateRelation(payload);
      alert("Create success");
    }

    onSaved();
  };

  return (
    <div className="page-container">
      <div className="form-header">
        <div className="page-title">
          {relId ? `Edit Relation - ${relId}` : "Create Relation"}
        </div>

        <div className="form-header-actions">
          <button className="btn btn-secondary" onClick={onBack}>
            Back
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            Save
          </button>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">Basic Information</div>

        <div className="form-grid">
          <div className="field">
            <label>Template ID</label>
            <input
              value={form.test_case_template_id}
              onChange={(e) =>
                setForm({ ...form, test_case_template_id: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Pre Template ID</label>
            <input
              value={form.pre_test_case_template_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  pre_test_case_template_id: e.target.value
                })
              }
            />
          </div>

          <div className="field">
            <label>Tenant ID</label>
            <input
              value={form.tenant_id}
              onChange={(e) =>
                setForm({ ...form, tenant_id: e.target.value })
              }
            />
          </div>

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
      </div>
    </div>
  );
}