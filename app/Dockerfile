FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN  pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./scripts/entrypoint.sh

# Use bash to run the entrypoint so the script's shebang and bash-specific features behave as expected
ENTRYPOINT ["/bin/bash", "/app/scripts/entrypoint.sh"]