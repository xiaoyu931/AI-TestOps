import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (id: number) => void;
};

type SearchForm = {
  dispatcher_plan_id: string;
  que_name: string;
  exe_machine: string;
  batch_name: string;
};

const initialSearchForm: SearchForm = {
  dispatcher_plan_id: "",
  que_name: "",
  exe_machine: "",
  batch_name: ""
};

export default function TestDispatcherListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState<SearchForm>(initialSearchForm);
  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const pageSize = 10;

  const handleAdd = () => {
    if (onAdd) {
      onAdd();
      return;
    }
    nav("/dispatcher/create");
  };

  const handleEdit = (id: number) => {
    if (onEdit) {
      onEdit(id);
      return;
    }
    nav(`/dispatcher/edit/${id}`);
  };

  const loadData = async (targetPage = page, currentSearch = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getTestDispatchers({
        dispatcher_plan_id: currentSearch.dispatcher_plan_id
          ? Number(currentSearch.dispatcher_plan_id)
          : undefined,
        que_name: currentSearch.que_name || undefined,
        exe_machine: currentSearch.exe_machine || undefined,
        batch_name: currentSearch.batch_name || undefined,
        page: targetPage,
        page_size: pageSize
      });

      setRows(res.data?.data || []);
      setTotal(res.data?.total || 0);
    } catch (e: any) {
      console.error("Load dispatcher list error:", e);
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

  const handleDelete = async (id: number) => {
    const ok = window.confirm(`Confirm delete dispatcher_plan_id=${id}?`);
    if (!ok) return;

    try {
      await testopsApi.deleteTestDispatcher(id);
      alert("Deleted successfully");

      const totalPage = Math.max(1, Math.ceil((total - 1) / pageSize));
      const nextPage = page > totalPage ? totalPage : page;
      setPage(nextPage);
      await loadData(nextPage, searchForm);
    } catch (e: any) {
      console.error("Delete dispatcher error:", e);
      alert(e?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="page-container">
      <div className="page-title">Test Plan Config</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Dispatcher Plan ID</label>
            <input
              value={searchForm.dispatcher_plan_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, dispatcher_plan_id: e.target.value })
              }
              placeholder="Enter dispatcher_plan_id"
            />
          </div>

          <div className="field">
            <label>Que Name</label>
            <input
              value={searchForm.que_name}
              onChange={(e) =>
                setSearchForm({ ...searchForm, que_name: e.target.value })
              }
              placeholder="Enter que name"
            />
          </div>

          <div className="field">
            <label>Exe Machine</label>
            <input
              value={searchForm.exe_machine}
              onChange={(e) =>
                setSearchForm({ ...searchForm, exe_machine: e.target.value })
              }
              placeholder="Enter exe machine"
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
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleClear}>
            Clear
          </button>
          <button className="btn btn-primary" onClick={handleSearch}>
            Search
          </button>
          <button className="btn btn-success" onClick={handleAdd}>
            Add Plan
          </button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Plan List</div>
          <div>Total {total}</div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>Dispatcher Plan ID</th>
                <th>Batch Name</th>
                <th>Que Name</th>
                <th>Exe Machine</th>
                <th>Send Email</th>
                <th>Pass Rate Switch</th>
                <th>Pass Rate</th>
                <th>Update Jira</th>
                <th>Create Bug</th>
                <th>Create Date</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((row) => (
                <tr key={row.dispatcher_plan_id}>
                  <td>{row.dispatcher_plan_id}</td>
                  <td>{row.batch_name || "-"}</td>
                  <td>{row.que_name || "-"}</td>
                  <td>{row.exe_machine || "-"}</td>
                  <td>{row.send_email ?? "-"}</td>
                  <td>{row.pass_rate_switch ?? "-"}</td>
                  <td>{row.pass_rate || "-"}</td>
                  <td>{row.update_jira || "-"}</td>
                  <td>{row.create_bug || "-"}</td>
                  <td>{row.create_date || "-"}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn btn-link"
                        onClick={() => handleEdit(row.dispatcher_plan_id)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-link danger"
                        onClick={() => handleDelete(row.dispatcher_plan_id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {rows.length === 0 && (
                <tr>
                  <td colSpan={14} className="empty-row">
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