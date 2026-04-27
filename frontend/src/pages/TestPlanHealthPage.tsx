import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { testopsApi } from "../api/testops";

type PlanItem = {
  plan_name: string;
  latest_batch_id: number;
  latest_success_rate: number;
  latest_total: number;
  latest_failed: number;
  trend: string;
  risk_level: string;
  top_issue?: string;
};

type RootCauseItem = {
  pattern: string;
  count: number;
};

type SortKey = "failed" | "rate" | "name";
type RiskFilter = "ALL" | "HIGH" | "MEDIUM" | "LOW";
type TrendFilter = "ALL" | "UP" | "DOWN" | "STABLE";

export default function TestPlanHealthPage() {
  const nav = useNavigate();

  const [attentionPlans, setAttentionPlans] = useState<PlanItem[]>([]);
  const [corePlans, setCorePlans] = useState<PlanItem[]>([]);
  const [otherPlans, setOtherPlans] = useState<PlanItem[]>([]);
  const [rootCauses, setRootCauses] = useState<RootCauseItem[]>([]);
  const [loading, setLoading] = useState(false);

  // 查询输入态
  const [keywordInput, setKeywordInput] = useState("");

  // 查询应用态
  const [keyword, setKeyword] = useState("");
  const [riskFilter, setRiskFilter] = useState<RiskFilter>("ALL");
  const [trendFilter, setTrendFilter] = useState<TrendFilter>("ALL");
  const [sortKey, setSortKey] = useState<SortKey>("failed");
  const [onlyFailed, setOnlyFailed] = useState(false);

  // Other Plans 折叠
  const [showOther, setShowOther] = useState(false);
  const [showHighGroup, setShowHighGroup] = useState(true);
  const [showMediumGroup, setShowMediumGroup] = useState(true);
  const [showLowGroup, setShowLowGroup] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await testopsApi.getTestPlanHealth();
      const data = res.data || {};

      setAttentionPlans(data.attention_plans || []);
      setCorePlans(data.core_plans || []);
      setOtherPlans(data.non_core_plans || []);
      setRootCauses(data.root_cause_ranking || []);
    } catch (e) {
      console.error(e);
      alert("Failed to load Test Plan Health");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setKeyword(keywordInput);
  };

  const handleReset = () => {
    setKeywordInput("");
    setKeyword("");
    setRiskFilter("ALL");
    setTrendFilter("ALL");
    setSortKey("failed");
    setOnlyFailed(false);
  };

  const goFailure = (batchId?: number, planName?: string, issue?: string) => {
    let url = "/failure-analysis";
    const params = new URLSearchParams();

    if (batchId) params.set("batch_id", String(batchId));
    if (planName) params.set("plan_name", planName);
    if (issue) params.set("issue", issue);

    const query = params.toString();
    if (query) url += `?${query}`;

    nav(url);
  };

  const getTrendIcon = (trend: string) => {
    if (trend === "UP") return "↑";
    if (trend === "DOWN") return "↓";
    return "→";
  };

  const riskRank = (risk: string) => {
    if (risk === "HIGH") return 0;
    if (risk === "MEDIUM") return 1;
    return 2;
  };

  const filterPlans = (plans: PlanItem[]) => {
    return plans.filter((p) => {
      const kw = keyword.toLowerCase().trim();

      const matchKeyword =
        !kw ||

        // Plan 名匹配
        p.plan_name.toLowerCase().includes(kw) ||

        // top_issue 直接匹配
        (p.top_issue || "").toLowerCase().includes(kw) ||

        // ⭐ 反向匹配（很关键）
        kw.includes((p.top_issue || "").toLowerCase()) ||

        // ⭐ 拆词匹配（解决 Billing Account / HeadTable 这种）
        kw.split(" ").some((k) =>
          (p.top_issue || "").toLowerCase().includes(k)
        );

      const matchRisk = riskFilter === "ALL" || p.risk_level === riskFilter;
      const matchTrend = trendFilter === "ALL" || p.trend === trendFilter;
      const matchOnlyFailed = !onlyFailed || p.latest_failed > 0;

      return matchKeyword && matchRisk && matchTrend && matchOnlyFailed;
    });
  };

  const sortPlans = (plans: PlanItem[]) => {
    const cloned = [...plans];

    cloned.sort((a, b) => {
      if (sortKey === "failed") {
        if (b.latest_failed !== a.latest_failed) {
          return b.latest_failed - a.latest_failed;
        }
        return riskRank(a.risk_level) - riskRank(b.risk_level);
      }

      if (sortKey === "rate") {
        return a.latest_success_rate - b.latest_success_rate;
      }

      return a.plan_name.localeCompare(b.plan_name);
    });

    return cloned;
  };

  const filteredAttentionPlans = useMemo(() => {
    return sortPlans(filterPlans(attentionPlans));
  }, [attentionPlans, keyword, riskFilter, trendFilter, onlyFailed, sortKey]);

  const filteredCorePlans = useMemo(() => {
    return sortPlans(filterPlans(corePlans));
  }, [corePlans, keyword, riskFilter, trendFilter, onlyFailed, sortKey]);

  const filteredOtherPlans = useMemo(() => {
    return sortPlans(filterPlans(otherPlans));
  }, [otherPlans, keyword, riskFilter, trendFilter, onlyFailed, sortKey]);

  const groupedOtherPlans = useMemo(() => {
    return {
      HIGH: filteredOtherPlans.filter((p) => p.risk_level === "HIGH"),
      MEDIUM: filteredOtherPlans.filter((p) => p.risk_level === "MEDIUM"),
      LOW: filteredOtherPlans.filter((p) => p.risk_level === "LOW"),
    };
  }, [filteredOtherPlans]);

  const renderPlanRow = (
    p: PlanItem,
    idx: number,
    highlight = false,
    prefix = "row"
  ) => (
    <tr
      key={`${prefix}-${p.plan_name}-${idx}`}
      className={highlight ? "row-highlight" : ""}
      onClick={() => goFailure(p.latest_batch_id, p.plan_name, p.top_issue)}
      style={{ cursor: "pointer" }}
    >
      <td>{p.plan_name}</td>
      <td>{p.latest_success_rate}%</td>
      <td>{getTrendIcon(p.trend)}</td>
      <td>
        <span className={`risk-badge risk-${p.risk_level.toLowerCase()}`}>
          {p.risk_level}
        </span>
      </td>
      <td style={{ color: "#cf1322", fontWeight: 600 }}>
        {p.latest_failed}
      </td>
      <td>{p.top_issue || "-"}</td>
    </tr>
  );

  if (loading) return <div className="loading-box">Loading...</div>;

  return (
    <div className="page-container">
      <div className="page-title">Test Plan Health</div>

      {/* ===============================
          查询条件
      =============================== */}
      <div className="search-card">
        <div className="search-card-title">View Filter</div>

        <div className="search-grid">
          <div className="field">
            <label>Keyword</label>
            <input
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              placeholder="Search by plan name or main issue"
            />
          </div>

          <div className="field">
            <label>Risk</label>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value as RiskFilter)}
            >
              <option value="ALL">All</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="field">
            <label>Trend</label>
            <select
              value={trendFilter}
              onChange={(e) => setTrendFilter(e.target.value as TrendFilter)}
            >
              <option value="ALL">All</option>
              <option value="UP">Up</option>
              <option value="DOWN">Down</option>
              <option value="STABLE">Stable</option>
            </select>
          </div>

          <div className="field">
            <label>Sort By</label>
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
            >
              <option value="failed">Failed Count</option>
              <option value="rate">Success Rate</option>
              <option value="name">Plan Name</option>
            </select>
          </div>

          <div className="field">
            <label>Show Only</label>
            <select
              value={onlyFailed ? "FAILED" : "ALL"}
              onChange={(e) => setOnlyFailed(e.target.value === "FAILED")}
            >
              <option value="ALL">All Plans</option>
              <option value="FAILED">Failed Plans Only</option>
            </select>
          </div>
        </div>

        <div className="search-actions">
          <button className="btn btn-secondary" onClick={handleReset}>
            Clear
          </button>
          <button className="btn btn-primary" onClick={handleSearch}>
            Search
          </button>
        </div>
      </div>

      {/* ===============================
          Need Attention
      =============================== */}
      <div className="table-card">
        <div className="table-header">
          <div>🚨 Need Attention</div>
          <div>Total {filteredAttentionPlans.length}</div>
        </div>

        {filteredAttentionPlans.length === 0 ? (
          <div className="empty-row">No Data</div>
        ) : (
          <div>
            {filteredAttentionPlans.map((p, idx) => (
              <div
                key={`attention-${idx}`}
                className="attention-item"
                onClick={() =>
                  goFailure(p.latest_batch_id, p.plan_name, p.top_issue)
                }
              >
                <div className="attention-title">
                  {idx + 1}. {p.plan_name}
                </div>
                <div className="attention-meta">
                  Failed: {p.latest_failed} | Rate: {p.latest_success_rate}%
                </div>
                <div className="attention-issue">{p.top_issue || "-"}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ===============================
          Core Plans
      =============================== */}
      <div className="table-card">
        <div className="table-header">
          <div>⭐ Core Plans</div>
          <div>Total {filteredCorePlans.length}</div>
        </div>

        {filteredCorePlans.length === 0 ? (
          <div className="empty-row">No Data</div>
        ) : (
          <table className="case-table fixed-table">
            <thead>
              <tr>
                <th style={{ width: "35%" }}>Plan</th>
                <th style={{ width: "15%" }}>Success Rate</th>
                <th style={{ width: "10%" }}>Trend</th>
                <th style={{ width: "15%" }}>Risk</th>
                <th style={{ width: "10%" }}>Failed</th>
                <th style={{ width: "15%" }}>Main Issue</th>
              </tr>
            </thead>
            <tbody>
              {filteredCorePlans.map((p, idx) =>
                renderPlanRow(p, idx, true, "core")
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* ===============================
          Other Plans
      =============================== */}
      <div className="table-card">
        <div
          className="table-header clickable-header"
          onClick={() => setShowOther((v) => !v)}
          title="Click to expand/collapse"
        >
          <div>📊 Other Plans ({filteredOtherPlans.length})</div>
          <div>{showOther ? "▲" : "▼"}</div>
        </div>

        {!showOther ? (
          <div className="empty-row">Other plans are grouped and collapsed. Click to expand.</div>
        ) : filteredOtherPlans.length === 0 ? (
          <div className="empty-row">No Data</div>
        ) : (
          <table className="case-table fixed-table">
            <thead>
              <tr>
                <th style={{ width: "35%" }}>Plan</th>
                <th style={{ width: "15%" }}>Success Rate</th>
                <th style={{ width: "10%" }}>Trend</th>
                <th style={{ width: "15%" }}>Risk</th>
                <th style={{ width: "10%" }}>Failed</th>
                <th style={{ width: "15%" }}>Main Issue</th>
              </tr>
            </thead>

            <tbody>
              <tr
                className="group-row"
                onClick={() => setShowHighGroup((v) => !v)}
              >
                <td colSpan={6}>
                  🔥 High Risk ({groupedOtherPlans.HIGH.length}) {showHighGroup ? "▲" : "▼"}
                </td>
              </tr>
              {showHighGroup &&
                groupedOtherPlans.HIGH.map((p, idx) =>
                  renderPlanRow(p, idx, false, "high")
                )}

              <tr
                className="group-row"
                onClick={() => setShowMediumGroup((v) => !v)}
              >
                <td colSpan={6}>
                  🟡 Medium Risk ({groupedOtherPlans.MEDIUM.length}) {showMediumGroup ? "▲" : "▼"}
                </td>
              </tr>
              {showMediumGroup &&
                groupedOtherPlans.MEDIUM.map((p, idx) =>
                  renderPlanRow(p, idx, false, "medium")
                )}

              <tr
                className="group-row"
                onClick={() => setShowLowGroup((v) => !v)}
              >
                <td colSpan={6}>
                  🟢 Low Risk ({groupedOtherPlans.LOW.length}) {showLowGroup ? "▲" : "▼"}
                </td>
              </tr>
              {showLowGroup &&
                groupedOtherPlans.LOW.map((p, idx) =>
                  renderPlanRow(p, idx, false, "low")
                )}
            </tbody>
          </table>
        )}
      </div>

      {/* ===============================
          Top Root Causes
      =============================== */}
      <div className="table-card">
        <div className="table-header">
          <div>🔥 Top Root Causes</div>
          <div>Total {rootCauses.length}</div>
        </div>

        {rootCauses.length === 0 ? (
          <div className="empty-row">No Data</div>
        ) : (
          <div className="pattern-list">
            {rootCauses.map((r, idx) => (
              <div
                key={`root-${idx}`}
                className="pattern-card"
                onClick={() => {
                  // const keyword = r.pattern
                  //   .toLowerCase()
                  //   .replace("selector:", "")
                  //   .replace("sap api:", "")
                  //   .replace(/[_:]/g, " ")
                  //   .trim();

                  // setKeyword(keyword);
                  // setKeywordInput(keyword); // ⭐ 同步输入框（很重要）
                  // setShowOther(true);
                  // window.scrollTo({ top: 300, behavior: "smooth" });
                }}
              >
                <div className="pattern-left">
                  <div className="pattern-title">{r.pattern}</div>
                  {/* <div className="pattern-suggestion">
                    Click to filter related plans
                  </div> */}
                </div>

                <div className="pattern-count">{r.count}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}