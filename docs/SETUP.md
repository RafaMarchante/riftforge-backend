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

## Database (Docker)

The database runs in a Docker container. Make sure Docker Desktop is installed and running before proceeding.

Open Docker Desktop and wait until the engine status shows "Running" in the bottom left corner. Then, in a terminal at the project root, start the database:

docker-compose up -d db

The `-d` flag runs it in the background. To stop it:

docker-compose down

To check that the container is running:

docker-compose ps

Once the container is up, run Django migrations as usual:

python manage.py migrate

You need to start Docker Desktop and run `docker-compose up -d db` every time you restart your machine, before running the development server.

## Django project

Run database migrations:

python manage.py migrate

Run the development server:

python manage.py runserver

Visit http://127.0.0.1:8000 in your browser.

## Email (Mailtrap)

During development, emails are caught by Mailtrap — a service that acts as a fake inbox so you can test the full email flow (sending, receiving, clicking links) without delivering anything to real addresses.

**Setup:**

1. Create a free account at https://mailtrap.io
2. Go to **Sandboxes → My Sandbox → Credentials**
3. Select **Django** from the integration dropdown to get the exact settings
4. Add the following to your `.env` file:
```
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=your_mailtrap_user
EMAIL_HOST_PASSWORD=your_mailtrap_password
EMAIL_USE_TLS=True
```
5. Make sure your `settings.py` reads these values:
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
```
Once configured, trigger a registration and the email will appear in your Mailtrap inbox. You can open it and click the verification link exactly as a real user would.

## Debugging

Debugging in VS Code: create a `launch.json` with Python → Django configuration:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Django",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}\\src\\manage.py",
            "args": [
                "runserver"
            ],
            "django": true
        }
    ]
}
```

Always work inside the virtual environment. Pull latest changes with git pull origin main, commit your work, and push. Update `requirements.txt` whenever dependencies change:

pip freeze > requirements.txt
