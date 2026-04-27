import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";
import {
  getComponentExecutionStateColor,
  getComponentExecutionStateText
} from "../utils/status";

type Props = {
  caseExeId?: number | null;
};

type SearchForm = {
  test_case_exe_id: string;
  test_component_id: string;
  test_component_name: string;
  state: string;
};

const initialSearchForm: SearchForm = {
  test_case_exe_id: "",
  test_component_id: "",
  test_component_name: "",
  state: ""
};

export default function ComponentExecutionListPage({ caseExeId }: Props) {
  const [searchForm, setSearchForm] = useState<SearchForm>(initialSearchForm);

  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const pageSize = 10;

  /* ================= 参数构建 ================= */
  const buildParams = (form: SearchForm) => {
    const p: any = {};

    if (form.test_case_exe_id)
      p.test_case_exe_id = Number(form.test_case_exe_id);

    if (form.test_component_id)
      p.test_component_id = Number(form.test_component_id);

    if (form.test_component_name)
      p.test_component_name = form.test_component_name;

    if (form.state !== "") p.state = Number(form.state);

    return p;
  };

  /* ================= 数据加载 ================= */
  const loadData = async (targetPage = 1, form = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getComponentExecutions({
        ...buildParams(form),
        page: targetPage,
        page_size: pageSize
      });

      setRows(res.data?.data || []);
      setTotal(res.data?.total || 0);
    } catch (e) {
      console.error(e);
      alert("Load failed");
    } finally {
      setLoading(false);
    }
  };

  /* ================= ⭐ 核心：路由驱动 ================= */
  useEffect(() => {
    const nextSearch: SearchForm = {
      ...initialSearchForm,
      test_case_exe_id: caseExeId ? String(caseExeId) : ""
    };

    setSearchForm(nextSearch);
    setPage(1);
    loadData(1, nextSearch);
  }, [caseExeId]);

  /* ================= 搜索 ================= */
  const handleSearch = async () => {
    setPage(1);
    await loadData(1, searchForm);
  };

  const handleClear = async () => {
    const nextSearch = { ...initialSearchForm };
    setSearchForm(nextSearch);
    setPage(1);
    await loadData(1, nextSearch);
  };

  /* ================= 分页 ================= */
  const handlePrev = async () => {
    if (page === 1) return;
    const next = page - 1;
    setPage(next);
    await loadData(next, searchForm);
  };

  const handleNext = async () => {
    const totalPage = Math.ceil(total / pageSize) || 1;
    if (page >= totalPage) return;
    const next = page + 1;
    setPage(next);
    await loadData(next, searchForm);
  };

  /* ================= UI ================= */
  return (
    <div className="page-container">
      <div className="page-title">Component Execution</div>

      {/* ===== 搜索 ===== */}
      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Case Exe ID</label>
            <input
              value={searchForm.test_case_exe_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  test_case_exe_id: e.target.value
                })
              }
              placeholder="Enter case exe id"
            />
          </div>

          <div className="field">
            <label>Component ID</label>
            <input
              value={searchForm.test_component_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  test_component_id: e.target.value
                })
              }
              placeholder="Enter component id"
            />
          </div>

          <div className="field">
            <label>Component Name</label>
            <input
              value={searchForm.test_component_name}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  test_component_name: e.target.value
                })
              }
              placeholder="Enter component name"
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
              <option value="0">Init</option>
              <option value="2">Success</option>
              <option value="3">Failed</option>
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

      {/* ===== 表格 ===== */}
      <div className="table-card">
        <div className="table-header">
          <div>Component Execution List</div>
          <div>Total {total}</div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Case Exe ID</th>
                <th>Component ID</th>
                <th>Component Name</th>
                <th>State</th>
                <th>Create Date</th>
                <th>Finish Date</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((row) => (
                <tr key={row.TEST_COMPONENT_EXE_ID}>
                  <td>{row.TEST_COMPONENT_EXE_ID}</td>
                  <td>{row.TEST_CASE_EXE_ID}</td>
                  <td>{row.TEST_COMPONENT_ID}</td>
                  <td>{row.TEST_COMPONENT_NAME}</td>

                  <td
                    style={{
                      color: getComponentExecutionStateColor(row.STATE),
                      fontWeight: 500
                    }}
                  >
                    {getComponentExecutionStateText(row.STATE)}
                  </td>

                  <td>{row.CREATE_DATE || "-"}</td>
                  <td>{row.FINISH_DATE || "-"}</td>
                </tr>
              ))}

              {rows.length === 0 && (
                <tr>
                  <td colSpan={7} className="empty-row">
                    No Data
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        <div className="pagination-bar">
          <button onClick={handlePrev} disabled={page === 1}>
            Prev
          </button>

          <span>
            Page {page} / {Math.ceil(total / pageSize) || 1}
          </span>

          <button
            onClick={handleNext}
            disabled={page >= (Math.ceil(total / pageSize) || 1)}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}