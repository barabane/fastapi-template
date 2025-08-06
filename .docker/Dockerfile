FROM python:3.12-slim

RUN mkdir -p /opt/app && mkdir -p /home/user

RUN useradd -r user && \
    chown -R user /opt/app && \
    chown -R user /home/user

WORKDIR /opt/app
USER user

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

ENV PYTHONPATH=/opt/app

COPY .docker/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
