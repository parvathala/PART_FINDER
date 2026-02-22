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
