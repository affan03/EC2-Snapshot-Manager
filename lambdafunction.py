import boto3
from datetime import datetime, timezone
import boto3
from datetime import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    sns = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:region:account-id:topic-name' 

    try:
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:backup', 'Values': ['true']}])
        total_snapshot_size = 0 
        snapshot_count = 0  

        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                for volume in instance['BlockDeviceMappings']:
                    filters = [
                        {'Name': 'volume-id', 'Values': [volume['Ebs']['VolumeId']]},
                        {'Name': 'status', 'Values': ['completed']}
                    ]
                    snapshots = ec2.describe_snapshots(Filters=filters, OwnerIds=['self'])
                    snapshots = sorted(snapshots['Snapshots'], key=lambda x: x['StartTime'], reverse=True)

                    old_snapshot_id = snapshots[0]['SnapshotId'] if snapshots else None
                    old_snapshot_size = snapshots[0]['VolumeSize'] if snapshots else 0

                    new_snapshot = ec2.create_snapshot(VolumeId=volume['Ebs']['VolumeId'], Description='Automated backup')
                    ec2.create_tags(Resources=[new_snapshot['SnapshotId']],
                                    Tags=[{'Key': 'Timestamp', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                                          {'Key': 'Environment', 'Value': 'Production'}])
                    snapshot_count += 1
                    total_snapshot_size += new_snapshot['VolumeSize']

                    if old_snapshot_id:
                        ec2.delete_snapshot(SnapshotId=old_snapshot_id)
                        total_snapshot_size -= old_snapshot_size

        cloudwatch.put_metric_data(
            Namespace='EC2/Snapshots',
            MetricData=[
                {
                    'MetricName': 'SnapshotCount',
                    'Value': snapshot_count,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'TotalSnapshotSize',
                    'Value': total_snapshot_size,
                    'Unit': 'Gigabytes'
                }
            ]
        )


        sns.publish(
            TopicArn=sns_topic_arn,
            Message='Backup successfully created for all tagged EC2 instances, old snapshots removed.',
            Subject='Backup Success Notification'
        )
    except Exception as e:
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=f'Failed to create backup or clean old backups: {str(e)}',
            Subject='Backup Failure Notification'
        )
        raise e
