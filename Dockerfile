FROM node:20-alpine AS web-build

WORKDIR /src

COPY package.json package-lock.json /src/
RUN npm ci

COPY . /src/
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY api/app /app/app
COPY --from=web-build /src/dist /app/web/dist

EXPOSE 8800

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8800", "--proxy-headers", "--forwarded-allow-ips", "*"]
