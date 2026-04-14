# Django Project Setup

This guide explains how to set up the Django project using VS Code, including virtual environment, dependencies, and debugging.

Make sure you have Python 3.14 or higher, VS Code, and Git installed.

## Clone the repository:

git clone https://github.com/yourusername/yourproject.git
cd yourproject

## Virtual environment

Create and activate a virtual environment in the project root:

python -m venv .venv

Activate it:

Windows PowerShell: .\.venv\Scripts\Activate.ps1  
Windows CMD: .\.venv\Scripts\activate.bat  
Linux/macOS: source .venv/bin/activate

Open the folder in VS Code and select the Python interpreter from `.venv` (Ctrl+Shift+P → Python: Select Interpreter → choose `.venv`). Recommended extensions: Python, Pylance, Django.

To automatically get the virtual environment in a new terminal, I suggest adding this to the 'settings.json' file:

```
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true
    "terminal.integrated.profiles.windows": {
        "PowerShell": {
            "source": "PowerShell",
            "args": ["-NoExit", "-Command", "& '${workspaceFolder}\\.venv\\Scripts\\Activate.ps1'"]
        }
    },
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

## Install dependencies

Upgrade pip and install dependencies:

pip install --upgrade pip  
pip install -r requirements.txt

## Django project

Run database migrations:

python manage.py migrate

Run the development server:

python manage.py runserver

Visit http://127.0.0.1:8000 in your browser.

## Debugging

Debugging in VS Code: create a `launch.json` with Python → Django configuration:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "--noreload"],
            "django": true
        }
    ]
}
```

Always work inside the virtual environment. Pull latest changes with git pull origin main, commit your work, and push. Update `requirements.txt` whenever dependencies change:

pip freeze > requirements.txt
