import { useEffect, useState } from "react";
import { Button, Space, Table, App } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import api, { downloadFile } from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";

export default function Overdue() {
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);

  const load = async () => {
    const { data } = await api.get("/api/reports/overdue");
    setRows(data);
  };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <div className="page-head">
        <h1>F6 · Quá hạn & phí phạt</h1>
        <p>Phí trễ hạn = Đơn giá × 10% × số ngày trễ (cộng dồn theo từng bộ áo)</p>
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<DownloadOutlined />} onClick={() => downloadFile("/api/export/overdue.csv", "qua-han.csv")}>CSV</Button>
        <Button onClick={() => downloadFile("/api/export/overdue.xlsx", "qua-han.xlsx")}>Excel</Button>
        <Button onClick={() => downloadFile("/api/export/overdue.pdf", "qua-han.pdf")}>PDF</Button>
      </Space>
      <Table
        rowKey="maHopDong"
        dataSource={rows}
        rowClassName="overdue-row"
        columns={[
          { title: "Mã HĐ", dataIndex: "maHopDong" },
          { title: "Khách", dataIndex: "tenKH" },
          { title: "Bộ áo", dataIndex: "items", render: (items) => items.map((i) => i.maDress).join(", ") },
          { title: "Hạn trả", dataIndex: "ngayTraDuKien", render: fmtDate },
          { title: "Số ngày trễ", dataIndex: "soNgayTre" },
          { title: "Tiền phạt", dataIndex: "phiTreHan", render: vnd },
          {
            title: "Thao tác",
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={async () => { try { await api.post(`/api/rentals/${r.maHopDong}/pay-penalty`); message.success("Đã ghi nhận thanh toán phí"); load(); } catch (e) { message.error(errText(e)); } }}>Thanh toán phí</Button>
                <Button size="small" type="primary" danger onClick={() => modal.confirm({
                  title: "Xác nhận trả lại?",
                  content: `Phí phạt ${vnd(r.phiTreHan)}`,
                  onOk: async () => {
                    try { await api.post(`/api/rentals/${r.maHopDong}/return`, {}); message.success("Đã nhận trả"); load(); }
                    catch (e) { message.error(errText(e)); }
                  },
                })}>Xác nhận trả</Button>
              </Space>
            ),
          },
        ]}
      />
    </div>
  );
}
