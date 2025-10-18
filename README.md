# USA Visa Appointment Checker Bot (Ecuador) 🚀

Automated system to check available US visa appointments in Ecuador and receive email alerts.

## 📋 Features

- Checks appointment availability every 30 minutes
- Runs in background (headless mode)
- Email notifications via Gmail
- Detailed logging system
- Cross-platform compatibility

## ⚙️ Requirements

- Python 3.8+
- Chrome Browser
- ChromeDriver (matching your Chrome version)
- Python packages: `selenium`, `python-dotenv`

## 🛠️ Installation

# Clone repository

git clone https://github.com/yourusername/bot-usa-visa-appointment-available-checker-ecuador.git
cd bot-usa-visa-appointment-available-checker-ecuador

# Install dependencies

pip install -r requirements.txt

# Configure credentials

cp credentials.example.py credentials.py
nano credentials.py # Add your Gmail credentials

## 🚦 Usage Commands

### For macOS/Linux

| Action                | Command                                  |
| --------------------- | ---------------------------------------- | ----------------------- |
| **Run in background** | `nohup python3 main.py > app.log 2>&1 &` |
| **View logs**         | `tail -f app.log`                        |
| **Stop program**      | `pkill -f "python3 main.py"`             |
| **Check if running**  | `ps aux                                  | grep "python3 main.py"` |

### For Linux

| **Acción**                    | **Comando**                              |
| ----------------------------- | ---------------------------------------- | ----------------------- |
| **Ejecutar en segundo plano** | `nohup python3 main.py > app.log 2>&1 &` |
| **Ver logs en tiempo real**   | `tail -f app.log`                        |
| **Detener el proceso**        | `pkill -f "python3 main.py"`             |
| **Ver si está corriendo**     | `ps aux                                  | grep "python3 main.py"` |

### For Windows (PowerShell)

| Action                | Command                                                  |
| --------------------- | -------------------------------------------------------- |
| **Run in background** | `Start-Process -WindowStyle Hidden python.exe "main.py"` |
| **View logs**         | `Get-Content app.log -Wait`                              |
| **Stop program**      | `taskkill /IM python.exe /F`                             |
| **Check if running**  | `Get-Process python`                                     |

## 🔄 Advanced Scheduling

### macOS (Persistent after reboot)

1. Create plist file:
   sudo nano /Library/LaunchDaemons/com.visa.checker.plist

2. Add this configuration:
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.visa.checker</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/PATH/TO/main.py</string>
       </array>
       <key>StartInterval</key>
       <integer>1800</integer>
       <key>RunAtLoad</key>
       <true/>
   </dict>
   </plist>

3. Load service:
   sudo launchctl load /Library/LaunchDaemons/com.visa.checker.plist

### Windows (Task Scheduler)

1. Create Basic Task with:
   - Trigger: "Daily" with "Repeat task every 30 minutes"
   - Action: `Start a program`
     - Program: `python.exe`
     - Arguments: `"C:\PATH\TO\main.py"`

## 📝 Log Management

- Logs auto-save to `app.log`
- Rotate logs weekly:

# Linux/macOS

logrotate config_file.conf

Sample `config_file.conf`:
/path/to/app.log {
weekly
rotate 4
compress
missingok
notifempty
}

# Execute Backend

1. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Dependencies:**

   ```bash
   pip install flask flask-cors
   ```

3. **Run the Flask App:**
   Navigate to the backend folder and run:
   ```bash
   python app.py
   ```
   Alternatively, set the FLASK_APP variable and use:
   ```bash
   export FLASK_APP=app.py
   flask run | flask run --port=5001
   ```
   The backend will be available at `http://127.0.0.1:5000`.

---

# Execute Frontend

1. **Navigate to Your Next.js Project Folder.**
2. **Install Dependencies:**
   ```bash
   npm install
   ```
   or if using yarn:
   ```bash
   yarn install
   ```
3. **Run the Development Server:**
   ```bash
   npm run dev
   ```
   or with yarn:
   ```bash
   yarn dev
   ```
   The frontend will be available at `http://localhost:3000`.

## ⚠️ Important Notes

- Chrome Driver download Page: https://googlechromelabs.github.io/chrome-for-testing/
- 🔒 Never commit `credentials.py` to version control
- 📧 Test email configuration before deployment
- ⏰ Verify scheduler is working with initial test runs
- 🌐 Maintain stable internet connection for bot operation

## 📬 Support

For issues contact: [your.email@domain.com](mailto:your.email@domain.com)
