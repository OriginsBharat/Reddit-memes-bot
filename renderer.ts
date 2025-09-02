import { ipcRenderer } from 'electron';

document.getElementById('generate-video').addEventListener('click', () => {
    const settings = {
        redditClientId: (document.getElementById('reddit-client-id') as HTMLInputElement).value,
        redditClientSecret: (document.getElementById('reddit-client-secret') as HTMLInputElement).value,
        uberduckKey: (document.getElementById('uberduck-key') as HTMLInputElement).value,
        uberduckSecret: (document.getElementById('uberduck-secret') as HTMLInputElement).value,
        voiceSample: (document.getElementById('voice-sample') as HTMLInputElement).files[0]?.path,
    };

    ipcRenderer.send('generate-video', settings);
});

ipcRenderer.on('log', (event, message) => {
    const log = document.getElementById('log') as HTMLTextAreaElement;
    log.value += message + '\n';
});

ipcRenderer.on('video-ready', (event, path) => {
    const downloadLink = document.getElementById('download-link') as HTMLAnchorElement;
    downloadLink.href = path;
    downloadLink.style.display = 'block';
});
