import { ConfigProvider, App as AntApp, theme as antTheme } from "antd";
import viVN from "antd/locale/vi_VN";
import enUS from "antd/locale/en_US";
import { useEffect, useState } from "react";
import { Spin } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import api from "./services/api";
import { logout } from "./store/authSlice";
import { canAccess } from "./utils/roles";
import AppLayout from "./layouts/AppLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ServiceTypes from "./pages/ServiceTypes";
import Services from "./pages/Services";
import ServiceCatalog from "./pages/ServiceCatalog";
import Dresses from "./pages/Dresses";
import Customers from "./pages/Customers";
import Rentals from "./pages/Rentals";
import Unreturned from "./pages/Unreturned";
import Overdue from "./pages/Overdue";
import DressLookup from "./pages/DressLookup";
import CustomerLookup from "./pages/CustomerLookup";
import Reports from "./pages/Reports";
import Users from "./pages/Users";
import AuditLogs from "./pages/AuditLogs";
import Settings from "./pages/Settings";
import Appointments from "./pages/Appointments";

function Guard({ children }) {
  const token = useSelector((s) => s.auth.token);
  const role = useSelector((s) => s.auth.user?.role);
  const loc = useLocation();
  const dispatch = useDispatch();
  const [ready, setReady] = useState(!token);

  useEffect(() => {
    if (!token) {
      setReady(true);
      return undefined;
    }
    let cancelled = false;
    api.get("/api/auth/me")
      .then(() => { if (!cancelled) setReady(true); })
      .catch(() => {
        if (!cancelled) {
          dispatch(logout());
          setReady(true);
        }
      });
    return () => { cancelled = true; };
  }, [token, dispatch]);

  if (!ready) return <div style={{ padding: 80, textAlign: "center" }}><Spin /></div>;
  if (!token) return <Navigate to="/login" replace />;
  if (!canAccess(role, loc.pathname === "" ? "/" : loc.pathname)) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  const { theme, lang } = useSelector((s) => s.ui);
  const dark = theme === "dark";
  return (
    <ConfigProvider
      locale={lang === "en" ? enUS : viVN}
      theme={{
        algorithm: dark ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm,
        token: {
          colorPrimary: "#795290",
          colorInfo: "#795290",
          colorWarning: "#c59b27",
          borderRadius: 10,
          fontFamily: "'Plus Jakarta Sans', sans-serif",
        },
      }}
    >
      <AntApp>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <Guard>
                <AppLayout />
              </Guard>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="service-types" element={<ServiceTypes />} />
            <Route path="services" element={<Services />} />
            <Route path="catalog" element={<ServiceCatalog />} />
            <Route path="dresses" element={<Dresses />} />
            <Route path="customers" element={<Customers />} />
            <Route path="rentals" element={<Rentals />} />
            <Route path="appointments" element={<Appointments />} />
            <Route path="unreturned" element={<Unreturned />} />
            <Route path="overdue" element={<Overdue />} />
            <Route path="dress-lookup" element={<DressLookup />} />
            <Route path="customer-lookup" element={<CustomerLookup />} />
            <Route path="reports" element={<Reports />} />
            <Route path="users" element={<Users />} />
            <Route path="audit" element={<AuditLogs />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </AntApp>
    </ConfigProvider>
  );
}
