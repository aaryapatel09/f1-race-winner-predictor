import os
import subprocess
import logging
import json
from typing import Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoringSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.prometheus_dir = self.base_dir / 'prometheus'
        self.grafana_dir = self.base_dir / 'grafana'
        self.alertmanager_dir = self.base_dir / 'alertmanager'

    def create_directories(self):
        """Create necessary directories for monitoring"""
        try:
            # Create Prometheus directories
            (self.prometheus_dir / 'rules').mkdir(parents=True, exist_ok=True)
            (self.prometheus_dir / 'data').mkdir(parents=True, exist_ok=True)

            # Create Grafana directories
            (self.grafana_dir / 'provisioning' / 'dashboards').mkdir(parents=True, exist_ok=True)
            (self.grafana_dir / 'provisioning' / 'datasources').mkdir(parents=True, exist_ok=True)
            (self.grafana_dir / 'data').mkdir(parents=True, exist_ok=True)

            # Create Alertmanager directories
            (self.alertmanager_dir / 'data').mkdir(parents=True, exist_ok=True)

            logger.info("Created monitoring directories")
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
            raise

    def setup_prometheus(self):
        """Set up Prometheus configuration"""
        try:
            # Create Prometheus configuration
            prometheus_config = {
                'global': {
                    'scrape_interval': '15s',
                    'evaluation_interval': '15s'
                },
                'scrape_configs': [
                    {
                        'job_name': 'prometheus',
                        'static_configs': [
                            {'targets': ['localhost:9090']}
                        ]
                    },
                    {
                        'job_name': 'node-exporter',
                        'static_configs': [
                            {'targets': ['node-exporter:9100']}
                        ]
                    },
                    {
                        'job_name': 'f1-predictor',
                        'static_configs': [
                            {'targets': ['web:80']}
                        ],
                        'metrics_path': '/metrics'
                    }
                ],
                'rule_files': [
                    'rules/*.yml'
                ],
                'alerting': {
                    'alertmanagers': [
                        {
                            'static_configs': [
                                {'targets': ['alertmanager:9093']}
                            ]
                        }
                    ]
                }
            }

            with open(self.prometheus_dir / 'prometheus.yml', 'w') as f:
                json.dump(prometheus_config, f, indent=2)

            logger.info("Created Prometheus configuration")
        except Exception as e:
            logger.error(f"Error setting up Prometheus: {str(e)}")
            raise

    def setup_alertmanager(self):
        """Set up Alertmanager configuration"""
        try:
            # Create Alertmanager configuration
            alertmanager_config = {
                'global': {
                    'resolve_timeout': '5m'
                },
                'route': {
                    'group_by': ['alertname', 'cluster', 'service'],
                    'group_wait': '30s',
                    'group_interval': '5m',
                    'repeat_interval': '4h',
                    'receiver': 'email-notifications'
                },
                'receivers': [
                    {
                        'name': 'email-notifications',
                        'email_configs': [
                            {
                                'to': os.getenv('ALERT_EMAIL', 'admin@example.com'),
                                'from': os.getenv('SMTP_FROM', 'alerts@example.com'),
                                'smarthost': os.getenv('SMTP_HOST', 'smtp.example.com:587'),
                                'auth_username': os.getenv('SMTP_USER', ''),
                                'auth_password': os.getenv('SMTP_PASS', ''),
                                'auth_secret': os.getenv('SMTP_SECRET', ''),
                                'require_tls': True
                            }
                        ]
                    }
                ]
            }

            with open(self.alertmanager_dir / 'alertmanager.yml', 'w') as f:
                json.dump(alertmanager_config, f, indent=2)

            logger.info("Created Alertmanager configuration")
        except Exception as e:
            logger.error(f"Error setting up Alertmanager: {str(e)}")
            raise

    def setup_grafana(self):
        """Set up Grafana configuration"""
        try:
            # Create Grafana datasource configuration
            datasource_config = {
                'apiVersion': 1,
                'datasources': [
                    {
                        'name': 'Prometheus',
                        'type': 'prometheus',
                        'access': 'proxy',
                        'url': 'http://prometheus:9090',
                        'isDefault': True,
                        'editable': False,
                        'version': 1,
                        'jsonData': {
                            'timeInterval': '15s',
                            'queryTimeout': '30s',
                            'httpMethod': 'GET'
                        }
                    }
                ]
            }

            with open(self.grafana_dir / 'provisioning' / 'datasources' / 'prometheus.yml', 'w') as f:
                json.dump(datasource_config, f, indent=2)

            logger.info("Created Grafana datasource configuration")
        except Exception as e:
            logger.error(f"Error setting up Grafana: {str(e)}")
            raise

    def setup_permissions(self):
        """Set up directory permissions"""
        try:
            # Set permissions for Prometheus
            subprocess.run(['chmod', '-R', '777', str(self.prometheus_dir / 'data')], check=True)

            # Set permissions for Grafana
            subprocess.run(['chmod', '-R', '777', str(self.grafana_dir / 'data')], check=True)

            # Set permissions for Alertmanager
            subprocess.run(['chmod', '-R', '777', str(self.alertmanager_dir / 'data')], check=True)

            logger.info("Set directory permissions")
        except Exception as e:
            logger.error(f"Error setting permissions: {str(e)}")
            raise

    def setup(self):
        """Set up the complete monitoring environment"""
        try:
            logger.info("Starting monitoring setup...")
            self.create_directories()
            self.setup_prometheus()
            self.setup_alertmanager()
            self.setup_grafana()
            self.setup_permissions()
            logger.info("Monitoring setup completed successfully")
        except Exception as e:
            logger.error(f"Error in monitoring setup: {str(e)}")
            raise

if __name__ == "__main__":
    setup = MonitoringSetup()
    setup.setup() 