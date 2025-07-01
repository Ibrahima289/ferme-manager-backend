ferme-manager-backend/
├── Dockerfile
├── docker-compose.prod.yml
├── .do/app.yaml
├── loki-config.yaml
├── promtail-config.yaml
├── alertmanager-config.yaml
├── prometheus.yml
├── alert.rules
├── package.json
├── app.js
├── server.js
├── config/config.js
├── middleware/auth.js
├── models/index.js
├── models/user.js
├── models/stock.js
├── models/finance.js
├── models/alerte.js
├── routes/auth.js
├── routes/stocks.js
├── routes/finances.js
└── routes/alertes.js
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
version: '3.8'
services:
  api:
    build: .
    restart: always
    ports:
      - "3000:3000"
    environment:
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASS: ${DB_PASS}
      DB_HOST: ${DB_HOST}
      JWT_SECRET: ${JWT_SECRET}

  loki:
    image: grafana/loki:3.0.0
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/mnt/config/loki-config.yaml
    command: -config.file=/mnt/config/loki-config.yaml

  promtail:
    image: grafana/promtail:3.0.0
    volumes:
      - ./promtail-config.yaml:/mnt/config/promtail-config.yaml
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - loki
    command: -config.file=/mnt/config/promtail-config.yaml

  alertmanager:
    image: prom/alertmanager:v0.23.0
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager-config.yaml:/config/alertmanager.yml
      - alertmanager-data:/data

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alert.rules:/etc/prometheus/alert.rules:ro
    depends_on:
      - api
      - alertmanager

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - loki

volumes:
  alertmanager-data:
  grafana_data:
