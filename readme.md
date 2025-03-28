# EC2 Automated Snapshot Management System

This project implements an automated backup management system for Amazon EC2 instances, designed to enhance data durability and operational resilience. Utilizing AWS services such as EC2, Lambda, SNS, and CloudWatch, the system provides a robust solution for creating, managing, and monitoring EC2 snapshots, ensuring business continuity and compliance with data protection policies.



# Purpose

The primary purpose of this project is to automate the creation and deletion of snapshots for EC2 instances tagged with `backup:true`. This ensures that critical data on EC2 volumes is backed up at regular intervals without manual intervention, reducing the risk of data loss due to failures or other disruptions.

This project has its importance in many ways like our data of EC2 instance is always protected and backed up, it reduces manual efforts to backup data, helps manage costs by deleting old backups when new backups are done, and supports compliance with regulatory requirements for data retention by ensuring that backups are performed regularly and reliably.


## Features
- **Automated Snapshots**: Automatically manage snapshots based on specific tags.
- **Cost Efficiency**: Deletes old snapshots upon creation of new ones to manage costs effectively.
- **Reliability**: Ensures that snapshots are taken reliably and consistently without human error.
- **Notification System**: Uses Amazon SNS for success and failure notifications.
- **Monitoring**: Utilizes AWS CloudWatch for monitoring snapshot count and size with custom metrics.

## EC2 Instance

EC2 instances are tagged with backup:true so that lambda function could identify which instances to make backup of.


## Lambda Function

The Lambda function is the core component that handles the automation of snapshot creation and deletion. Here is a brief overview of how the Lambda function operates:

- Queries EC2 instances with a specific tag.
- Manages snapshots for each volume attached to these instances.
- Tags new snapshots and deletes old ones based on predefined criteria.
- Publishes custom metrics to CloudWatch and sends notifications via SNS.
## EventBridge Configuration

EventBridge is configured to trigger this Lambda function weekly using the following cron expression:

cron(0 6 ? * MON *)

This schedule triggers the function every Monday at 6:00 AM UTC.

##  SNS Configuration

Amazon SNS is used for sending notifications about the success or failure of the snapshot operations:

-   **Topic Creation**: A standard SNS topic is created.
    
-   **Subscription**: An email subscription is set up to alert an administrator.



## CloudWatch

In this project, we use CloudWatch to set alerts for the snapshot count and total size. We have utilized the namespace `EC2/Snapshots` in the Lambda function. Within the CloudWatch service, under metrics, you can find this custom namespace `EC2/Snapshots`.

Once it is confirmed that the metrics are being collected, alarms will be created to notify about certain thresholds. In the alarm section of CloudWatch, an alarm for the custom namespace `EC2/Snapshots` is created using the `SnapshotCount` metric, and the desired level is set. In this setup, we have configured the threshold to alert when no snapshots have been created by setting the level to 0, ensuring that notifications are sent for this alarm.

Similarly, an alarm for the `TotalSnapshotSize` is also set up to monitor significant changes in storage used by snapshots. This comprehensive monitoring setup ensures that we are immediately alerted to any operational anomalies in our snapshot management process.

# Permissions
Permissions are managed through IAM policies that allow the Lambda function to interact with EC2, SNS, and CloudWatch.
