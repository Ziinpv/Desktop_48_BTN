import { useEffect, useMemo, useState } from "react";
import { Button, Calendar, Card, DatePicker, Form, Input, Modal, Select, Space, Table, Tag, App } from "antd";
import dayjs from "dayjs";
import api from "../services/api";
import { errText } from "../utils/format";

const PHOTOGS = ["Minh Khoa", "Hải Yến", "Tuấn Anh"];
const ROOMS = ["Studio A", "Studio B", "Phim trường ngoài trời"];

export default function Appointments() {
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();
  const [month, setMonth] = useState(dayjs());

  const load = async () => {
    const from = month.startOf("month").format("YYYY-MM-DD");
    const to = month.endOf("month").format("YYYY-MM-DD");
    const [{ data: ap }, { data: kh }, { data: dv }] = await Promise.all([
      api.get("/api/appointments", { params: { fromDate: from, toDate: to } }),
      api.get("/api/customers"),
      api.get("/api/services"),
    ]);
    setRows(ap);
    setCustomers(kh);
    setServices(dv);
  };
  useEffect(() => { load(); }, [month]);

  const byDay = useMemo(() => {
    const map = {};
    rows.forEach((r) => {
      const d = (r.batDau || "").slice(0, 10);
      map[d] = map[d] || [];
      map[d].push(r);
    });
    return map;
  }, [rows]);

  const save = async () => {
    const v = await form.validateFields();
    const payload = {
      maKH: v.maKH,
      maDV: v.maDV,
      nhiepAnh: v.nhiepAnh,
      phong: v.phong,
      batDau: v.range[0].format("YYYY-MM-DDTHH:mm:ss"),
      ketThuc: v.range[1].format("YYYY-MM-DDTHH:mm:ss"),
      trangThai: v.trangThai,
      ghiChu: v.ghiChu,
    };
    try {
      if (editing) await api.put(`/api/appointments/${editing.maLich}`, payload);
      else await api.post("/api/appointments", payload);
      message.success("Đã lưu lịch hẹn");
      setOpen(false);
      load();
    } catch (e) {
      message.error(errText(e));
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>Lịch hẹn chụp</h1>
        <p>Nối dịch vụ F2 với khách hàng · khung giờ, nhiếp ảnh gia, phòng studio</p>
      </div>
      <Button type="primary" style={{ marginBottom: 16 }} onClick={() => { setEditing(null); form.resetFields(); form.setFieldsValue({ trangThai: "DA_DAT", range: [dayjs().hour(9).minute(0), dayjs().hour(11).minute(0)] }); setOpen(true); }}>Đặt lịch</Button>
      <div className="kpi-grid" style={{ gridTemplateColumns: "1.1fr 1fr" }}>
        <Card>
          <Calendar
            fullscreen={false}
            value={month}
            onChange={setMonth}
            cellRender={(value, info) => {
              if (info.type !== "date") return info.originNode;
              const list = byDay[value.format("YYYY-MM-DD")] || [];
              return (
                <div>
                  {list.map((a) => <div key={a.maLich} style={{ fontSize: 11 }}>{(a.batDau || "").slice(11, 16)} {a.tenKH}</div>)}
                </div>
              );
            }}
          />
        </Card>
        <Card title="Lịch trong tháng">
          <Table
            size="small"
            rowKey="maLich"
            dataSource={rows}
            pagination={false}
            columns={[
              { title: "Mã", dataIndex: "maLich", width: 80 },
              { title: "Khách", dataIndex: "tenKH" },
              { title: "Dịch vụ", dataIndex: "tenDV" },
              { title: "Bắt đầu", dataIndex: "batDau", render: (v) => v?.replace("T", " ").slice(0, 16) },
              { title: "Photog.", dataIndex: "nhiepAnh" },
              { title: "Phòng", dataIndex: "phong" },
              { title: "TT", dataIndex: "trangThai", render: (v) => <Tag>{v}</Tag> },
              {
                title: "",
                render: (_, r) => (
                  <Space>
                    <Button size="small" onClick={() => { setEditing(r); form.setFieldsValue({ ...r, range: [dayjs(r.batDau), dayjs(r.ketThuc)] }); setOpen(true); }}>Sửa</Button>
                    <Button size="small" danger onClick={() => modal.confirm({ title: "Hủy lịch?", onOk: async () => { await api.delete(`/api/appointments/${r.maLich}`); load(); } })}>Xóa</Button>
                  </Space>
                ),
              },
            ]}
          />
        </Card>
      </div>
      <Modal title={editing ? "Cập nhật lịch" : "Đặt lịch chụp"} open={open} onOk={save} onCancel={() => setOpen(false)} width={560}>
        <Form form={form} layout="vertical">
          <Form.Item name="maKH" label="Khách hàng" rules={[{ required: true }]}><Select showSearch optionFilterProp="label" options={customers.map((c) => ({ value: c.maKH, label: `${c.maKH} · ${c.tenKH}` }))} /></Form.Item>
          <Form.Item name="maDV" label="Dịch vụ (F2)"><Select allowClear options={services.map((s) => ({ value: s.maDV, label: s.tenDV }))} /></Form.Item>
          <Form.Item name="range" label="Khung giờ" rules={[{ required: true }]}><DatePicker.RangePicker showTime format="DD/MM/YYYY HH:mm" style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="nhiepAnh" label="Nhiếp ảnh gia"><Select allowClear options={PHOTOGS.map((x) => ({ value: x, label: x }))} /></Form.Item>
          <Form.Item name="phong" label="Phòng / bối cảnh"><Select allowClear options={ROOMS.map((x) => ({ value: x, label: x }))} /></Form.Item>
          <Form.Item name="trangThai" label="Trạng thái"><Select options={[{ value: "DA_DAT", label: "Đã đặt" }, { value: "DA_CHUP", label: "Đã chụp" }, { value: "HUY", label: "Hủy" }]} /></Form.Item>
          <Form.Item name="ghiChu" label="Ghi chú"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
