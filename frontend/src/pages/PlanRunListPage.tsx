import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onView?: (batchId: number) => void;
};

type SearchForm = {
  batch_id: string;
  batch_name: string;
  plan_id: string;
  execution_machine: string;
  task_status: string;
  status: string;
  create_date_from: string;
  create_date_to: string;
};

const initialSearchForm: SearchForm = {
  batch_id: "",
  batch_name: "",
  plan_id: "",
  execution_machine: "",
  task_status: "",
  status: "",
  create_date_from: "",
  create_date_to: ""
};

function getTaskStatusText(value: number) {
  const map: Record<number, { text: string; color: string }> = {
    0: { text: "Not Sent", color: "#999" },
    1: { text: "Ready", color: "#1890ff" },
    2: { text: "Sent", color: "#52c41a" },
    3: { text: "Failed", color: "#ff4d4f" },
    4: { text: "Triggered", color: "#faad14" },
    5: { text: "No Need", color: "#aaa" },
    9: { text: "Jira Updated", color: "#722ed1" }
  };

  const item = map[value];

  return item ? (
    <span style={{ color: item.color, fontWeight: 500 }}>
      {item.text}
    </span>
  ) : (
    value ?? "-"
  );
}

function getStatusText(value: number) {
  switch (value) {
    case 0:
      return "Inactive";
    case 1:
      return "Active";
    default:
      return String(value ?? "-");
  }
}

export default function PlanRunListPage({ onView }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState<SearchForm>(initialSearchForm);
  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const pageSize = 10;

  const handleView = (id: number) => {
    if (onView) {
      onView(id);
      return;
    }
    nav(`/execution-detail/${id}`);
  };

  const loadData = async (targetPage = page, currentSearch = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getPlanRuns({
        batch_id: currentSearch.batch_id ? Number(currentSearch.batch_id) : undefined,
        batch_name: currentSearch.batch_name || undefined,
        plan_id: currentSearch.plan_id ? Number(currentSearch.plan_id) : undefined,
        execution_machine: currentSearch.execution_machine || undefined,
        task_status:
          currentSearch.task_status !== "" ? Number(currentSearch.task_status) : undefined,
        status: currentSearch.status !== "" ? Number(currentSearch.status) : undefined,
        create_date_from: currentSearch.create_date_from || undefined,
        create_date_to: currentSearch.create_date_to || undefined,
        page: targetPage,
        page_size: pageSize
      });

      setRows(res.data?.data || []);
      setTotal(res.data?.total || 0);
    } catch (e: any) {
      console.error("Load plan runs error:", e);
      alert(e?.response?.data?.detail || "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(page, searchForm);
  }, [page]);

  const handleSearch = async () => {
    setPage(1);
    await loadData(1, searchForm);
  };

  const handleClear = async () => {
    setSearchForm(initialSearchForm);
    setPage(1);
    await loadData(1, initialSearchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Plan Runs</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Batch ID</label>
            <input
              value={searchForm.batch_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, batch_id: e.target.value })
              }
              placeholder="Enter batch id"
            />
          </div>

          <div className="field">
            <label>Batch Name</label>
            <input
              value={searchForm.batch_name}
              onChange={(e) =>
                setSearchForm({ ...searchForm, batch_name: e.target.value })
              }
              placeholder="Enter batch name"
            />
          </div>

          <div className="field">
            <label>Plan ID</label>
            <input
              value={searchForm.plan_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, plan_id: e.target.value })
              }
              placeholder="Enter plan id"
            />
          </div>

          <div className="field">
            <label>Execution Machine</label>
            <input
              value={searchForm.execution_machine}
              onChange={(e) =>
                setSearchForm({ ...searchForm, execution_machine: e.target.value })
              }
              placeholder="Enter execution machine"
            />
          </div>

          <div className="field">
            <label>Task Status</label>
            <select
              value={searchForm.task_status}
              onChange={(e) =>
                setSearchForm({ ...searchForm, task_status: e.target.value })
              }
            >
              <option value="">All</option>
              <option value="0">Not Sent</option>
              <option value="1">Ready to Send</option>
              <option value="2">Email Sent</option>
              <option value="3">Email Failed</option>
              <option value="4">Triggered</option>
              <option value="5">No Email Needed</option>
              <option value="9">Jira Updated</option>
            </select>
          </div>

          <div className="field">
            <label>Status</label>
            <select
              value={searchForm.status}
              onChange={(e) =>
                setSearchForm({ ...searchForm, status: e.target.value })
              }
            >
              <option value="">All</option>
              <option value="1">Active</option>
              <option value="0">Inactive</option>
            </select>
          </div>

          <div className="field">
            <label>Create Date From</label>
            <input
              type="datetime-local"
              value={searchForm.create_date_from}
              onChange={(e) =>
                setSearchForm({ ...searchForm, create_date_from: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Create Date To</label>
            <input
              type="datetime-local"
              value={searchForm.create_date_to}
              onChange={(e) =>
                setSearchForm({ ...searchForm, create_date_to: e.target.value })
              }
            />
          </div>
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleClear}>
            Clear
          </button>
          <button className="btn btn-primary" onClick={handleSearch}>
            Search
          </button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Run List</div>
          <div>Total {total}</div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>Batch ID</th>
                <th>Batch Name</th>
                <th>Plan ID</th>
                <th>Execution Machine</th>
                <th>Task Status</th>
                <th>Status</th>
                <th>Pass Rate</th>
                <th>Re Run</th>
                <th>Send Email</th>
                <th>Create Date</th>
                <th>Finish Date</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((row) => (
                <tr key={row.batch_id}>
                  <td>{row.batch_id}</td>
                  <td>{row.batch_name || "-"}</td>
                  <td>{row.plan_id ?? "-"}</td>
                  <td>{row.execution_machine || "-"}</td>
                  <td>{getTaskStatusText(row.task_status)}</td>
                  <td>{getStatusText(row.status)}</td>
                  <td>{row.pass_rate || "-"}</td>
                  <td>{row.re_run ?? "-"}</td>
                  <td>{row.send_email ?? "-"}</td>
                  <td>{row.create_date || "-"}</td>
                  <td>{row.finish_date || "-"}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn btn-link"
                        onClick={() => handleView(row.batch_id)}
                      >
                        View Detail
                      </button>

                      <button
                        className="btn btn-link"
                        style={{ color: "#f59e0b" }}
                        onClick={() =>
                          nav(`/failure-analysis?batch_id=${row.batch_id}&plan_name=${encodeURIComponent(row.batch_name || "")}`)
                        }
                      >
                        Failure Analysis
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {rows.length === 0 && (
                <tr>
                  <td colSpan={12} className="empty-row">
                    No Data
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

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
      </div>
    </div>
  );
}