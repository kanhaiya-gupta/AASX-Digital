#!/usr/bin/env python3
"""
AASX Digital Twin Analytics Framework - Deployment Script
Automates the Docker build, tag, push, and ECS deployment process.

Usage:
    python deploy_app.py

Requirements:
    - Docker installed and running
    - AWS CLI configured with appropriate permissions
    - ECR repository access
"""

import subprocess
import sys
import time
import json
from datetime import datetime

# Configuration
DOCKERFILE_PATH = "deployment/configs/docker/Dockerfile.app"
IMAGE_NAME = "aasx-digital-production"
ECR_REGISTRY = "642137768321.dkr.ecr.eu-central-1.amazonaws.com"
ECR_REPOSITORY = "aasx-digital-production"
ECS_CLUSTER = "aasx-digital-cluster"
ECS_SERVICE = "aasx-digital-service"
AWS_REGION = "eu-central-1"

def run_command(command, description, check=True):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout:
            print(f"✅ {description} completed successfully")
            if len(result.stdout) < 500:  # Only print short outputs
                print(f"Output: {result.stdout.strip()}")
        
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        sys.exit(1)

def check_prerequisites():
    """Check if required tools are available."""
    print("🔍 Checking prerequisites...")
    
    # Check Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not installed or not running")
        sys.exit(1)
    
    # Check AWS CLI
    try:
        subprocess.run(["aws", "--version"], check=True, capture_output=True)
        print("✅ AWS CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ AWS CLI is not installed or not configured")
        sys.exit(1)

def login_to_ecr():
    """Login to AWS ECR."""
    command = f"aws ecr get-login-password --region {AWS_REGION} | docker login --username AWS --password-stdin {ECR_REGISTRY}"
    run_command(command, "Logging in to AWS ECR")

def build_docker_image():
    """Build the Docker image with --no-cache."""
    command = f"docker build --no-cache -f {DOCKERFILE_PATH} -t {IMAGE_NAME} ."
    run_command(command, "Building Docker image with --no-cache")

def tag_docker_image():
    """Tag the Docker image for ECR."""
    command = f"docker tag {IMAGE_NAME}:latest {ECR_REGISTRY}/{ECR_REPOSITORY}:latest"
    run_command(command, "Tagging Docker image for ECR")

def push_to_ecr():
    """Push the Docker image to ECR."""
    command = f"docker push {ECR_REGISTRY}/{ECR_REPOSITORY}:latest"
    run_command(command, "Pushing Docker image to ECR")

def deploy_to_ecs():
    """Deploy the updated image to ECS."""
    command = f"aws ecs update-service --cluster {ECS_CLUSTER} --service {ECS_SERVICE} --force-new-deployment --region {AWS_REGION}"
    run_command(command, "Deploying to ECS")

def wait_for_deployment():
    """Wait for ECS deployment to complete."""
    print("\n⏳ Waiting for ECS deployment to complete...")
    print("This may take 5-10 minutes...")
    
    max_attempts = 30  # 30 attempts * 20 seconds = 10 minutes
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Check deployment status
            command = f"aws ecs describe-services --cluster {ECS_CLUSTER} --services {ECS_SERVICE} --region {AWS_REGION} --query 'services[0].deployments[0].{{Status:status,RolloutState:rolloutState,RunningCount:runningCount,DesiredCount:desiredCount}}'"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                deployment_info = json.loads(result.stdout.strip())
                status = deployment_info.get('Status', 'UNKNOWN')
                rollout_state = deployment_info.get('RolloutState', 'UNKNOWN')
                running_count = deployment_info.get('RunningCount', 0)
                desired_count = deployment_info.get('DesiredCount', 0)
                
                print(f"Status: {status}, Rollout: {rollout_state}, Running: {running_count}/{desired_count}")
                
                # Check if deployment is complete
                if (status == 'PRIMARY' and 
                    rollout_state == 'COMPLETED' and 
                    running_count == desired_count and 
                    running_count > 0):
                    print("✅ Deployment completed successfully!")
                    return True
                elif rollout_state == 'FAILED':
                    print("❌ Deployment failed!")
                    return False
                    
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Error parsing deployment status: {e}")
        
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts} - Waiting 20 seconds...")
        time.sleep(20)
    
    print("⚠️ Deployment status check timed out. Please check manually.")
    return False

def test_deployment():
    """Test if the deployment is working."""
    print("\n🧪 Testing deployment...")
    
    # Test health endpoint
    command = "curl -s https://aasx-digital.de/health"
    result = run_command(command, "Testing health endpoint", check=False)
    
    if result.returncode == 0 and "healthy" in result.stdout.lower():
        print("✅ Health check passed!")
        return True
    else:
        print("❌ Health check failed!")
        print(f"Response: {result.stdout}")
        return False

def main():
    """Main deployment function."""
    print("🚀 AASX Digital Twin Analytics Framework - Deployment Script")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Image: {IMAGE_NAME}")
    print(f"ECR: {ECR_REGISTRY}/{ECR_REPOSITORY}")
    print(f"ECS: {ECS_CLUSTER}/{ECS_SERVICE}")
    print("=" * 60)
    
    # Step 1: Check prerequisites
    check_prerequisites()
    
    # Step 2: Login to ECR
    login_to_ecr()
    
    # Step 3: Build Docker image
    build_docker_image()
    
    # Step 4: Tag for ECR
    tag_docker_image()
    
    # Step 5: Push to ECR
    push_to_ecr()
    
    # Step 6: Deploy to ECS
    deploy_to_ecs()
    
    # Step 7: Wait for deployment
    if wait_for_deployment():
        # Step 8: Test deployment
        if test_deployment():
            print("\n🎉 Deployment completed successfully!")
            print("🌐 Your website is available at: https://aasx-digital.de")
        else:
            print("\n⚠️ Deployment completed but health check failed.")
            print("Please check the website manually.")
    else:
        print("\n⚠️ Deployment may still be in progress.")
        print("Please check the ECS console for status.")
    
    print("\n" + "=" * 60)
    print("Deployment script finished!")

if __name__ == "__main__":
    main()
