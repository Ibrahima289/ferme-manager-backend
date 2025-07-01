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
  name: ferme-manager-api
services:
- name: api
  git:
    repo: Ibrahima289/ferme-manager-backend
    branch: main
  dockerfile_path: Dockerfile
  envs:
    - key: DB_NAME
      value: ${DB_NAME}
      type: SECRET
    - key: DB_USER
      value: ${DB_USER}
      type: SECRET
    - key: DB_PASS
      value: ${DB_PASS}
      type: SECRET
    - key: DB_HOST
      value: ${DB_HOST}
      type: SECRET
    - key: JWT_SECRET
      value: ${JWT_SECRET}
      type: SECRET
  http_port: 3000
  instances:
    size: basic-xxs
    count: 1
  auto_deploy: true
auth_enabled: false
server:
  http_listen_port: 3100
common:
  path_prefix: /loki
schema_config:
  configs:
  - from: 2020-10-15
    store: boltdb-shipper
    object_store: filesystem
    schema: v11
    index:
      prefix: index_
      period: 168h
storage_config:
  boltdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks
    server:
  http_listen_port: 9080
positions:
  filename: /tmp/positions.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
  - job_name: containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_label_logging_jobname']
        action: keep
        regex: api_logs
      - source_labels: ['__meta_docker_container_label_logging_jobname']
        target_label: job
    pipeline_stages:
      - docker: {}
      - global:
  resolve_timeout: 5m
route:
  receiver: email
  group_by: ['alertname']
  repeat_interval: 4h
receivers:
  - name: email
    email_configs:
      - to: mon.email@domaine.com
        from: alert@mon-domaine.com
        smarthost: smtp.mondomaine.com:587
        auth_username: alert@mon-domaine.com
        auth_identity: alert@mon-domaine.com
        auth_password: motdepasseSMTP
        global:
  scrape_interval: 15s
evaluation_interval: 15s
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']
  - job_name: api
    metrics_path: /metrics
    static_configs:
      - targets: ['api:3000']
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
rule_files:
  - "/etc/prometheus/alert.rules"
  - groups:
- name: api-health
  rules:
    - alert: ApiDown
      expr: up{job="api"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "API Ferme Manager injoignable"
        description: "Aucune réponse détectée depuis plus de 2 minutes"
      {
  "name": "ferme-manager-backend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.2",
    "sequelize": "^6.31.1",
    "pg": "^8.11.1",
    "pg-hstore": "^2.3.4",
    "jsonwebtoken": "^9.0.0",
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "swagger-ui-express": "^4.7.2",
    "swagger-jsdoc": "^6.2.8"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "supertest": "^6.6.3"
  }

}
const express = require('express');
const cors = require('cors');
const { sequelize } = require('./models');
const authRoutes = require('./routes/auth');
const stockRoutes = require('./routes/stocks');
const financeRoutes = require('./routes/finances');
const alerteRoutes = require('./routes/alertes');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUI = require('swagger-ui-express');

const swaggerSpec = swaggerJsdoc({
  swaggerDefinition: {
    openapi: '3.0.0',
    info: { title: 'Ferme Manager API', version: '1.0.0' },
    components: {
      securitySchemes: {
        bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' }
      }
    },
    security: [{ bearerAuth: [] }]
  },
  apis: ['./routes/*.js']
});

const app = express();
app.use(cors());
app.use(express.json());
app.use('/api-docs', swaggerUI.serve, swaggerUI.setup(swaggerSpec));
app.use('/auth', authRoutes);
app.use('/stocks', stockRoutes);
app.use('/finances', financeRoutes);
app.use('/alertes', alerteRoutes);

(async () => {
  await sequelize.sync();
})();

module.exports = app;
const app = require('./app');
const config = require('./config/config');
app.listen(config.port, () =>
  console.log(`API running on port ${config.port}`)
);
require('dotenv').config();

module.exports = {
  port: process.env.PORT || 3000,
  jwtSecret: process.env.JWT_SECRET || 'change-me',
  db: {
    database: process.env.DB_NAME || 'ferme_db',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASS || 'postgres',
    host: process.env.DB_HOST || 'localhost',
    dialect: 'postgres'
  }
};
const jwt = require('jsonwebtoken');
const config = require('../config/config');

function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ msg: 'Token manquant' });
  jwt.verify(token, config.jwtSecret, (err, decoded) => {
    if (err) return res.status(401).json({ msg: 'Token invalide' });
    req.user = decoded;
    next();
  });
}

function authorize(roles = []) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role))
      return res.status(403).json({ msg: 'Accès refusé' });
    next();
  };
}

module.exports = { authenticate, authorize };
const { Sequelize } = require('sequelize');
const config = require('../config/config');

const sequelize = new Sequelize(config.db.database, config.db.user, config.db.password, config.db);

const models = {
  User: require('./user')(sequelize),
  Stock: require('./stock')(sequelize),
  Finance: require('./finance')(sequelize),
  Alerte: require('./alerte')(sequelize)
};

Object.values(models).forEach(m => m.associate && m.associate(models));
models.sequelize = sequelize;
models.Sequelize = Sequelize;

module.exports = models;
const { DataTypes, Model } = require('sequelize');
const bcrypt = require('bcryptjs');

module.exports = sequelize => {
  class User extends Model {
    validPassword(pw) {
      return bcrypt.compareSync(pw, this.password);
    }
  }
  User.init({
    username: { type: DataTypes.STRING, unique: true, allowNull: false },
    password: { type: DataTypes.STRING, allowNull: false },
    role: { type: DataTypes.ENUM('admin', 'gestionnaire'), defaultValue: 'gestionnaire' }
  }, { sequelize, modelName: 'user' });

  User.beforeCreate(async user => {
    user.password = await bcrypt.hash(user.password, 10);
  });

  return User;
};
const { DataTypes, Model } = require('sequelize');
module.exports = sequelize => {
  class Stock extends Model {}
  Stock.init({
    nom: DataTypes.STRING,
    qte: DataTypes.FLOAT
  }, { sequelize, modelName: 'stock' });
  return Stock;
};
const { DataTypes, Model } = require('sequelize');
module.exports = sequelize => {
  class Finance extends Model {}
  Finance.init({
    date: DataTypes.DATEONLY,
    type: DataTypes.ENUM('revenu', 'dépense'),
    montant: DataTypes.FLOAT,
    categorie: DataTypes.STRING
  }, { sequelize, modelName: 'finance' });
  return Finance;
};
const { DataTypes, Model } = require('sequelize');
module.exports = sequelize => {
  class Alerte extends Model {}
  Alerte.init({
    nom: DataTypes.STRING,
    date: DataTypes.DATEONLY
  }, { sequelize, modelName: 'alerte' });
  return Alerte;
};
const express = require('express');
const jwt = require('jsonwebtoken');
const { User } = require('../models');
const { authenticate, authorize } = require('../middleware/auth');
const config = require('../config/config');

const router = express.Router();

router.post('/register', authenticate, authorize(['admin']), async (req, res) => {
  const { username, password, role } = req.body;
  const user = await User.create({ username, password, role });
  res.json({ id: user.id, username: user.username, role: user.role });
});

router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = await User.findOne({ where: { username } });
  if (!user || !user.validPassword(password))
    return res.status(401).json({ msg: 'Identifiants incorrects' });
  const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, config.jwtSecret, { expiresIn: '8h' });
  res.json({ token, role: user.role });
});

module.exports = router;
const express = require('express');
const { Stock } = require('../models');
const { authenticate } = require('../middleware/auth');
const router = express.Router();

/**
 * @swagger
 * /stocks:
 *   get:
 *     summary: Liste des stocks
 */
router.get('/', authenticate, async (req, res) => {
  res.json(await Stock.findAll());
});

router.post('/', authenticate, async (req, res) => {
  const s = await Stock.create(req.body);
  res.status(201).json(s);
});

router.put('/:id', authenticate, async (req, res) => {
  const s = await Stock.findByPk(req.params.id);
  if (!s) return res.status(404).json({ msg: 'Introuvable' });
  await s.update(req.body);
  res.json(s);
});

router.delete('/:id', authenticate, async (req, res) => {
  const count = await Stock.destroy({ where: { id: req.params.id } });
  res.json(count ? { msg: 'Supprimé' } : { msg: 'Introuvable' });
});

module.exports = router;
const express = require('express');
const { Finance } = require('../models');
const { authenticate } = require('../middleware/auth');
const router = express.Router();

router.get('/', authenticate, async (req, res) => {
  const items = await Finance.findAll({ order: [['date', 'DESC']] });
  res.json(items);
});

router.post('/', authenticate, async (req, res) => {
  const f = await Finance.create(req.body);
  res.status(201).json(f);
});

router.put('/:id', authenticate, async (req, res) => {
  const f = await Finance.findByPk(req.params.id);
  if (!f) return res.status(404).json({ msg: 'Introuvable' });
  await f.update(req.body);
  res.json(f);
});

router.delete('/:id', authenticate, async (req, res) => {
  const count = await Finance.destroy({ where: { id: req.params.id } });
  res.json(count ? { msg: 'Supprimé' } : { msg: 'Introuvable' });
});

module.exports = router;
const express = require('express');
const { Alerte } = require('../models');
const { authenticate } = require('../middleware/auth');
const router = express.Router();

router.get('/', authenticate, async (req, res) => {
  const items = await Alerte.findAll({ order: [['date', 'ASC']] });
  res.json(items);
});

router.post('/', authenticate, async (req, res) => {
  const a = await Alerte.create(req.body);
  res.status(201).json(a);
});

router.put('/:id', authenticate, async (req, res) => {
  const a = await Alerte.findByPk(req.params.id);
  if (!a) return res.status(404).json({ msg: 'Introuvable' });
  await a.update(req.body);
  res.json(a);
});

router.delete('/:id', authenticate, async (req, res) => {
  const count = await Alerte.destroy({ where: { id: req.params.id } });
  res.json(count ? { msg: 'Supprimé' } : { msg: 'Introuvable' });
});

module.exports = router;
