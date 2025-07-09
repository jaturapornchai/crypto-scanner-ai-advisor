
```bash
# Clean build with Pattern Detector dependencies
docker buildx build --platform linux/amd64 --no-cache -t jaturapornchai/getspot:latest --push .
```

### Deploy Commands (Updated for Pattern Detector Fix)
```bash
ssh root@178.128.55.234
# password : 19682511

cd /mnt/volume_sgp1_02/jeadbot

# Stop existing container
sudo docker-compose stop

# Pull latest fixed image  
sudo docker pull jaturapornchai/getspot:latest

# Complete cleanup to avoid cached issues
sudo docker-compose down
sudo docker system prune -f

# Test the container before full deployment
sudo docker run --rm -it jaturapornchai/getspot:latest python test_docker.py

# Start with environment variables
sudo docker-compose up -d

# Monitor logs
sudo docker logs -f getspot
```
