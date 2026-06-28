<div align="center">
  <img
    src="Images/images_for_readme/PYSCHECARElogo.png"
    alt="PsycheCare Logo"
    width="520">
</div>

# 🧠 PsycheCare

> **AI-Powered Mental Health Support Platform**
>
> PsycheCare combines artificial intelligence, personalized care, and digital wellness tools to help individuals manage stress, anxiety, depression, and overall mental well-being.

---

## 🌟 Key Features

| Feature                             | Description                                                          |
| ----------------------------------- | -------------------------------------------------------------------- |
| 🤖 **Arya AI Assistant**            | 24/7 emotional support, mood tracking, and guided conversations.     |
| 🚨 **Emergency SOS**                | Quick access to emergency contacts and crisis resources.             |
| 📅 **Appointment Management**       | Schedule therapy sessions and receive reminders.                     |
| 🧠 **Personalized Treatment Plans** | AI-generated plans tailored to each user's needs.                    |
| 💊 **Medication Management**        | Track prescriptions, schedules, and medication information.          |
| 📄 **Report Reader**                | Simplifies medical and therapy reports into understandable insights. |
| 📊 **Progress Tracking**            | Monitor mood trends and mental wellness over time.                   |

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- FontAwesome

### Backend & AI

- PHP
- Python 3
- TensorFlow / Keras
- NLTK
- NumPy
- Autocorrect

---

# 🚀 Getting Started

## Prerequisites

Before running the project, install:

| Requirement | Version                 |
| ----------- | ----------------------- |
| Python      | 3.8+                    |
| PHP         | 7.4+                    |
| Git         | Latest                  |
| Browser     | Chrome / Firefox / Edge |

---

# 💻 Running the Project

PsycheCare contains multiple components. Choose the setup that matches your contribution.

## Option 1 — Frontend Development

For contributors working on:

- UI/UX
- HTML
- CSS
- Client-side JavaScript

### Run Locally

```bash
# Using Node
npx serve .

# OR using Python
python3 -m http.server 8000
```

Open:

```text
http://localhost:8000
```

> ✅ Recommended for most first-time contributors.

---

## Option 2 — Full Application Development

For contributors working on:

- AI Chatbot
- Backend Logic
- NLP Models
- Machine Learning Features

### Clone Repository

```bash
git clone https://github.com/Niteshagarwal01/PYSCHECARE.git
cd PYSCHECARE
```

### Install Dependencies

It is highly recommended to create and activate a virtual environment before installing dependencies:

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### Configure Environment Variables

The server requires specific environment variables to run securely. Create a `.env` file in the root directory by copying the example file:

*   **Linux/macOS/Git Bash**:
    ```bash
    cp .env.example .env
    ```
*   **Windows (Command Prompt)**:
    ```cmd
    copy .env.example .env
    ```
*   **Windows (PowerShell)**:
    ```powershell
    Copy-Item .env.example .env
    ```

Open the newly created `.env` file and configure the following variables:
*   `ALLOWED_ORIGIN`: The client application's origin URL allowed to make requests via CORS (e.g., `http://localhost:8000` or `http://localhost`).
*   `CHAT_API_SECRET`: A secure, random string/key used for signing and validating chat session tokens.

> ⚠️ **IMPORTANT**: The Flask server will raise a fatal `ValueError` and fail to start if the `ALLOWED_ORIGIN` environment variable is not defined.

### Start Application

```bash
python app.py
```

The application will usually be available at:

```text
http://127.0.0.1:5000
```

---

## Option 3 — PHP Features

For contributors working on:

- Login System
- Contact Forms
- PHP Functionality

Move the project into your web server directory:

```text
XAMPP  → htdocs/
WAMP   → www/
```

Access:

```text
http://localhost/PYSCHECARE
```

> 💡 Some features may require both PHP and Python services running simultaneously.

---

# 🤝 Quick Start for Contributors

### 1️⃣ Read the Documentation

- README.md
- CONTRIBUTING.md
- chatbot_integration_README.md

### 2️⃣ Claim an Issue

Before making changes, ensure an issue has been assigned to you.

### 3️⃣ Sync Your Fork

```bash
git fetch upstream
git checkout main
git rebase upstream/main
```

### 4️⃣ Create a Branch

```bash
git checkout -b feat/short-description
```

Examples:

```text
feat/add-theme-toggle
fix/issue-25-navbar-bug
docs/update-readme
```

### 5️⃣ Make Changes

Follow the coding standards outlined in CONTRIBUTING.md.

### 6️⃣ Submit a Pull Request

- Push your branch
- Open a PR
- Link the issue
- Complete the PR template

---

# 📚 Useful Resources

| Resource                      | Purpose                             |
| ----------------------------- | ----------------------------------- |
| CONTRIBUTING.md               | Contribution workflow and standards |
| chatbot_integration_README.md | AI chatbot documentation            |
| requirements.txt              | Python dependencies                 |
| app.py                        | Main backend entry point            |

---

# 📂 Project Structure

| File                          | Description                      |
| ----------------------------- | -------------------------------- |
| README.md                     | Project overview and setup guide |
| CONTRIBUTING.md               | Contribution guidelines          |
| chatbot_integration_README.md | Chatbot documentation            |
| requirements.txt              | Python dependency list           |
| app.py                        | Backend application entry point  |

---

# 🎯 Our Mission

PsycheCare aims to make mental health support accessible, personalized, and stigma-free through technology-driven solutions that empower individuals on their wellness journey.

---

# 💼 Revenue Model

- ⭐ Premium Memberships
- 🏢 Corporate Wellness Programs
- 🤝 Grants & Partnerships
- 📚 Premium Mental Health Resources

---

# 📷 Screenshots

## Dashboard Overview

![Dashboard Overview](Images/images_for_readme/secondPage.PNG)

Central dashboard displaying personalized mental health tools and resources.

---

## Stress Relief Activity

![Stress Relief Activity](Images/images_for_readme/carGameImg.PNG)

Interactive wellness feature designed to improve engagement and reduce stress.

---

## Arya AI Assistant

![Arya AI Assistant](Images/images_for_readme/chatBotImg.PNG)

Conversational AI interface providing emotional support and mental health guidance.

---

## Mobile Experience

![Mobile Experience](Images/images_for_readme/mobileVersion.PNG)

Responsive design optimized for smartphones and tablets.

---

## Resource Dashboard

![Resource Dashboard](Images/images_for_readme/secondPage.PNG)

Additional tools, resources, and navigation options available to users.

---

## Analytics & Progress Tracking

![Analytics & Progress Tracking](Images/images_for_readme/statisticsImg.PNG)

Visual insights into mood trends, wellness metrics, and user progress.
