import { useEffect, useState } from "react";
import { Table } from "antd";
import api from "../services/api";

export default function AuditLogs() {
  const [rows, setRows] = useState([]);
  useEffect(() => { api.get("/api/system/audit").then((r) => setRows(r.data)); }, []);
  return (
    <div>
      <div className="page-head">
        <h1>Nhật ký audit</h1>
        <p>Ai · làm gì · lúc nào · trên thực thể nào</p>
      </div>
      <Table
        rowKey="id"
        dataSource={rows}
        columns={[
          { title: "Thời gian", dataIndex: "createdAt", render: (v) => v?.replace("T", " ").slice(0, 19) },
          { title: "Người dùng", dataIndex: "username" },
          { title: "Hành động", dataIndex: "action" },
          { title: "Thực thể", dataIndex: "entity" },
          { title: "Mã", dataIndex: "entityId" },
          { title: "Chi tiết", dataIndex: "detail" },
        ]}
      />
    </div>
  );
}
