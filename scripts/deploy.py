import os
import subprocess
import logging
import json
from typing import Dict, Any
import boto3
from google.cloud import compute_v1
from google.cloud import aiplatform
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudDeployer:
    def __init__(self):
        self.cloud_provider = os.getenv('CLOUD_PROVIDER', 'gcp')
        self.project_id = os.getenv('PROJECT_ID')
        self.region = os.getenv('REGION')
        self.instance_type = os.getenv('INSTANCE_TYPE', 'n1-standard-2')
        
        if self.cloud_provider == 'aws':
            self.ec2 = boto3.client('ec2')
            self.ecr = boto3.client('ecr')
        elif self.cloud_provider == 'gcp':
            self.compute_client = compute_v1.InstancesClient()
            self.aiplatform_client = aiplatform.gapic.PredictionServiceClient()

    def build_docker_image(self):
        """Build Docker image"""
        try:
            logger.info("Building Docker image...")
            subprocess.run(['docker', 'build', '-t', 'f1-predictor', '.'], check=True)
            logger.info("Docker image built successfully")
        except Exception as e:
            logger.error(f"Error building Docker image: {str(e)}")
            raise

    def deploy_to_aws(self):
        """Deploy to AWS"""
        try:
            # Create ECR repository if it doesn't exist
            try:
                self.ecr.create_repository(repositoryName='f1-predictor')
            except self.ecr.exceptions.RepositoryAlreadyExistsException:
                pass

            # Get ECR login token
            token = self.ecr.get_authorization_token()
            endpoint = token['authorizationData'][0]['proxyEndpoint']
            token = token['authorizationData'][0]['authorizationToken']

            # Login to ECR
            subprocess.run([
                'docker', 'login',
                '-u', 'AWS',
                '-p', token,
                endpoint
            ], check=True)

            # Tag and push image
            subprocess.run([
                'docker', 'tag',
                'f1-predictor:latest',
                f'{endpoint}/f1-predictor:latest'
            ], check=True)
            subprocess.run([
                'docker', 'push',
                f'{endpoint}/f1-predictor:latest'
            ], check=True)

            # Create EC2 instance
            response = self.ec2.run_instances(
                ImageId='ami-0c7217cdde317cfec',  # Ubuntu 22.04 LTS
                InstanceType=self.instance_type,
                MinCount=1,
                MaxCount=1,
                UserData=open('scripts/aws_user_data.sh').read(),
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'f1-predictor'}]
                }]
            )

            instance_id = response['Instances'][0]['InstanceId']
            logger.info(f"Created EC2 instance: {instance_id}")

            return instance_id

        except Exception as e:
            logger.error(f"Error deploying to AWS: {str(e)}")
            raise

    def deploy_to_gcp(self):
        """Deploy to Google Cloud Platform"""
        try:
            # Initialize AI Platform
            aiplatform.init(project=self.project_id, location=self.region)

            # Create model
            model = aiplatform.Model.upload(
                display_name='f1-predictor',
                artifact_uri='gs://your-bucket/models',
                serving_container_image_uri='gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-13:latest'
            )

            # Deploy model
            endpoint = model.deploy(
                machine_type=self.instance_type,
                accelerator_type=None,
                accelerator_count=None,
                min_replica_count=1,
                max_replica_count=1
            )

            logger.info(f"Deployed model to endpoint: {endpoint.resource_name}")
            return endpoint.resource_name

        except Exception as e:
            logger.error(f"Error deploying to GCP: {str(e)}")
            raise

    def deploy(self):
        """Deploy the application"""
        try:
            # Build Docker image
            self.build_docker_image()

            # Deploy based on cloud provider
            if self.cloud_provider == 'aws':
                instance_id = self.deploy_to_aws()
                logger.info(f"Deployed to AWS EC2 instance: {instance_id}")
            elif self.cloud_provider == 'gcp':
                endpoint = self.deploy_to_gcp()
                logger.info(f"Deployed to GCP AI Platform endpoint: {endpoint}")
            else:
                raise ValueError(f"Unsupported cloud provider: {self.cloud_provider}")

            # Save deployment info
            deployment_info = {
                'cloud_provider': self.cloud_provider,
                'project_id': self.project_id,
                'region': self.region,
                'instance_type': self.instance_type,
                'timestamp': datetime.now().isoformat()
            }

            with open('deployment_info.json', 'w') as f:
                json.dump(deployment_info, f, indent=2)

        except Exception as e:
            logger.error(f"Error in deployment: {str(e)}")
            raise

if __name__ == "__main__":
    deployer = CloudDeployer()
    deployer.deploy() 