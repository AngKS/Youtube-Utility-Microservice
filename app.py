import requests
from bs4 import BeautifulSoup as bs
from openai import OpenAI, OpenAIError
import boto3
import re
import json

MODEL = "gpt-3.5-turbo-0125"

def fetch_api_key():
    try:

        # get the api key from the AWS Parameter Store
        ssm = boto3.client('ssm')
        print("Client Created!")
        response = ssm.get_parameter(Name='openai-api-key', WithDecryption=True)
        print("SSM PARAMETER:", response)
        return response['Parameter']['Value']
    except Exception as e:
        print("Error fetching API key:", str(e))
        return None
    
    except boto3.exceptions.ParamValidationError as e:
        print("Parameter Key Validation Error:", str(e))
        return None



class YoutubeTranscriber:
    def __init__(self, url: str):
        assert re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url), "Invalid URL"
        self.url = url
        self.title = None
        self.transcript = None

    def get_youtube_url_content(self) -> requests.models.Response:
        print("Requesting URL...")
        response = requests.get(self.url)
        print("URL Requested, StatusCode: ", response.status_code)
        return response
    
    def get_transcript_content(self, url: str) -> requests.models.Response:
        print("Requesting Transcript URL...")
        response = requests.get(url)
        print("Transcript URL Requested, StatusCode: ", response.status_code)
        return response

    def get_transcript_url(self, soup) -> str:
        print("Parsing Transcript URL...")
        scripts = soup.find_all('script')
        split_scripts = str(scripts).split('"')
        for script in split_scripts:
            if "/api/timedtext" in script:
                transcript_url = script
                parsed_url = transcript_url.replace("\\u0026", "&")
                print("Transcript URL Found: ", parsed_url)
                return parsed_url
        raise ValueError("Transcript URL Not Found")

    def parse_youtube_url_content(self, response: requests.models.Response) -> str:
        print("Parsing URL Content...")
        soup = bs(response.text, 'html.parser')
        self.title = soup.title.string
        print("Title: ", self.title)
        transcript_url = self.get_transcript_url(soup)

        if transcript_url is not None:
            return transcript_url
        return None
    
    
    def parse_xml(self, response: requests.models.Response):
        print("Parsing XML...")
        soup = bs(response.text, 'lxml-xml')
        text = soup.get_text()
        text = text.replace("&gt;", ">")
        text = text.replace("&lt;", "<")
        text = text.replace("&quot;", '"')
        text = text.replace("&apos;", "'")
        text = text.replace("&amp;", "&")
        text = text.replace("&#39;", "'")
        text = text.replace("&nbsp;", " ")
        text = text.replace("&ldquo;", '"')
        text = text.replace("&rdquo;", '"')
        text = text.replace("&rsquo;", "'")
        text = text.replace("&lsquo;", "'")
        text = text.replace("&hellip;", "...")
        text = text.replace("&mdash;", "--")
        text = text.replace("&ndash;", "-")
        text = text.replace("&middot;", "·")
        text = text.replace("\n", " ")

        self.transcript = text
        print("Transcript Parsed!")
        return
    

    def get_transcript(self):
        response = self.get_youtube_url_content()
        transcript_url = self.parse_youtube_url_content(response)
        response = self.get_transcript_content(transcript_url)
        self.parse_xml(response)
        return self.transcript

    def summarize(self):
        if self.transcript is None:
            return "Transcript not found, please call the get_transcript method first"


        PROMPT = """
            You are an intelligent youtube video transcript analyzer and summarizer. The user will provide you with a video transcript and all you have to do is to create a summary of the entire video transcript to capture as much information and details as possible within a short paragraph of not more than 6 sentences long. Afterwards, you are to think through the transcript content step by step, and carefully identify and extract every single key point mentioned in the video transcript in point form after providing the transcript summary. Example response:

            Summary:

            
            Keypoints:
            1. Keypoint 1 
            2. Keypoint 2
        """
        print("Fetching API Key...")
        API_KEY = fetch_api_key()
        print("API Key fetched!")

        client = OpenAI(
            api_key=API_KEY
        )
        print("Generating Summary...")
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT
                    },
                    {
                        "role": "user",
                        "content": self.transcript
                    }
                ]
            )
        except OpenAIError as e:
            print("Error occurred while generating summary: ", e)
            return None
        print("Summary Generated!")

        response = response.choices[0].message.content
        # parse the response to remove "\n" and "\"
        response = response.replace("\\", "")
        return response

    

def lambda_handler(event, context):
    try:
        # get url from event body
        print("Event: ", event)
        # parse the event body as json
        body = json.loads(event['body'])

        url = body['url']
        method = body['method']
        # check if method is either transcript or summary
        transcriber = YoutubeTranscriber(url)
        transcript = transcriber.get_transcript()
        if method == "transcript":
            response_body = {
                "video_title": transcriber.title,
                "transcript": transcript
            }
        elif method == "summary":
            summary = transcriber.summarize()
            response_body = {
                "video_title": transcriber.title,
                "transcript": transcript,
                "summary": summary
            }
        else:
            raise ValueError("Invalid method. Method should be either 'transcript' or 'summary'.")
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_body)
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "error": str(e)
        }
