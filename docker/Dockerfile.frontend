# docker/Dockerfile.frontend
# AegisCare — Streamlit Frontend

FROM python:3.11-slim

LABEL maintainer="AegisCare Team"
LABEL description="AegisCare Streamlit Frontend"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install from requirements.txt first so all pinned versions are respected,
# then ensure the packages the frontend actually uses are present.
# NOTE: api_client.py uses httpx (async + sync HTTP). The previous image
# installed `requests` instead, which caused ImportError on every API call.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit plotly pandas python-dotenv httpx

COPY . .

# Bug 4 fix: frontend/app.py uses absolute package imports
# (e.g. "from frontend.pages import ..."). Streamlit does not add the
# project root to sys.path automatically, so without PYTHONPATH those
# imports raise ModuleNotFoundError. Setting it here fixes the issue
# for both `docker-compose up` and any direct `docker run`.
ENV PYTHONPATH=/app

RUN useradd -m -u 1000 aegiscare && chown -R aegiscare:aegiscare /app
USER aegiscare

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
