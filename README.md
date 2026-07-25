<div align="center">

# ⌨️ KeyScope

### Browser-Based Keylogger for Educational & Cybersecurity Learning

*A lightweight web application that demonstrates browser-based keyboard event monitoring, real-time analytics, and typing behavior visualization using HTML, CSS, and JavaScript.*

<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
<img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge"/>

---

**Real-Time Logging • Analytics Dashboard • Typing Statistics • Export Reports**

</div>

---

# 📖 Overview

KeyScope is an educational browser-based keylogger developed to demonstrate how keyboard events are captured, processed, analyzed, and visualized inside a web browser.

The project records keyboard activity **only within the active browser window**, making it suitable for learning JavaScript event handling, browser APIs, and cybersecurity concepts in a safe environment.

Unlike operating-system keyloggers, this project **cannot monitor keystrokes outside the web page**.

---

# ✨ Features

- ⌨️ Real-Time Keyboard Event Monitoring
- 📊 Interactive Analytics Dashboard
- 📈 Key Frequency Analysis
- ⚡ Typing Speed (Keys Per Second)
- 🕒 Session Duration Tracking
- 🔑 Modifier Key Detection
- 🎵 Keyboard Sound Simulation
- 📄 TXT Export
- 📁 JSON Export
- 🌙 Dark Theme
- 📱 Responsive Design

---

# 📸 Project Preview

## Home Page

> Replace with your screenshot

![Home](screenshots/home.png)

---

## Dashboard

![Dashboard](screenshots/dashboard.png)

---

## Event Logger

![Logger](screenshots/logger.png)

---

## Statistics

![Statistics](screenshots/statistics.png)

---

## Export Report

![Export](screenshots/export.png)

---

# 🏗️ System Architecture

```text
                  User
                    │
                    ▼
             Keyboard Input
                    │
                    ▼
        JavaScript Event Listener
          (keydown / keyup)
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
 Event Logger  Session Manager  Audio Engine
        │           │           │
        └───────────┼───────────┘
                    ▼
            Analytics Engine
      • Typing Speed
      • Key Frequency
      • Session Time
      • Event Counter
                    │
                    ▼
          Dashboard Interface
                    │
                    ▼
         Export (TXT / JSON)
```

---

# 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Frontend | HTML5, CSS3, JavaScript |
| Browser APIs | Keyboard Events API, DOM API, Web Audio API |
| Data Export | Blob API, JSON |

---

# 📂 Project Structure

```text
KeyScope
│
├── index.html
├── styles.css
├── app.js
├── app.py
├── detector_engine.py
├── win32_keylogger.py
├── PROJECTMain.py
│
├── screenshots/
│
├── docs/
│
└── README.md
```

---

# 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/NarottamKumar01/KeyScope-Browser-Based-Keylogger-for-Educational-Purposes.git
```

Open the project

```bash
cd https://github.com/NarottamKumar01/KeyScope-Browser-Based-Keylogger-for-Educational-Purposes
```

Launch

```text
Open index.html in your browser
```

---

# 🎯 Learning Objectives

This project demonstrates:

- JavaScript Keyboard Events
- Event Handling
- DOM Manipulation
- Browser APIs
- User Activity Monitoring
- Frontend Analytics
- Cybersecurity Awareness

---

# 🛣️ Future Improvements

- AI-Based Typing Analysis
- Keyboard Heatmap
- CSV Export
- PDF Report Generation
- User Authentication
- Database Integration
- Cloud Dashboard
- Real-Time Monitoring

---

# 👥 Contributors

- **Narottam Kumar**
- **Simardeep Singh Bhatti**
- **Maroof Ahmad Malik**
- **Sushil Dhiman**

---

# 📜 License

This project is licensed under the **MIT License**.

---

# ⚠️ Disclaimer

This project has been developed **strictly for educational, research, and cybersecurity awareness purposes.**

It captures keyboard events **only inside the active browser window** and **does not function as a system-wide keylogger**.

The authors do not encourage or support the misuse of this project for unauthorized monitoring or malicious activities.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

Made with ❤️ by Team **ByteShield**

</div>