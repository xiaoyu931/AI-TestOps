import { useEffect, useState } from "react";
import { testopsApi } from "../api/testops";

type Props = {
  batchId?: number | null;
};

type SearchForm = {
  batch_detail_id: string;
  batch_id: string;
  cfg_id: string;
  status: string;
  task_status: string;
  create_date_from: string;
  create_date_to: string;
};

const initialSearchForm: SearchForm = {
  batch_detail_id: "",
  batch_id: "",
  cfg_id: "",
  status: "",
  task_status: "",
  create_date_from: "",
  create_date_to: ""
};

function getStatusText(value: number) {
  switch (value) {
    case 1:
      return "Processing";
    case 2:
      return "Success";
    case 3:
      return "UiPath Failed";
    case 4:
      return "Verifying";
    case 5:
      return "Verify Success";
    case 6:
      return "Verify Failed";
    case 7:
      return "Verify Triggered";
    case 8:
      return "UiPath Submitted";
    case 9:
      return "Ordering";
    case 10:
      return "Order Success";
    case 11:
      return "Order Failed";
    case 12:
      return "Order Triggered";
    case 13:
      return "No Order Needed";
    case 14:
      return "No Verify Needed";
    default:
      return String(value ?? "-");
  }
}

function getTaskStatusText(value: number) {
  switch (value) {
    case 0:
      return "Order Not Completed";
    case 1:
      return "Order Completed";
    case 2:
      return "Finished";
    default:
      return value !== undefined && value !== null ? String(value) : "-";
  }
}

export default function BatchDetailPage({ batchId }: Props) {
  const [searchForm, setSearchForm] = useState<SearchForm>(initialSearchForm);
  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const [page, setPage] = useState(1);
  const pageSize = 10;

  const loadData = async (targetPage = 1, currentSearch = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getBatchDetails({
        batch_detail_id: currentSearch.batch_detail_id
          ? Number(currentSearch.batch_detail_id)
          : undefined,
        batch_id: currentSearch.batch_id
          ? Number(currentSearch.batch_id)
          : undefined,
        cfg_id: currentSearch.cfg_id ? Number(currentSearch.cfg_id) : undefined,
        status:
          currentSearch.status !== ""
            ? Number(currentSearch.status)
            : undefined,
        task_status:
          currentSearch.task_status !== ""
            ? Number(currentSearch.task_status)
            : undefined,
        create_date_from: currentSearch.create_date_from || undefined,
        create_date_to: currentSearch.create_date_to || undefined,
        page: targetPage,
        page_size: pageSize
      });

      setRows(res.data?.data || []);
      setTotal(res.data?.total || 0);
    } catch (e: any) {
      console.error("Load batch details error:", e);
      alert(e?.response?.data?.detail || "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  // 进入页面或 batchId 变化时：
  // 1) 菜单进入：batchId 为空 -> 展示全部列表
  // 2) View Detail 进入：batchId 有值 -> 自动带 batch_id 查询
  useEffect(() => {
    const nextSearch: SearchForm = {
      ...initialSearchForm,
      batch_id: batchId ? String(batchId) : ""
    };

    setSearchForm(nextSearch);
    setPage(1);
    loadData(1, nextSearch);
  }, [batchId]);

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

  const handlePrevPage = async () => {
    if (page === 1) return;
    const nextPage = page - 1;
    setPage(nextPage);
    await loadData(nextPage, searchForm);
  };

  const handleNextPage = async () => {
    const totalPage = Math.ceil(total / pageSize) || 1;
    if (page >= totalPage) return;
    const nextPage = page + 1;
    setPage(nextPage);
    await loadData(nextPage, searchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Execution Detail</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Batch Detail ID</label>
            <input
              value={searchForm.batch_detail_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  batch_detail_id: e.target.value
                })
              }
              placeholder="Enter batch detail id"
            />
          </div>

          <div className="field">
            <label>Batch ID</label>
            <input
              value={searchForm.batch_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  batch_id: e.target.value
                })
              }
              placeholder="Enter batch id"
            />
          </div>

          <div className="field">
            <label>CFG ID</label>
            <input
              value={searchForm.cfg_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  cfg_id: e.target.value
                })
              }
              placeholder="Enter cfg id"
            />
          </div>

          <div className="field">
            <label>Status</label>
            <select
              value={searchForm.status}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  status: e.target.value
                })
              }
            >
              <option value="">All</option>
              <option value="1">Processing</option>
              <option value="2">Success</option>
              <option value="3">UiPath Failed</option>
              <option value="4">Verifying</option>
              <option value="5">Verify Success</option>
              <option value="6">Verify Failed</option>
              <option value="7">Verify Triggered</option>
              <option value="8">UiPath Submitted</option>
              <option value="9">Ordering</option>
              <option value="10">Order Success</option>
              <option value="11">Order Failed</option>
              <option value="12">Order Triggered</option>
              <option value="13">No Order Needed</option>
              <option value="14">No Verify Needed</option>
            </select>
          </div>

          <div className="field">
            <label>Task Status</label>
            <select
              value={searchForm.task_status}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  task_status: e.target.value
                })
              }
            >
              <option value="">All</option>
              <option value="0">Order Not Completed</option>
              <option value="1">Order Completed</option>
              <option value="2">Finished</option>
            </select>
          </div>

          <div className="field">
            <label>Create Date From</label>
            <input
              type="datetime-local"
              value={searchForm.create_date_from}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  create_date_from: e.target.value
                })
              }
            />
          </div>

          <div className="field">
            <label>Create Date To</label>
            <input
              type="datetime-local"
              value={searchForm.create_date_to}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  create_date_to: e.target.value
                })
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
          <div>Detail List</div>
          <div>Total {total}</div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>Batch Detail ID</th>
                <th>Batch ID</th>
                <th>CFG ID</th>
                <th>UiPath Case Exe ID</th>
                <th>Order Case Exe ID</th>
                <th>Verify Case Exe ID</th>
                <th>Status</th>
                <th>Task Status</th>
                <th>Create Date</th>
                <th>Finish Date</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((row) => (
                <tr key={row.batch_detail_id}>
                  <td>{row.batch_detail_id}</td>
                  <td>{row.batch_id ?? "-"}</td>
                  <td>{row.cfg_id ?? "-"}</td>
                  <td>{row.uipath_case_exe_id ?? "-"}</td>
                  <td>{row.order_case_exe_id ?? "-"}</td>
                  <td>{row.verify_case_exe_id ?? "-"}</td>
                  <td>{getStatusText(row.status)}</td>
                  <td>{getTaskStatusText(row.task_status)}</td>
                  <td>{row.create_date || "-"}</td>
                  <td>{row.finish_date || "-"}</td>
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
        )}

        <div className="pagination-bar">
          <button onClick={handlePrevPage} disabled={page === 1}>
            Prev
          </button>

          <span>
            Page {page} / {Math.ceil(total / pageSize) || 1}
          </span>

          <button
            onClick={handleNextPage}
            disabled={page >= (Math.ceil(total / pageSize) || 1)}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}