import { useEffect, useState } from "react";
import { Button, Select, Space, Table, App } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import api, { downloadFile } from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";
import { useSelector } from "react-redux";
import StatusTag from "../components/StatusTag";
import { canDo } from "../utils/roles";

export default function Unreturned() {
  const { message, modal } = App.useApp();
  const canReturn = canDo(useSelector((s) => s.auth.user?.role), "returnDress");
  const [rows, setRows] = useState([]);
  const [sort, setSort] = useState("date");

  const load = async () => {
    const { data } = await api.get("/api/reports/unreturned", { params: { sort } });
    setRows(data);
  };
  useEffect(() => { load(); }, [sort]);

  return (
    <div>
      <div className="page-head">
        <h1>F5 · Khách hàng thuê chưa trả</h1>
        <p>Hợp đồng còn ≤ 3 ngày được tô cam · Desktop / email / SMS nhắc khách khi studio bật</p>
      </div>
      <Space style={{ marginBottom: 16 }} wrap>
        <Select value={sort} onChange={setSort} options={[{ value: "date", label: "Theo hạn trả" }, { value: "customer", label: "Theo tên khách" }]} />
        <Button icon={<DownloadOutlined />} onClick={() => downloadFile("/api/export/unreturned.csv", "chua-tra.csv")}>CSV</Button>
        <Button onClick={() => downloadFile("/api/export/unreturned.xlsx", "chua-tra.xlsx")}>Excel</Button>
        <Button onClick={() => downloadFile("/api/export/unreturned.pdf", "chua-tra.pdf")}>PDF</Button>
        <Button onClick={async () => {
          try {
            const { data } = await api.post("/api/system/remind", { channels: ["email", "sms"] });
            message.success(`Đã gửi ${data.sent} nhắc hạn (email/SMS). Thất bại: ${data.failed}`);
          } catch (e) { message.error(errText(e)); }
        }}>Gửi email/SMS nhắc hạn</Button>
      </Space>
      <Table
        rowKey="maHopDong"
        dataSource={rows}
        rowClassName={(r) => (r.trangThai === "QUA_HAN" ? "overdue-row" : r.sapHetHan ? "soon-row" : "")}
        columns={[
          { title: "Mã HĐ", dataIndex: "maHopDong" },
          { title: "Khách hàng", dataIndex: "tenKH", sorter: (a, b) => a.tenKH.localeCompare(b.tenKH) },
          { title: "SĐT", dataIndex: "sdt" },
          { title: "Bộ áo", dataIndex: "items", render: (items) => items.map((i) => `${i.maDress} ${i.tenAo}`).join("; ") },
          { title: "Ngày thuê", dataIndex: "ngayThue", render: fmtDate, sorter: (a, b) => a.ngayThue.localeCompare(b.ngayThue) },
          { title: "Dự kiến trả", dataIndex: "ngayTraDuKien", render: fmtDate },
          {
            title: "Còn lại",
            dataIndex: "ngayConLai",
            width: 110,
            render: (v, r) => (r.trangThai === "QUA_HAN" ? `Trễ ${r.soNgayTre} ngày` : `${v} ngày`),
          },
          { title: "Cọc", dataIndex: "tienCoc", render: vnd },
          { title: "TT", dataIndex: "trangThai", render: (v, r) => <>{<StatusTag value={v} />}{r.sapHetHan ? " · sắp hết hạn" : ""}</> },
          {
            title: "Thao tác",
            render: (_, r) => canReturn ? (
              <Button size="small" type="primary" onClick={() => modal.confirm({
                title: "Thu hồi áo?",
                onOk: async () => {
                  try { await api.post(`/api/rentals/${r.maHopDong}/return`, {}); message.success("Đã thu hồi"); load(); }
                  catch (e) { message.error(errText(e)); }
                },
              })}>Thu hồi</Button>
            ) : "Chỉ xem",
          },
        ]}
      />
    </div>
  );
}
