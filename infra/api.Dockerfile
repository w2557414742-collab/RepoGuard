FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir '.[api,refactor,architecture]' && git config --system --add safe.directory /target
COPY infra/service_entry.py /opt/repoguard/service_entry.py
ENV REPOGUARD_REPOSITORY=/target REPOGUARD_DATABASE=/index/index.sqlite PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python", "/opt/repoguard/service_entry.py"]
