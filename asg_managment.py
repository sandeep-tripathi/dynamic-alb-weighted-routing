import boto3
from typing import Any, Dict

def create_asg(asg_name: str, launch_config_name: str, min_size: int, max_size: int) -> None:
    """Create an Auto Scaling Group."""
    client = boto3.client('autoscaling')
    client.create_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchConfigurationName=launch_config_name,
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=min_size,
        AvailabilityZones=['eu-central-1a']
    )
