import { useEffect, useMemo, useState } from "react";
import { Button, Card, Checkbox, DatePicker, Drawer, Form, Input, InputNumber, Modal, Select, Space, Table, App, Alert } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";
import PaymentPanel from "../components/PaymentPanel";

export default function Rentals() {
  const { t } = useTranslation();
  const { message, modal } = App.useApp();
  const [rows, setRows] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [dresses, setDresses] = useState([]);
  const [status, setStatus] = useState("");
  const [filterSize, setFilterSize] = useState();
  const [filterMau, setFilterMau] = useState();
  const [open, setOpen] = useState(false);
  const [payRow, setPayRow] = useState(null);
  const [form] = Form.useForm();
  const selected = Form.useWatch("dresses", form) || [];

  const load = async () => {
    const [{ data: rentals }, { data: kh }, { data: ao }] = await Promise.all([
      api.get("/api/rentals", { params: { status } }),
      api.get("/api/customers"),
      api.get("/api/dresses"),
    ]);
    setRows(rentals);
    setCustomers(kh);
    setDresses(ao);
  };
  useEffect(() => { load(); }, [status]);

  const available = dresses.filter((d) => {
    if (!(d.trangThai === "SAN_SANG" || selected.includes(d.maDress))) return false;
    if (filterSize && d.size !== filterSize) return false;
    if (filterMau && d.mau !== filterMau) return false;
    return true;
  });
  const summary = useMemo(() => {
    const items = dresses.filter((d) => selected.includes(d.maDress));
    const rent = items.reduce((s, d) => s + d.donGia, 0);
    const coc = items.reduce((s, d) => s + d.tienCoc, 0);
    return { rent, coc, count: items.length };
  }, [selected, dresses]);

  const onCreate = async () => {
    const v = await form.validateFields();
    try {
      await api.post("/api/rentals", {
        maKH: v.maKH,
        dresses: v.dresses,
        ngayThue: v.ngayThue.format("YYYY-MM-DD"),
        ngayTraDuKien: v.ngayTraDuKien.format("YYYY-MM-DD"),
        tienCoc: v.tienCoc,
        ghiChu: v.ghiChu,
      });
      message.success("Đã lập hợp đồng thuê");
      setOpen(false);
      load();
    } catch (e) {
      message.error(errText(e));
    }
  };

  const doReturn = (r) => {
    modal.confirm({
      title: `Nhận trả ${r.maHopDong}?`,
      content: `Phí trễ hạn hiện tại: ${vnd(r.phiTreHan)}`,
      onOk: async () => {
        try {
          await api.post(`/api/rentals/${r.maHopDong}/return`, {});
          message.success("Đã nhận trả");
          load();
        } catch (e) {
          message.error(errText(e));
        }
      },
    });
  };

  return (
    <div>
      <div className="page-head">
        <h1>F3 · Hợp đồng thuê áo cưới</h1>
        <p>Tối đa 3 bộ/khách · Cọc = 50% đơn giá · Không trùng ngày thuê cùng bộ áo</p>
      </div>
      <Space style={{ marginBottom: 16 }} wrap>
        <Select allowClear placeholder="Trạng thái" style={{ width: 180 }} value={status || undefined} onChange={(v) => setStatus(v || "")} options={[{ value: "DANG_THUE", label: "Đang thuê" }, { value: "QUA_HAN", label: "Quá hạn" }, { value: "DA_TRA", label: "Đã trả" }]} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); form.setFieldsValue({ ngayThue: dayjs(), ngayTraDuKien: dayjs().add(3, "day"), dresses: [], tienCoc: 0 }); setOpen(true); }}>Lập phiếu thuê</Button>
      </Space>
      <Table
        rowKey="maHopDong"
        dataSource={rows}
        columns={[
          { title: "Mã HĐ", dataIndex: "maHopDong" },
          { title: "Khách", dataIndex: "tenKH" },
          { title: "Ngày thuê", dataIndex: "ngayThue", render: fmtDate },
          { title: "Hạn trả", dataIndex: "ngayTraDuKien", render: fmtDate },
          { title: "Bộ áo", dataIndex: "items", render: (items) => items.map((i) => i.maDress).join(", ") },
          { title: "Cọc", dataIndex: "tienCoc", render: vnd },
          { title: "Còn lại", dataIndex: "conNo", render: vnd },
          { title: "TT", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
          {
            title: t("actions"),
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={() => setPayRow(r)}>Sổ thu</Button>
                {r.trangThai !== "DA_TRA" ? <Button size="small" danger onClick={() => doReturn(r)}>Nhận trả</Button> : "Hoàn tất"}
              </Space>
            ),
          },
        ]}
      />
      <Modal title="Lập phiếu thuê áo cưới" open={open} onOk={onCreate} onCancel={() => setOpen(false)} width={720} okText="Lưu hợp đồng">
        <Alert type="info" showIcon style={{ marginBottom: 12 }} message="Khách thuê tối đa 3 bộ cùng lúc. Bộ áo hỏng hóc sẽ bị chặn." />
        <Form form={form} layout="vertical">
          <Form.Item name="maKH" label="Khách hàng" rules={[{ required: true }]}>
            <Select showSearch optionFilterProp="label" options={customers.map((c) => ({ value: c.maKH, label: `${c.maKH} · ${c.tenKH}` }))} />
          </Form.Item>
          <Space>
            <Form.Item name="ngayThue" label="Ngày thuê" rules={[{ required: true }]}><DatePicker /></Form.Item>
            <Form.Item name="ngayTraDuKien" label="Ngày trả dự kiến" rules={[{ required: true }]}><DatePicker /></Form.Item>
          </Space>
          <Space style={{ marginBottom: 8 }}>
            <Select allowClear placeholder="Lọc size" style={{ width: 120 }} value={filterSize} onChange={setFilterSize} options={[...new Set(dresses.map((d) => d.size).filter(Boolean))].map((x) => ({ value: x, label: x }))} />
            <Select allowClear placeholder="Lọc màu" style={{ width: 140 }} value={filterMau} onChange={setFilterMau} options={[...new Set(dresses.map((d) => d.mau).filter(Boolean))].map((x) => ({ value: x, label: x }))} />
          </Space>
          <Form.Item name="dresses" label="Chọn bộ áo (tối đa 3)" rules={[{ required: true }]}>
            <Checkbox.Group
              onChange={(vals) => {
                if (vals.length > 3) {
                  message.warning("Tối đa 3 bộ trên một phiếu / khách");
                  form.setFieldValue("dresses", vals.slice(0, 3));
                  return;
                }
                const coc = dresses.filter((d) => vals.includes(d.maDress)).reduce((s, d) => s + d.tienCoc, 0);
                form.setFieldValue("tienCoc", coc);
              }}
            >
              <div style={{ display: "grid", gap: 8 }}>
                {available.map((d) => (
                  <Checkbox key={d.maDress} value={d.maDress} disabled={d.trangThai === "HON_HOC"}>
                    <strong>{d.maDress}</strong> · {d.tenAo} · {d.size || "?"} · {d.mau || "?"} {d.phuKien ? `· PK: ${d.phuKien}` : ""} · thuê {vnd(d.donGia)} · cọc {vnd(d.tienCoc)}
                    {d.trangThai === "HON_HOC" ? " (hỏng hóc)" : ""}
                  </Checkbox>
                ))}
              </div>
            </Checkbox.Group>
          </Form.Item>
          <Card size="small">
            Đã chọn {summary.count}/3 bộ · Tổng thuê {vnd(summary.rent)} · Cọc 50% {vnd(summary.coc)}
          </Card>
          <Form.Item name="tienCoc" label="Tiền cọc thu" style={{ marginTop: 12 }}><InputNumber style={{ width: "100%" }} min={0} /></Form.Item>
          <Form.Item name="ghiChu" label="Ghi chú"><Input.TextArea /></Form.Item>
        </Form>
      </Modal>
      <Drawer title={payRow ? `Sổ thanh toán · ${payRow.maHopDong}` : "Sổ thanh toán"} open={!!payRow} onClose={() => setPayRow(null)} width={720}>
        {payRow && <PaymentPanel rental={payRow} onChanged={load} />}
      </Drawer>
    </div>
  );
}
