import boto3
import unittest
from moto import mock_elbv2, mock_cloudwatch
from alb_weighted_routing import update_target_group_weights, get_instance_utilization

class TestAlbWeightedRouting(unittest.TestCase):

    @mock_elbv2
    @mock_cloudwatch
    def setUp(self):
        """Set up mocked AWS services."""
        self.elb_client = boto3.client('elbv2', region_name='eu-central-1')
        self.cloudwatch_client = boto3.client('cloudwatch', region_name='eu-central-1')
        
        # Create a mocked ALB
        self.lb = self.elb_client.create_load_balancer(
            Name='my-load-balancer',
            Subnets=['subnet-12345'],
            SecurityGroups=['sg-12345'],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )

        # Create mocked target groups
        self.tg1 = self.elb_client.create_target_group(
            Name='my-target-group-1',
            Protocol='HTTP',
            Port=80,
            VpcId='vpc-12345'
        )

        self.tg2 = self.elb_client.create_target_group(
            Name='my-target-group-2',
            Protocol='HTTP',
            Port=80,
            VpcId='vpc-12345'
        )

        self.listener = self.elb_client.create_listener(
            LoadBalancerArn=self.lb['LoadBalancers'][0]['LoadBalancerArn'],
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': self.tg1['TargetGroups'][0]['TargetGroupArn'],
                    'ForwardConfig': {
                        'TargetGroups': [
                            {
                                'TargetGroupArn': self.tg1['TargetGroups'][0]['TargetGroupArn'],
                                'Weight': 1
                            }
                        ],
                    }
                }
            ]
        )

    def test_update_target_group_weights(self):
        """Test updating target group weights."""
        alb_arn = self.listener['Listeners'][0]['ListenerArn']
        target_group_arns = {
            'i-1234567890abcdef0': self.tg1['TargetGroups'][0]['TargetGroupArn'],
            'i-abcdef1234567890': self.tg2['TargetGroups'][0]['TargetGroupArn']
        }
        weights = {
            'i-1234567890abcdef0': 80,
            'i-abcdef1234567890': 20
        }

        # Call the function to update target group weights
        update_target_group_weights(alb_arn, target_group_arns, self.elb_client)

        # Verify that the target group weights are updated correctly
        updated_listener = self.elb_client.describe_listeners(ListenerArns=[alb_arn])
        forwarded_target_groups = updated_listener['Listeners'][0]['DefaultActions'][0]['ForwardConfig']['TargetGroups']
        
        for tg in forwarded_target_groups:
            arn = tg['TargetGroupArn']
            weight = tg['Weight']
            self.assertEqual(weights[target_group_arns[arn]], weight)

    @mock_cloudwatch
    def test_get_instance_utilization(self):
        """Test retrieving instance utilization metrics from CloudWatch."""
        instance_id = 'i-1234567890abcdef0'
        self.cloudwatch_client.put_metric_data(
            Namespace='AWS/EC2',
            MetricData=[
                {
                    'MetricName': 'CPUUtilization',
                    'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
                    'Value': 60.0,
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'MemoryUtilization',
                    'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
                    'Value': 70.0,
                    'Unit': 'Percent'
                }
            ]
        )

        # Call the function to get utilization
        cpu, memory = get_instance_utilization(instance_id, self.cloudwatch_client)

        # Verify the returned CPU and Memory utilization
        self.assertEqual(cpu, 60.0)
        self.assertEqual(memory, 70.0)

if __name__ == '__main__':
    unittest.main()
