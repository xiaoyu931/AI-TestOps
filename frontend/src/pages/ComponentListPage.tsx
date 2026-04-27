import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (id: number) => void;
};

export default function ComponentListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState({
    component_id: "",
    component_name: "",
    component_type: "",
    component_file: ""
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
    nav("/component/create");
  };

  const handleEdit = (id: number) => {
    if (onEdit) {
      onEdit(id);
      return;
    }
    nav(`/component/edit/${id}`);
  };

  const loadData = async (targetPage = page, form = searchForm) => {
    const res = await testopsApi.getComponents({
      component_id: form.component_id ? Number(form.component_id) : undefined,
      component_name: form.component_name || undefined,
      component_type: form.component_type || undefined,
      component_file: form.component_file || undefined,
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
      component_id: "",
      component_name: "",
      component_type: "",
      component_file: ""
    };
    setSearchForm(empty);
    setPage(1);

    const res = await testopsApi.getComponents({
      page: 1,
      page_size: pageSize
    });

    setRows(res.data.data || []);
    setTotal(res.data.total || 0);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm(`Are you sure to delete component ${id}?`)) return;
    await testopsApi.deleteComponent(id);
    alert("Delete success");
    await loadData(page, searchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Component Management</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Component ID</label>
            <input
              value={searchForm.component_id}
              onChange={(e) => setSearchForm({ ...searchForm, component_id: e.target.value })}
              placeholder="Enter component_id"
            />
          </div>

          <div className="field">
            <label>Component Name</label>
            <input
              value={searchForm.component_name}
              onChange={(e) => setSearchForm({ ...searchForm, component_name: e.target.value })}
              placeholder="Enter Component Name"
            />
          </div>

          <div className="field">
            <label>Component Type</label>
            <input
              value={searchForm.component_type}
              onChange={(e) => setSearchForm({ ...searchForm, component_type: e.target.value })}
              placeholder="Enter Component Type"
            />
          </div>

          <div className="field">
            <label>Component File</label>
            <input
              value={searchForm.component_file}
              onChange={(e) => setSearchForm({ ...searchForm, component_file: e.target.value })}
              placeholder="Enter Component File"
            />
          </div>
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleClear}>Clear</button>
          <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          <button className="btn btn-success" onClick={handleAdd}>Add Component</button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Component List</div>
          <div>Total {total}</div>
        </div>

        <table className="case-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>File</th>
              <th>Remark</th>
              <th>State</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.component_id}>
                <td>{row.component_id}</td>
                <td>{row.component_name}</td>
                <td>{row.component_type}</td>
                <td>{row.component_file}</td>
                <td>{row.remark}</td>
                <td>{row.state}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn btn-link" onClick={() => handleEdit(row.component_id)}>Edit</button>
                    <button className="btn btn-link danger" onClick={() => handleDelete(row.component_id)}>Delete</button>
                  </div>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td colSpan={7} className="empty-row">No Data</td></tr>
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