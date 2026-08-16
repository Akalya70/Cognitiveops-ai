import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      "Network error. Please check that the backend is running.";
    return Promise.reject(new Error(message));
  }
);

// Dashboard
export const getDashboardSummary = () => client.get("/dashboard/summary").then((r) => r.data);

// Services
export const getServices = () => client.get("/services").then((r) => r.data);
export const getService = (id) => client.get(`/services/${id}`).then((r) => r.data);
export const createService = (payload) => client.post("/services", payload).then((r) => r.data);
export const updateService = (id, payload) => client.put(`/services/${id}`, payload).then((r) => r.data);

// Incidents
export const getIncidents = (params = {}) => client.get("/incidents", { params }).then((r) => r.data);
export const getIncident = (id) => client.get(`/incidents/${id}`).then((r) => r.data);
export const createIncident = (payload) => client.post("/incidents", payload).then((r) => r.data);
export const updateIncident = (id, payload) => client.put(`/incidents/${id}`, payload).then((r) => r.data);
export const deleteIncident = (id) => client.delete(`/incidents/${id}`);
export const analyzeIncident = (id) => client.post(`/incidents/${id}/analyze`).then((r) => r.data);
export const resolveIncident = (id) => client.post(`/incidents/${id}/resolve`).then((r) => r.data);

// Logs
export const getLogs = (params = {}) => client.get("/logs", { params }).then((r) => r.data);
export const createLog = (payload) => client.post("/logs", payload).then((r) => r.data);

// Metrics
export const getMetrics = (params = {}) => client.get("/metrics", { params }).then((r) => r.data);
export const getLatestMetrics = () => client.get("/metrics/latest").then((r) => r.data);
export const getMetricsForService = (serviceName, limit = 100) =>
  client.get(`/metrics/${encodeURIComponent(serviceName)}`, { params: { limit } }).then((r) => r.data);

// Deployments
export const getDeployments = (params = {}) => client.get("/deployments", { params }).then((r) => r.data);
export const createDeployment = (payload) => client.post("/deployments", payload).then((r) => r.data);

// Analysis
export const analyzeService = (serviceName, windowMinutes = 30) =>
  client
    .get(`/analysis/service/${encodeURIComponent(serviceName)}`, { params: { window_minutes: windowMinutes } })
    .then((r) => r.data);

// Simulation
export const simulateNormal = () => client.post("/simulation/normal").then((r) => r.data);
export const simulateDatabaseFailure = () => client.post("/simulation/database-failure").then((r) => r.data);
export const simulateMemoryOverload = () => client.post("/simulation/memory-overload").then((r) => r.data);
export const simulateBadDeployment = () => client.post("/simulation/bad-deployment").then((r) => r.data);
export const simulateNetworkFailure = () => client.post("/simulation/network-failure").then((r) => r.data);
export const simulateApiTimeout = () => client.post("/simulation/api-timeout").then((r) => r.data);

// Auth
export const login = (username, password) => client.post("/auth/login", { username, password }).then((r) => r.data);

export default client;
