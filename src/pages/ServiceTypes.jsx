import { useEffect, useState } from "react";
import { Button, Form, Input, Modal, Select, Space, Switch, Table, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { errText } from "../utils/format";

export default function ServiceTypes() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("all");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const load = async () => {
    const { data } = await api.get("/api/service-types", { params: { q, status } });
    setRows(data);
  };
  useEffect(() => { load(); }, [q, status]);

  const onSave = async () => {
    const v = await form.validateFields();
    try {
      if (editing) await api.put(`/api/service-types/${editing.maLoaiDV}`, v);
      else await api.post("/api/service-types", v);
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
        <h1>F1 · Loại dịch vụ</h1>
        <p>CRUD loại dịch vụ — không trùng mã, mô tả bắt buộc</p>
      </div>
      <Space style={{ marginBottom: 16 }} wrap>
        <Input.Search allowClear placeholder="Tên / mã loại" onSearch={setQ} onChange={(e) => !e.target.value && setQ("")} />
        <Select value={status} onChange={setStatus} style={{ width: 160 }} options={[{ value: "all", label: "Tất cả" }, { value: "active", label: "Hoạt động" }, { value: "inactive", label: "Ngừng" }]} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); form.setFieldsValue({ trangThai: true }); setOpen(true); }}>{t("add")}</Button>
      </Space>
      <Table
        rowKey="maLoaiDV"
        dataSource={rows}
        columns={[
          { title: "Mã loại", dataIndex: "maLoaiDV" },
          { title: "Tên loại", dataIndex: "tenLoaiDV" },
          { title: "Mô tả", dataIndex: "moTa" },
          { title: "Số DV", dataIndex: "soDichVu" },
          { title: "TT", dataIndex: "trangThai", render: (v) => (v ? "Hoạt động" : "Ngừng") },
          {
            title: t("actions"),
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => { setEditing(r); form.setFieldsValue(r); setOpen(true); }}>{t("edit")}</Button>
                <Button size="small" danger onClick={() => modal.confirm({ title: t("confirmDelete"), onOk: async () => { try { await api.delete(`/api/service-types/${r.maLoaiDV}`); message.success(t("success")); load(); } catch (e) { message.error(errText(e)); } } })}>{t("delete")}</Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editing ? "Cập nhật loại dịch vụ" : "Thêm loại dịch vụ"} open={open} onOk={onSave} onCancel={() => setOpen(false)} okText={t("save")}>
        <Form form={form} layout="vertical">
          <Form.Item name="maLoaiDV" label="Mã loại"><Input disabled={!!editing} placeholder="Tự sinh nếu trống" /></Form.Item>
          <Form.Item name="tenLoaiDV" label="Tên loại" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="moTa" label="Mô tả" rules={[{ required: true, message: "Mô tả không được để trống" }]}><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="trangThai" label="Hoạt động" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
