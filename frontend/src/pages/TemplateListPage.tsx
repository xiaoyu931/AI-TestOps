import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (id: number) => void;
};

export default function TemplateListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState({
    template_id: "",
    template_name: "",
    module: "",
    test_case_type: ""
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
    nav("/template/create");
  };

  const handleEdit = (id: number) => {
    if (onEdit) {
      onEdit(id);
      return;
    }
    nav(`/template/edit/${id}`);
  };

  const loadData = async (targetPage = page, form = searchForm) => {
    const res = await testopsApi.getTemplates({
      template_id: form.template_id ? Number(form.template_id) : undefined,
      template_name: form.template_name || undefined,
      module: form.module || undefined,
      test_case_type: form.test_case_type || undefined,
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
      template_id: "",
      template_name: "",
      module: "",
      test_case_type: ""
    };
    setSearchForm(empty);
    setPage(1);

    const res = await testopsApi.getTemplates({
      page: 1,
      page_size: pageSize
    });

    setRows(res.data.data || []);
    setTotal(res.data.total || 0);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm(`Are you sure to delete template ${id}?`)) return;
    await testopsApi.deleteTemplate(id);
    alert("Delete success");
    await loadData(page, searchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Template Management</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Template ID</label>
            <input
              value={searchForm.template_id}
              onChange={(e) => setSearchForm({ ...searchForm, template_id: e.target.value })}
              placeholder="Enter template_id"
            />
          </div>

          <div className="field">
            <label>Template Name</label>
            <input
              value={searchForm.template_name}
              onChange={(e) => setSearchForm({ ...searchForm, template_name: e.target.value })}
              placeholder="Enter Template Name"
            />
          </div>

          <div className="field">
            <label>Module</label>
            <input
              value={searchForm.module}
              onChange={(e) => setSearchForm({ ...searchForm, module: e.target.value })}
              placeholder="Enter Module"
            />
          </div>

          <div className="field">
            <label>Case Type</label>
            <input
              value={searchForm.test_case_type}
              onChange={(e) => setSearchForm({ ...searchForm, test_case_type: e.target.value })}
              placeholder="Enter Case Type"
            />
          </div>
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleClear}>Clear</button>
          <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          <button className="btn btn-success" onClick={handleAdd}>Add Template</button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Template List</div>
          <div>Total {total}</div>
        </div>

        <table className="case-table">
          <thead>
            <tr>
              <th>Template ID</th>
              <th>Template Name</th>
              <th>Module</th>
              <th>Case Type</th>
              <th>Is Browser</th>
              <th>State</th>
              <th>Create Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.template_id}>
                <td>{row.template_id}</td>
                <td>{row.template_name}</td>
                <td>{row.module}</td>
                <td>{row.test_case_type}</td>
                <td>{row.is_browser}</td>
                <td>{row.state}</td>
                <td>{row.create_date}</td>
                <td>
                  <div className="action-buttons">
                    <button className="btn btn-link" onClick={() => handleEdit(row.template_id)}>Edit</button>
                    <button className="btn btn-link danger" onClick={() => handleDelete(row.template_id)}>Delete</button>
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