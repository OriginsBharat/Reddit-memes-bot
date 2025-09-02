import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { runMemeBot } from './bot';

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadFile('index.html');

  ipcMain.on('generate-video', async (event, settings) => {
    try {
      await runMemeBot(settings, (log) => {
        mainWindow.webContents.send('log', log);
      });
      mainWindow.webContents.send('video-ready', 'path/to/video.mp4'); // Placeholder
    } catch (error) {
      mainWindow.webContents.send('log', `Error: ${error.message}`);
    }
  });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
