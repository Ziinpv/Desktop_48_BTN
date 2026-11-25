import { useEffect, useState } from "react";
import { Button, Drawer, Space, Table, App } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import api, { downloadFile } from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";
import PaymentPanel from "../components/PaymentPanel";
import QrScanBar from "../components/QrScanBar";

export default function Overdue() {
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [payRow, setPayRow] = useState(null);
  const [active, setActive] = useState(null);

  const load = async () => {
    const { data } = await api.get("/api/reports/overdue");
    setRows(data);
  };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <div className="page-head">
        <h1>F6 · Quá hạn & phí phạt</h1>
        <p>Phí trễ hạn = Đơn giá × 10% × số ngày trễ · Quét QR áo (F7) để mở đúng hợp đồng thay vì gõ mã</p>
      </div>
      <div style={{ marginBottom: 16 }}>
        <QrScanBar
          onFound={async (code) => {
            try {
              const { data } = await api.get("/api/lookup/qr", { params: { q: code } });
              setActive(data);
              message.success(`Đã mở ${data.maHopDong} · ${data.tenKH}`);
            } catch (e) {
              message.error(errText(e));
            }
          }}
        />
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<DownloadOutlined />} onClick={() => downloadFile("/api/export/overdue.csv", "qua-han.csv")}>CSV</Button>
        <Button onClick={() => downloadFile("/api/export/overdue.xlsx", "qua-han.xlsx")}>Excel</Button>
        <Button onClick={() => downloadFile("/api/export/overdue.pdf", "qua-han.pdf")}>PDF</Button>
      </Space>
      <Table
        rowKey="maHopDong"
        dataSource={rows}
        rowClassName={(r) => (active?.maHopDong === r.maHopDong ? "overdue-row" : "overdue-row")}
        onRow={(r) => ({
          style: active?.maHopDong === r.maHopDong ? { outline: "2px solid #c59b27" } : undefined,
        })}
        columns={[
          { title: "Mã HĐ", dataIndex: "maHopDong" },
          { title: "Khách", dataIndex: "tenKH" },
          { title: "Bộ áo", dataIndex: "items", render: (items) => items.map((i) => i.maDress).join(", ") },
          { title: "Hạn trả", dataIndex: "ngayTraDuKien", render: fmtDate },
          { title: "Số ngày trễ", dataIndex: "soNgayTre" },
          { title: "Tiền phạt", dataIndex: "phiTreHan", render: vnd },
          { title: "Còn lại", dataIndex: "conNo", render: vnd },
          {
            title: "Thao tác",
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => setPayRow(r)}>Sổ thu</Button>
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
      <Drawer
        title={active ? `Hợp đồng ${active.maHopDong} · ${active.tenKH}` : "Hợp đồng"}
        open={!!active}
        onClose={() => setActive(null)}
        width={760}
        extra={active ? (
          <Space>
            <Button onClick={() => setPayRow(active)}>Sổ thu</Button>
            <Button onClick={async () => { try { await api.post(`/api/rentals/${active.maHopDong}/pay-penalty`); message.success("Đã ghi nhận thanh toán phí"); load(); } catch (e) { message.error(errText(e)); } }}>Thanh toán phí</Button>
            <Button type="primary" danger onClick={() => modal.confirm({
              title: "Xác nhận trả lại?",
              content: `Phí phạt ${vnd(active.phiTreHan)}`,
              onOk: async () => {
                try { await api.post(`/api/rentals/${active.maHopDong}/return`, {}); message.success("Đã nhận trả"); setActive(null); load(); }
                catch (e) { message.error(errText(e)); }
              },
            })}>Xác nhận trả</Button>
          </Space>
        ) : null}
      >
        {active && (
          <div>
            <p>Khách: <strong>{active.tenKH}</strong> · {active.sdt}</p>
            <p>Bộ áo: {active.boAo}</p>
            <p>Hạn trả: {fmtDate(active.ngayTraDuKien)} · Trễ {active.soNgayTre || 0} ngày · Phí {vnd(active.phiTreHan)}</p>
            <p>Còn nợ: <strong>{vnd(active.conNo)}</strong></p>
            <PaymentPanel rental={active} onChanged={load} />
          </div>
        )}
      </Drawer>
      <Drawer title={payRow ? `Sổ thanh toán · ${payRow.maHopDong}` : "Sổ thanh toán"} open={!!payRow} onClose={() => setPayRow(null)} width={720}>
        {payRow && <PaymentPanel rental={payRow} onChanged={load} />}
      </Drawer>
    </div>
  );
}
