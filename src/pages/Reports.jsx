import { useEffect, useState } from "react";
import { Button, Card, DatePicker, Space, Spin, Statistic } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, Pie, PieChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api, { downloadFile } from "../services/api";
import { vnd } from "../utils/format";

const COLORS = ["#795290", "#c59b27", "#10b981", "#ef4444", "#64748b", "#e76f51"];

export default function Reports() {
  const [range, setRange] = useState([dayjs().startOf("month"), dayjs()]);
  const [data, setData] = useState(null);

  const load = async (from = range[0], to = range[1]) => {
    const { data: payload } = await api.get("/api/reports/charts", {
      params: { fromDate: from.format("YYYY-MM-DD"), toDate: to.format("YYYY-MM-DD") },
    });
    setData(payload);
  };
  useEffect(() => { load(); }, []);

  if (!data) return <Spin />;

  const revenue = data.revenue.labels.map((label, i) => ({
    name: label,
    dichVu: data.revenue.services[i],
    thueAo: data.revenue.rentals[i],
    daThu: data.revenue.collected[i],
    luotThue: data.rentalVolume[i],
  }));
  const pie = [
    { name: "Đang thuê", value: data.dressStatus.renting },
    { name: "Sẵn sàng", value: data.dressStatus.ready },
    { name: "Hỏng", value: data.dressStatus.damaged },
    { name: "Hết hàng", value: data.dressStatus.out },
  ];
  const qs = `fromDate=${data.fromDate}&toDate=${data.toDate}`;

  return (
    <div>
      <div className="page-head">
        <h1>Biểu đồ doanh thu & tỷ lệ cho thuê</h1>
        <p>Lọc từ–đến để đối soát cuối tháng · Xuất PDF cùng khoảng ngày</p>
      </div>
      <Space wrap style={{ marginBottom: 16 }}>
        <DatePicker.RangePicker
          value={range}
          onChange={(v) => {
            if (!v) return;
            setRange(v);
            load(v[0], v[1]);
          }}
        />
        <Button onClick={() => { const v = [dayjs().startOf("month"), dayjs()]; setRange(v); load(v[0], v[1]); }}>Tháng này</Button>
        <Button onClick={() => { const v = [dayjs().subtract(1, "month").startOf("month"), dayjs().subtract(1, "month").endOf("month")]; setRange(v); load(v[0], v[1]); }}>Tháng trước</Button>
        <Button onClick={() => { const v = [dayjs().startOf("year"), dayjs()]; setRange(v); load(v[0], v[1]); }}>Từ đầu năm</Button>
        <Button type="primary" icon={<DownloadOutlined />} onClick={() => downloadFile(`/api/export/charts.pdf?${qs}`, `bao-cao-${data.fromDate}-${data.toDate}.pdf`)}>Xuất PDF</Button>
      </Space>
      <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(4, minmax(0, 1fr))", marginBottom: 16 }}>
        <Card size="small"><Statistic title="Dịch vụ" value={data.totals.services} formatter={vnd} /></Card>
        <Card size="small"><Statistic title="Thuê áo" value={data.totals.rentals} formatter={vnd} /></Card>
        <Card size="small"><Statistic title="Đã thu (sổ TT)" value={data.totals.collected} formatter={vnd} /></Card>
        <Card size="small"><Statistic title="Lượt hợp đồng" value={data.totals.contracts} /></Card>
      </div>
      <Card title={`Doanh thu ${data.fromDate} → ${data.toDate}`} style={{ marginBottom: 16 }}>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={revenue}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="dichVu" name="Dịch vụ" stroke="#795290" strokeWidth={2} />
            <Line type="monotone" dataKey="thueAo" name="Thuê áo" stroke="#c59b27" strokeWidth={2} />
            <Line type="monotone" dataKey="daThu" name="Đã thu" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>
      <div className="kpi-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <Card title="Top dịch vụ trong khoảng">
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
        <Card title="Tỷ lệ kho áo cưới (hiện tại)">
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
