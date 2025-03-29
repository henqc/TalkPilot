import { app, BrowserWindow } from "electron";
import path from "path";

app.on("ready", () => {
  const mainWindow = new BrowserWindow({
    width: 1000,
    height: 1000,
  });

  mainWindow.loadFile(path.join(app.getAppPath(), "/dist-react/index.html"));
});
