# Simple Serverless Youtube Video Utility Microservice
<!-- add image -->
![Infrastructure](https://github.com/AngKS/Youtube-Utility-Microservice/blob/main/assets/infrastructure.png?raw=true)

This is a simple serverless microservice that allows you to provide a youtube video URL and get back the video's title, video transcript and a GPT summary of the video.

## Program Flow
The program flow of this microservice is as follows:
1. The microservice accepts a POST request with a youtube video URL and a method to retrieve the video transcript.
2. The 2 methods accepted are: `transcript` and `summary`.
3. If the method is `transcript`, the microservice will return the video's title and transcript.
4. If the method is `summary`, the microservice will return the video's title, transcript and a GPT summary of the video.

## Architecture
The architecture of this microservice is as follows:
1. The microservice is hosted on AWS Lambda.
2. The API Gateway is used to route the requests to the Lambda function.
3. The Lambda handler is a python script that is deployed as an image on AWS ECR.
4. The function uses the Python requests library to call the Youtube API to retrieve the video's title and transcript as well as utilize the OpenAI Library to generate a GPT summary of the video.

## How to Use
To use this microservice, you can send a POST request to the API Gateway endpoint with the following JSON payload:
```json
{
    "url": "https://www.youtube.com/watch?v=video_id",
    "method": "transcript"
}
```
The `url` field should contain the URL of the youtube video and the `method` field should contain either `transcript` or `summary`.

### Response
The microservice will return a JSON response with the following fields:
```json
{
    "title": "Video Title",
    "transcript": "Video Transcript",
    "summary": "GPT Summary"
}
```
The `title` field contains the title of the video, the `transcript` field contains the video transcript and the `summary` field contains the GPT summary of the video.



## Prerequisites
To deploy this microservice, you will need the following:
1. An AWS account
2. Docker installed on your local machine
3. AWS CLI installed on your local machine
4. An OpenAI API key
5. Existing ECR repository


## Deployment

To deploy this microservice, you can use the `deploy.sh` script provided in the repository. The script will build the docker image, push it to ECR and deploy the Lambda function using the AWS CLI.
    
    ```bash
    ./deploy.sh
    ```
    
## Author
- [Ang Kah Shin](https://www.linkedin.com/in/kahshinang)
