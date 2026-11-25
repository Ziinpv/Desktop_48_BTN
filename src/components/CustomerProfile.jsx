import { Button, Card, Empty, Statistic, Table, Typography } from "antd";
import { downloadFile } from "../services/api";
import { fmtDate, vnd } from "../utils/format";
import StatusTag from "./StatusTag";

function lateText(r) {
  if (!r.soNgayTre) return r.hanTra === "DUNG_HAN" ? "Đúng hạn" : "—";
  return `Trễ ${r.soNgayTre} ngày`;
}

export default function CustomerProfile({ customer }) {
  if (!customer) return <Empty description="Không có dữ liệu khách hàng" />;

  return (
    <div>
      <Typography.Paragraph type="secondary" style={{ marginBottom: 16 }}>
        {customer.sdt || "—"} · {customer.email || "—"} · {customer.diaChi || "—"}
      </Typography.Paragraph>
      <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(4, minmax(0, 1fr))" }}>
        <Card size="small"><Statistic title="Dịch vụ đã dùng" value={customer.serviceTotal || 0} formatter={vnd} /></Card>
        <Card size="small"><Statistic title="Đã cọc" value={customer.depositTotal || 0} formatter={vnd} /></Card>
        <Card size="small"><Statistic title="Đã thanh toán" value={customer.paidTotal || 0} formatter={vnd} /></Card>
        <Card size="small"><Statistic title="Còn nợ" value={customer.outstanding || 0} valueStyle={{ color: customer.outstanding ? "#ef4444" : undefined }} formatter={vnd} /></Card>
      </div>

      <Typography.Title level={5} style={{ marginTop: 8 }}>Dịch vụ đã sử dụng</Typography.Title>
      <Table
        size="small"
        rowKey="id"
        pagination={false}
        locale={{ emptyText: "Chưa sử dụng dịch vụ nào" }}
        dataSource={customer.services || []}
        columns={[
          { title: "Mã DV", dataIndex: "maDV", width: 90 },
          { title: "Tên dịch vụ", dataIndex: "tenDV" },
          { title: "Loại", dataIndex: "loaiDV" },
          { title: "Ngày dùng", dataIndex: "ngaySD", render: fmtDate, width: 120 },
          { title: "Thành tiền", dataIndex: "giaLucSD", render: vnd, width: 140, align: "right" },
        ]}
      />

      <Typography.Title level={5} style={{ marginTop: 20 }}>Thuê áo cưới</Typography.Title>
      <Table
        size="small"
        rowKey="maHopDong"
        pagination={false}
        locale={{ emptyText: "Chưa có hợp đồng thuê áo" }}
        dataSource={customer.rentals || []}
        scroll={{ x: 980 }}
        columns={[
          { title: "Mã HĐ", dataIndex: "maHopDong", width: 90, fixed: "left" },
          { title: "Bộ áo", dataIndex: "boAo", ellipsis: true },
          { title: "Ngày nhận", dataIndex: "ngayNhan", render: fmtDate, width: 110 },
          { title: "Hạn trả", dataIndex: "ngayTraDuKien", render: fmtDate, width: 110 },
          { title: "Ngày trả", dataIndex: "ngayTraThucTe", render: fmtDate, width: 110 },
          {
            title: "Hạn",
            dataIndex: "hanTra",
            width: 150,
            render: (v, r) => (
              <>
                <StatusTag value={v} />
                {r.soNgayTre ? <div style={{ fontSize: 12, color: "#ef4444" }}>{lateText(r)}</div> : null}
              </>
            ),
          },
          { title: "Đã cọc", dataIndex: "tienCoc", render: vnd, width: 120, align: "right" },
          { title: "Tiền thuê", dataIndex: "tienThue", render: vnd, width: 120, align: "right" },
          { title: "Phí trễ", dataIndex: "phiTreHan", render: vnd, width: 110, align: "right" },
          { title: "Đã thanh toán", dataIndex: "daThanhToan", render: vnd, width: 130, align: "right" },
          { title: "Còn nợ", dataIndex: "conNo", render: vnd, width: 110, align: "right" },
        ]}
      />

      <Typography.Title level={5} style={{ marginTop: 20 }}>Lịch sử giao dịch</Typography.Title>
      <Table
        size="small"
        rowKey="id"
        pagination={false}
        locale={{ emptyText: "Chưa có giao dịch" }}
        dataSource={customer.transactions || []}
        columns={[
          { title: "Ngày", dataIndex: "ngay", render: (v) => (v ? v.replace("T", " ").slice(0, 19) : "—") },
          { title: "HĐ", dataIndex: "maHopDong" },
          { title: "Trạng thái", dataIndex: "trangThai", render: (v) => <StatusTag value={v} /> },
          { title: "Số tiền", dataIndex: "tienPhat", render: vnd, align: "right" },
          { title: "Ghi chú", dataIndex: "ghiChu" },
        ]}
      />

      <Button type="link" style={{ paddingLeft: 0, marginTop: 12 }} onClick={() => downloadFile(`/api/export/invoice/${customer.maKH}`, `hoa-don-${customer.maKH}.pdf`)}>
        Tải hóa đơn PDF
      </Button>
    </div>
  );
}
