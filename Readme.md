# Shalomium Monitoring WebApp (VaultiGuard)

The project was divided into two parts

## Part 1

Ingest and Sample the Aggregator Sensor Readings via AWS IoT Core & Analytics This was completed and demonstrated on the AWS Web Management Console

## Part 2

Continuously Monitor the Aggregator Sensor Readings and provide Human Friendly interpretations on a Web Application Interface which should be made available via any standard web browser using Infrastructure as Code (IaC) tools.

We ensured our solution was highly available by deploying our EC2 instances and Load balancer into two availability zones and the EC2 instances were made highly disposable by:

- Deploying an autoscaling group with a launch template
- Storing the web application artefacts in Amazon S3

Key Feautures of the Web app include:
-  Automatic updates every 120 seconds
-  Access to historical readings
-  Email alerts when there is an alarm trigger.



