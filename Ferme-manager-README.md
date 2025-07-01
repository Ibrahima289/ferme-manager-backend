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
