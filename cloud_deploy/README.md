# 🅿️ Free Parking Bot - Cloud Deployment

This is the cloud deployment configuration for the Free Parking Bot, suitable for various cloud platforms including AWS, Google Cloud, Heroku, and others.

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Bot token from @BotFather

#### Quick Start
```bash
# Create .env file
echo "BOT_TOKEN=your_bot_token_here" > .env

# Build and run
docker-compose up -d

# Check status
docker-compose ps
```

#### Environment Variables
- `BOT_TOKEN`: Your bot token from @BotFather
- `DB_PATH`: Path to SQLite database (default: `/app/data/parking.db`)

### 2. Heroku Deployment

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Setup
```bash
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set BOT_TOKEN=your_bot_token_here

# Deploy
git add .
git commit -m "Deploy parking bot"
git push heroku main

# Initialize database
heroku run python osm_fetcher.py
```

#### Procfile
```
web: python main.py
```

### 3. AWS/GCP Deployment

#### Using Kubernetes
```bash
# Apply configuration
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=parking-bot
```

#### Using ECS/Fargate
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker build -t parking-bot .
docker push parking-bot

# Deploy to ECS
aws ecs create-service --service-name parking-bot --task-definition parking-bot-task --desired-count 1
```

## Database Setup

### First Time Setup
```bash
# For Docker
docker-compose exec parking-bot python osm_fetcher.py

# For Heroku
heroku run python osm_fetcher.py

# For direct Python
python osm_fetcher.py
```

### Database Migration
The SQLite database will be automatically created on first run. For cloud deployments, ensure the database directory has write permissions.

## Monitoring

### Logs
```bash
# Docker
docker-compose logs -f parking-bot

# Heroku
heroku logs --tail

# Kubernetes
kubectl logs -f deployment/parking-bot
```

### Health Checks
The container includes health checks that can be monitored through your cloud provider's dashboard.

## Scaling

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use a shared database (recommend PostgreSQL for production)
- Implement Redis for session management if needed

### Vertical Scaling
- Increase CPU/memory allocation based on load
- Monitor database performance and consider indexing

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram bot token | Yes | - |
| `DB_PATH` | Database file path | No | `parking.db` |

## Security Considerations

1. **Bot Token**: Never commit to version control, use environment variables
2. **Database**: Store in persistent volume, not container ephemeral storage
3. **Network**: Use private networking where possible
4. **Updates**: Regularly update base images and dependencies

## Troubleshooting

### Common Issues
- **Bot not responding**: Check `BOT_TOKEN` environment variable
- **Database errors**: Ensure database directory is writable
- **Memory issues**: Monitor resource usage and scale accordingly

### Debug Commands
```bash
# Check container logs
docker-compose logs parking-bot

# Test database connection
python -c "import sqlite3; print(sqlite3.connect('parking.db'))"

# Test bot token
python -c "import os; print('BOT_TOKEN:', os.environ.get('BOT_TOKEN', 'Not set'))"
```