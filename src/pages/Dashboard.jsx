import { useEffect, useState } from "react";
import { Button, Card, Empty, Statistic, Table, Typography, Spin } from "antd";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { errText, fmtDate, vnd } from "../utils/format";
import StatusTag from "../components/StatusTag";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const nav = useNavigate();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const { data: payload } = await api.get("/api/reports/dashboard");
      setData(payload);
    } catch (e) {
      setError(errText(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading && !data) return <Spin />;
  if (error && !data) {
    return (
      <Empty description={error || "Không tải được dữ liệu"}>
        <Button type="primary" onClick={load}>Thử lại</Button>
      </Empty>
    );
  }
  if (!data) return <Spin />;

  return (
    <div>
      <div className="page-head">
        <h1>Tổng quan studio</h1>
        <p>Theo dõi dịch vụ cưới, kho trang phục và cảnh báo thuê mượn</p>
      </div>
      <div className="kpi-grid">
        <Card className="kpi-card"><Statistic title="Tổng dịch vụ" value={data.totalServices} /></Card>
        <Card className="kpi-card"><Statistic title="Kho áo cưới" value={data.totalDresses} suffix={`/ ${data.availableDresses} sẵn sàng`} /></Card>
        <Card className="kpi-card"><Statistic title="Chưa trả" value={data.unreturned} /></Card>
        <Card className="kpi-card"><Statistic title="Quá hạn" value={data.overdue} valueStyle={{ color: "#ef4444" }} /></Card>
      </div>
      <div className="kpi-grid" style={{ gridTemplateColumns: "1.4fr 1fr" }}>
        <Card title="Hợp đồng quá hạn cần xử lý">
          <Table
            size="small"
            rowKey="maHopDong"
            pagination={false}
            dataSource={data.overdueList}
            columns={[
              { title: "HĐ", dataIndex: "maHopDong" },
              { title: "Khách", dataIndex: "tenKH" },
              { title: "Hạn trả", dataIndex: "ngayTraDuKien", render: fmtDate },
              { title: "Trễ", dataIndex: "soNgayTre", render: (n) => `${n} ngày` },
              { title: "Phạt", dataIndex: "phiTreHan", render: vnd },
              { title: "TT", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
            ]}
            onRow={() => ({ onClick: () => nav("/overdue"), style: { cursor: "pointer" } })}
          />
        </Card>
        <Card title="Phân bố loại dịch vụ">
          {(data.categories || []).map((c) => (
            <div key={c.code} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>{c.name}</span>
                <strong>{c.count}</strong>
              </div>
              <div style={{ height: 8, background: "#eee", borderRadius: 99 }}>
                <div style={{ width: `${Math.max(8, (c.count / Math.max(1, data.totalServices)) * 100)}%`, height: "100%", background: "linear-gradient(90deg,#795290,#c59b27)", borderRadius: 99 }} />
              </div>
            </div>
          ))}
          <Typography.Paragraph type="secondary" style={{ marginTop: 16 }}>
            Doanh thu dịch vụ: {vnd(data.revenueServices)} · Doanh thu thuê: {vnd(data.revenueRentals)}
          </Typography.Paragraph>
        </Card>
      </div>
    </div>
  );
}
