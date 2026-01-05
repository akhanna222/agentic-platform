# 🚀 AWS EC2 Quick Start Guide

Deploy the Agentic Platform on AWS EC2 in **2 commands**!

---

## ⚡ One-Command Deployment

After launching your EC2 instance, run these commands:

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/akhanna222/agentic-platform.git
cd agentic-platform
```

### **Step 2: Run the Auto-Deploy Script**
```bash
./aws-deploy.sh
```

**That's it!** 🎉

The script will automatically:
- ✅ Install all dependencies
- ✅ Set up virtual environment
- ✅ Kill any processes on ports 8000-8010
- ✅ Ask for your OpenAI API key
- ✅ Test the API connection
- ✅ Start the web server on port 8005

---

## 📋 What You Need

### **Before You Start:**

1. **AWS EC2 Instance**
   - Ubuntu 22.04 LTS recommended
   - At least t2.medium (2 vCPU, 4GB RAM)
   - Python 3.11+ installed (script will install if missing)

2. **OpenAI API Key**
   - Get one at: https://platform.openai.com/api-keys
   - Starts with `sk-proj-` or `sk-`

3. **Security Group Configuration**
   - Port 22 (SSH) - open to your IP
   - Port 8005 (Web UI) - open to `0.0.0.0/0` or your IP

---

## 🔧 Security Group Setup

### **Method 1: AWS Console**

1. Go to **EC2 Dashboard** → **Security Groups**
2. Select your instance's security group
3. Click **Edit inbound rules**
4. Click **Add rule**
5. Configure:
   - **Type**: Custom TCP
   - **Port**: 8005
   - **Source**: 0.0.0.0/0 (or "My IP" for security)
6. Click **Save rules**

### **Method 2: AWS CLI**

```bash
# Get your security group ID
SECURITY_GROUP_ID=$(aws ec2 describe-instances \
  --instance-ids $(curl -s http://169.254.169.254/latest/meta-data/instance-id) \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
  --output text)

# Add rule for port 8005
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 8005 \
  --cidr 0.0.0.0/0
```

---

## 🌐 Access Your Platform

After the script completes, access the platform at:

```
http://YOUR_EC2_PUBLIC_IP:8005
```

**Example:**
```
http://54.123.45.67:8005
```

The script will show you the exact URL!

---

## 🎯 What Happens During Deployment

The `aws-deploy.sh` script performs these steps:

1. **Check Python Version** - Ensures Python 3.11+ is available
2. **Create Virtual Environment** - Isolates Python dependencies
3. **Install Dependencies** - Installs all required packages
4. **Clean Up Ports** - Kills any processes on ports 8000-8010
5. **Configure API Key** - Prompts for OpenAI API key
6. **Test Connection** - Verifies OpenAI API works
7. **Get Public IP** - Finds your EC2 public IP
8. **Security Group Info** - Shows how to open port 8005
9. **Start Server** - Launches the web UI on port 8005

---

## 🔄 Restart the Server

If you need to restart later:

```bash
cd ~/agentic-platform

# Method 1: Using the script (recommended)
./aws-deploy.sh

# Method 2: Manual start
source venv/bin/activate
python3 web_server.py
```

---

## 🛠️ Troubleshooting

### **"Permission denied" when running script**
```bash
chmod +x aws-deploy.sh
./aws-deploy.sh
```

### **"Port already in use"**
The script automatically kills processes on ports 8000-8010.
If you still have issues:
```bash
sudo lsof -ti:8005 | xargs sudo kill -9
./aws-deploy.sh
```

### **"Connection refused" in browser**
1. Check security group has port 8005 open
2. Verify server is running: `ps aux | grep web_server`
3. Check server logs for errors

### **"OpenAI API error"**
1. Verify your API key is correct
2. Check you have API credits: https://platform.openai.com/usage
3. Ensure internet connectivity: `ping api.openai.com`

---

## 🚀 Next Steps

Once deployed:

1. **Select an Agent** - Choose from 6 specialized agents
2. **Build Something** - Try the Ship Agent to build a web app
3. **Analyze Data** - Use the Data Agent for visualizations
4. **Automate Tasks** - Use the Browser Agent for web scraping

---

## 📊 Instance Recommendations

| Use Case | Instance Type | Notes |
|----------|--------------|-------|
| Testing | t2.micro | Free tier eligible, basic usage |
| Development | t2.medium | Recommended for building apps |
| Production | t2.large | Better performance |
| Heavy Workloads | t3.xlarge | Data analysis, large apps |

---

## 💰 Cost Estimation

**t2.medium (recommended):**
- **On-Demand**: ~$0.0464/hour (~$33/month if running 24/7)
- **Spot Instance**: ~$0.014/hour (~$10/month if running 24/7)

**Tip:** Stop the instance when not in use to save costs!

```bash
# From your local machine
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID
```

---

## 🔐 Security Best Practices

1. **Use Elastic IP** - Get a static IP for your instance
2. **Restrict SSH** - Only allow SSH from your IP
3. **Restrict Web UI** - Only allow port 8005 from your IP
4. **Use HTTPS** - Set up SSL/TLS for production
5. **Keep Updated** - Regularly update packages
6. **Backup** - Create AMI snapshots regularly

---

## 📚 Additional Resources

- **Main Documentation**: See [README.md](README.md)
- **AWS EC2 Guide**: See [docs/deployment/AWS_DEPLOYMENT.md](docs/deployment/AWS_DEPLOYMENT.md)
- **Troubleshooting**: See [docs/guides/INSTALLATION.md](docs/guides/INSTALLATION.md)

---

## 🆘 Get Help

If you encounter issues:

1. Check server logs: `tail -f ~/agentic-platform/logs/*`
2. Check GitHub issues: https://github.com/akhanna222/agentic-platform/issues
3. Run the Test Agent to validate setup

---

**Happy Building!** 🚀

Your Agentic Platform is ready to build amazing things with AI!
