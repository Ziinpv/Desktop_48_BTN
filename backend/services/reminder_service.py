import json
import logging
import os
import smtplib
import urllib.request
from email.message import EmailMessage
from typing import Iterable

logger = logging.getLogger("luxe.reminders")


def smtp_configured() -> bool:
    return bool(os.getenv("LUXE_SMTP_HOST") and os.getenv("LUXE_SMTP_FROM"))


def sms_configured() -> bool:
    return bool(os.getenv("LUXE_SMS_WEBHOOK"))


def _send_email(to_addr: str, subject: str, body: str) -> dict:
    host = os.getenv("LUXE_SMTP_HOST")
    from_addr = os.getenv("LUXE_SMTP_FROM")
    if not host or not from_addr or not to_addr:
        return {"ok": False, "channel": "email", "to": to_addr, "message": "Thiếu SMTP hoặc email khách"}
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, int(os.getenv("LUXE_SMTP_PORT", "587")), timeout=15) as smtp:
            smtp.starttls()
            user = os.getenv("LUXE_SMTP_USER")
            password = os.getenv("LUXE_SMTP_PASSWORD")
            if user:
                smtp.login(user, password or "")
            smtp.send_message(msg)
        return {"ok": True, "channel": "email", "to": to_addr}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Email reminder failed")
        return {"ok": False, "channel": "email", "to": to_addr, "message": str(exc)}


def _send_sms(phone: str, body: str) -> dict:
    webhook = os.getenv("LUXE_SMS_WEBHOOK")
    if not webhook or not phone:
        return {"ok": False, "channel": "sms", "to": phone, "message": "Thiếu webhook SMS hoặc SĐT"}
    payload = json.dumps({"to": phone, "message": body}).encode("utf-8")
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
        return {"ok": True, "channel": "sms", "to": phone}
    except Exception as exc:  # noqa: BLE001
        logger.exception("SMS reminder failed")
        return {"ok": False, "channel": "sms", "to": phone, "message": str(exc)}


def remind_contracts(rows: Iterable[dict], channels: list[str]) -> dict:
    results = []
    for row in rows:
        name = row.get("tenKH") or row.get("maKH")
        code = row.get("maHopDong")
        due = row.get("ngayTraDuKien") or ""
        remain = row.get("ngayConLai")
        late = row.get("soNgayTre") or 0
        if late:
            body = f"LUXE Wedding Studio: hop dong {code} da tre {late} ngay. Vui long tra ao."
        else:
            body = f"LUXE Wedding Studio: hop dong {code} con {remain} ngay (han {due}). Vui long tra ao dung han."
        subject = f"[LUXE] Nhac han hop dong {code}"
        if "email" in channels:
            results.append(_send_email(row.get("email") or "", subject, f"Kinh gui {name},\n\n{body}"))
        if "sms" in channels:
            results.append(_send_sms(row.get("sdt") or "", body))
    return {
        "smtpConfigured": smtp_configured(),
        "smsConfigured": sms_configured(),
        "sent": sum(1 for r in results if r.get("ok")),
        "failed": sum(1 for r in results if not r.get("ok")),
        "results": results,
    }
