import { useEffect, useMemo } from "react";
import { Layout, Menu, Button, Space, Switch, Dropdown, Avatar, Badge } from "antd";
import {
  DashboardOutlined,
  AppstoreOutlined,
  GiftOutlined,
  SkinOutlined,
  TeamOutlined,
  FileProtectOutlined,
  SearchOutlined,
  UserSwitchOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  BarChartOutlined,
  SafetyOutlined,
  AuditOutlined,
  SettingOutlined,
  LogoutOutlined,
  CameraOutlined,
} from "@ant-design/icons";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import { logout } from "../store/authSlice";
import { setCollapsed, setLang, toggleTheme } from "../store/uiSlice";
import i18n from "../i18n";

const { Sider, Header, Content } = Layout;

export default function AppLayout() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const loc = useLocation();
  const dispatch = useDispatch();
  const collapsed = useSelector((s) => s.ui.collapsed);
  const theme = useSelector((s) => s.ui.theme);
  const lang = useSelector((s) => s.ui.lang);
  const user = useSelector((s) => s.auth.user);
  const dark = theme === "dark";

  useEffect(() => {
    i18n.changeLanguage(lang);
  }, [lang]);

  const items = useMemo(
    () => [
      { type: "group", label: t("overview"), children: [{ key: "/", icon: <DashboardOutlined />, label: t("dashboard") }] },
      {
        type: "group",
        label: t("catalog"),
        children: [
          { key: "/service-types", icon: <AppstoreOutlined />, label: t("serviceTypes") },
          { key: "/services", icon: <GiftOutlined />, label: t("services") },
          { key: "/catalog", icon: <AppstoreOutlined />, label: t("catalogPage") },
          { key: "/dresses", icon: <SkinOutlined />, label: t("dresses") },
          { key: "/customers", icon: <TeamOutlined />, label: t("customers") },
        ],
      },
      {
        type: "group",
        label: t("rentalBiz"),
        children: [{ key: "/rentals", icon: <FileProtectOutlined />, label: t("rentals") }],
      },
      {
        type: "group",
        label: t("lookup"),
        children: [
          { key: "/dress-lookup", icon: <SearchOutlined />, label: t("dressLookup") },
          { key: "/customer-lookup", icon: <UserSwitchOutlined />, label: t("customerLookup") },
        ],
      },
      {
        type: "group",
        label: t("reports"),
        children: [
          { key: "/unreturned", icon: <ClockCircleOutlined />, label: t("unreturned") },
          { key: "/overdue", icon: <WarningOutlined />, label: t("overdue") },
          { key: "/reports", icon: <BarChartOutlined />, label: t("charts") },
        ],
      },
      {
        type: "group",
        label: t("system"),
        children: [
          ...(user?.role === "admin" ? [{ key: "/users", icon: <SafetyOutlined />, label: t("users") }] : []),
          { key: "/audit", icon: <AuditOutlined />, label: t("audit") },
          { key: "/settings", icon: <SettingOutlined />, label: t("settings") },
        ],
      },
    ],
    [t, user]
  );

  return (
    <Layout className="luxe-app" style={{ minHeight: "100vh" }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(v) => dispatch(setCollapsed(v))} width={272}>
        <div className="brand-block">
          <div className="brand-icon">
            <CameraOutlined />
          </div>
          {!collapsed && (
            <div>
              <h2 className="serif">{t("brand")}</h2>
              <small>{t("brandSub")}</small>
            </div>
          )}
        </div>
        {!collapsed && (
          <div className="student-chip">
            <strong>Hoàng Long (2212407)</strong>
            <div>{t("ruleMax")}</div>
          </div>
        )}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[loc.pathname]}
          items={items}
          onClick={({ key }) => nav(key)}
          style={{ background: "transparent", border: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{ background: dark ? "#1f1b2e" : "#fff", padding: "0 20px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ color: dark ? "#c59b27" : "#795290", fontWeight: 600 }}>LUXE WEDDING STUDIO</div>
          <Space size="middle">
            <Switch checked={dark} checkedChildren={t("dark")} unCheckedChildren={t("light")} onChange={() => dispatch(toggleTheme())} />
            <Button onClick={() => dispatch(setLang(lang === "vi" ? "en" : "vi"))}>{lang === "vi" ? "EN" : "VI"}</Button>
            <Badge color="gold">
              <Avatar style={{ background: "#795290" }}>{user?.fullName?.[0] || "A"}</Avatar>
            </Badge>
            <Dropdown
              menu={{
                items: [{ key: "out", icon: <LogoutOutlined />, label: t("logout"), onClick: () => { dispatch(logout()); nav("/login"); } }],
              }}
            >
              <Button type="text">{user?.fullName}</Button>
            </Dropdown>
          </Space>
        </Header>
        <Content className={`luxe-content${dark ? " dark" : ""}`}>
          <div className="page-wrap">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
