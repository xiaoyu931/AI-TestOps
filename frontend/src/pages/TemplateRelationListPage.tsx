import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type Props = {
  onAdd?: () => void;
  onEdit?: (id: number) => void;
};

export default function TemplateRelationListPage({ onAdd, onEdit }: Props) {
  const nav = useNavigate();

  const [searchForm, setSearchForm] = useState({
    rel_id: "",
    test_case_template_id: "",
    pre_test_case_template_id: ""
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
    nav("/template-relation/create");
  };

  const handleEdit = (id: number) => {
    if (onEdit) {
      onEdit(id);
      return;
    }
    nav(`/template-relation/edit/${id}`);
  };

  const loadData = async (targetPage = page, form = searchForm) => {
    const res = await testopsApi.getTemplateRelations({
      rel_id: form.rel_id ? Number(form.rel_id) : undefined,
      test_case_template_id: form.test_case_template_id
        ? Number(form.test_case_template_id)
        : undefined,
      pre_test_case_template_id: form.pre_test_case_template_id
        ? Number(form.pre_test_case_template_id)
        : undefined,
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
      rel_id: "",
      test_case_template_id: "",
      pre_test_case_template_id: ""
    };
    setSearchForm(empty);
    setPage(1);

    const res = await testopsApi.getTemplateRelations({
      page: 1,
      page_size: pageSize
    });

    setRows(res.data.data || []);
    setTotal(res.data.total || 0);
  };

  const handleDelete = async (relId: number) => {
    const ok = window.confirm(`Are you sure to delete relation ${relId}?`);
    if (!ok) return;

    await testopsApi.deleteTemplateRelation(relId);
    alert("Delete success");
    await loadData(page, searchForm);
  };

  return (
    <div className="page-container">
      <div className="page-title">Template Relation Management</div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
          <div className="field">
            <label>Relation ID</label>
            <input
              value={searchForm.rel_id}
              onChange={(e) =>
                setSearchForm({ ...searchForm, rel_id: e.target.value })
              }
              placeholder="Enter relation id"
            />
          </div>

          <div className="field">
            <label>Template ID</label>
            <input
              value={searchForm.test_case_template_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  test_case_template_id: e.target.value
                })
              }
              placeholder="Enter template id"
            />
          </div>

          <div className="field">
            <label>Pre Template ID</label>
            <input
              value={searchForm.pre_test_case_template_id}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  pre_test_case_template_id: e.target.value
                })
              }
              placeholder="Enter pre template id"
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
            Add Relation
          </button>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Relation List</div>
          <div>Total {total}</div>
        </div>

        <table className="case-table">
          <thead>
            <tr>
              <th>Relation ID</th>
              <th>Template ID</th>
              <th>Pre Template ID</th>
              <th>Tenant ID</th>
              <th>State</th>
              <th>Create Date</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((row) => (
              <tr key={row.rel_id}>
                <td>{row.rel_id}</td>
                <td>{row.test_case_template_id}</td>
                <td>{row.pre_test_case_template_id}</td>
                <td>{row.tenant_id ?? "-"}</td>
                <td>{row.state ?? 0}</td>
                <td>{row.create_date || "-"}</td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-link"
                      onClick={() => handleEdit(row.rel_id)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-link danger"
                      onClick={() => handleDelete(row.rel_id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
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