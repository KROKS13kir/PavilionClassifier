# Этап 1: сборка фронта
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Этап 2: nginx + фронт
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY /nginx.conf /etc/nginx/nginx.conf