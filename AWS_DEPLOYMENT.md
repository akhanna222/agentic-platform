# AWS Deployment Guide

This guide provides comprehensive instructions for deploying the Agentic Platform on AWS using various services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [EC2 Deployment](#ec2-deployment)
4. [ECS/Fargate Deployment](#ecsfargate-deployment)
5. [Lambda Deployment](#lambda-deployment)
6. [Cost Optimization](#cost-optimization)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- AWS CLI installed and configured
- Docker (for ECS/Lambda deployments)
- Python 3.11+ (for EC2 deployment)
- AWS account with appropriate permissions

### Install AWS CLI

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter default output format (json)
```

### Set Up Environment Variables

Create a `.env` file with your configuration:

```bash
OPENAI_API_KEY=your-openai-key
AWS_REGION=us-east-1
LOG_LEVEL=INFO
MAX_AGENT_STEPS=20
```

## Deployment Options

### Comparison Table

| Service | Best For | Cost | Scalability | Management |
|---------|----------|------|-------------|------------|
| EC2 | Long-running tasks | $$ | Manual | High |
| ECS Fargate | Container workloads | $$$ | Auto | Medium |
| Lambda | Event-driven tasks | $ | Auto | Low |

## EC2 Deployment

EC2 is ideal for long-running agent processes and development environments.

### Step 1: Launch EC2 Instance

```bash
# Create a security group
aws ec2 create-security-group \
    --group-name agentic-platform-sg \
    --description "Security group for Agentic Platform"

# Allow SSH access (adjust IP as needed)
aws ec2 authorize-security-group-ingress \
    --group-name agentic-platform-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Launch EC2 instance (Ubuntu 22.04)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-groups agentic-platform-sg \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=agentic-platform}]'
```

### Step 2: Connect and Setup

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Install pip and uv
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
pip install uv

# Install git
sudo apt install -y git
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/agentic-platform.git
cd agentic-platform

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies using uv
uv pip install -r requirements.txt

# Create config
cp config/config.example.toml config/config.toml

# Edit config with your API keys
nano config/config.toml
# Or set environment variable
export OPENAI_API_KEY="your-key"
```

### Step 4: Run as a Service

Create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/agentic-platform.service
```

Add the following content:

```ini
[Unit]
Description=Agentic Platform Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/agentic-platform
Environment="OPENAI_API_KEY=your-key"
ExecStart=/home/ubuntu/agentic-platform/venv/bin/python main.py --prompt "Your task here"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable agentic-platform
sudo systemctl start agentic-platform

# Check status
sudo systemctl status agentic-platform

# View logs
sudo journalctl -u agentic-platform -f
```

## ECS/Fargate Deployment

ECS Fargate provides serverless container deployment without managing servers.

### Step 1: Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name agentic-platform

# Get login credentials
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Docker Image

```bash
# Build Docker image
docker build -t agentic-platform .

# Tag image
docker tag agentic-platform:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-platform:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-platform:latest
```

### Step 3: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name agentic-platform-cluster
```

### Step 4: Create Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "agentic-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "agentic-platform",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentic-platform:latest",
      "essential": true,
      "environment": [
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/agentic-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register the task definition:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### Step 5: Create CloudWatch Log Group

```bash
aws logs create-log-group --log-group-name /ecs/agentic-platform
```

### Step 6: Store Secrets in AWS Secrets Manager

```bash
# Store OpenAI API key
aws secretsmanager create-secret \
    --name openai-api-key \
    --secret-string "your-openai-api-key"
```

### Step 7: Run Task

```bash
# Run task on Fargate
aws ecs run-task \
    --cluster agentic-platform-cluster \
    --launch-type FARGATE \
    --task-definition agentic-platform \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

### Step 8: Create Service (Optional - for long-running tasks)

```bash
aws ecs create-service \
    --cluster agentic-platform-cluster \
    --service-name agentic-platform-service \
    --task-definition agentic-platform \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

## Lambda Deployment

Lambda is ideal for event-driven, short-running tasks (max 15 minutes).

### Step 1: Create Lambda-Compatible Package

Create `lambda_handler.py`:

```python
import asyncio
import json
import os

from app.agent.platform import PlatformAgent


def lambda_handler(event, context):
    """
    AWS Lambda handler for Agentic Platform

    Event format:
    {
        "prompt": "Your task here",
        "max_steps": 10
    }
    """
    async def run_agent():
        prompt = event.get("prompt", "")
        max_steps = event.get("max_steps", 10)

        if not prompt:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No prompt provided"})
            }

        try:
            agent = await PlatformAgent.create(max_steps=max_steps)
            response = await agent.run(prompt)
            await agent.cleanup()

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "response": response,
                    "steps_used": agent.current_step
                })
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    # Run async function
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_agent())
```

### Step 2: Create Deployment Package

```bash
# Create deployment directory
mkdir lambda-package
cd lambda-package

# Copy application files
cp -r ../app .
cp ../lambda_handler.py .
cp ../requirements.txt .

# Install dependencies
pip install -r requirements.txt -t .

# Create zip file
zip -r ../lambda-function.zip .
cd ..
```

### Step 3: Create Lambda Function

```bash
# Create execution role first
aws iam create-role \
    --role-name lambda-agentic-platform \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }]
    }'

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name lambda-agentic-platform \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create Lambda function
aws lambda create-function \
    --function-name agentic-platform \
    --runtime python3.12 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-agentic-platform \
    --handler lambda_handler.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --timeout 900 \
    --memory-size 1024 \
    --environment Variables={OPENAI_API_KEY=your-key}
```

### Step 4: Test Lambda Function

```bash
# Create test event
cat > test-event.json << EOF
{
  "prompt": "What is the current time?",
  "max_steps": 5
}
EOF

# Invoke function
aws lambda invoke \
    --function-name agentic-platform \
    --payload file://test-event.json \
    response.json

# View response
cat response.json
```

### Step 5: Create API Gateway (Optional)

```bash
# Create REST API
aws apigatewayv2 create-api \
    --name agentic-platform-api \
    --protocol-type HTTP \
    --target arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:agentic-platform

# Add Lambda permission for API Gateway
aws lambda add-permission \
    --function-name agentic-platform \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com
```

## Cost Optimization

### EC2 Cost Optimization
- Use **Spot Instances** for non-critical workloads (up to 90% savings)
- Right-size instances based on actual usage
- Use **Reserved Instances** for long-term deployments (up to 72% savings)
- Enable **Auto Scaling** to scale down during low usage

```bash
# Request Spot Instance
aws ec2 request-spot-instances \
    --spot-price "0.05" \
    --instance-count 1 \
    --type "one-time" \
    --launch-specification file://spot-specification.json
```

### ECS Cost Optimization
- Use **Fargate Spot** for non-critical tasks (up to 70% savings)
- Right-size CPU and memory allocations
- Use **Auto Scaling** based on CloudWatch metrics
- Schedule tasks during off-peak hours

### Lambda Cost Optimization
- Optimize memory allocation (affects CPU)
- Minimize package size
- Use reserved concurrency only when needed
- Enable **Lambda Power Tuning** for optimization

### General AWS Cost Optimization
- Use **CloudWatch** to monitor resource usage
- Set up **billing alerts**
- Use **AWS Cost Explorer** to analyze spending
- Tag resources for cost allocation
- Use **S3** for storing large files instead of EBS

## Monitoring and Logging

### CloudWatch Metrics

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name agentic-platform \
    --dashboard-body file://dashboard.json
```

### CloudWatch Alarms

```bash
# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
    --alarm-name agentic-platform-errors \
    --alarm-description "Alert on high error rate" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold
```

### CloudWatch Logs Insights

Query logs using CloudWatch Logs Insights:

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

### X-Ray Tracing (Optional)

Enable AWS X-Ray for distributed tracing:

```bash
# Update Lambda function to use X-Ray
aws lambda update-function-configuration \
    --function-name agentic-platform \
    --tracing-config Mode=Active
```

## Security Best Practices

### IAM Policies
- Use **least privilege** principle
- Create separate IAM roles for different services
- Enable **MFA** for AWS accounts
- Rotate credentials regularly

### Secrets Management
- Store API keys in **AWS Secrets Manager** or **Parameter Store**
- Never hardcode credentials
- Use **IAM roles** instead of access keys when possible
- Enable encryption at rest

### Network Security
- Use **VPC** for network isolation
- Configure **Security Groups** properly
- Use **Private Subnets** for compute resources
- Enable **VPC Flow Logs**

### Example: Retrieve Secrets in Code

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('openai-api-key')
api_key = secrets['api_key']
```

## Troubleshooting

### Common Issues

#### EC2 Connection Issues
```bash
# Check instance status
aws ec2 describe-instance-status --instance-ids i-xxxxx

# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

#### ECS Task Not Starting
```bash
# Check task status
aws ecs describe-tasks \
    --cluster agentic-platform-cluster \
    --tasks task-id

# View logs
aws logs tail /ecs/agentic-platform --follow
```

#### Lambda Timeout
- Increase timeout limit (max 15 minutes)
- Optimize code for faster execution
- Consider using Step Functions for longer workflows

#### Out of Memory
- Increase memory allocation
- Optimize memory usage in code
- Monitor CloudWatch metrics

### Debug Logs

Enable debug logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in config.toml
[platform]
log_level = "DEBUG"
```

## Auto-Scaling Configuration

### EC2 Auto Scaling

```bash
# Create launch template
aws ec2 create-launch-template \
    --launch-template-name agentic-platform-template \
    --version-description v1 \
    --launch-template-data file://launch-template.json

# Create Auto Scaling group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name agentic-platform-asg \
    --launch-template LaunchTemplateName=agentic-platform-template \
    --min-size 1 \
    --max-size 5 \
    --desired-capacity 2 \
    --vpc-zone-identifier "subnet-xxxxx,subnet-yyyyy"
```

### ECS Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/agentic-platform-cluster/agentic-platform-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 1 \
    --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/agentic-platform-cluster/agentic-platform-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Backup and Disaster Recovery

### Workspace Backup to S3

```bash
# Create S3 bucket
aws s3 mb s3://agentic-platform-backups

# Sync workspace to S3
aws s3 sync /home/ubuntu/agentic-platform/workspace s3://agentic-platform-backups/workspace

# Create cron job for automatic backups
(crontab -l 2>/dev/null; echo "0 2 * * * aws s3 sync /home/ubuntu/agentic-platform/workspace s3://agentic-platform-backups/workspace") | crontab -
```

### Snapshot EC2 Volumes

```bash
# Create snapshot
aws ec2 create-snapshot \
    --volume-id vol-xxxxx \
    --description "Agentic Platform backup $(date +%Y-%m-%d)"
```

## Estimated Costs

### EC2 (t3.medium, us-east-1)
- On-Demand: ~$30/month
- Reserved (1 year): ~$18/month
- Spot: ~$9/month

### ECS Fargate (1 vCPU, 2GB RAM)
- Running 24/7: ~$35/month
- Running 8 hours/day: ~$12/month

### Lambda
- 1M requests, 512MB, 30s avg: ~$10/month
- Free tier: 1M requests/month

### Additional Costs
- Data transfer: ~$5-20/month
- CloudWatch Logs: ~$5/month
- Secrets Manager: $0.40/secret/month

## Next Steps

1. Choose your deployment method based on requirements
2. Set up monitoring and alerting
3. Configure auto-scaling if needed
4. Implement backup strategy
5. Set up CI/CD pipeline for automated deployments
6. Review and optimize costs monthly

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## Support

For AWS-specific issues:
- Check AWS Service Health Dashboard
- Contact AWS Support
- Visit AWS Forums

For platform issues:
- Open GitHub issue
- Check platform documentation
- Review troubleshooting section
