# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml /app/
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false && poetry install --no-interaction
COPY . /app
CMD ["python", "-m", "bot.app.main"]
