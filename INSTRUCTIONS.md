# Meme Bot Application Setup Instructions

This guide will walk you through the final, correct steps to set up and run the Meme Bot application. This process will create a clean, isolated environment for the app so it will work perfectly.

---

### **Part 1: One-Time Setup**

You only need to do this once.

1.  **Install Python 3.9:**
    *   If you don't have it already, please install Python 3.9 from the official Python website: [https://www.python.org/downloads/release/python-3913/](https://www.python.org/downloads/release/python-3913/)
    *   **Important:** During installation, make sure to check the box that says "Add Python 3.9 to PATH".

2.  **Get the Latest Code:**
    *   Download the latest version of the project code into a new, clean folder.

3.  **Open a Terminal in the Project Folder:**
    *   Navigate to the project directory in your PowerShell or Command Prompt.

4.  **Create the Virtual Environment:**
    *   Run this command. It will use the Python 3.9 you just installed to create a `venv` folder in your project directory.
    *   ```powershell
      py -3.9 -m venv venv
      ```

5.  **Activate the Environment:**
    *   Now, run this command to "enter" the isolated environment. You'll know it's active because your command prompt will change to show `(venv)`.
    *   ```powershell
      .\venv\Scripts\activate
      ```

6.  **Install All Dependencies:**
    *   Finally, run this command. It will install the correct, conflict-free versions of all the necessary libraries into the virtual environment.
    *   ```powershell
      pip install -r requirements.txt
      ```

The one-time setup is now complete!

---

### **Part 2: How to Run the App (Every Time)**

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

That's it! The application window will open. You can then go to "Settings" to enter your API keys and voice sample, and then start generating videos.
