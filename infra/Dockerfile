# Review candidate only: base digest and transitive package hashes remain unpinned.
# Must not be exposed on a public host; the API has no production auth/quotas/TLS.
FROM python:3.12.7-slim-bookworm
WORKDIR /opt/psychneuro
COPY . .
RUN python -m pip install --no-cache-dir -e '.[w03]' 'uvicorn==0.34.0'
RUN useradd --create-home --uid 10001 reviewer && mkdir -p /tmp/w04 && chown reviewer:reviewer /tmp/w04
USER reviewer
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "psychneuro.w04.server:app_factory", "--factory", "--host", "127.0.0.1", "--port", "8000"]
