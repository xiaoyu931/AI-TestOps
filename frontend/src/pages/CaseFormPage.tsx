import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

type Props = {
  mode: "create" | "edit";
  cfgId: number | null;
  onBack: () => void;
  onSaved: () => void;
};

type FormDataType = {
  // case_name: string;
  template_id: number | "";
  verify_template_id: number | "";
  verify_template_name: string;
  trigger_mode: number;
  cron_expression: string;
  task_status: number;
  environment: string;
  machine: string;
  tenant_id: string;
  state: number;
  inst_id: string;
  uipath_case_name: string;
  uipath_entry: string;
  case_id: string;
  test_data_text: string;
};

const defaultJsonTemplate = `{
  "login": {
    "userName": "",
    "password": ""
  },
  "menu": {},
  "order": {}
}`;

const initialForm: FormDataType = {
  // case_name: "",
  template_id: "",
  verify_template_id: "",
  verify_template_name: "",
  trigger_mode: 2,
  cron_expression: "0 0 0 * * ?",
  task_status: 1,
  environment: "T0",
  machine: "",
  tenant_id: "21",
  state: 1,
  inst_id: "",
  uipath_case_name: "",
  uipath_entry: "",
  case_id: "",
  test_data_text: defaultJsonTemplate
};

export default function CaseFormPage({
  mode,
  cfgId,
  onBack,
  onSaved
}: Props) {
  const [form, setForm] = useState<FormDataType>(initialForm);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const pageTitle = mode === "create" ? "Create Case" : `Edit Case - ${cfgId}`;

  const loadTemplates = async () => {
    try {
      const res = await testopsApi.getTemplates({
        page: 1,
        page_size: 1000
      });

      let list = Array.isArray(res.data) ? res.data : res.data?.data || [];

      list = list.sort(
        (a: any, b: any) => Number(a.template_id) - Number(b.template_id)
      );

      setTemplates(list);
    } catch (e) {
      console.error("Load templates error:", e);
      alert("Failed to load templates");
    }
  };

  const loadCaseDetail = async (id: number) => {
    try {
      const res = await testopsApi.getCaseDetail(id);
      const d = res.data;

      setForm({
        ...initialForm,
        // case_name: d.case_name || "",
        template_id: d.template_id ? d.template_id : "",
        verify_template_id: d.verify_template_id ? d.verify_template_id : "",
        verify_template_name: d.verify_template_name || "",
        trigger_mode: d.trigger_mode ?? 2,
        cron_expression: d.cron_expression || "0 0 0 * * ?",
        task_status: d.task_status ?? 1,
        environment: d.environment || "T0",
        machine: d.machine || "",
        tenant_id: d.tenant_id || "21",
        state: d.state ?? 1,
        inst_id: d.inst_id || "",
        uipath_case_name: d.uipath_case_name || "",
        uipath_entry: d.uipath_entry || "",
        case_id: d.case_id || "",
        test_data_text: JSON.stringify(d.test_data || {}, null, 2)
      });
    } catch (e: any) {
      console.error("Load case detail error:", e);
      alert(e?.response?.data?.detail || "Failed to load case detail");
    }
  };

  useEffect(() => {
    const init = async () => {
      setForm(initialForm);
      await loadTemplates();

      if (mode === "edit" && cfgId !== null) {
        await loadCaseDetail(cfgId);
      }
    };

    init();
  }, [mode, cfgId]);

  const handleLoadDefaultJson = () => {
    setForm({ ...form, test_data_text: defaultJsonTemplate });
  };

  const handleSubmit = async () => {
    let parsedJson = {};

    try {
      parsedJson = form.test_data_text.trim()
        ? JSON.parse(form.test_data_text)
        : {};
    } catch {
      alert("UiPath JSON format is invalid");
      return;
    }

    const orderTemplate = templates.find(
      (t) => Number(t.template_id) === Number(form.template_id)
    );

    const verifyTemplate = templates.find(
      (t) => Number(t.template_id) === Number(form.verify_template_id)
    );

    const payload = {
      template_id: form.template_id === "" ? 0 : Number(form.template_id),
      test_case_name:
        form.template_id === ""
        ? ""
        : (orderTemplate?.template_name || ""),
      verify_template_id:
        form.verify_template_id === "" ? 0 : Number(form.verify_template_id),
      verify_template_name:
        form.verify_template_id === ""
        ? ""
        : (verifyTemplate?.template_name || ""),
      trigger_mode: Number(form.trigger_mode),
      cron_expression: form.cron_expression,
      task_status: Number(form.task_status),
      environment: form.environment,
      machine: form.machine,
      tenant_id: form.tenant_id,
      state: Number(form.state),
      inst_id: form.inst_id,
      uipath_case_name: form.uipath_case_name,
      uipath_entry: form.uipath_entry,
      case_id: form.case_id,
      test_data: parsedJson
    };

    setLoading(true);
    try {
      if (mode === "create") {
        await testopsApi.createCase(payload);
        alert("Created successfully");
      } else if (cfgId !== null) {
        await testopsApi.updateCase(cfgId, payload);
        alert("Updated successfully");
      }

      onSaved();
    } catch (e: any) {
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
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">Basic Information</div>

        <div className="form-grid">
          {/* <div className="field">
            <label>Order Template Name</label>
            <input
              value={form.case_name}
              onChange={(e) =>
                setForm({ ...form, case_name: e.target.value })
              }
            />
          </div> */}

          <div className="field">
            <label>Environment</label>
            <input
              value={form.environment}
              onChange={(e) =>
                setForm({ ...form, environment: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Machine</label>
            <input
              value={form.machine}
              onChange={(e) => setForm({ ...form, machine: e.target.value })}
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
            <label>TEST_INST_ID</label>
            <input
              value={form.inst_id}
              onChange={(e) => setForm({ ...form, inst_id: e.target.value })}
            />
          </div>

          <div className="field">
            <label>UiPath Entry</label>
            <input
              value={form.uipath_entry}
              onChange={(e) =>
                setForm({ ...form, uipath_entry: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>UiPath Case Name</label>
            <input
              value={form.uipath_case_name}
              onChange={(e) =>
                setForm({ ...form, uipath_case_name: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Case ID</label>
            <input
              value={form.case_id}
              onChange={(e) => setForm({ ...form, case_id: e.target.value })}
            />
          </div>

          <div className="field">
            <label>Trigger Mode</label>
            <input
              type="number"
              value={form.trigger_mode}
              onChange={(e) =>
                setForm({ ...form, trigger_mode: Number(e.target.value) })
              }
            />
          </div>

          <div className="field">
            <label>Cron Expression</label>
            <input
              value={form.cron_expression}
              onChange={(e) =>
                setForm({ ...form, cron_expression: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Task Status</label>
            <input
              type="number"
              value={form.task_status}
              onChange={(e) =>
                setForm({ ...form, task_status: Number(e.target.value) })
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

      <div className="form-card">
        <div className="section-title">Template Configuration</div>

        <div className="form-grid">
          <div className="field">
            <label>Order Template</label>
            <select
              value={form.template_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  template_id: e.target.value === "" ? "" : Number(e.target.value)
                })
              }
            >
              <option value="">No order processing required</option>
              {templates.map((t) => (
                <option key={t.template_id} value={t.template_id}>
                  {t.template_id} - {t.template_name}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Verify Template</label>
            <select
              value={form.verify_template_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  verify_template_id:
                    e.target.value === "" ? "" : Number(e.target.value)
                })
              }
            >
              <option value="">No data validation required</option>
              {templates.map((t) => (
                <option key={t.template_id} value={t.template_id}>
                  {t.template_id} - {t.template_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="tips-box">
          <div>Generation Rules:</div>
          <div>1. Only one UiPath record will be generated.</div>
          <div>
            2. If an Order Template is selected, one Order record will be generated.
          </div>
          <div>
            3. If a Verify Template is selected, one Verify record will be generated.
          </div>
        </div>
      </div>

      <div className="form-card">
        <div className="section-title">UiPath Test Data</div>

        <div className="json-actions">
          <button className="btn btn-secondary" onClick={handleLoadDefaultJson}>
            Load Default JSON Template
          </button>
        </div>

        <textarea
          className="json-editor"
          value={form.test_data_text}
          onChange={(e) =>
            setForm({ ...form, test_data_text: e.target.value })
          }
        />
      </div>
    </div>
  );
}