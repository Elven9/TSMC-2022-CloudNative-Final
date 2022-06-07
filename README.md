# TSMC Cloud Native class final project: Digital Business
A solution for collecting Internet volume for some key words with CI/CD workflow automation.

# Architecture
![](https://i.imgur.com/i71m0dX.png)
## Components
### Crawler Scheduler
- Cronjob to generate URL
- Send URLs to RabbitMQ

### RabbitMQ
- Queue URLs

### Crawler
- Consume URLs from RabbitMQ
- Parse URL data
- Generate result and store into InfluxDB

### InfluxDB
- Keep data from Crawler

### Grafana
- Read data from InfluxDB
- Show the result figure

# CI/CD Workflow Design
Dev branch for development, with a CI workflow for test/build (push) images to dockerhub; after some feature or bug released/fixed, contributor can raise a pull request merge dev branch to master.
The pull request for master branch will need at least one reviewer approval comment to accept the request.
After merge the request to master, ArgoCD will sync the application status to cluster.
![](https://i.imgur.com/84ddoUA.png)

## Tools
Github Action use for CI workflow, run pytest and build (push) image to dockerhub.
ArgoCD use for install helm charts on GCP cluster.
![](https://i.imgur.com/E61rfKD.png)

# Application Present
(Grafana dashboard)

![](https://i.imgur.com/FRo6fP4.jpg)

# Contribution
