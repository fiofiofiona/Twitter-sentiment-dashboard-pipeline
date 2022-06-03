##### final-project-twitter
# Dashboard Service of Targeted Sentiment Analysis on Trending Twitter Topics
Group Members: 
<br>. Emily Yeh: Set up Lambda Function streaming tweet search result on AWS via Tweepy package, Case Study on the key word "Abortion Rights" 
<br>. Fiona Lee: Create S3 buckets to store the tweet raw data and RDS db to store select tweet data including sentiment analysis results
<br>. Helen Yap: Set up Lambda function to perform Sentiment Analysis on tweets and upsert tweet data to RDS 
<br>. Yutai Li: Build the dashboard to analyze and visualize the descriptive statistics and sentiment classification results 

## Introduction
We propose a workflow for analyzing the sentiments surrounding trending topics on Twitter. We will first stream the Twitter API to the AWS services, and provide analytical data upon keyword queries. By conducting content analysis tasks such as sentiment classification on those tweet conversations and organizing the descriptive information on a dashboard, our pipeline could allow users to gain the insights of how a specified topic is led and discussed by opinion leaders. 

Given the vast growth in social media usage and reliance for news and information, developing a large-scale method to collect and analyze Twitter data as described above would help inform how users feel and perceive the information that can then potentially inform downstream decision-making behaviors.  

## Deploying Tweet Data

## Parallelization Design
The current pipeline leverages the 10 allowed invocations of Lambda functions to parallelize sentiment analysis and RDS upsert. A stepfunction is used to pass 10 batches of tweet data to the Lambda function carrying the boto3 client call to AWS Comprehend and RDS. 

## Dashboard Interface

## Case Study: Abortion Rights

## Prospects of scalability
Our data pipeline is scalable on multiple fronts: 
* **SQS queue:** AWS's SQS queue already has high throughput allowing for even bigger streams of data than we currently have (and are limited by Twitter APIs). If needed, throughput can be further increased by horizontally scaling up SQS by: increasing the number of threads per client, adding more clients
and or increasing the number of threads per client. 

* **Lambda functions:** We are currently limited to 10 invocations of Lambda by AWS Academy. To scale up to potentially 10,000 Lambda functions, we recommend switching to a personal AWS account. 

* **RDS:** If greater storage capacity is needed, it is possible to modify the instance type of the current RDS db. If there is uncertainty regarding future workload size, it is also possible to set RDS to automatically scale. 




## References
* https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-throughput-horizontal-scaling-and-batching.html 
* https://aws.amazon.com/blogs/database/scaling-your-amazon-rds-instance-vertically-and-horizontally/


