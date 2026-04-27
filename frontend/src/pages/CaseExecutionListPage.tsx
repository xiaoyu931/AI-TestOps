import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";
import { getCaseExecutionStateText } from "../utils/status";

type Props = {
  onView?: (id: number) => void;
};

export default function CaseExecutionListPage({ onView }: Props) {
  const nav = useNavigate();

  const initialSearchForm = {
    test_case_exe_id: "",
    cfg_id: "",
    test_case_name: "",
    execution_machine: "",
    state: ""
  };

  const [searchForm, setSearchForm] = useState(initialSearchForm);
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
    nav(`/component-execution/${id}`);
  };

  const buildParams = (form = searchForm) => {
    const params: any = {};

    if (form.test_case_exe_id)
      params.test_case_exe_id = Number(form.test_case_exe_id);

    if (form.cfg_id)
      params.cfg_id = Number(form.cfg_id);

    if (form.test_case_name)
      params.test_case_name = form.test_case_name;

    if (form.execution_machine)
      params.execution_machine = form.execution_machine;

    if (form.state)
      params.state = Number(form.state);

    return params;
  };

  const loadData = async (targetPage = page, form = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getCaseExecutions({
        ...buildParams(form),
        page: targetPage,
        page_size: pageSize
      });

      setRows(res.data?.data || []);
      setTotal(res.data?.total || 0);
    } catch (e: any) {
      console.error("Load case executions error:", e);
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

  const formatTime = (t: string) => {
    if (!t) return "-";
    return t.replace("T", " ").slice(0, 19);
  };

  const getStateColor = (value: number) => {
    if ([2, 5, 10].includes(value)) return "#16a34a";
    if ([3, 6, 11].includes(value)) return "#dc2626";
    if ([1, 4, 9].includes(value)) return "#f59e0b";
    return "#6b7280";
  };

  return (
    <div className="page-container">
      <div className="page-title">Case Execution</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Case Exe ID</label>
            <input
              value={searchForm.test_case_exe_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, test_case_exe_id: e.target.value })
              }
              placeholder="Enter case exe id"
            />
          </div>

          <div className="field">
            <label>CFG ID</label>
            <input
              value={searchForm.cfg_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, cfg_id: e.target.value })
              }
              placeholder="Enter cfg id"
            />
          </div>

          <div className="field">
            <label>Case Name</label>
            <input
              value={searchForm.test_case_name}
              onChange={(e) =>
                setSearchForm({ ...searchForm, test_case_name: e.target.value })
              }
              placeholder="Enter case name"
            />
          </div>

          <div className="field">
            <label>Execution Machine</label>
            <input
              value={searchForm.execution_machine}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  execution_machine: e.target.value
                })
              }
              placeholder="Enter execution machine"
            />
          </div>

          <div className="field">
            <label>State</label>
            <select
              value={searchForm.state}
              onChange={(e) =>
                setSearchForm({ ...searchForm, state: e.target.value })
              }
            >
              <option value="">All</option>
              <option value="1">Running</option>
              <option value="2">Case Success</option>
              <option value="3">Case Failed</option>
              <option value="4">Verifying</option>
              <option value="5">Verify Success</option>
              <option value="6">Verify Failed</option>
              <option value="7">Triggered Verify</option>
              <option value="8">UiPath Submit Success</option>
              <option value="9">Order Processing</option>
              <option value="10">Order Success</option>
              <option value="11">Order Failed</option>
              <option value="12">Triggered Order</option>
              <option value="13">No Order Needed</option>
              <option value="14">No Verify Needed</option>
            </select>
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
          <div>Case Execution List</div>
          <div>Total {total}</div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>CFG</th>
                <th>Machine</th>
                <th>State</th>
                <th>Create Date</th>
                <th>Finish Date</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((item) => (
                <tr key={item.TEST_CASE_EXE_ID}>
                  <td>{item.TEST_CASE_EXE_ID}</td>
                  <td>{item.TEST_CASE_NAME}</td>
                  <td>{item.CFG_ID}</td>
                  <td>{item.EXECUTION_MACHINE}</td>

                  <td style={{ color: getStateColor(item.STATE) }}>
                    {getCaseExecutionStateText(item.STATE)}
                  </td>

                  <td>{formatTime(item.CREATE_DATE)}</td>
                  <td>{formatTime(item.FINISH_DATE)}</td>

                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn btn-link"
                        onClick={() => handleView(item.TEST_CASE_EXE_ID)}
                      >
                        View Detail
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {rows.length === 0 && (
                <tr>
                  <td colSpan={8} className="empty-row">
                    No Data
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        <div className="pagination-bar">
          <button onClick={() => setPage(page - 1)} disabled={page === 1}>
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