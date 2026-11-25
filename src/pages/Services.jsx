import { useEffect, useState } from "react";
import { Button, Form, Input, InputNumber, Modal, Select, Space, Table, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { errText, vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";

export default function Services() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [types, setTypes] = useState([]);
  const [q, setQ] = useState("");
  const [typeId, setTypeId] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("ma_dv");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const load = async () => {
    const { data } = await api.get("/api/services", { params: { q, typeId, status, sort } });
    setRows(data);
  };
  useEffect(() => { api.get("/api/service-types").then((r) => setTypes(r.data)); }, []);
  useEffect(() => { load(); }, [q, typeId, status, sort]);

  const onSave = async () => {
    const v = await form.validateFields();
    try {
      if (editing) await api.put(`/api/services/${editing.maDV}`, v);
      else await api.post("/api/services", v);
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
        <h1>F2 · Dịch vụ cưới</h1>
        <p>CRUD dịch vụ — đơn giá ≥ 0, tự sinh mã DV</p>
      </div>
      <Space wrap style={{ marginBottom: 16 }}>
        <Input.Search allowClear placeholder="Tên / mã DV" onSearch={setQ} onChange={(e) => !e.target.value && setQ("")} />
        <Select allowClear placeholder="Loại DV" style={{ width: 220 }} value={typeId || undefined} onChange={(v) => setTypeId(v || "")} options={types.map((t) => ({ value: t.maLoaiDV, label: t.tenLoaiDV }))} />
        <Select allowClear placeholder="Trạng thái" style={{ width: 160 }} value={status || undefined} onChange={(v) => setStatus(v || "")} options={[{ value: "active", label: "Còn hàng" }, { value: "out_of_stock", label: "Hết hàng" }, { value: "inactive", label: "Ngừng" }]} />
        <Select value={sort} onChange={setSort} style={{ width: 160 }} options={[{ value: "ma_dv", label: "Mã" }, { value: "price_asc", label: "Giá tăng" }, { value: "price_desc", label: "Giá giảm" }]} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); form.setFieldsValue({ donGia: 0, trangThai: "active" }); setOpen(true); }}>{t("add")}</Button>
      </Space>
      <Table
        rowKey="maDV"
        dataSource={rows}
        columns={[
          { title: "Mã DV", dataIndex: "maDV" },
          { title: "Tên DV", dataIndex: "tenDV" },
          { title: "Loại", dataIndex: "tenLoaiDV" },
          { title: "Đơn giá", dataIndex: "donGia", render: vnd, sorter: (a, b) => a.donGia - b.donGia },
          { title: "Mô tả", dataIndex: "moTa" },
          { title: "TT", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
          {
            title: t("actions"),
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => { setEditing(r); form.setFieldsValue(r); setOpen(true); }}>{t("edit")}</Button>
                <Button size="small" danger onClick={() => modal.confirm({ title: t("confirmDelete"), onOk: async () => { try { await api.delete(`/api/services/${r.maDV}`); message.success(t("success")); load(); } catch (e) { message.error(errText(e)); } } })}>{t("delete")}</Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editing ? "Cập nhật dịch vụ" : "Thêm dịch vụ (mã tự sinh)"} open={open} onOk={onSave} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="tenDV" label="Tên dịch vụ" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="maLoaiDV" label="Loại DV" rules={[{ required: true }]}><Select options={types.map((t) => ({ value: t.maLoaiDV, label: t.tenLoaiDV }))} /></Form.Item>
          <Form.Item name="donGia" label="Đơn giá" rules={[{ required: true, type: "number", min: 0 }]}><InputNumber style={{ width: "100%" }} min={0} step={100000} /></Form.Item>
          <Form.Item name="moTa" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="hinhAnh" label="Ảnh (URL)"><Input /></Form.Item>
          <Form.Item name="trangThai" label="Trạng thái"><Select options={[{ value: "active", label: "Còn hàng" }, { value: "out_of_stock", label: "Hết hàng" }, { value: "inactive", label: "Ngừng" }]} /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
