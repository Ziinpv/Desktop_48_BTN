import { useEffect, useState } from "react";
import { Button, DatePicker, Drawer, Form, Input, Modal, Select, Space, Spin, Table, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { canDo } from "../utils/roles";
import dayjs from "dayjs";
import api from "../services/api";
import { errText, fmtDate } from "../utils/format";
import CustomerProfile from "../components/CustomerProfile";

const SOURCES = ["Facebook", "TikTok", "Giới thiệu", "Walk-in", "Website", "Khác"].map((v) => ({ value: v, label: v }));
const MONTHS = Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: `Tháng ${i + 1}` }));

function toForm(row) {
  if (!row) return {};
  return { ...row, ngayCuoi: row.ngayCuoi ? dayjs(row.ngayCuoi) : null };
}

export default function Customers() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const canEdit = canDo(useSelector((s) => s.auth.user?.role), "createRental");
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [nguon, setNguon] = useState();
  const [thangCuoi, setThangCuoi] = useState();
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();
  const [profileOpen, setProfileOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const load = async () => {
    const { data } = await api.get("/api/customers", { params: { q, nguon, thangCuoi } });
    setRows(data);
  };
  useEffect(() => { load(); }, [q, nguon, thangCuoi]);

  const openProfile = async (customer) => {
    setProfileOpen(true);
    setProfileLoading(true);
    setProfile(null);
    try {
      const { data } = await api.get("/api/lookup/customer", { params: { q: customer.maKH } });
      const match = data.find((x) => x.maKH === customer.maKH) || data[0] || null;
      setProfile(match);
      if (!match) message.warning("Không tìm thấy hồ sơ sử dụng dịch vụ");
    } catch (e) {
      message.error(errText(e));
    } finally {
      setProfileLoading(false);
    }
  };

  const onSave = async () => {
    const v = await form.validateFields();
    const payload = { ...v, ngayCuoi: v.ngayCuoi ? v.ngayCuoi.format("YYYY-MM-DD") : null };
    try {
      if (editing) await api.put(`/api/customers/${editing.maKH}`, payload);
      else await api.post("/api/customers", payload);
      message.success(t("success"));
      setOpen(false);
      load();
    } catch (e) {
      message.error(errText(e));
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>Khách hàng</h1>
        <p>Hồ sơ cặp đôi, ngày cưới và nguồn khách — dùng để nhắc lịch và lọc mùa vụ</p>
      </div>
      <Space wrap style={{ marginBottom: 16 }}>
        <Input.Search allowClear placeholder="Tên / mã / SĐT / cô dâu / chú rể" onSearch={setQ} onChange={(e) => !e.target.value && setQ("")} style={{ width: 280 }} />
        <Select allowClear placeholder="Nguồn khách" options={SOURCES} value={nguon} onChange={setNguon} style={{ width: 160 }} />
        <Select allowClear placeholder="Tháng cưới" options={MONTHS} value={thangCuoi} onChange={setThangCuoi} style={{ width: 140 }} />
        {canEdit ? <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setOpen(true); }}>{t("add")}</Button> : null}
      </Space>
      <Table
        rowKey="maKH"
        dataSource={rows}
        columns={[
          { title: "Mã KH", dataIndex: "maKH", width: 90 },
          {
            title: "Tên liên hệ",
            dataIndex: "tenKH",
            render: (name, r) => (
              <Button type="link" className="customer-name-link" onClick={() => openProfile(r)}>
                {name}
              </Button>
            ),
          },
          { title: "Cặp đôi", render: (_, r) => [r.tenVo, r.tenChong].filter(Boolean).join(" & ") || "—" },
          { title: "Ngày cưới", dataIndex: "ngayCuoi", render: fmtDate, width: 120 },
          { title: "Nguồn", dataIndex: "nguonKhach", width: 120 },
          { title: "SĐT", dataIndex: "sdt", width: 120 },
          {
            title: t("actions"),
            width: 220,
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => openProfile(r)}>Hồ sơ</Button>
                {canEdit ? <Button size="small" onClick={() => { setEditing(r); form.setFieldsValue(toForm(r)); setOpen(true); }}>{t("edit")}</Button> : null}
                {canEdit ? <Button size="small" danger onClick={() => modal.confirm({ title: t("confirmDelete"), onOk: async () => { try { await api.delete(`/api/customers/${r.maKH}`); message.success(t("success")); load(); } catch (e) { message.error(errText(e)); } } })}>{t("delete")}</Button> : null}
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editing ? "Cập nhật khách" : "Thêm khách hàng"} open={open} onOk={onSave} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="tenKH" label="Tên liên hệ" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="tenVo" label="Tên cô dâu"><Input /></Form.Item>
          <Form.Item name="tenChong" label="Tên chú rể"><Input /></Form.Item>
          <Form.Item name="ngayCuoi" label="Ngày cưới"><DatePicker style={{ width: "100%" }} /></Form.Item>
          <Form.Item name="nguonKhach" label="Nguồn khách"><Select allowClear options={SOURCES} /></Form.Item>
          <Form.Item name="sdt" label="SĐT"><Input /></Form.Item>
          <Form.Item name="email" label="Email"><Input /></Form.Item>
          <Form.Item name="diaChi" label="Địa chỉ"><Input /></Form.Item>
        </Form>
      </Modal>
      <Drawer
        title={profile ? `Hồ sơ · [${profile.maKH}] ${profile.tenKH}` : "Hồ sơ khách hàng"}
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        width="min(1080px, 96vw)"
        destroyOnClose
      >
        {profileLoading ? <Spin /> : <CustomerProfile customer={profile} />}
      </Drawer>
    </div>
  );
}
