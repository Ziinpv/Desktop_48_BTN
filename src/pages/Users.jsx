import { useEffect, useState } from "react";
import { Button, Form, Input, Modal, Select, Space, Switch, Table, App } from "antd";
import { useSelector } from "react-redux";
import api from "../services/api";
import { errText } from "../utils/format";

export default function Users() {
  const me = useSelector((s) => s.auth.user);
  const { message } = App.useApp();
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const load = async () => {
    try {
      const { data } = await api.get("/api/auth/users");
      setRows(data);
    } catch (e) {
      message.error(errText(e));
    }
  };
  useEffect(() => { load(); }, []);

  if (me?.role !== "admin") return <p>Chỉ quản trị viên mới xem được trang này.</p>;

  const onSave = async () => {
    const v = await form.validateFields();
    try {
      await api.post("/api/auth/users", v);
      message.success("Đã tạo tài khoản");
      setOpen(false);
      load();
    } catch (e) {
      message.error(errText(e));
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>Người dùng & phân quyền</h1>
        <p>Admin / Staff · mật khẩu hash bcrypt · JWT session</p>
      </div>
      <Button type="primary" style={{ marginBottom: 16 }} onClick={() => { form.resetFields(); form.setFieldsValue({ role: "staff", isActive: true }); setOpen(true); }}>Thêm người dùng</Button>
      <Table
        rowKey="id"
        dataSource={rows}
        columns={[
          { title: "Tài khoản", dataIndex: "username" },
          { title: "Họ tên", dataIndex: "fullName" },
          { title: "Vai trò", dataIndex: "role" },
          { title: "Kích hoạt", dataIndex: "isActive", render: (v) => (v ? "Có" : "Không") },
          {
            title: "Thao tác",
            render: (_, r) => (
              <Space>
                <Button size="small" onClick={async () => { await api.patch(`/api/auth/users/${r.id}`, { isActive: !r.isActive }); load(); }}>
                  {r.isActive ? "Khóa" : "Mở"}
                </Button>
              </Space>
            ),
          },
        ]}
      />
      <Modal title="Tạo tài khoản" open={open} onOk={onSave} onCancel={() => setOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="Tài khoản" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="fullName" label="Họ tên" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="password" label="Mật khẩu" rules={[{ required: true }]}><Input.Password /></Form.Item>
          <Form.Item name="role" label="Vai trò"><Select options={[{ value: "admin", label: "Admin" }, { value: "staff", label: "Staff" }]} /></Form.Item>
          <Form.Item name="isActive" label="Kích hoạt" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
