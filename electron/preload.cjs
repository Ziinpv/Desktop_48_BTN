const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("luxeDesktop", {
  info: () => ipcRenderer.invoke("app:info"),
  openPath: (target) => ipcRenderer.invoke("app:open-path", target),
  chooseFolder: () => ipcRenderer.invoke("app:choose-folder"),
  print: () => ipcRenderer.invoke("app:print"),
  saveFile: (payload) => ipcRenderer.invoke("app:save-file", payload),
});
