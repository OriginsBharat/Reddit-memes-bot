# Meme Bot Application Setup Instructions

This guide will walk you through the final, correct steps to set up and run the Meme Bot application.

---

### **Part 1: One-Time Setup**

You only need to do this once.

1.  **Install Python 3.9:**
    *   If you don't have it already, please install Python 3.9 from the official Python website: [https://www.python.org/downloads/release/python-3913/](https://www.python.org/downloads/release/python-3913/)
    *   **Important:** During installation, make sure to check the box that says "Add Python 3.9 to PATH".

2.  **Set Up Google Cloud Account and Credentials:**
    *   This application uses the Google Cloud Text-to-Speech API to provide high-quality voices. You will need to set up a Google Cloud account and get a credentials file.
    *   Follow the official Google Cloud guide to set up your account and enable the Text-to-Speech API: [https://cloud.google.com/text-to-speech/docs/before-you-begin](https://cloud.google.com/text-to-speech/docs/before-you-begin)
    *   At the end of the process, you will download a JSON file with your credentials. Save this file somewhere safe on your computer.

3.  **Get the Latest Code:**
    *   Download the latest version of the project code into a new, clean folder.

4.  **Create and Activate a Virtual Environment:**
    *   Open a terminal (PowerShell or Command Prompt) in the project directory.
    *   Run these commands to create and activate a clean, isolated environment for the app:
    *   ```powershell
      py -3.9 -m venv venv
      .\venv\Scripts\activate
      ```

5.  **Install All Dependencies:**
    *   Finally, run this command to install all the necessary libraries into the virtual environment.
    *   ```powershell
      pip install -r requirements.txt
      ```

The one-time setup is now complete!

---

### **Part 2: How to Run the App**

Now, whenever you want to run the application, just follow these steps:

1.  **Open a new terminal** in the project folder.

2.  **Activate the environment:**
    ```powershell
    .\venv\Scripts\activate
    ```

3.  **Run the app:**
    ```powershell
    python app.py
    ```

4.  **Configure Settings:**
    *   The application window will open. Click the "Settings" button.
    *   Fill in all the required fields:
        *   Your Reddit API credentials.
        *   Your Reddit username and password (for upvoting).
        *   Click the "Browse..." button to select the Google Cloud JSON credentials file you downloaded earlier.
        *   Choose a voice from the dropdown menu.
    *   Click "Save".

5.  **Generate and Download:**
    *   Click the "Generate Video" button to start the process.
    *   When it's done, the "Download Video" button will become active. Click it to save your video.

---

### **Customizing Your Videos**

To use your own custom intros, outros, and backgrounds, simply replace the following files in the project directory with your own `.mp4` files:

*   **`intro.mp4`**: Your custom intro video. **(Recommended length: 3-5 seconds)**
*   **`outro.mp4`**: Your custom outro video. **(Recommended length: 3-5 seconds)**
*   **`background.mp4`**: Your custom background gameplay video. This video will be looped and blurred, so any length is fine.

The application will automatically use these files when it creates your meme compilations.
