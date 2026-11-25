import { useEffect, useState } from "react";
import { Button, Form, Input, InputNumber, Modal, Select, Space, Table, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { errText, vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";

const LOAI = ["Váy Cưới Luxury", "Váy Cưới Minimalist", "Áo Dài Cưới Truyền Thống", "Vest Chú Rể Cao Cấp"];

export default function Dresses() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();
  const donGia = Form.useWatch("donGia", form);

  const load = async () => {
    const { data } = await api.get("/api/dresses", { params: { q, status } });
    setRows(data);
  };
  useEffect(() => { load(); }, [q, status]);

  const onSave = async () => {
    const v = await form.validateFields();
    try {
      if (editing) await api.put(`/api/dresses/${editing.maDress}`, v);
      else await api.post("/api/dresses", v);
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
        <h1>Kho áo cưới</h1>
        <p>Cọc tự động = Đơn giá × 50%</p>
      </div>
      <Space wrap style={{ marginBottom: 16 }}>
        <Input.Search allowClear placeholder="Mã / tên / loại áo" onSearch={setQ} onChange={(e) => !e.target.value && setQ("")} />
        <Select allowClear placeholder="Trạng thái" style={{ width: 180 }} value={status || undefined} onChange={(v) => setStatus(v || "")} options={[{ value: "SAN_SANG", label: "Còn hàng" }, { value: "DANG_THUE", label: "Đang thuê" }, { value: "HET_HANG", label: "Hết hàng" }, { value: "HON_HOC", label: "Hỏng hóc" }]} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); form.resetFields(); form.setFieldsValue({ donGia: 0, trangThai: "SAN_SANG" }); setOpen(true); }}>{t("add")}</Button>
      </Space>
      <Table
        rowKey="maDress"
        dataSource={rows}
        columns={[
          { title: "Mã", dataIndex: "maDress" },
          { title: "Ảnh", dataIndex: "hinhAnh", render: (u) => u ? <img className="thumb" src={u} alt="" /> : "—" },
          { title: "Tên áo", dataIndex: "tenAo" },
          { title: "Loại", dataIndex: "loaiAo" },
          { title: "Đơn giá", dataIndex: "donGia", render: vnd },
          { title: "Cọc 50%", dataIndex: "tienCoc", render: vnd },
          { title: "Kho", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
          {
            title: t("actions"),
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => { setEditing(r); form.setFieldsValue(r); setOpen(true); }}>{t("edit")}</Button>
                <Button size="small" danger onClick={() => modal.confirm({ title: t("confirmDelete"), onOk: async () => { try { await api.delete(`/api/dresses/${r.maDress}`); message.success(t("success")); load(); } catch (e) { message.error(errText(e)); } } })}>{t("delete")}</Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title={editing ? "Cập nhật áo cưới" : "Thêm áo cưới"} open={open} onOk={onSave} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="tenAo" label="Tên áo" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="loaiAo" label="Loại áo" rules={[{ required: true }]}><Select options={LOAI.map((x) => ({ value: x, label: x }))} /></Form.Item>
          <Form.Item name="donGia" label="Đơn giá" rules={[{ required: true, type: "number", min: 0 }]}><InputNumber min={0} style={{ width: "100%" }} /></Form.Item>
          <p>Tiền cọc đề xuất: <strong>{vnd((donGia || 0) * 0.5)}</strong></p>
          <Form.Item name="hinhAnh" label="Ảnh URL"><Input /></Form.Item>
          <Form.Item name="trangThai" label="Trạng thái"><Select options={[{ value: "SAN_SANG", label: "Còn hàng" }, { value: "HET_HANG", label: "Hết hàng" }, { value: "HON_HOC", label: "Hỏng hóc" }, { value: "DANG_THUE", label: "Đang thuê" }]} /></Form.Item>
          <Form.Item name="ghiChu" label="Ghi chú"><Input.TextArea /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
