FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pytest==8.3.5 coverage==7.8.2
COPY src/repoguard/pytest_coverage.py /usr/local/lib/python3.12/site-packages/repoguard/pytest_coverage.py
COPY infra/runner_entry.py /opt/repoguard/runner_entry.py
