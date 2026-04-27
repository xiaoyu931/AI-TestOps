import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (id: number) => void;
};

export default function ParameterListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState({
    parameter_id: "",
    parameter_name: "",
    parameter_path: "",
    parameter_type: ""
  });

  const [rows, setRows] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const handleAdd = () => {
    if (onAdd) {
      onAdd();
      return;
    }
    nav("/parameter/create");
  };

  const handleEdit = (id: number) => {
    if (onEdit) {
      onEdit(id);
      return;
    }
    nav(`/parameter/edit/${id}`);
  };

  const loadData = async (targetPage = page, form = searchForm) => {
    const res = await testopsApi.getParameters({
      parameter_id: form.parameter_id ? Number(form.parameter_id) : undefined,
      parameter_name: form.parameter_name || undefined,
      parameter_path: form.parameter_path || undefined,
      parameter_type: form.parameter_type || undefined,
      page: targetPage,
      page_size: pageSize
    });

    setRows(res.data.data || []);
    setTotal(res.data.total || 0);
  };

  useEffect(() => {
    loadData(page, searchForm);
  }, [page]);

  const handleSearch = async () => {
    setPage(1);
    await loadData(1, searchForm);
  };

  const handleClear = async () => {
    const empty = {
      parameter_id: "",
      parameter_name: "",
      parameter_path: "",
      parameter_type: ""
    };
    setSearchForm(empty);
    setPage(1);

    const res = await testopsApi.getParameters({
      page: 1,
      page_size: pageSize
    });

    setRows(res.data.data || []);
    setTotal(res.data.total || 0);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm(`Are you sure to delete parameter ${id}?`)) return;
    await testopsApi.deleteParameter(id);
    alert("Delete success");
    await loadData(page, searchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Parameter Management</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Parameter ID</label>
            <input
              value={searchForm.parameter_id}
              onChange={(e) => setSearchForm({ ...searchForm, parameter_id: e.target.value })}
              placeholder="Enter parameter_id"
            />
          </div>

          <div className="field">
            <label>Parameter Name</label>
            <input
              value={searchForm.parameter_name}
              onChange={(e) => setSearchForm({ ...searchForm, parameter_name: e.target.value })}
              placeholder="Enter Parameter Name"
            />
          </div>

          <div className="field">
            <label>Parameter Path</label>
            <input
              value={searchForm.parameter_path}
              onChange={(e) => setSearchForm({ ...searchForm, parameter_path: e.target.value })}
              placeholder="Enter Parameter Path"
            />
          </div>

          <div className="field">
            <label>Parameter Type</label>
            <input
              value={searchForm.parameter_type}
              onChange={(e) => setSearchForm({ ...searchForm, parameter_type: e.target.value })}
              placeholder="Enter Parameter Type"
            />
          </div>
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleClear}>Clear</button>
          <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          <button className="btn btn-success" onClick={handleAdd}>Add Parameter</button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Parameter List</div>
          <div>Total {total}</div>
        </div>

        <table className="case-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Path</th>
              <th>Type</th>
              <th>Default Value</th>
              <th>Remark</th>
              <th>State</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.parameter_id}>
                <td>{row.parameter_id}</td>
                <td>{row.parameter_name}</td>
                <td>{row.parameter_path}</td>
                <td>{row.parameter_type}</td>
                <td>{row.default_value}</td>
                <td>{row.remark}</td>
                <td>{row.state}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn btn-link" onClick={() => handleEdit(row.parameter_id)}>Edit</button>
                    <button className="btn btn-link danger" onClick={() => handleDelete(row.parameter_id)}>Delete</button>
                  </div>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={8} className="empty-row">No Data</td></tr>
            )}
          </tbody>
        </table>

        <div className="pagination-bar">
          <button onClick={() => setPage(page - 1)} disabled={page === 1}>Prev</button>
          <span>Page {page} / {Math.ceil(total / pageSize) || 1}</span>
          <button onClick={() => setPage(page + 1)} disabled={page >= Math.ceil(total / pageSize)}>Next</button>
        </div>
      </div>
    </div>
  );
}