import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432
    password = os.environ.get("DB_PASSWORD", "password")
    user, name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 8000 if host == "localhost" else 80
    return f"http://{host}:{port}"
