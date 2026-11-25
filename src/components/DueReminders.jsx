import { useEffect } from "react";
import { App } from "antd";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const KEY = "luxe-due-reminded";

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

export default function DueReminders() {
  const { notification } = App.useApp();
  const nav = useNavigate();

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      try {
        const { data } = await api.get("/api/reports/due-soon");
        if (cancelled || !data?.length) return;
        const due = data.filter((r) => r.sapHetHan);
        const late = data.filter((r) => r.trangThai === "QUA_HAN");
        const stamp = `${todayKey()}:${data.map((r) => r.maHopDong).join(",")}`;
        if (sessionStorage.getItem(KEY) === stamp) return;
        sessionStorage.setItem(KEY, stamp);
        const body = [
          due.length ? `${due.length} hợp đồng còn ≤ 3 ngày` : "",
          late.length ? `${late.length} hợp đồng quá hạn` : "",
        ].filter(Boolean).join(" · ");
        notification.warning({
          message: "Nhắc hạn trả áo",
          description: body,
          duration: 8,
          onClick: () => nav("/unreturned"),
        });
        if (localStorage.getItem("luxe-desktop-notify") !== "off") {
          window.luxeDesktop?.notify?.({ title: "LUXE WEDDING STUDIO", body });
        }
      } catch {
        /* ignore until backend ready */
      }
    };
    run();
    return () => { cancelled = true; };
  }, [nav, notification]);

  return null;
}
