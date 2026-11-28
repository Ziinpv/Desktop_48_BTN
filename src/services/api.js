import axios from "axios";
import { store } from "../store";
import { logout } from "../store/authSlice";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

function isLoginRoute() {
  const hash = window.location.hash || "";
  const path = window.location.pathname || "";
  return hash.includes("login") || path.includes("login");
}

function goLogin() {
  if (window.luxeDesktop) window.location.hash = "#/login";
  else window.location.assign("/login");
}

api.interceptors.request.use((config) => {
  const token = store.getState().auth.token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") err.message = detail;
    if (err.response?.status === 401 && !isLoginRoute()) {
      store.dispatch(logout());
      goLogin();
    }
    return Promise.reject(err);
  }
);

export async function downloadFile(url, filename) {
  const res = await api.get(url, { responseType: "blob" });
  const blob = new Blob([res.data]);
  const href = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(href);
}

export default api;
