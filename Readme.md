# This is a repository for CIL Academy's Cohort 6 Shalomium Group Technical Challenge by Group 4

The task was divided into two parts

## Part 1

Ingest and Sample the Aggregator Sensor Readings via AWS IoT Core & Analytics This was completed and demonstrated on the AWS Web Management Console

## Part 2

Continuously Monitor the Aggregator Sensor Readings and provide Human Friendly interpretations on a Web Application Interface which should be made available via any standard web browser using Infrastructure as Code (IaC) tools.

We ensured our solution was highly available by deploying our EC2 instances and Load balancer into two availability zones and the EC2 instances were made highly disposable by

- Deploying an autoscaling group with a launch template
- Storing the web application artefacts in Amazon S3

## Reference Architecture

The Reference Architecture used for this project is attached below

![Alt text][GTC-Group4-Arch]
[GTC-Group4-Arch]: GTC-Group4-Arch.png

The Web Application can be viewed here [Group 4 Webapp](https://gtc4.tspace.uk)
