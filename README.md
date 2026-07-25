<div align="center">

# ⌨️ KeyScope

### Browser-Based Keylogger for Educational & Cybersecurity Learning

*A lightweight web application that demonstrates browser-based keystroke logging, real-time analytics, and keyboard event visualization using modern JavaScript.*

<br>

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![MIT License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## 📖 About

**KeyScope** is a browser-based keylogger built using **HTML, CSS, and JavaScript** to demonstrate how keyboard events are captured and processed within a web application.

The application records keystrokes in real time, tracks typing activity, analyzes keyboard usage, and provides an interactive dashboard with session statistics and export functionality.

Unlike traditional operating system keyloggers, **KeyScope only monitors keyboard events within the active browser page**, making it suitable for educational demonstrations, web development learning, and cybersecurity awareness.

---

## ✨ Features

- ⌨️ Real-Time Keystroke Logging
- 📊 Live Analytics Dashboard
- 📈 Key Frequency Analysis
- ⏱️ Session Duration Tracking
- ⚡ Keys Per Second (KPS)
- 🔑 Modifier Key Detection
- 🎵 Keyboard Sound Simulation
- 📜 Event Logging
- 📄 TXT Report Export
- 📁 JSON Report Export
- 🌙 Dark / Light Theme
- 📱 Responsive User Interface

---

## 📸 Preview

> Replace these placeholders with screenshots after uploading them.

| Dashboard | Event Logs |
|-----------|------------|
| ![](screenshots/dashboard.png) | ![](screenshots/logs.png) |

| Statistics | Export |
|-----------|---------|
| ![](screenshots/stats.png) | ![](screenshots/export.png) |

---

## 🏗️ System Architecture

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
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
 Session Manager   Event Logger   Audio Engine
      │               │               │
      └───────────────┴───────────────┘
                      │
                      ▼
             Analytics Engine
      • Event Counter
      • Session Timer
      • Keys Per Second
      • Key Frequency
      • Modifier Keys
                      │
                      ▼
            Dashboard Interface
                      │
                      ▼
          Export (TXT / JSON)
```

---

## ⚙️ Tech Stack

| Frontend | Browser APIs | Export |
|----------|--------------|--------|
| HTML5 | Keyboard Events API | TXT |
| CSS3 | DOM API | JSON |
| JavaScript | Web Audio API | Blob API |

---

## 📂 Project Structure

```text
KeyScope/
│
├── assets/
│   ├── css/
│   ├── js/
│   ├── icons/
│   └── sounds/
│
├── screenshots/
├── docs/
│
├── index.html
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/KeyScope.git
```

Go to the project directory

```bash
cd KeyScope
```

Run the application by opening

```text
index.html
```

in your preferred web browser.

---

## 🎯 Use Cases

- Cybersecurity Education
- Ethical Hacking Demonstrations
- JavaScript Event Handling
- Browser API Learning
- Keyboard Interaction Analysis
- Academic Mini Projects

---

## 🛣️ Roadmap

- ✅ Browser-based keystroke logging
- ✅ Live dashboard
- ✅ Session management
- ✅ Event logging
- ✅ TXT & JSON export
- ⏳ Keyboard heatmap
- ⏳ CSV/PDF export
- ⏳ AI-based typing analysis
- ⏳ Cloud synchronization

---

## 👥 Contributors

- **Narottam Kumar**
- **Simardeep Singh Bhatti**
- **Maroof Ahmad Malik**
- **Sushil Dhiman**

---

## 📄 License

This project is licensed under the **MIT License**.

---

## ⚠️ Educational Disclaimer

This project was developed **strictly for educational and cybersecurity learning purposes**.

It captures keyboard events **only within the active browser page** and **does not function as a system-wide keylogger** or monitor input from other applications.

---

<div align="center">

### ⭐ If you found this project helpful, consider giving it a star!

Made with ❤️ using HTML, CSS & JavaScript

</div>
