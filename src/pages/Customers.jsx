import { useEffect, useState } from "react";
import { Button, Form, Input, Modal, Space, Table, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { errText } from "../utils/format";

export default function Customers() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const load = async () => {
    const { data } = await api.get("/api/customers", { params: { q } });
    setRows(data);
  };
  useEffect(() => { load(); }, [q]);

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
        <p>Hồ sơ khách phục vụ thuê áo và sử dụng dịch vụ</p>
      </div>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search allowClear placeholder="Tên / mã / SĐT" onSearch={setQ} onChange={(e) => !e.target.value && setQ("")} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); setOpen(true); }}>{t("add")}</Button>
      </Space>
      <Table
        rowKey="maKH"
        dataSource={rows}
        columns={[
          { title: "Mã KH", dataIndex: "maKH" },
          { title: "Tên", dataIndex: "tenKH" },
          { title: "SĐT", dataIndex: "sdt" },
          { title: "Email", dataIndex: "email" },
          { title: "Địa chỉ", dataIndex: "diaChi" },
          {
            title: t("actions"),
            render: (_, r) => (
              <Space>
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
    </div>
  );
}
