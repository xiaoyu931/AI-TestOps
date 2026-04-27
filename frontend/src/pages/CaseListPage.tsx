import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (cfgId: number) => void;
};

type SearchForm = {
  cfg_id: string;
  uipath_case_name: string;
  environment: string;
  machine: string;
  template_id: string;
  verify_template_id: string;
};

const initialSearchForm: SearchForm = {
  cfg_id: "",
  uipath_case_name: "",
  environment: "",
  machine: "",
  template_id: "",
  verify_template_id: ""
};

export default function CaseListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState<SearchForm>(initialSearchForm);
  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleAdd = () => {
    onAdd ? onAdd() : nav("/case/create");
  };

  const handleEdit = (cfgId: number) => {
    onEdit ? onEdit(cfgId) : nav(`/case/edit/${cfgId}`);
  };

  /* ================= ⭐ 核心优化：拉全量模板 ================= */
  const loadTemplates = async () => {
    try {
      let page = 1;
      const pageSize = 100;
      let all: any[] = [];

      while (true) {
        const res = await testopsApi.getTemplates({
          page,
          page_size: pageSize
        });

        const list = res.data?.data || [];

        all = [...all, ...list];

        if (list.length < pageSize) break;

        page++;
      }

      all.sort((a, b) => Number(a.template_id) - Number(b.template_id));

      setTemplates(all);
    } catch (e) {
      console.error("Load templates error:", e);
    }
  };

  const loadCases = async (targetPage = page, form = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getCases({
        uipath_case_name : form.uipath_case_name  || undefined,
        cfg_id: form.cfg_id || undefined,
        environment: form.environment || undefined,
        machine: form.machine || undefined,
        template_id: form.template_id
          ? Number(form.template_id)
          : undefined,
        verify_template_id: form.verify_template_id
          ? Number(form.verify_template_id)
          : undefined,
        page: targetPage,
        page_size: pageSize
      });

      setRows(res.data?.data || []);
      setTotal(res.data?.total || 0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    loadCases(page, searchForm);
  }, [page]);

  const handleSearch = async () => {
    setPage(1);
    await loadCases(1, searchForm);
  };

  const handleClear = async () => {
    setSearchForm(initialSearchForm);
    setPage(1);
    await loadCases(1, initialSearchForm);
  };

  const handleDelete = async (cfgId: number) => {
    if (!window.confirm(`Are you sure to delete cfg_id=${cfgId}?`)) return;

    try {
      await testopsApi.deleteCase(cfgId);
      alert("Delete success");
      await loadCases(page, searchForm);
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="page-container">
      <div className="page-title">Case Management</div>

      {/* ================= 搜索 ================= */}
      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>CFG_ID</label>
            <input
              value={searchForm.cfg_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, cfg_id: e.target.value })
              }
              placeholder="Enter cfg_id"
            />
          </div>

          <div className="field">
            <label>UiPath Case Name</label>
            <input
              value={searchForm.uipath_case_name}
              onChange={(e) =>
                setSearchForm({ ...searchForm, uipath_case_name: e.target.value })
              }
              placeholder="Enter UiPath Case Name"
            />
          </div>

          <div className="field">
            <label>Environment</label>
            <input
              value={searchForm.environment}
              onChange={(e) =>
                setSearchForm({ ...searchForm, environment: e.target.value })
              }
              placeholder="For example: stage3 / T0"
            />
          </div>

          <div className="field">
            <label>Machine</label>
            <input
              value={searchForm.machine}
              onChange={(e) =>
                setSearchForm({ ...searchForm, machine: e.target.value })
              }
              placeholder="For example: 10.1.248.31"
            />
          </div>

          {/* ⭐ Order Template
          <div className="field">
            <label>Order Template</label>
            <select
              value={searchForm.template_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  template_id: e.target.value
                })
              }
            >
              <option value="">All</option>
              {templates.map((t) => (
                <option key={t.template_id} value={t.template_id}>
                  {t.template_id} - {t.template_name}
                </option>
              ))}
            </select>
          </div> */}

          {/* ⭐ Verify Template
          <div className="field">
            <label>Verify Template</label>
            <select
              value={searchForm.verify_template_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  verify_template_id: e.target.value
                })
              }
            >
              <option value="">All</option>
              {templates.map((t) => (
                <option key={t.template_id} value={t.template_id}>
                  {t.template_id} - {t.template_name}
                </option>
              ))}
            </select>
          </div> */}
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleClear}>
            Clear
          </button>
          <button className="btn btn-primary" onClick={handleSearch}>
            Search
          </button>
          <button className="btn btn-success" onClick={handleAdd}>
            Add Case
          </button>
        </div>
      </div>

      {/* ================= 表格 ================= */}
      <div className="table-card">
        <div className="table-header">
          <div>Case List</div>
          <div>Total {total}</div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <>
            <table className="case-table">
              <thead>
                <tr>
                  <th>CFG_ID</th>
                  <th>UiPath Case Name</th>
                  {/* <th>Order Template</th>
                  <th>Verify Template</th> */}
                  <th>Environment</th>
                  <th>Machine</th>
                  <th>UiPath Entry</th>
                  <th>Task Status</th>
                  <th>Create Date</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {rows.map((row) => (
                  <tr key={row.cfg_id}>
                    <td>{row.cfg_id}</td>
                    <td>{row.uipath_case_name}</td>
                    {/* <td>{row.test_case_name  ?? "-"}</td>
                    <td>{row.verify_template_name ?? "-"}</td> */}
                    <td>{row.environment || "-"}</td>
                    <td>{row.machine || "-"}</td>
                    <td>{row.uipath_entry ?? "-"}</td>
                    <td>{row.task_status ?? "-"}</td>
                    <td>{row.create_date || "-"}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn btn-link"
                          onClick={() => handleEdit(row.cfg_id)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-link danger"
                          onClick={() => handleDelete(row.cfg_id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {rows.length === 0 && (
                  <tr>
                    <td colSpan={10} className="empty-row">
                      No Data
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            <div className="pagination-bar">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
              >
                Prev
              </button>

              <span>
                Page {page} / {Math.ceil(total / pageSize) || 1}
              </span>

              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / pageSize)}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}