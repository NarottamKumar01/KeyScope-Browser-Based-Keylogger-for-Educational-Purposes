# ⌨️ KeyScope
### Browser-Based Keylogger for Educational & Cybersecurity Learning

![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Overview

**KeyScope** is a browser-based keylogger developed using **HTML, CSS, and JavaScript** for educational and cybersecurity learning. The application captures keyboard events within the active browser window, records keystrokes in real time, maintains typing statistics, and exports session logs.

The project demonstrates how browser keyboard events work and helps students understand keyboard event handling, event logging, and basic cybersecurity concepts.

> **Educational Purpose:** This project is intended solely for learning and cybersecurity awareness. It only captures keyboard events within the active webpage and does not monitor system-wide keyboard activity.

---

## ✨ Features

- 🔑 Real-time keystroke logging
- 📊 Live typing statistics
- ⌨️ Keyboard event monitoring
- 📈 Key frequency analysis
- ⏱️ Session timer
- 🎹 Keyboard sound simulation
- 📋 Event logging
- 📄 Export reports as TXT
- 📁 Export reports as JSON
- 🌙 Light/Dark theme support
- ⚡ Interactive dashboard

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| HTML5 | Structure |
| CSS3 | User Interface |
| JavaScript | Core Logic |
| DOM API | Dynamic Updates |
| Web Audio API | Keyboard Sound |
| Blob API | File Export |

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
          │       │       │
          ▼       ▼       ▼
   Session    Event     Audio
   Manager    Logger    Engine
          │       │
          └───┬───┘
              ▼
      Analytics Engine
              │
              ▼
      Dashboard Interface
              │
              ▼
      TXT / JSON Export
```

---

## ⚙️ Working

1. User starts a monitoring session.
2. Keyboard events are captured using JavaScript event listeners.
3. Every keystroke is recorded.
4. Typing statistics are updated in real time.
5. Event logs are displayed on the dashboard.
6. Users can export the session report in TXT or JSON format.

---

## 📂 Project Structure

```
KeyScope/
│
├── assets/
│   ├── css/
│   ├── js/
│   ├── sounds/
│   └── icons/
│
├── screenshots/
│
├── docs/
│
├── index.html
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/KeyScope.git
```

Open the project folder

```bash
cd KeyScope
```

Launch

```text
Open index.html in your browser
```

---

## 📸 Screenshots

Add screenshots inside the **screenshots/** folder.

Example

```
screenshots/

home.png

dashboard.png

logs.png

statistics.png

export.png
```

---

## 🎯 Applications

- Cybersecurity Education
- Ethical Hacking Demonstrations
- Browser Event Learning
- JavaScript Event Handling
- User Interaction Analysis
- Academic Projects

---

## 🚧 Future Enhancements

- AI-based typing analysis
- Keyboard heatmap
- CSV & PDF export
- Cloud synchronization
- User authentication
- Advanced analytics
- Typing accuracy prediction
- Keyboard shortcut detection

---

## 🤝 Contributors

- Narottam Kumar
- Simardeep Singh Bhatti
- Maroof Ahmad Malik
- Sushil Dhiman

---

## 📜 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.
