import { useEffect, useState } from "react";
import { Card, Image, Segmented, Tag, Typography } from "antd";
import api from "../services/api";
import { vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";

export default function ServiceCatalog() {
  const [data, setData] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    api.get("/api/services/catalog").then((r) => setData(r.data));
  }, []);

  return (
    <div>
      <div className="page-head">
        <h1>F4 · Danh mục dịch vụ theo loại</h1>
        <p>Hình ảnh, tên, giá, trạng thái — lọc còn hàng / hết hàng</p>
      </div>
      <Segmented
        style={{ marginBottom: 16 }}
        value={filter}
        onChange={setFilter}
        options={[
          { label: "Tất cả", value: "all" },
          { label: "Còn hàng", value: "active" },
          { label: "Hết hàng", value: "out_of_stock" },
        ]}
      />
      {data.map((g) => {
        const list = g.services.filter((s) => filter === "all" || s.trangThai === filter);
        return (
          <div key={g.maLoaiDV} style={{ marginBottom: 28 }}>
            <Typography.Title level={4} className="serif" style={{ color: "#795290" }}>
              {g.tenLoaiDV} <Tag>{g.maLoaiDV}</Tag>
            </Typography.Title>
            <Typography.Paragraph type="secondary">{g.moTa}</Typography.Paragraph>
            <div className="catalog-grid">
              {list.map((s) => (
                <Card key={s.maDV} hoverable cover={s.hinhAnh ? <Image src={s.hinhAnh} height={140} style={{ objectFit: "cover" }} /> : null}>
                  <Card.Meta title={s.tenDV} description={s.moTa} />
                  <div style={{ marginTop: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ color: "#795290" }}>{vnd(s.donGia)}</strong>
                    <StatusTag value={s.trangThai} />
                  </div>
                </Card>
              ))}
              {!list.length && <Typography.Text type="secondary">Không có dịch vụ.</Typography.Text>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
