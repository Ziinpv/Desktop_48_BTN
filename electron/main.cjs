const { app, BrowserWindow, ipcMain, shell, dialog } = require("electron");
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
  const cwd = projectRoot();
  const { cmd, args } = pythonCmd();
  backendProcess = spawn(cmd, args, { cwd, env, windowsHide: true });
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
    await mainWindow.loadURL(process.env.VITE_DEV_SERVER);
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
  try {
    await waitForHealth("http://127.0.0.1:8000/api/health", 2500);
  } catch {
    startBackend();
    await waitForHealth("http://127.0.0.1:8000/api/health");
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
