# Product Part Finder - Public Deployment

A modern, responsive web application built with Python (Flask) and a Pandas backend, using local CSV data.

> **Note:** The local SQLite database and registration flow have been removed to prepare this application for public sharing.

## Hardcoded Testing Credentials
For the current iteration, to allow reviewers to access the application without needing to create accounts, the authentication is hardcoded to:
* **Email:** `test@test.com`
* **Password:** `password`

## Beginner-Friendly Deployment Instructions

Because Render.com connects directly to GitHub to host your code for free, we first need to get this folder onto GitHub. Here is exactly how to do it step-by-step:

### Part 1: Uploading to GitHub
1. **Create a GitHub Account:** Go to [GitHub.com](https://github.com/) and sign up for a free account.
2. **Download GitHub Desktop:** Go to [desktop.github.com](https://desktop.github.com/) and download the app. This makes uploading code much easier than using the command line!
3. **Sign In to GitHub Desktop:** Open the app and sign in with your new GitHub account.
4. **Add Your Local Folder:**
   - In GitHub Desktop, go to `File` > `Add Local Repository...`
   - Click `Choose...` and select your `PART_FINDER` folder on your Desktop, then click `Add Repository`.
   - A warning will pop up saying "This directory does not appear to be a Git repository." Click the blue **create a repository** text right below it.
   - Leave the settings as they are and click **Create Repository**.
5. **Publish to GitHub:**
   - Click the blue **Publish repository** button at the top right (or in the middle of the screen).
   - Uncheck the box that says "Keep this code private" (so Render can easily access it).
   - Click **Publish repository**. Your code is now live on GitHub!

### Part 2: Hosting on Render.com
1. **Create a Render Account:** Go to [Render.com](https://render.com/) and click **Get Started**. Sign up using the **GitHub** button so they are automatically linked.
2. **Create a Web Service:**
   - Once logged in, click the **New +** button at the top right and select **Web Service**.
   - You should see a list of your GitHub repositories. Find the one you just created (e.g., `PART_FINDER`) and click **Connect**.
3. **Deploy the App:**
   - Because we created a `render.yaml` file earlier, Render already knows exactly how to build and start your application!
   - Just scroll down and click the **Deploy Web Service** button.
4. **Wait and Share:** Render will take a few minutes to install Python and start the app. Once it says "Live" in green, you can click the `.onrender.com` link at the top left of the screen. Share this link with your reviewers!

## Local Testing Instructions
If you wish to test it locally before deploying to Render:

1. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Flask application:**
   ```bash
   flask run
   ```
   *Alternatively, you can run:*
   ```bash
   python app.py
   ```
3. **Access the application:**
   Open a web browser and go to `http://127.0.0.1:5000`

---

## 🤖 AI Parts Assistant (Built-in Chatbot)

This application includes a fully functional, AI-powered Chatbot directly on the search page! 

### 1. Prerequisites
- **OpenAI API Key**: The chatbot uses OpenAI to process natural language.

### 2. How to Enable the Chatbot
To power the chatbot's "brain", you just need to set your OpenAI key as an environment variable before starting the server.

**In your terminal (VS Code):**
```bash
# On Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# On Mac/Linux
export OPENAI_API_KEY="your-api-key-here"
```

Once the key is set, run `flask run` again. When you log into the application, you will see the **AI Parts Assistant** panel on the right side of the screen.

### 3. Usage
You can ask the assistant natural language questions instead of using the strict search bar:
* *"What parts are compatible with TDI1000106?"*
* *"A customer needs an alternate for part 56003342, do we have any?"*
* *"I found distributor number 987654, what Product ID is that for?"*

The AI will intelligently search the `PARTS_DATA.csv` and formulate a conversational reply!
