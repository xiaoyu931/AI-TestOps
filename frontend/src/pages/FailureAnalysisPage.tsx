import { useMemo, useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { testopsApi } from "../api/testops";

type SearchForm = {
  batch_id: string;
  cfg_id: string;
  uipath_case_name: string;
  create_date_from: string;
  create_date_to: string;
};

type Summary = {
  total: number;
  failed: number;
  success: number;
  success_rate: number;
};

type StageItem = {
  stage: string;
  count: number;
};

type ErrorTypeItem = {
  error_type: string;
  count: number;
};

type PatternItem = {
  pattern: string;
  title: string;
  suggestion: string;
  count: number;
  percent: number;
};

type FailureDetail = {
  test_case_exe_id: number;
  batch_id?: number;
  cfg_id?: number;
  uipath_case_name?: string;
  stage: string;
  state: number;
  state_text: string;
  error_type: string;
  error_reason?: string;
  suggestion?: string;
  error_pattern?: string;
  error_summary?: string;
  component_name?: string;
  create_date?: string;
  finish_date?: string;
};

const initialSearchForm: SearchForm = {
  batch_id: "",
  cfg_id: "",
  uipath_case_name: "",
  create_date_from: "",
  create_date_to: ""
};

const emptySummary: Summary = {
  total: 0,
  failed: 0,
  success: 0,
  success_rate: 0
};

function getErrorTypeColor(errorType: string) {
  switch (errorType) {
    case "UI_SELECTOR":
      return "#d4380d";
    case "DATA_ERROR":
      return "#1677ff";
    case "TIMEOUT":
      return "#fa8c16";
    case "LOGIN":
      return "#722ed1";
    case "NETWORK":
      return "#13c2c2";
    case "SCRIPT_CAPTURE_ERROR":
      return "#cf1322";
    case "CODE_ERROR":
      return "#595959";
    default:
      return "#666";
  }
}

export default function FailureAnalysisPage() {
  const [searchParams] = useSearchParams();

  const batchIdFromUrl = searchParams.get("batch_id") || "";
  const planNameFromUrl = searchParams.get("plan_name") || "";
  const issueFromUrl = searchParams.get("issue") || "";

  const [searchForm, setSearchForm] = useState<SearchForm>({
    ...initialSearchForm,
    batch_id: batchIdFromUrl
  });

  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [stageDistribution, setStageDistribution] = useState<StageItem[]>([]);
  const [errorTypeDistribution, setErrorTypeDistribution] = useState<ErrorTypeItem[]>([]);
  const [patternDistribution, setPatternDistribution] = useState<PatternItem[]>([]);
  const [topIssue, setTopIssue] = useState<PatternItem | null>(null);
  const [failureDetails, setFailureDetails] = useState<FailureDetail[]>([]);

  const [selectedPattern, setSelectedPattern] = useState<string | null>(issueFromUrl || null);
  const [loading, setLoading] = useState(false);

  const loadData = async (currentSearch = searchForm) => {
    setLoading(true);
    try {
      const res = await testopsApi.getFailureAnalysis({
        batch_id: currentSearch.batch_id ? Number(currentSearch.batch_id) : undefined,
        cfg_id: currentSearch.cfg_id ? Number(currentSearch.cfg_id) : undefined,
        uipath_case_name: currentSearch.uipath_case_name || undefined,
        create_date_from: currentSearch.create_date_from || undefined,
        create_date_to: currentSearch.create_date_to || undefined
      });

      const data = res.data || {};

      setSummary(data.summary || emptySummary);
      setStageDistribution(data.stage_distribution || []);
      setErrorTypeDistribution(data.error_type_distribution || []);
      setPatternDistribution(data.error_pattern_distribution || []);
      setTopIssue(data.top_issue || null);
      setFailureDetails(data.failure_details || []);

      if (!issueFromUrl) {
        setSelectedPattern(null);
      }
    } catch (e: any) {
      console.error("Load failure analysis error:", e);
      alert(e?.response?.data?.detail || "Failed to load failure analysis");
    } finally {
      setLoading(false);
    }
  };

  // 进入页面时，如果 URL 里有 batch_id，则自动查询
  useEffect(() => {
    const nextSearchForm: SearchForm = {
      ...initialSearchForm,
      batch_id: batchIdFromUrl
    };

    setSearchForm(nextSearchForm);

    if (batchIdFromUrl) {
      loadData(nextSearchForm);
    }
  }, [batchIdFromUrl]);

  // 如果 URL 里带了 issue，等 patternDistribution 加载出来后自动匹配选中
  useEffect(() => {
    if (!issueFromUrl || patternDistribution.length === 0) return;

    const target = patternDistribution.find((item) => {
      return (
        item.pattern === issueFromUrl ||
        item.title === issueFromUrl ||
        item.pattern.toLowerCase() === issueFromUrl.toLowerCase() ||
        item.title.toLowerCase() === issueFromUrl.toLowerCase()
      );
    });

    if (target) {
      setSelectedPattern(target.pattern);
    }
  }, [issueFromUrl, patternDistribution]);

  const handleSearch = async () => {
    await loadData(searchForm);
  };

  const handleClear = async () => {
    setSearchForm(initialSearchForm);
    setSummary(emptySummary);
    setStageDistribution([]);
    setErrorTypeDistribution([]);
    setPatternDistribution([]);
    setTopIssue(null);
    setFailureDetails([]);
    setSelectedPattern(null);
  };

  const filteredFailureDetails = useMemo(() => {
    if (!selectedPattern) {
      return failureDetails;
    }
    return failureDetails.filter(
      (row) => row.error_pattern === selectedPattern
    );
  }, [failureDetails, selectedPattern]);

  return (
    <div className="page-container">
      <div className="page-title">
        Failure Analysis
        {planNameFromUrl ? ` - ${planNameFromUrl}` : ""}
      </div>

      <div className="search-card">
        <div className="search-card-title">Search Condition</div>

        <div className="search-grid">
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
            <label>UiPath Case Name</label>
            <input
              value={searchForm.uipath_case_name}
              onChange={(e) =>
                setSearchForm({
                  ...searchForm,
                  uipath_case_name: e.target.value
                })
              }
              placeholder="Enter UiPath case name"
            />
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

      <div className="summary-grid">
        <div className="summary-card">
          <div className="summary-card-label">Total Cases</div>
          <div className="summary-card-value">{summary.total}</div>
        </div>

        <div className="summary-card">
          <div className="summary-card-label">Failed Cases</div>
          <div className="summary-card-value failure">{summary.failed}</div>
        </div>

        <div className="summary-card">
          <div className="summary-card-label">Success Cases</div>
          <div className="summary-card-value success">{summary.success}</div>
        </div>

        <div className="summary-card">
          <div className="summary-card-label">Success Rate</div>
          <div className="summary-card-value">{summary.success_rate}%</div>
        </div>
      </div>

      {topIssue && (
        <div
          className="table-card"
          style={{
            background: "#fff7e6",
            border: "1px solid #ffd591"
          }}
        >
          <div
            style={{
              fontSize: 14,
              fontWeight: 700,
              color: "#d46b08",
              marginBottom: 8
            }}
          >
            🔥 Top Root Cause
          </div>

          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: "#262626",
              marginBottom: 8
            }}
          >
            {topIssue.title}
          </div>

          <div
            style={{
              fontSize: 14,
              color: "#595959",
              marginBottom: 8
            }}
          >
            {topIssue.suggestion}
          </div>

          <div
            style={{
              fontSize: 13,
              color: "#8c8c8c"
            }}
          >
            Affected Cases: {topIssue.count} ({topIssue.percent}% of failed cases)
          </div>
        </div>
      )}

      <div className="analysis-two-columns">
        <div className="table-card">
          <div className="table-header">
            <div>Failure Stage Distribution</div>
            <div>Total {stageDistribution.reduce((sum, item) => sum + item.count, 0)}</div>
          </div>

          {stageDistribution.length === 0 ? (
            <div className="empty-row">No Data</div>
          ) : (
            <table className="case-table">
              <thead>
                <tr>
                  <th>Stage</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {stageDistribution.map((item) => (
                  <tr key={item.stage}>
                    <td>{item.stage}</td>
                    <td>{item.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="table-card">
          <div className="table-header">
            <div>Error Type Distribution</div>
            <div>Total {errorTypeDistribution.reduce((sum, item) => sum + item.count, 0)}</div>
          </div>

          {errorTypeDistribution.length === 0 ? (
            <div className="empty-row">No Data</div>
          ) : (
            <table className="case-table">
              <thead>
                <tr>
                  <th>Error Type</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {errorTypeDistribution.map((item) => (
                  <tr key={item.error_type}>
                    <td>{item.error_type}</td>
                    <td>{item.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>Error Pattern Distribution</div>
          <div>Total {patternDistribution.reduce((sum, item) => sum + item.count, 0)}</div>
        </div>

        {patternDistribution.length === 0 ? (
          <div className="empty-row">No Data</div>
        ) : (
          <div className="pattern-list">
            {patternDistribution.map((item) => {
              const selected = selectedPattern === item.pattern;

              return (
                <div
                  key={item.pattern}
                  className="pattern-card"
                  onClick={() =>
                    setSelectedPattern(selected ? null : item.pattern)
                  }
                  style={{
                    cursor: "pointer",
                    background: selected ? "#e6f4ff" : undefined,
                    border: selected ? "1px solid #91caff" : undefined
                  }}
                  title="Click to filter failure details"
                >
                  <div className="pattern-left">
                    <div className="pattern-title">
                      {item.title}
                    </div>

                    <div className="pattern-suggestion">
                      {item.suggestion}
                    </div>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <div className="pattern-count">
                      {item.count}
                    </div>

                    <div style={{ fontSize: 12, color: "#888" }}>
                      {item.percent}%
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="table-card">
        <div className="table-header">
          <div>
            Failure Detail List
            {selectedPattern && (
              <span style={{ marginLeft: 8, color: "#1677ff", fontWeight: 500 }}>
                (Filtered by selected pattern)
              </span>
            )}
          </div>

          <div>
            Total {filteredFailureDetails.length}
            {selectedPattern && (
              <button
                className="btn btn-link"
                style={{ marginLeft: 12 }}
                onClick={() => setSelectedPattern(null)}
              >
                Clear Filter
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading-box">Loading...</div>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>Test Case Exe ID</th>
                <th>Batch ID</th>
                <th>CFG ID</th>
                <th>UiPath Case Name</th>
                <th>Stage</th>
                <th>Status</th>
                <th>Error Type</th>
                <th>Reason</th>
                <th>Suggestion</th>
                <th>Component</th>
                <th>Error Summary</th>
                <th>Create Date</th>
              </tr>
            </thead>

            <tbody>
              {filteredFailureDetails.map((row) => (
                <tr key={`${row.test_case_exe_id}-${row.error_pattern || "na"}`}>
                  <td>{row.test_case_exe_id}</td>
                  <td>{row.batch_id ?? "-"}</td>
                  <td>{row.cfg_id ?? "-"}</td>
                  <td>{row.uipath_case_name || "-"}</td>
                  <td>{row.stage}</td>
                  <td>{row.state_text}</td>

                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        padding: "2px 8px",
                        borderRadius: 12,
                        fontSize: 12,
                        fontWeight: 600,
                        color: "#fff",
                        background: getErrorTypeColor(row.error_type)
                      }}
                    >
                      {row.error_type}
                    </span>
                  </td>

                  <td className="error-reason">
                    {row.error_reason || "-"}
                  </td>

                  <td
                    className="error-suggestion"
                    title={row.suggestion || ""}
                    style={{
                      maxWidth: 260,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      fontSize: 13
                    }}
                  >
                    {row.suggestion || "-"}
                  </td>

                  <td>{row.component_name || "Not Triggered"}</td>

                  <td
                    className="error-summary"
                    title={row.error_summary || ""}
                    style={{
                      maxWidth: 360,
                      whiteSpace: "normal",
                      wordBreak: "break-word",
                      lineHeight: 1.5
                    }}
                  >
                    {row.error_summary || "-"}
                  </td>

                  <td>{row.create_date || "-"}</td>
                </tr>
              ))}

              {!loading && filteredFailureDetails.length === 0 && (
                <tr>
                  <td colSpan={12} className="empty-row">
                    No Data
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}