const { app, BrowserWindow, ipcMain, Notification, shell, dialog } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const http = require("http");

let mainWindow = null;
let backendProcess = null;
const isDev = !app.isPackaged;

function projectRoot() {
  return isDev ? path.join(__dirname, "..") : path.join(process.resourcesPath);
}

function dataDir() {
  const dir = path.join(app.getPath("userData"), "data");
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function waitForHealth(url, timeoutMs = 40000) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const tick = () => {
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode === 200) resolve(true);
        else retry();
      });
      req.on("error", retry);
      req.setTimeout(1500, () => {
        req.destroy();
        retry();
      });
    };
    const retry = () => {
      if (Date.now() - started > timeoutMs) reject(new Error("Backend timeout"));
      else setTimeout(tick, 400);
    };
    tick();
  });
}

function pythonCmd() {
  const win = process.platform === "win32";
  const bundledName = win ? "luxe-api.exe" : "luxe-api";
  const bundled = path.join(projectRoot(), "luxe-api", bundledName);
  if (fs.existsSync(bundled)) return { cmd: bundled, args: [], cwd: path.dirname(bundled) };
  const venv = win
    ? path.join(projectRoot(), ".venv", "Scripts", "python.exe")
    : path.join(projectRoot(), ".venv", "bin", "python");
  if (fs.existsSync(venv)) return { cmd: venv, args: ["-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"] };
  if (win) return { cmd: "py", args: ["-3", "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"] };
  return { cmd: "python3", args: ["-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"] };
}

function startBackend() {
  const env = {
    ...process.env,
    LUXE_DB_PATH: path.join(dataDir(), "luxe_studio.db"),
    LUXE_BACKUP_DIR: path.join(dataDir(), "backups"),
    LUXE_UPLOAD_DIR: path.join(dataDir(), "uploads"),
    LUXE_LOG_DIR: path.join(dataDir(), "logs"),
    PYTHONPATH: projectRoot(),
  };
  const { cmd, args, cwd } = pythonCmd();
  backendProcess = spawn(cmd, args, { cwd: cwd || projectRoot(), env, windowsHide: true });
  backendProcess.on("error", (err) => {
    console.error("[api] spawn failed", err);
    dialog.showErrorBox("Không khởi động được máy chủ", String(err.message || err));
  });
  backendProcess.stdout.on("data", (d) => console.log(`[api] ${d}`));
  backendProcess.stderr.on("data", (d) => console.log(`[api] ${d}`));
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: "#1e1b2e",
    title: "LUXE WEDDING STUDIO",
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  if (isDev && process.env.VITE_DEV_SERVER) {
    const url = process.env.VITE_DEV_SERVER;
    let loaded = false;
    for (let i = 0; i < 6 && !loaded; i += 1) {
      try {
        await mainWindow.loadURL(url);
        loaded = true;
      } catch (err) {
        console.error(`[electron] loadURL retry ${i + 1}:`, err.message || err);
        await new Promise((resolve) => setTimeout(resolve, 700));
      }
    }
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    await mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }
}

function registerIpc() {
  ipcMain.handle("app:info", () => ({
    version: app.getVersion(),
    userData: app.getPath("userData"),
    dbPath: path.join(dataDir(), "luxe_studio.db"),
  }));
  ipcMain.handle("app:open-path", async (_e, target) => {
    if (!target) return { ok: false };
    await shell.openPath(target);
    return { ok: true };
  });
  ipcMain.handle("app:choose-folder", async () => {
    const result = await dialog.showOpenDialog(mainWindow, { properties: ["openDirectory", "createDirectory"] });
    if (result.canceled || !result.filePaths[0]) return null;
    return result.filePaths[0];
  });
  ipcMain.handle("app:print", async () => {
    if (!mainWindow) return { ok: false };
    mainWindow.webContents.print({ silent: false });
    return { ok: true };
  });
  ipcMain.handle("app:notify", (_e, { title, body }) => {
    if (!Notification.isSupported()) return { ok: false };
    const n = new Notification({ title: title || "LUXE WEDDING STUDIO", body: body || "" });
    n.on("click", () => {
      if (mainWindow) {
        if (mainWindow.isMinimized()) mainWindow.restore();
        mainWindow.show();
        mainWindow.focus();
      }
    });
    n.show();
    return { ok: true };
  });
  ipcMain.handle("app:save-file", async (_e, { defaultPath, data, encoding }) => {
    const result = await dialog.showSaveDialog(mainWindow, { defaultPath });
    if (result.canceled || !result.filePath) return { ok: false };
    const buf = Buffer.from(data, encoding || "base64");
    fs.writeFileSync(result.filePath, buf);
    return { ok: true, path: result.filePath };
  });
}

app.whenReady().then(async () => {
  registerIpc();
  app.on("web-contents-created", (_e, contents) => {
    contents.session.setPermissionRequestHandler((_wc, permission, cb) => {
      cb(["media", "notifications"].includes(permission));
    });
  });
  try {
    await waitForHealth("http://127.0.0.1:8000/api/health", 2500);
  } catch {
    startBackend();
    try {
      await waitForHealth("http://127.0.0.1:8000/api/health", 60000);
    } catch (err) {
      dialog.showErrorBox(
        "Không kết nối được máy chủ nội bộ",
        "Ứng dụng không khởi động được API trên cổng 8000. Hãy đóng bản đang chạy rồi mở lại.\n\n" + String(err.message || err)
      );
    }
  }
  await createWindow();
});

app.on("window-all-closed", () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  if (backendProcess) backendProcess.kill();
});
