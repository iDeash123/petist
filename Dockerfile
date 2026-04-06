
FROM python:3.12-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


ENV UV_SYSTEM_PYTHON=1
ENV PYTHONUNBUFFERED=1


COPY pyproject.toml uv.lock ./


RUN uv sync --frozen --no-install-project


COPY . .


EXPOSE 8000


CMD ["uv", "run", "gunicorn", "petist.wsgi:application", "--bind", "0.0.0.0:8000"]