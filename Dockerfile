# uma imagem por aplicação: docker build --build-arg APP=cpu|memory|io
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev

ARG APP
RUN test -n "$APP" || (echo "faltou --build-arg APP" && exit 1)
ENV APP=${APP} PATH=/app/.venv/bin:$PATH DATA_DIR=/app/data
EXPOSE 8001 8002 8003

CMD ["sh", "-c", "exec python -m poi.run \"$APP\""]
