# Stage 1: build the React dashboard
FROM node:20-alpine AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Flask app serving the API + built dashboard
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend /fe/dist ./frontend/dist
EXPOSE 5000
CMD gunicorn -b 0.0.0.0:${PORT:-5000} app:app
