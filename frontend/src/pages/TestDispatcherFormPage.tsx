import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

type Props = {
  id: number | null;
  onBack: () => void;
};

type FormDataType = {
  que_name: string;
  exe_machine: string;
  plan_id: string;
  batch_name: string;
  send_email: string;
  pass_rate_switch: string;
  pass_rate: string;
  default_msg_to_list: string;
  msg_cc_list: string;
  msg_to_list: string;
  case_list: string;
  actual_case_list: string;
  explanation: string;
  update_jira: string;
  create_bug: string;
  uipath_exe_machone: string;
};

const initialForm: FormDataType = {
  que_name: "",
  exe_machine: "",
  plan_id: "0",
  batch_name: "",
  send_email: "0",
  pass_rate_switch: "0",
  pass_rate: "",
  default_msg_to_list: "",
  msg_cc_list: "",
  msg_to_list: "",
  case_list: "",
  actual_case_list: "",
  explanation: "",
  update_jira: "",
  create_bug: "",
  uipath_exe_machone: ""
};

export default function TestDispatcherFormPage({ id, onBack }: Props) {
  const [form, setForm] = useState<FormDataType>(initialForm);
  const [loading, setLoading] = useState(false);

  const pageTitle = id ? `Edit Plan - ${id}` : "Create Plan";

  const loadDetail = async () => {
    if (!id) return;

    try {
      const res = await testopsApi.getTestDispatcherDetail(id);
      const d = res.data;

      setForm({
        que_name: d.que_name || "",
        exe_machine: d.exe_machine || "",
        plan_id: String(d.plan_id ?? 0),
        batch_name: d.batch_name || "",
        send_email: String(d.send_email ?? 0),
        pass_rate_switch: String(d.pass_rate_switch ?? 0),
        pass_rate: d.pass_rate || "",
        default_msg_to_list: d.default_msg_to_list || "",
        msg_cc_list: d.msg_cc_list || "",
        msg_to_list: d.msg_to_list || "",
        case_list: d.case_list || "",
        actual_case_list: d.actual_case_list || "",
        explanation: d.explanation || "",
        update_jira: d.update_jira || "",
        create_bug: d.create_bug || "",
        uipath_exe_machone: d.uipath_exe_machone || ""
      });
    } catch (e: any) {
      console.error("Load dispatcher detail error:", e);
      alert(e?.response?.data?.detail || "Failed to load detail");
    }
  };

  useEffect(() => {
    loadDetail();
  }, [id]);

  const handleSave = async () => {
    const payload = {
      que_name: form.que_name,
      exe_machine: form.exe_machine,
      plan_id: Number(form.plan_id || 0),
      batch_name: form.batch_name,
      send_email: Number(form.send_email || 0),
      pass_rate_switch: Number(form.pass_rate_switch || 0),
      pass_rate: form.pass_rate,
      default_msg_to_list: form.default_msg_to_list,
      msg_cc_list: form.msg_cc_list,
      msg_to_list: form.msg_to_list,
      case_list: form.case_list,
      actual_case_list: form.actual_case_list,
      explanation: form.explanation,
      update_jira: form.update_jira,
      create_bug: form.create_bug,
      uipath_exe_machone: form.uipath_exe_machone
    };

    setLoading(true);
    try {
      if (id) {
        await testopsApi.updateTestDispatcher(id, payload);
        alert("Updated successfully");
      } else {
        await testopsApi.createTestDispatcher(payload);
        alert("Created successfully");
      }
      onBack();
    } catch (e: any) {
      console.error("Save dispatcher error:", e);
      alert(e?.response?.data?.detail || "Save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="form-header">
        <div className="page-title">{pageTitle}</div>
        <div className="form-header-actions">
          <button className="btn btn-secondary" onClick={onBack}>
            Back
          </button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">Basic Information</div>

        <div className="form-grid">
          <div className="field">
            <label>Que Name</label>
            <input
              value={form.que_name}
              onChange={(e) => setForm({ ...form, que_name: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Exe Machine</label>
            <input
              value={form.exe_machine}
              onChange={(e) => setForm({ ...form, exe_machine: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Plan ID</label>
            <input
              value={form.plan_id}
              onChange={(e) => setForm({ ...form, plan_id: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Batch Name</label>
            <input
              value={form.batch_name}
              onChange={(e) => setForm({ ...form, batch_name: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Send Email</label>
            <input
              value={form.send_email}
              onChange={(e) => setForm({ ...form, send_email: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Pass Rate Switch</label>
            <input
              value={form.pass_rate_switch}
              onChange={(e) =>
                setForm({ ...form, pass_rate_switch: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Pass Rate</label>
            <input
              value={form.pass_rate}
              onChange={(e) => setForm({ ...form, pass_rate: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Update Jira</label>
            <input
              value={form.update_jira}
              onChange={(e) => setForm({ ...form, update_jira: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Create Bug</label>
            <input
              value={form.create_bug}
              onChange={(e) => setForm({ ...form, create_bug: e.target.value })}
            />
          </div>

          <div className="field">
            <label>UiPath Exe Machine</label>
            <input
              value={form.uipath_exe_machone}
              onChange={(e) =>
                setForm({ ...form, uipath_exe_machone: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Explanation</label>
            <input
              value={form.explanation}
              onChange={(e) =>
                setForm({ ...form, explanation: e.target.value })
              }
            />
          </div>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">Message Configuration</div>

        <div className="form-grid">
          <div className="field">
            <label>Default Msg To List</label>
            <input
              value={form.default_msg_to_list}
              onChange={(e) =>
                setForm({ ...form, default_msg_to_list: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Msg CC List</label>
            <input
              value={form.msg_cc_list}
              onChange={(e) =>
                setForm({ ...form, msg_cc_list: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Msg To List</label>
            <input
              value={form.msg_to_list}
              onChange={(e) =>
                setForm({ ...form, msg_to_list: e.target.value })
              }
            />
          </div>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">Case Data</div>

        <div className="field">
          <label>Case List</label>
          <textarea
            className="json-editor"
            value={form.case_list}
            onChange={(e) => setForm({ ...form, case_list: e.target.value })}
          />
        </div>

        <div className="field" style={{ marginTop: "16px" }}>
          <label>Actual Case List</label>
          <textarea
            className="json-editor"
            value={form.actual_case_list}
            onChange={(e) =>
              setForm({ ...form, actual_case_list: e.target.value })
            }
          />
        </div>
      </div>
    </div>
  );
}