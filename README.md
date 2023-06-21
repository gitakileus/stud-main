# Stud Domain Seller Projects

## Clone repository

```commandline
    git clone https://github.com/startupbreeders/stud.git
```

## VS Code

Open the repository in VS Code.

```commandline
    cd stud
    code .
```

When asked to open in a container say yes.

Open a terminal within VS Code by pressing Ctrl + Shift + ~

```
    cp .env.example .env
    virtualenv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt
```

## Create DB

```commandline
    python3 manage.py makemigrations
    python3 manage.py migrate
```

## Generate static files

```commandline
    python3 manage.py collectstatic
```

## Run

```commandline
    python3 manage.py runserver
```

## Administration

Visit http://127.0.0.1:8000/admin/

## activate virtual env
env\Scripts\activate