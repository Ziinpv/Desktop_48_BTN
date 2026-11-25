import { useEffect, useState } from "react";
import { Button, Card, Form, Input, List, Space, Typography, App } from "antd";
import api from "../services/api";
import { errText } from "../utils/format";

export default function Settings() {
  const { message, modal } = App.useApp();
  const [info, setInfo] = useState(null);
  const [backups, setBackups] = useState([]);
  const [form] = Form.useForm();

  const load = async () => {
    const [{ data: s }, { data: b }] = await Promise.all([api.get("/api/system/settings"), api.get("/api/system/backups")]);
    setInfo(s);
    setBackups(b);
  };
  useEffect(() => { load(); }, []);

  const changePass = async () => {
    const v = await form.validateFields();
    try {
      await api.post("/api/auth/change-password", v);
      message.success("Đã đổi mật khẩu");
      form.resetFields();
    } catch (e) {
      message.error(errText(e));
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>Cài đặt, sao lưu & đồng bộ</h1>
        <p>Backup mỗi ngày lúc 02:00 · có thể copy sang thư mục Google Drive / OneDrive</p>
      </div>
      <div className="kpi-grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <Card title="Quy định nghiệp vụ">
          {info && (
            <ul>
              <li>Tối đa bộ đang thuê / khách: <strong>{info.maxActiveDresses}</strong></li>
              <li>Tỷ lệ cọc: <strong>{info.depositRate * 100}%</strong></li>
              <li>Phí trễ hạn: <strong>{info.lateFeeRate * 100}%</strong> × số ngày</li>
              <li>Cảnh báo sắp hết hạn: <strong>{info.dueSoonDays} ngày</strong></li>
              <li>CSDL: {info.dbPath}</li>
              <li>Thư mục backup: {info.backupDir}</li>
            </ul>
          )}
          <Space>
            <Button type="primary" onClick={async () => { const { data } = await api.post("/api/system/backup"); message.success(data.ok ? "Đã sao lưu" : data.message); load(); }}>Sao lưu ngay</Button>
            <Button onClick={() => window.luxeDesktop?.openPath?.(info?.backupDir)}>Mở thư mục backup</Button>
          </Space>
          <Typography.Paragraph type="secondary" style={{ marginTop: 12 }}>
            Cloud sync: đặt biến môi trường LUXE_CLOUD_SYNC_DIR trỏ tới thư mục Google Drive hoặc OneDrive trên máy.
          </Typography.Paragraph>
        </Card>
        <Card title="Đổi mật khẩu">
          <Form form={form} layout="vertical" onFinish={changePass}>
            <Form.Item name="password" label="Mật khẩu mới" rules={[{ required: true, min: 6 }]}><Input.Password /></Form.Item>
            <Button type="primary" htmlType="submit">Cập nhật</Button>
          </Form>
        </Card>
      </div>
      <Card title="Bản sao lưu gần đây" style={{ marginTop: 16 }}>
        <List
          dataSource={backups}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button key="res" danger onClick={() => modal.confirm({
                  title: "Khôi phục bản này? Ứng dụng sẽ ghi đè CSDL hiện tại.",
                  onOk: async () => {
                    try { await api.post("/api/system/restore", { name: item.name }); message.success("Đã restore — hãy đăng nhập lại nếu cần"); }
                    catch (e) { message.error(errText(e)); }
                  },
                })}>Restore</Button>,
              ]}
            >
              <List.Item.Meta title={item.name} description={`${item.createdAt} · ${(item.size / 1024).toFixed(1)} KB`} />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
}
