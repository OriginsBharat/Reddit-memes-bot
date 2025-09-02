# Meme Bot Application Setup Instructions (Electron Version)

This guide will walk you through the final, correct steps to set up and run the new Electron-based Meme Bot application.

---

### **Prerequisite: Install Node.js**

If you don't have it already, please install Node.js (which includes the `npm` command). You can download it from the official website: **[https://nodejs.org/](https://nodejs.org/)** (the LTS version is recommended).

---

### **Part 1: Setup and Installation**

1.  **Get the Latest Code:**
    *   Make sure you have the latest version of the project code in a clean folder.

2.  **Open a Terminal:**
    *   Open your terminal (PowerShell or Command Prompt) in the project directory.

3.  **Install Dependencies:**
    *   Run this single command. It will download all the necessary libraries defined in `package.json`.
    *   ```bash
      npm install
      ```

---

### **Part 2: Running the Application**

1.  **Start the App:**
    *   In the same terminal, run this command:
    *   ```bash
      npm start
      ```
    *   The application window will now open.

2.  **Configure Your Settings:**
    *   In the application window, you will see input fields for your API keys. You will need to get these from the respective services:
        *   **Reddit:** Client ID and Client Secret.
        *   **Uberduck:** API Key and Secret (you can get these by signing up on the Uberduck.ai website).
        *   **Voice Sample:** A `.wav` file of the voice you want to clone.
    *   Enter your keys and select your voice file in the app, then click **"Save Settings"**.

3.  **Generate Your Video:**
    *   Click the **"Generate Video"** button. The progress will be shown in the log window.
    *   When it's done, a download link will appear.

---

### **(Optional) Creating a Standalone `.exe` Installer**

If you want to create a single `.exe` file that you can run without using the terminal, run this command *after* you have installed the dependencies (after Step 3 in Part 1):

```bash
npm run dist
```

This will create a `dist` folder in your project directory containing the installer.
