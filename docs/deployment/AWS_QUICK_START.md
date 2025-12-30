# Quick Start: AWS Deployment

This is a **quick reference** for deploying the Agentic Platform web UI on AWS. For detailed instructions, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md).

## 🚀 Fastest Deployment Options

### Option 1: EC2 (Easiest - 10 minutes)

**Best for:** Testing, development, small-scale production

```bash
# 1. Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name your-key \
    --security-groups default

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Quick setup
sudo apt update && sudo apt install -y python3.11 python3-pip git nginx
git clone https://github.com/yourusername/agentic-platform.git
cd agentic-platform
pip3 install -r requirements-minimal.txt

# 4. Start web server
export OPENAI_API_KEY=sk-...
python3 web_server.py

# Access at: http://your-instance-ip:8000
```

**Cost:** ~$30/month (t3.medium on-demand)

---

### Option 2: ECS Fargate (Production - 30 minutes)

**Best for:** Production, auto-scaling, high availability

```bash
# 1. Build and push Docker image
docker build -t agentic-platform .
aws ecr create-repository --repository-name agentic-platform
aws ecr get-login-password | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker tag agentic-platform:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/agentic-platform:latest
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/agentic-platform:latest

# 2. Create ECS cluster and task
aws ecs create-cluster --cluster-name agentic-platform
aws ecs register-task-definition --cli-input-json file://ecs-task-def.json

# 3. Create load balancer and service
aws elbv2 create-load-balancer --name agentic-alb --subnets subnet-1 subnet-2
aws ecs create-service --cluster agentic-platform --service-name web --task-definition agentic-platform --desired-count 2 --launch-type FARGATE

# Access at: http://your-alb-dns.amazonaws.com
```

**Cost:** ~$35/month (1 vCPU, 2GB RAM, 24/7)

---

### Option 3: One-Click Deploy (CloudFormation)

**Best for:** Automated infrastructure setup

Save this as `cloudformation.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Agentic Platform Web UI Deployment

Parameters:
  OpenAIApiKey:
    Type: String
    NoEcho: true
    Description: Your OpenAI API key

  InstanceType:
    Type: String
    Default: t3.medium
    Description: EC2 instance type

Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Agentic Platform Security Group
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: ami-0c55b159cbfafe1f0  # Ubuntu 22.04
      SecurityGroupIds:
        - !Ref SecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          set -e

          # Update system
          apt-get update
          apt-get install -y python3.11 python3-pip git nginx

          # Clone repository
          cd /home/ubuntu
          git clone https://github.com/yourusername/agentic-platform.git
          cd agentic-platform

          # Install dependencies
          pip3 install -r requirements-minimal.txt

          # Create systemd service
          cat > /etc/systemd/system/agentic-web.service << EOF
          [Unit]
          Description=Agentic Platform Web UI
          After=network.target

          [Service]
          Type=simple
          User=ubuntu
          WorkingDirectory=/home/ubuntu/agentic-platform
          Environment="OPENAI_API_KEY=${OpenAIApiKey}"
          ExecStart=/usr/bin/python3 web_server.py
          Restart=always

          [Install]
          WantedBy=multi-user.target
          EOF

          # Configure Nginx
          cat > /etc/nginx/sites-available/default << 'EOF'
          server {
            listen 80;
            location / {
              proxy_pass http://127.0.0.1:8000;
              proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection "upgrade";
              proxy_set_header Host $host;
            }
            location /ws {
              proxy_pass http://127.0.0.1:8000;
              proxy_http_version 1.1;
              proxy_set_header Upgrade $http_upgrade;
              proxy_set_header Connection "upgrade";
              proxy_read_timeout 3600s;
            }
          }
          EOF

          # Start services
          systemctl daemon-reload
          systemctl enable agentic-web
          systemctl start agentic-web
          systemctl restart nginx

Outputs:
  WebUIURL:
    Description: Web UI URL
    Value: !Sub 'http://${EC2Instance.PublicDnsName}'
```

Deploy with:

```bash
aws cloudformation create-stack \
    --stack-name agentic-platform \
    --template-body file://cloudformation.yaml \
    --parameters ParameterKey=OpenAIApiKey,ParameterValue=sk-...

# Get URL
aws cloudformation describe-stacks \
    --stack-name agentic-platform \
    --query 'Stacks[0].Outputs[?OutputKey==`WebUIURL`].OutputValue' \
    --output text
```

**Cost:** ~$30/month (t3.medium)

---

## 🎯 Which Option Should You Choose?

| Scenario | Best Option | Why |
|----------|-------------|-----|
| Quick testing | EC2 (Option 1) | Fast setup, easy debugging |
| Production app | ECS Fargate (Option 2) | Auto-scaling, high availability |
| Automated setup | CloudFormation (Option 3) | Reproducible infrastructure |
| Budget-conscious | EC2 Spot | Up to 90% cost savings |
| Serverless | Lambda + API Gateway | Pay per request only |

---

## 📊 Cost Comparison

### Running 24/7 for 1 Month:

| Service | Configuration | Cost |
|---------|--------------|------|
| **EC2 On-Demand** | t3.medium | $30.37 |
| **EC2 Spot** | t3.medium | ~$9.00 |
| **EC2 Reserved (1yr)** | t3.medium | $18.00 |
| **ECS Fargate** | 1 vCPU, 2GB | $35.42 |
| **Lambda** | 100k requests/day | ~$15.00 |

### Additional Costs:
- **Data Transfer:** $0.09/GB (first 10TB)
- **Load Balancer:** $16.20/month + $0.008/LCU-hour
- **CloudWatch Logs:** ~$5/month (10GB)
- **Secrets Manager:** $0.40/secret/month

---

## ⚡ Quick Commands Reference

### EC2 Management

```bash
# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Check web service status
sudo systemctl status agentic-web

# View logs
sudo journalctl -u agentic-web -f

# Restart service
sudo systemctl restart agentic-web

# Update code
cd /home/ubuntu/agentic-platform
git pull
sudo systemctl restart agentic-web
```

### ECS Management

```bash
# List services
aws ecs list-services --cluster agentic-platform

# Update service (after new image push)
aws ecs update-service --cluster agentic-platform --service web --force-new-deployment

# View logs
aws logs tail /ecs/agentic-platform --follow

# Scale service
aws ecs update-service --cluster agentic-platform --service web --desired-count 4
```

### Security Group Updates

```bash
# Allow your IP for SSH (replace YOUR_IP)
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_IP/32

# Allow HTTP/HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

---

## 🔒 Security Checklist

Before going to production:

- [ ] Use **AWS Secrets Manager** for API keys (not environment variables)
- [ ] Enable **HTTPS** with Let's Encrypt or AWS ACM
- [ ] Configure **Security Groups** to allow only necessary ports
- [ ] Enable **CloudWatch** logging and monitoring
- [ ] Set up **IAM roles** with least privilege
- [ ] Enable **VPC** for network isolation
- [ ] Configure **backup** strategy for persistent data
- [ ] Set up **CloudWatch Alarms** for errors and high usage
- [ ] Enable **AWS WAF** if using ALB (optional)
- [ ] Configure **rate limiting** to prevent abuse

---

## 🆘 Troubleshooting

### Web UI not accessible

```bash
# Check if service is running
sudo systemctl status agentic-web

# Check if port 8000 is listening
sudo netstat -tlnp | grep 8000

# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check security group
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### OpenAI API errors

```bash
# Test API key
export OPENAI_API_KEY=sk-...
python3 -c "
import openai
client = openai.OpenAI()
print(client.models.list())
"

# Check logs for errors
sudo journalctl -u agentic-web -n 100
```

### High costs

```bash
# Check current spending
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost

# Set up billing alert
aws cloudwatch put-metric-alarm \
    --alarm-name high-billing \
    --alarm-description "Alert when bill exceeds $100" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 21600 \
    --evaluation-periods 1 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold
```

---

## 📚 Next Steps

1. **SSL/HTTPS Setup:** See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md#step-7-setup-sslhttps-with-lets-encrypt)
2. **Custom Domain:** Configure Route 53 DNS
3. **Auto-Scaling:** Set up based on CPU/memory metrics
4. **CI/CD Pipeline:** GitHub Actions or AWS CodePipeline
5. **Monitoring:** CloudWatch dashboards and alarms
6. **Backup Strategy:** Automated S3 backups

---

## 📞 Support

- **AWS Issues:** [AWS Support](https://console.aws.amazon.com/support)
- **Platform Issues:** [GitHub Issues](https://github.com/yourusername/agentic-platform/issues)
- **Detailed Docs:** [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

**Built with ❤️ by the Agentic Platform Team**
