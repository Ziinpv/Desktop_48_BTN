export function vnd(n) {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(Number(n || 0));
}

export function fmtDate(value) {
  if (!value) return "—";
  const d = String(value).slice(0, 10);
  const [y, m, day] = d.split("-");
  if (!y || !m || !day) return value;
  return `${day}/${m}/${y}`;
}

export function errText(e) {
  return e?.response?.data?.detail || e?.message || "Đã xảy ra lỗi";
}
