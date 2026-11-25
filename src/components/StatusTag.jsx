import { Tag } from "antd";

const MAP = {
  active: { color: "green", vi: "Hoạt động", en: "Active" },
  inactive: { color: "default", vi: "Ngừng", en: "Inactive" },
  out_of_stock: { color: "orange", vi: "Hết hàng", en: "Out of stock" },
  SAN_SANG: { color: "green", vi: "Còn hàng", en: "Ready" },
  DANG_THUE: { color: "blue", vi: "Đang thuê", en: "Renting" },
  HET_HANG: { color: "orange", vi: "Hết hàng", en: "Unavailable" },
  HON_HOC: { color: "red", vi: "Hỏng hóc", en: "Damaged" },
  QUA_HAN: { color: "red", vi: "Quá hạn", en: "Overdue" },
  DA_TRA: { color: "green", vi: "Đã trả", en: "Returned" },
  HUY: { color: "default", vi: "Hủy", en: "Cancelled" },
  DUNG_HAN: { color: "green", vi: "Đúng hạn", en: "On time" },
  TRE_HAN: { color: "red", vi: "Trễ hạn", en: "Late" },
  TRONG_HAN: { color: "blue", vi: "Trong hạn", en: "On schedule" },
  SAP_HET_HAN: { color: "orange", vi: "Sắp hết hạn", en: "Due soon" },
  THANH_TOAN_PHAT: { color: "gold", vi: "Thanh toán phí", en: "Penalty paid" },
};

export default function StatusTag({ value, lang = "vi" }) {
  const meta = MAP[value] || { color: "purple", vi: value, en: value };
  return <Tag color={meta.color}>{lang === "en" ? meta.en : meta.vi}</Tag>;
}
