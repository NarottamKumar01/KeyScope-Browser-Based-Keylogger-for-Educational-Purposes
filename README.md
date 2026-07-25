# ⌨️ KeyScope
### Browser-Based Keylogger for Educational & Cybersecurity Learning

<p align="center">

![GitHub stars](https://img.shields.io/github/stars/yourusername/KeyScope?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/yourusername/KeyScope?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/yourusername/KeyScope?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</p>

---

## 📖 Overview

**KeyScope** is a browser-based keylogger developed using **HTML, CSS, and JavaScript** for educational and cybersecurity learning.

The application demonstrates how keyboard events are captured inside a web browser using JavaScript event listeners. It records keystrokes in real time, maintains typing statistics, tracks modifier keys, generates event logs, and allows exporting reports in TXT and JSON formats.

Unlike traditional system-level keyloggers, **KeyScope only captures keyboard events occurring within the active webpage**, making it suitable for learning browser event handling, JavaScript programming, and cybersecurity concepts in a safe environment.

> **Educational Disclaimer**
>
> This project is created **strictly for educational and cybersecurity awareness purposes**. It operates only within the active browser window and **does not capture system-wide keystrokes**.

---

# ✨ Features

- ⌨️ Real-Time Keystroke Logging
- 📊 Live Dashboard
- 📈 Key Frequency Analysis
- ⏱️ Session Duration Tracking
- ⚡ Keys Per Second (KPS)
- 🔑 Modifier Key Detection
- 🎵 Keyboard Sound Simulation
- 📜 Event Logging
- 📄 Export TXT Reports
- 📁 Export JSON Reports
- 🌙 Dark / Light Theme
- 💻 Responsive Interface

---

# 🚀 Demo

### Home Dashboard

```
(Add Screenshot Here)
```

### Event Logs

```
(Add Screenshot Here)
```

### Statistics Dashboard

```
(Add Screenshot Here)
```

### Export Functionality

```
(Add Screenshot Here)
```

---

# 🏗 System Architecture

```
                     User
                       │
                       ▼
               Keyboard Input
                       │
                       ▼
        JavaScript Event Listener
             (keydown / keyup)
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
 Session Manager   Event Logger   Audio Engine
      │                │                │
      └────────────┬───┴────────────────┘
                   │
                   ▼
           Analytics Engine
      • Event Counter
      • Session Timer
      • KPS
      • Key Frequency
      • Modifier Keys
                   │
                   ▼
          Dashboard Interface
                   │
                   ▼
        TXT / JSON Report Export
```

---

# ⚙️ Workflow

```
Start Session
      │
      ▼
Keyboard Input
      │
      ▼
Capture Key Events
      │
      ▼
Process JavaScript Events
      │
      ├──────────────┐
      ▼              ▼
Update Stats     Store Logs
      │              │
      └──────┬───────┘
             ▼
     Update Dashboard
             │
             ▼
      Export Reports
```

---

# 💻 Technology Stack

| Technology | Purpose |
|------------|---------|
| HTML5 | Structure |
| CSS3 | User Interface |
| JavaScript | Application Logic |
| DOM API | Dynamic Updates |
| Keyboard Events API | Capture Keyboard Input |
| Web Audio API | Keyboard Sound |
| Blob API | TXT & JSON Export |

---

# 📂 Project Structure

```
KeyScope/

│

├── assets/

│ ├── css/

│ ├── js/

│ ├── sounds/

│ └── icons/

│

├── screenshots/

│

├── docs/

│

├── index.html

├── README.md

├── LICENSE

├── CONTRIBUTING.md

└── .gitignore
```

---

# ⚡ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/KeyScope.git
```

Move into project directory

```bash
cd KeyScope
```

Open

```text
index.html
```

using your preferred browser.

---

# 🎯 Applications

- Cybersecurity Education
- Ethical Hacking Demonstrations
- Browser Event Analysis
- JavaScript Learning
- Keyboard Event Monitoring
- Academic Projects
- User Interaction Analytics

---

# 📊 Project Highlights

✔ Browser-Based Keylogger

✔ Event Logging

✔ Live Dashboard

✔ Session Management

✔ Keyboard Analytics

✔ Modifier Key Tracking

✔ Export Reports

✔ Responsive UI

---

# 🚀 Future Scope

- AI-based Typing Behaviour Analysis
- Keyboard Heatmap
- CSV Export
- PDF Report Generation
- Cloud Synchronization
- User Authentication
- Keyboard Shortcut Detection
- Machine Learning Analytics

---

# 👨‍💻 Contributors

<table>
<tr align="center">

<td>

<b>Narottam Kumar</b>

</td>

<td>

<b>Simardeep Singh Bhatti</b>

</td>

<td>

<b>Maroof Ahmad Malik</b>

</td>

<td>

<b>Sushil Dhiman</b>

</td>

</tr>
</table>

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 📜 License

This project is licensed under the **MIT License**.

---

# ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

It motivates us to continue improving the project.

---

<p align="center">

Made with ❤️ using HTML, CSS & JavaScript

</p>
