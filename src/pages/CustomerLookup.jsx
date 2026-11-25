import { useState } from "react";
import { Button, Card, DatePicker, Form, Input, Modal, Select, Space, Statistic, Table, Typography, App } from "antd";
import dayjs from "dayjs";
import api, { downloadFile } from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";

export default function CustomerLookup() {
  const { message } = App.useApp();
  const [q, setQ] = useState("");
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);
  const [services, setServices] = useState([]);
  const [form] = Form.useForm();
  const [currentKH, setCurrentKH] = useState(null);

  const search = async (value) => {
    const keyword = value ?? q;
    if (!keyword) return;
    try {
      const { data } = await api.get("/api/lookup/customer", { params: { q: keyword } });
      setRows(data);
      if (!data.length) message.warning("Không tìm thấy khách hàng");
    } catch (e) {
      message.error(errText(e));
    }
  };

  const addUsage = async () => {
    const v = await form.validateFields();
    try {
      await api.post("/api/lookup/service-usage", { ...v, ngaySD: v.ngaySD.format("YYYY-MM-DD"), maKH: currentKH });
      message.success("Đã ghi nhận dịch vụ");
      setOpen(false);
      search(currentKH);
    } catch (e) {
      message.error(errText(e));
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>F8 · Tra cứu dịch vụ theo khách hàng</h1>
        <p>Tổng chi phí thuê + dịch vụ · xuất hóa đơn / hóa đơn đỏ</p>
      </div>
      <Input.Search size="large" placeholder="Tên KH, mã KH, SĐT..." onSearch={search} onChange={(e) => setQ(e.target.value)} enterButton="Tra cứu" style={{ maxWidth: 560, marginBottom: 20 }} />
      {rows.map((c) => (
        <Card key={c.maKH} style={{ marginBottom: 16 }} title={`[${c.maKH}] ${c.tenKH}`} extra={<Space>
          <Button onClick={async () => { setCurrentKH(c.maKH); if (!services.length) { const { data } = await api.get("/api/services"); setServices(data); } form.resetFields(); form.setFieldsValue({ ngaySD: dayjs() }); setOpen(true); }}>Ghi dịch vụ</Button>
          <Button onClick={() => downloadFile(`/api/export/invoice/${c.maKH}`, `hoa-don-${c.maKH}.pdf`)}>Hóa đơn</Button>
          <Button onClick={() => downloadFile(`/api/export/invoice/${c.maKH}?red=true`, `hoa-don-do-${c.maKH}.pdf`)}>Hóa đơn đỏ</Button>
        </Space>}>
          <Typography.Paragraph type="secondary">{c.sdt} · {c.diaChi} · {c.email}</Typography.Paragraph>
          <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
            <Card><Statistic title="Dịch vụ" value={c.serviceTotal} formatter={vnd} /></Card>
            <Card><Statistic title="Thuê áo" value={c.rentalTotal} formatter={vnd} /></Card>
            <Card><Statistic title="Tổng chi phí" value={c.grandTotal} formatter={vnd} /></Card>
          </div>
          <Typography.Title level={5}>Dịch vụ đã sử dụng</Typography.Title>
          <Table size="small" rowKey="id" pagination={false} dataSource={c.services} columns={[
            { title: "Mã DV", dataIndex: "maDV" },
            { title: "Tên", dataIndex: "tenDV" },
            { title: "Loại", dataIndex: "loaiDV" },
            { title: "Ngày SD", dataIndex: "ngaySD", render: fmtDate },
            { title: "Giá lúc SD", dataIndex: "giaLucSD", render: vnd },
          ]} />
          <Typography.Title level={5} style={{ marginTop: 16 }}>Hợp đồng thuê</Typography.Title>
          <Table size="small" rowKey="maHopDong" pagination={false} dataSource={c.rentals} columns={[
            { title: "HĐ", dataIndex: "maHopDong" },
            { title: "Ngày thuê", dataIndex: "ngayThue", render: fmtDate },
            { title: "Số bộ", dataIndex: "soBo" },
            { title: "TT", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
          ]} />
          <Typography.Title level={5} style={{ marginTop: 16 }}>Lịch sử giao dịch</Typography.Title>
          <Table size="small" rowKey="id" pagination={false} dataSource={c.transactions} columns={[
            { title: "Ngày", dataIndex: "ngay", render: (v) => v ? v.replace("T", " ").slice(0, 19) : "—" },
            { title: "HĐ", dataIndex: "maHopDong" },
            { title: "Trạng thái", dataIndex: "trangThai" },
            { title: "Phí", dataIndex: "tienPhat", render: vnd },
            { title: "Ghi chú", dataIndex: "ghiChu" },
          ]} />
        </Card>
      ))}
      <Modal title="Ghi nhận dịch vụ đã dùng" open={open} onOk={addUsage} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="maDV" label="Dịch vụ" rules={[{ required: true }]}><Select options={services.map((s) => ({ value: s.maDV, label: `${s.maDV} · ${s.tenDV}` }))} /></Form.Item>
          <Form.Item name="ngaySD" label="Ngày sử dụng" rules={[{ required: true }]}><DatePicker /></Form.Item>
          <Form.Item name="ghiChu" label="Ghi chú"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
