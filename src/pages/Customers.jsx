import { useEffect, useState } from "react";
import { Button, Drawer, Form, Input, Modal, Space, Spin, Table, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { errText } from "../utils/format";
import CustomerProfile from "../components/CustomerProfile";

export default function Customers() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();
  const [profileOpen, setProfileOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const load = async () => {
    const { data } = await api.get("/api/customers", { params: { q } });
    setRows(data);
  };
  useEffect(() => { load(); }, [q]);

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
    try {
      if (editing) await api.put(`/api/customers/${editing.maKH}`, v);
      else await api.post("/api/customers", v);
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
        <p>Bấm tên khách để xem dịch vụ đã dùng, tiền cọc, thanh toán và hạn trả áo cưới</p>
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search allowClear placeholder="Tên / mã / SĐT" onSearch={setQ} onChange={(e) => !e.target.value && setQ("")} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setOpen(true); }}>{t("add")}</Button>
      </Space>
      <Table
        rowKey="maKH"
        dataSource={rows}
        columns={[
          { title: "Mã KH", dataIndex: "maKH", width: 100 },
          {
            title: "Tên",
            dataIndex: "tenKH",
            render: (name, r) => (
              <Button type="link" className="customer-name-link" onClick={() => openProfile(r)}>
                {name}
              </Button>
            ),
          },
          { title: "SĐT", dataIndex: "sdt" },
          { title: "Email", dataIndex: "email" },
          { title: "Địa chỉ", dataIndex: "diaChi" },
          {
            title: t("actions"),
            width: 200,
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => openProfile(r)}>Hồ sơ</Button>
                <Button size="small" onClick={() => { setEditing(r); form.setFieldsValue(r); setOpen(true); }}>{t("edit")}</Button>
                <Button size="small" danger onClick={() => modal.confirm({ title: t("confirmDelete"), onOk: async () => { try { await api.delete(`/api/customers/${r.maKH}`); message.success(t("success")); load(); } catch (e) { message.error(errText(e)); } } })}>{t("delete")}</Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editing ? "Cập nhật khách" : "Thêm khách hàng"} open={open} onOk={onSave} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="tenKH" label="Tên khách hàng" rules={[{ required: true }]}><Input /></Form.Item>
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
