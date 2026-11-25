import { useEffect, useState } from "react";
import { Button, Form, Input, InputNumber, Modal, Select, Space, Table, Typography, App } from "antd";
import { useSelector } from "react-redux";
import { canDo } from "../utils/roles";
import api, { downloadFile } from "../services/api";
import { errText, vnd } from "../utils/format";

const LOAI = [
  { value: "COC", label: "Tiền cọc" },
  { value: "THUE", label: "Tiền thuê áo" },
  { value: "PHI_TRE", label: "Phí trễ hạn" },
  { value: "DICH_VU", label: "Dịch vụ" },
  { value: "HOAN_COC", label: "Hoàn cọc" },
];

export default function PaymentPanel({ rental, onChanged }) {
  const { message } = App.useApp();
  const canPay = canDo(useSelector((s) => s.auth.user?.role), "collectPayment");
  const [rows, setRows] = useState(rental?.payments || []);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const load = async () => {
    if (!rental?.maHopDong) return;
    const { data } = await api.get("/api/payments", { params: { maHopDong: rental.maHopDong } });
    setRows(data);
  };
  useEffect(() => { setRows(rental?.payments || []); }, [rental]);

  const save = async () => {
    const v = await form.validateFields();
    try {
      await api.post("/api/payments", { ...v, maHopDong: rental.maHopDong, maKH: rental.maKH });
      message.success("Đã ghi sổ thanh toán");
      setOpen(false);
      load();
      onChanged?.();
    } catch (e) {
      message.error(errText(e));
    }
  };

  return (
    <div>
      <Space wrap style={{ marginBottom: 8 }}>
        <Typography.Text>Phải thu {vnd(rental.phaiThu)} · Đã thu {vnd(rental.daThanhToan)} · Còn lại {vnd(rental.conNo)}</Typography.Text>
        {canPay ? <Button size="small" type="primary" onClick={() => { form.resetFields(); form.setFieldsValue({ loai: rental.phiTreHan ? "PHI_TRE" : "THUE", phuongThuc: "TIEN_MAT", soTien: rental.conNo || rental.phiTreHan || 0 }); setOpen(true); }}>Thu tiền</Button> : null}
      </Space>
      <Table
        size="small"
        rowKey="maGD"
        pagination={false}
        dataSource={rows}
        columns={[
          { title: "Biên lai", dataIndex: "maBienLai" },
          { title: "Loại", dataIndex: "loaiTen", render: (v, r) => v || r.loai },
          { title: "Hình thức", dataIndex: "phuongThuc", render: (v) => (v === "CHUYEN_KHOAN" ? "CK" : "Tiền mặt") },
          { title: "Số tiền", dataIndex: "soTien", render: vnd, align: "right" },
          { title: "Còn lại", dataIndex: "soConLai", render: vnd, align: "right" },
          {
            title: "",
            render: (_, r) => <Button size="small" onClick={() => downloadFile(`/api/payments/${r.maGD}/receipt`, `bien-lai-${r.maBienLai}.pdf`)}>Biên lai</Button>,
          },
        ]}
      />
      <Modal title={`Thu tiền · ${rental.maHopDong}`} open={open} onOk={save} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="loai" label="Loại" rules={[{ required: true }]}><Select options={LOAI} /></Form.Item>
          <Form.Item name="phuongThuc" label="Hình thức" rules={[{ required: true }]}>
            <Select options={[{ value: "TIEN_MAT", label: "Tiền mặt" }, { value: "CHUYEN_KHOAN", label: "Chuyển khoản" }]} />
          </Form.Item>
          <Form.Item name="soTien" label="Số tiền" rules={[{ required: true, type: "number", min: 1 }]}><InputNumber style={{ width: "100%" }} min={1} /></Form.Item>
          <Form.Item name="ghiChu" label="Ghi chú"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
