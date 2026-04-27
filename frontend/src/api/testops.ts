import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 15000
});

export type CaseSearchParams = {
  case_name?: string;
  environment?: string;
  machine?: string;
  template_id?: number | "";
  verify_template_id?: number | "";
};

export const testopsApi = {
  // Case
  getCases(params?: any) {
    return API.get("/case-tasks", { params });
  },

  getCaseDetail(cfgId: number) {
    return API.get(`/case-tasks/${cfgId}`);
  },

  createCase(data: any) {
    return API.post("/case-tasks", data);
  },

  updateCase(cfgId: number, data: any) {
    return API.put(`/case-tasks/${cfgId}`, data);
  },

  deleteCase(cfgId: number) {
    return API.delete(`/case-tasks/${cfgId}`);
  },

    // Template
  getTemplates(params?: any) {
    return API.get("/templates", { params });
  },

  getTemplateDetail(templateId: number) {
    return API.get(`/templates/${templateId}`);
  },

  createTemplate(data: any) {
    return API.post("/templates", data);
  },

  updateTemplate(templateId: number, data: any) {
    return API.put(`/templates/${templateId}`, data);
  },

  deleteTemplate(templateId: number) {
    return API.delete(`/templates/${templateId}`);
  },

  //Template Rel
  getTemplateRelations: (params: any) =>
  API.get("/template-relations", { params }),

  getTemplateRelationDetail: (relId: number) =>
    API.get(`/template-relations/${relId}`),

  createTemplateRelation: (data: any) =>
    API.post("/template-relations", data),

  updateTemplateRelation: (relId: number, data: any) =>
    API.put(`/template-relations/${relId}`, data),

  deleteTemplateRelation: (relId: number) =>
    API.delete(`/template-relations/${relId}`),

  // Component
  getComponents(params?: any) {
    return API.get("/components", { params });
  },

  getComponentDetail(componentId: number) {
    return API.get(`/components/${componentId}`);
  },

  createComponent(data: any) {
    return API.post("/components", data);
  },

  updateComponent(componentId: number, data: any) {
    return API.put(`/components/${componentId}`, data);
  },

  deleteComponent(componentId: number) {
    return API.delete(`/components/${componentId}`);
  },

  // Parameter
  getParameters(params?: any) {
    return API.get("/parameters", { params });
  },

  getParameterDetail(parameterId: number) {
    return API.get(`/parameters/${parameterId}`);
  },

  createParameter(data: any) {
    return API.post("/parameters", data);
  },

  updateParameter(parameterId: number, data: any) {
    return API.put(`/parameters/${parameterId}`, data);
  },

  deleteParameter(parameterId: number) {
    return API.delete(`/parameters/${parameterId}`);
  },

  // Component Parameter
  getComponentParameters(params?: any) {
    return API.get("/component-parameters", { params });
  },

  getComponentParameterDetail(id: number) {
    return API.get(`/component-parameters/${id}`);
  },

  createComponentParameter(data: any) {
    return API.post("/component-parameters", data);
  },

  updateComponentParameter(id: number, data: any) {
    return API.put(`/component-parameters/${id}`, data);
  },

  deleteComponentParameter(id: number) {
    return API.delete(`/component-parameters/${id}`);
  },

  // ===== Test Dispatcher / Test Plan Config =====
  getTestDispatchers(params: any) {
    return API.get("/test-dispatcher", { params });
  },

  getTestDispatcherDetail(dispatcherPlanId: number) {
    return API.get(`/test-dispatcher/${dispatcherPlanId}`);
  },

  createTestDispatcher(data: any) {
    return API.post("/test-dispatcher", data);
  },

  updateTestDispatcher(dispatcherPlanId: number, data: any) {
    return API.put(`/test-dispatcher/${dispatcherPlanId}`, data);
  },

  deleteTestDispatcher(dispatcherPlanId: number) {
    return API.delete(`/test-dispatcher/${dispatcherPlanId}`);
  },

  // ===== Plan Runs =====
  getPlanRuns(params: any) {
    return API.get("/test-plans", { params });
  },

    // ===== Batch Detail =====
  getBatchDetails(params: any) {
    return API.get("/batch-details", { params });
  },

  // ===== Component Execution =====
  getComponentExecutions: (params: any) =>
    API.get("/component-executions", { params }),

  // ===== Case Executions =====
  getCaseExecutions: (params: any) =>
  API.get("/case-executions", { params }),

  // ===== Test Plan Health =====
  getTestPlanHealth() {
    return API.get("/test-plan-health");
  },

    // ===== Failure Analysis =====
  getFailureAnalysis(params: any) {
    return API.get("/failure-analysis", { params });
  }

  
};

export async function getComponents() {
  const res = await fetch("http://127.0.0.1:8000/components");
  return res.json();
}

export async function getParameters() {
  const res = await fetch("http://127.0.0.1:8000/parameters");
  return res.json();
}


