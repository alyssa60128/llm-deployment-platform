FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY services/control_plane/requirements.txt \
  services/control_plane/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
  && python -m pip install --no-cache-dir \
    -r services/control_plane/requirements.txt

COPY services services

EXPOSE 8080

CMD ["uvicorn", "services.control_plane.app.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]