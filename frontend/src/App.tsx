import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
  useLocation,
  useParams,
} from "react-router-dom";

import CaseListPage from "./pages/CaseListPage";
import CaseFormPage from "./pages/CaseFormPage";

import TemplateListPage from "./pages/TemplateListPage";
import TemplateFormPage from "./pages/TemplateFormPage";

import ComponentListPage from "./pages/ComponentListPage";
import ComponentFormPage from "./pages/ComponentFormPage";

import ParameterListPage from "./pages/ParameterListPage";
import ParameterFormPage from "./pages/ParameterFormPage";

import ComponentParameterListPage from "./pages/ComponentParameterListPage";
import ComponentParameterFormPage from "./pages/ComponentParameterFormPage";

import TemplateRelationListPage from "./pages/TemplateRelationListPage";
import TemplateRelationFormPage from "./pages/TemplateRelationFormPage";

import TestDispatcherListPage from "./pages/TestDispatcherListPage";
import PlanRunListPage from "./pages/PlanRunListPage";
import BatchDetailPage from "./pages/BatchDetailPage";
import TestDispatcherFormPage from "./pages/TestDispatcherFormPage";

import CaseExecutionListPage from "./pages/CaseExecutionListPage";
import ComponentExecutionListPage from "./pages/ComponentExecutionListPage";

import FailureAnalysisPage from "./pages/FailureAnalysisPage";
import TestPlanHealthPage from "./pages/TestPlanHealthPage";

/* ================= Wrapper ================= */

const CaseEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <CaseFormPage
      mode="edit"
      cfgId={id ? Number(id) : null}
      onBack={() => nav("/case")}
      onSaved={() => nav("/case")}
    />
  );
};

const TemplateEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <TemplateFormPage
      mode="edit"
      templateId={id ? Number(id) : null}
      onBack={() => nav("/template")}
      onSaved={() => nav("/template")}
    />
  );
};

const TemplateRelationEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <TemplateRelationFormPage
      relId={id ? Number(id) : null}
      onBack={() => nav("/template-relation")}
      onSaved={() => nav("/template-relation")}
    />
  );
};

const ComponentEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <ComponentFormPage
      mode="edit"
      componentId={id ? Number(id) : null}
      onBack={() => nav("/component")}
      onSaved={() => nav("/component")}
    />
  );
};

const ParameterEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <ParameterFormPage
      mode="edit"
      parameterId={id ? Number(id) : null}
      onBack={() => nav("/parameter")}
      onSaved={() => nav("/parameter")}
    />
  );
};

const MappingEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <ComponentParameterFormPage
      id={id ? Number(id) : undefined}
      onBack={() => nav("/mapping")}
    />
  );
};

const DispatcherEditWrapper = () => {
  const { id } = useParams();
  const nav = useNavigate();

  return (
    <TestDispatcherFormPage
      id={id ? Number(id) : null}
      onBack={() => nav("/dispatcher")}
    />
  );
};

/* ⭐ Execution Detail Wrapper */
const BatchWrapper = () => {
  const { id } = useParams();

  return (
    <BatchDetailPage
      key={id || "all"}   // ⭐ 防止状态复用
      batchId={id ? Number(id) : null}
    />
  );
};

/* ⭐ Component Execution Wrapper */
const ComponentExecutionWrapper = () => {
  const { id } = useParams();

  return (
    <ComponentExecutionListPage
      key={id || "all"}   // ⭐ 核心优化
      caseExeId={id ? Number(id) : null}
    />
  );
};

/* ================= Layout ================= */

function Layout() {
  const nav = useNavigate();
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + "/");

  return (
    <div className="layout-shell">
      <div className="sidebar">
        <div className="sidebar-logo">TestOps</div>

        {/* CASE */}
        <div className="sidebar-group-title">Case</div>
        <div
          className={`sidebar-item ${isActive("/case") ? "active" : ""}`}
          onClick={() => nav("/case")}
        >
          Case Management
        </div>

        {/* TEST PLAN */}
        <div className="sidebar-group-title">Test Plan</div>

        <div
          className={`sidebar-item ${isActive("/dispatcher") ? "active" : ""}`}
          onClick={() => nav("/dispatcher")}
        >
          Test Plan Config
        </div>

        <div
          className={`sidebar-item ${isActive("/plan-runs") ? "active" : ""}`}
          onClick={() => nav("/plan-runs")}
        >
          Plan Runs
        </div>

        <div
          className={`sidebar-item ${isActive("/execution-detail") ? "active" : ""}`}
          onClick={() => nav("/execution-detail")}
        >
          Execution Detail
        </div>

        {/* EXECUTION */}
        <div className="sidebar-group-title">Execution</div>

        <div
          className={`sidebar-item ${isActive("/case-execution") ? "active" : ""}`}
          onClick={() => nav("/case-execution")}
        >
          Case Execution
        </div>

        <div
          className={`sidebar-item ${isActive("/component-execution") ? "active" : ""}`}
          onClick={() => nav("/component-execution")}
        >
          Component Execution
        </div>

        {/* ANALYSIS */}
        <div className="sidebar-group-title">Analysis</div>

        <div
          className={`sidebar-item ${isActive("/failure-analysis") ? "active" : ""}`}
          onClick={() => nav("/failure-analysis")}
        >
          Failure Analysis
        </div>
        <div
          className={`sidebar-item ${
            isActive("/test-plan-health") ? "active" : ""
          }`}
          onClick={() => nav("/test-plan-health")}
        >
          Test Plan Health
        </div>


        {/* TEMPLATE */}
        <div className="sidebar-group-title">Template Layer</div>

        <div
          className={`sidebar-item ${isActive("/template") ? "active" : ""}`}
          onClick={() => nav("/template")}
        >
          Template Management
        </div>

        <div
          className={`sidebar-item ${isActive("/template-relation") ? "active" : ""}`}
          onClick={() => nav("/template-relation")}
        >
          Template Relation Management
        </div>

        <div
          className={`sidebar-item ${isActive("/component") ? "active" : ""}`}
          onClick={() => nav("/component")}
        >
          Component Management
        </div>

        <div
          className={`sidebar-item ${isActive("/parameter") ? "active" : ""}`}
          onClick={() => nav("/parameter")}
        >
          Parameter Management
        </div>

        <div
          className={`sidebar-item ${isActive("/mapping") ? "active" : ""}`}
          onClick={() => nav("/mapping")}
        >
          Component Parameter Mapping
        </div>
      </div>

      <div className="layout-main">
        <div className="layout-content">
        <Routes>

          {/* CASE */}
          <Route path="/case" element={<CaseListPage />} />
          <Route path="/case/create" element={
            <CaseFormPage mode="create" cfgId={null} onBack={() => nav("/case")} onSaved={() => nav("/case")} />
          } />
          <Route path="/case/edit/:id" element={<CaseEditWrapper />} />

          {/* TEST PLAN */}
          <Route path="/dispatcher" element={<TestDispatcherListPage />} />
          <Route path="/dispatcher/create" element={<TestDispatcherFormPage id={null} onBack={() => nav("/dispatcher")} />} />
          <Route path="/dispatcher/edit/:id" element={<DispatcherEditWrapper />} />

          {/* PLAN RUN */}
          <Route path="/plan-runs" element={<PlanRunListPage />} />

          {/* Execution Detail */}
          <Route path="/execution-detail" element={<BatchDetailPage />} />
          <Route path="/execution-detail/:id" element={<BatchWrapper />} />

          {/* EXECUTION */}
          <Route path="/case-execution" element={<CaseExecutionListPage />} />

          <Route
            path="/component-execution"
            element={<ComponentExecutionListPage caseExeId={null} />}
          />
          <Route
            path="/component-execution/:id"
            element={<ComponentExecutionWrapper />}
          />

          {/* ANALYSIS */}
          <Route path="/failure-analysis" element={<FailureAnalysisPage />} />
          <Route path="/test-plan-health" element={<TestPlanHealthPage />} />

          {/* TEMPLATE */}
          <Route path="/template" element={<TemplateListPage />} />
          <Route path="/template/create" element={<TemplateFormPage mode="create" templateId={null} onBack={() => nav("/template")} onSaved={() => nav("/template")} />} />
          <Route path="/template/edit/:id" element={<TemplateEditWrapper />} />

          {/* TEMPLATE RELATION */}
          <Route path="/template-relation" element={<TemplateRelationListPage />} />
          <Route path="/template-relation/create" element={<TemplateRelationFormPage relId={null} onBack={() => nav("/template-relation")} onSaved={() => nav("/template-relation")} />} />
          <Route path="/template-relation/edit/:id" element={<TemplateRelationEditWrapper />} />

          {/* COMPONENT */}
          <Route path="/component" element={<ComponentListPage />} />
          <Route path="/component/create" element={<ComponentFormPage mode="create" componentId={null} onBack={() => nav("/component")} onSaved={() => nav("/component")} />} />
          <Route path="/component/edit/:id" element={<ComponentEditWrapper />} />

          {/* PARAMETER */}
          <Route path="/parameter" element={<ParameterListPage />} />
          <Route path="/parameter/create" element={<ParameterFormPage mode="create" parameterId={null} onBack={() => nav("/parameter")} onSaved={() => nav("/parameter")} />} />
          <Route path="/parameter/edit/:id" element={<ParameterEditWrapper />} />

          {/* MAPPING */}
          <Route path="/mapping" element={<ComponentParameterListPage />} />
          <Route path="/mapping/create" element={<ComponentParameterFormPage onBack={() => nav("/mapping")} />} />
          <Route path="/mapping/edit/:id" element={<MappingEditWrapper />} />

        </Routes>
        </div>
      </div>
    </div>
  );
}

/* ================= App ================= */

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}