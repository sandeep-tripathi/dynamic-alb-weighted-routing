import boto3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple

def get_instance_utilization(instance_id: str, cloudwatch: boto3.client) -> Tuple[float, float]:
    """Retrieve CPU and memory utilization metrics from CloudWatch."""
    cpu = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'cpu',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/EC2',
                        'MetricName': 'CPUUtilization',
                        'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}]
                    },
                    'Period': 300,
                    'Stat': 'Average'
                }
            }
        ]
    )['MetricDataResults'][0]['Values'][0]

    memory = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'memory',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'CWAgent',
                        'MetricName': 'MemoryUtilization',
                        'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}]
                    },
                    'Period': 300,
                    'Stat': 'Average'
                }
            }
        ]
    )['MetricDataResults'][0]['Values'][0]

    return cpu, memory

def calculate_combined_utilization(cpu: float, memory: float) -> float:
    """Calculate combined utilization factor from CPU and memory metrics."""
    return (cpu + memory) / 2

def update_target_group_weights(alb_arn: str, target_group_weights: Dict[str, float], elb: boto3.client) -> None:
    """Update target group weights for ALB."""
    for tg_arn, weight in target_group_weights.items():
        elb.modify_listener(
            ListenerArn=alb_arn,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'ForwardConfig': {
                        'TargetGroups': [
                            {
                                'TargetGroupArn': tg_arn,
                                'Weight': int(weight)
                            }
                        ]
                    }
                }
            ]
        )


def display_iteration_table(iteration: int, utilization_data: Dict[str, Tuple[float, float]], weights: Dict[str, float]) -> None:
    """
    Display the utilization and weights for each EC2 instance in a table format.
    """
    table_data = []
    for instance_id, (cpu, memory) in utilization_data.items():
        combined_utilization = calculate_combined_utilization(cpu, memory)
        weight = weights[instance_id]
        table_data.append([instance_id, 80, cpu, memory, combined_utilization, weight])

    df = pd.DataFrame(table_data, columns=[
        "Instance ID", "Port", "CPU Utilization (%)", "Memory Utilization (%)", 
        "Combined Utilization Factor", "Weight"
    ])
    df.sort_values(by="Weight", ascending=True, inplace=True)
    
    print(f"\nIteration {iteration}:")
    print(df.to_string(index=False, justify='center'))

    lowest_weight_instance = df.iloc[0]
    highest_weight_instance = df.iloc[-1]
    
    print(f"\nLowest Weight: {lowest_weight_instance['Weight']} (Instance: {lowest_weight_instance['Instance ID']})")
    print(f"Highest Weight: {highest_weight_instance['Weight']} (Instance: {highest_weight_instance['Instance ID']})")

    print("\nRouting Information")
    print("+---------------------+------+")
    print("| Instance ID         | Port |")
    print("+---------------------+------+")
    for instance_id in df["Instance ID"]:
        print(f"| {instance_id:<19} |  80  |")
    print("+---------------------+------+")
    
    print("\nTarget group weights updated and traffic routed successfully.")


def main() -> None:
    cloudwatch = boto3.client('cloudwatch')
    elb = boto3.client('elbv2')

    target_groups = {
        "i-1234567890abcdef0": "arn:aws:elasticloadbalancing:region:account-id:targetgroup/your-tg-1/abc123",
        "i-abcdef1234567890": "arn:aws:elasticloadbalancing:region:account-id:targetgroup/your-tg-2/def456",
        "i-0abcdef1234567890": "arn:aws:elasticloadbalancing:region:account-id:targetgroup/your-tg-3/ghi789",
    }

    alb_arn = 'arn:aws:elasticloadbalancing:region:account-id:listener/app/your-alb/abcd1234'

    for iteration in range(5):
        utilization_data = {}
        weights = {}

        for instance_id in target_groups.keys():
            cpu, memory = get_instance_utilization(instance_id, cloudwatch)
            combined_utilization = calculate_combined_utilization(cpu, memory)
            weight = 100 - combined_utilization  # Higher utilization means lower weight
            
            utilization_data[instance_id] = (cpu, memory)
            weights[instance_id] = weight
        
        update_target_group_weights(alb_arn, {target_groups[instance_id]: weight for instance_id, weight in weights.items()}, elb)
        display_iteration_table(iteration + 1, utilization_data, weights)

if __name__ == "__main__":
    main()
