import { useState } from "react";
import { Button, Card, Image, Input, Space, Table, Timeline, Typography, App } from "antd";
import api from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";

export default function DressLookup() {
  const { message } = App.useApp();
  const [q, setQ] = useState("");
  const [rows, setRows] = useState([]);
  const [qr, setQr] = useState(null);

  const search = async (value) => {
    const keyword = value ?? q;
    if (!keyword) return;
    try {
      const { data } = await api.get("/api/lookup/dress", { params: { q: keyword } });
      setRows(data);
      if (!data.length) message.warning("Không tìm thấy bộ áo");
    } catch (e) {
      message.error(errText(e));
    }
  };

  const showQr = async (code) => {
    const { data } = await api.get(`/api/dresses/${code}/qr`);
    setQr(data);
  };

  return (
    <div>
      <div className="page-head">
        <h1>F7 · Tra cứu bộ áo cưới</h1>
        <p>Tìm theo mã, tên, loại · lịch sử thuê · in mã QR tracking</p>
      </div>
      <Input.Search size="large" placeholder="AC001, váy luxury, áo dài..." onSearch={search} onChange={(e) => setQ(e.target.value)} enterButton="Tra cứu" style={{ maxWidth: 560, marginBottom: 20 }} />
      {rows.map((d) => (
        <Card key={d.maDress} style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            {d.hinhAnh && <img className="detail-img" src={d.hinhAnh} alt={d.tenAo} />}
            <div style={{ flex: 1, minWidth: 280 }}>
              <Typography.Title level={3} className="serif">[{d.maDress}] {d.tenAo}</Typography.Title>
              <p>Loại: <strong>{d.loaiAo}</strong></p>
              <p>Đơn giá thuê: <strong>{vnd(d.donGia)}</strong> · Tiền cọc: <strong>{vnd(d.tienCoc)}</strong></p>
              <p>Kho: <StatusTag value={d.trangThai} /> {d.ghiChu}</p>
              <Space>
                <Button onClick={() => showQr(d.maDress)}>Mã QR tracking</Button>
                <Button onClick={() => window.luxeDesktop?.print?.() || window.print()}>In</Button>
              </Space>
              {qr?.maDress === d.maDress && (
                <div style={{ marginTop: 12 }}>
                  <Image src={qr.qr} width={160} />
                  <div>{qr.maDress}</div>
                </div>
              )}
              <Typography.Title level={5} style={{ marginTop: 20 }}>Lịch sử thuê mượn</Typography.Title>
              <Timeline
                items={(d.lichSu || []).map((h) => ({
                  color: h.trangThai === "QUA_HAN" ? "red" : h.trangThai === "DA_TRA" ? "green" : "blue",
                  children: `${fmtDate(h.ngayThue)} · ${h.tenKH} · ${h.maHopDong} · ${h.trangThai}`,
                }))}
              />
              <Table
                size="small"
                rowKey="maHopDong"
                pagination={false}
                dataSource={d.lichSu}
                columns={[
                  { title: "HĐ", dataIndex: "maHopDong" },
                  { title: "Khách", dataIndex: "tenKH" },
                  { title: "Thuê", dataIndex: "ngayThue", render: fmtDate },
                  { title: "Hạn", dataIndex: "ngayTraDuKien", render: fmtDate },
                  { title: "Trả", dataIndex: "ngayTraThucTe", render: fmtDate },
                  { title: "TT", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
                ]}
              />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
