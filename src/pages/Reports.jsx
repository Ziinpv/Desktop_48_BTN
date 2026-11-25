import { useEffect, useState } from "react";
import { Card, Spin } from "antd";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, Pie, PieChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../services/api";

const COLORS = ["#795290", "#c59b27", "#10b981", "#ef4444", "#64748b", "#e76f51"];

export default function Reports() {
  const [data, setData] = useState(null);
  useEffect(() => { api.get("/api/reports/charts").then((r) => setData(r.data)); }, []);
  if (!data) return <Spin />;

  const revenue = data.revenue.labels.map((label, i) => ({
    name: label,
    dichVu: data.revenue.services[i],
    thueAo: data.revenue.rentals[i],
    luotThue: data.rentalVolume[i],
  }));
  const pie = [
    { name: "Đang thuê", value: data.dressStatus.renting },
    { name: "Sẵn sàng", value: data.dressStatus.ready },
    { name: "Hỏng", value: data.dressStatus.damaged },
    { name: "Hết hàng", value: data.dressStatus.out },
  ];

  return (
    <div>
      <div className="page-head">
        <h1>Biểu đồ doanh thu & tỷ lệ cho thuê</h1>
        <p>Năm {data.year} · Dịch vụ theo tháng, top dịch vụ, tỷ lệ kho áo cưới</p>
      </div>
      <Card title="Doanh thu theo tháng" style={{ marginBottom: 16 }}>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={revenue}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="dichVu" name="Dịch vụ" stroke="#795290" strokeWidth={2} />
            <Line type="monotone" dataKey="thueAo" name="Thuê áo" stroke="#c59b27" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>
      <div className="kpi-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <Card title="Top dịch vụ">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.topServices}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="revenue" name="Doanh thu" fill="#795290" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card title="Tỷ lệ kho áo cưới">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={pie} dataKey="value" nameKey="name" outerRadius={100} label>
                {pie.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
