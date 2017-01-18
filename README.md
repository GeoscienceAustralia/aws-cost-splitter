# Cost Splitter
This tool will generate a seperate cost report for each of the report groups defined it config.yml

## Pre-requisites
1. AWS detailed billing report must be enabled [see AWS guide](http://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-reports.html#turnonreports)
2. AWS detailed billing must be exported to an s3 bucket [see AWS guide](http://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-reports.html#s3-prereqs)
3. You will need the access keys of an account with access to this bucket [see the AWS guide](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
4. Download and install python3 [see python.org](https://www.python.org/downloads/)
5. Install [AWS CLI](https://aws.amazon.com/cli)

## Installation
1. Download or clone this repo
2. `pip install boto3`
3. `pip install pyyaml`

## Configuration
1. Add your configuration information to the config.yml file
2. Configure aws so boto can use the credentials [see Boto3 guide](http://boto3.readthedocs.io/en/latest/guide/configuration.html)

## Running
Run the script with `python cost-splitter.py`
The last months detailed billing report will be downloaded from the s3 bucket to the temp folder
This file will be unzipped and analysed
The results will be printed in the console

```
For the month of 2016-11
Total Cost: 2009.0603445310903
Report 1 cost is 1371.572665764959
Report 2 cost is 521.8074312498701
Shared cost is 165.680247516731
completed in 34 seconds
```

## Debug mode
setting `Debug: true` in the config.yml will show a printed list of objects that do not match your specified tags

## Contributing
### Feature requests
Please register an issue for feature requests

### Branches
For ease of integration, please fork the **integration** branch and create a Pull Request

### Style
This repo uses pylint for style guide 

## Roadmap
1. ~~Create basic cost-splitting functionality~~
2. ~~Add email functionality~~
3. Modify script to be run as a lambda