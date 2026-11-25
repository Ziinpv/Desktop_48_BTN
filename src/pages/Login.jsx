import { useState } from "react";
import { Button, Form, Input, Typography, App } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { setSession } from "../store/authSlice";
import { errText } from "../utils/format";

export default function Login() {
  const { t } = useTranslation();
  const { message } = App.useApp();
  const dispatch = useDispatch();
  const nav = useNavigate();
  const theme = useSelector((s) => s.ui.theme);
  const [loading, setLoading] = useState(false);

  const onFinish = async (v) => {
    setLoading(true);
    try {
      const { data } = await api.post("/api/auth/login", v);
      dispatch(setSession(data));
      message.success("Xin chào " + data.user.fullName);
      nav("/");
    } catch (e) {
      message.error(errText(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-screen">
      <div className={`login-card${theme === "dark" ? " dark" : ""}`}>
        <Typography.Title className="serif" level={2} style={{ color: "#795290", marginBottom: 4 }}>
          LUXE WEDDING STUDIO
        </Typography.Title>
        <Typography.Paragraph type="secondary">{t("loginHint")}</Typography.Paragraph>
        <Form layout="vertical" onFinish={onFinish} initialValues={{ username: "admin", password: "admin123" }}>
          <Form.Item name="username" label={t("username")} rules={[{ required: true }]}>
            <Input size="large" />
          </Form.Item>
          <Form.Item name="password" label={t("password")} rules={[{ required: true }]}>
            <Input.Password size="large" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block size="large" loading={loading}>
            {t("signIn")}
          </Button>
        </Form>
        <Typography.Paragraph type="secondary" style={{ marginTop: 16, marginBottom: 0, fontSize: 12 }}>
          Admin: admin / admin123 · Staff: staff / staff123
        </Typography.Paragraph>
      </div>
    </div>
  );
}
