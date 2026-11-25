import { useEffect, useRef, useState } from "react";
import { Button, Input, Space, App } from "antd";
import { CameraOutlined, ScanOutlined } from "@ant-design/icons";

async function decodeFromBitmap(bitmap) {
  if (!window.BarcodeDetector) return "";
  const detector = new window.BarcodeDetector({ formats: ["qr_code"] });
  const codes = await detector.detect(bitmap);
  return codes[0]?.rawValue || "";
}

export default function QrScanBar({ onFound, placeholder = "Dán mã QR hoặc mã áo AC001..." }) {
  const { message } = App.useApp();
  const [q, setQ] = useState("");
  const [cam, setCam] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const tickRef = useRef(0);
  const foundRef = useRef(onFound);
  foundRef.current = onFound;

  const stopCam = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setCam(false);
  };

  useEffect(() => () => stopCam(), []);

  useEffect(() => {
    if (!cam) return undefined;
    let alive = true;
    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        if (!alive) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        const loop = async () => {
          if (!alive || !videoRef.current) return;
          try {
            if (videoRef.current.readyState >= 2) {
              const value = await decodeFromBitmap(videoRef.current);
              if (value) {
                setQ(value);
                foundRef.current(value);
                stopCam();
                return;
              }
            }
          } catch {
            /* keep scanning */
          }
          tickRef.current = window.setTimeout(loop, 400);
        };
        loop();
      } catch {
        message.error("Không mở được camera. Hãy dán mã QR hoặc chọn ảnh.");
        setCam(false);
      }
    };
    start();
    return () => {
      alive = false;
      window.clearTimeout(tickRef.current);
    };
  }, [cam, message]);

  const onFile = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const bitmap = await createImageBitmap(file);
      const value = await decodeFromBitmap(bitmap);
      if (!value) {
        message.warning("Không đọc được QR từ ảnh. Thử dán payload LUXE|DRESS|AC001");
        return;
      }
      setQ(value);
      onFound(value);
    } catch {
      message.error("Không đọc được ảnh QR");
    }
  };

  return (
    <Space wrap>
      <Input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onPressEnter={() => q && onFound(q)}
        placeholder={placeholder}
        style={{ width: 280 }}
        prefix={<ScanOutlined />}
      />
      <Button type="primary" onClick={() => q && onFound(q)}>Mở hợp đồng</Button>
      <Button icon={<CameraOutlined />} onClick={() => (cam ? stopCam() : setCam(true))}>
        {cam ? "Tắt camera" : "Quét camera"}
      </Button>
      <Button onClick={() => document.getElementById("luxe-qr-file")?.click()}>Ảnh QR</Button>
      <input id="luxe-qr-file" type="file" accept="image/*" hidden onChange={onFile} />
      {cam ? <video ref={videoRef} muted playsInline style={{ width: 220, borderRadius: 8, background: "#111" }} /> : null}
    </Space>
  );
}
