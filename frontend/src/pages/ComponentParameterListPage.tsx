import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (id: number) => void;
};

export default function ComponentParameterListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState({
    id: "",
    component_id: "",
    parameter_id: ""
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
    nav("/mapping/create");
  };

  const handleEdit = (id: number) => {
    if (onEdit) {
      onEdit(id);
      return;
    }
    nav(`/mapping/edit/${id}`);
  };

  const loadData = async (targetPage = page, form = searchForm) => {
    const res = await testopsApi.getComponentParameters({
      id: form.id || undefined,
      component_id: form.component_id || undefined,
      parameter_id: form.parameter_id || undefined,
      page: targetPage,
      page_size: pageSize
    });

    setRows(res.data.data || []);
    setTotal(res.data.total || 0);
  };

  useEffect(() => {
    loadData(page, searchForm);
  }, [page]);

  const handleSearch = () => {
    setPage(1);
    loadData(1, searchForm);
  };

  const handleClear = () => {
    const empty = { id: "", component_id: "", parameter_id: "" };
    setSearchForm(empty);
    setPage(1);
    loadData(1, empty);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure to delete this mapping?")) return;
    await testopsApi.deleteComponentParameter(id);
    alert("Delete success");
    loadData(page, searchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Component Parameter Mapping</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>ID</label>
            <input
              value={searchForm.id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, id: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Component ID</label>
            <input
              value={searchForm.component_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, component_id: e.target.value })
              }
            />
          </div>

          <div className="field">
            <label>Parameter ID</label>
            <input
              value={searchForm.parameter_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, parameter_id: e.target.value })
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

          <button className="btn btn-success" onClick={handleAdd}>
            Add Mapping
          </button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Mapping List</div>
          <div>Total {total}</div>
        </div>

        <table className="case-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Component</th>
              <th>Parameter</th>
              <th>Sort</th>
              <th>State</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.component_id}</td>
                <td>{row.parameter_id}</td>
                <td>{row.sort}</td>
                <td>{row.state}</td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-link"
                      onClick={() => handleEdit(row.id)}
                    >
                      Edit
                    </button>

                    <button
                      className="btn btn-link danger"
                      onClick={() => handleDelete(row.id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {rows.length === 0 && (
              <tr>
                <td colSpan={6} className="empty-row">
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
      </div>
    </div>
  );
}