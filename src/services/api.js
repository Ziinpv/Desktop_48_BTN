import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  try {
    const saved = JSON.parse(localStorage.getItem("luxe-auth") || "null");
    if (saved?.token) config.headers.Authorization = `Bearer ${saved.token}`;
  } catch {
    /* ignore */
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") err.message = detail;
    if (err.response?.status === 401 && !window.location.hash.includes("login") && !window.location.pathname.includes("login")) {
      localStorage.removeItem("luxe-auth");
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
