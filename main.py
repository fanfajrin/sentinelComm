import replicate
import pandas as pd
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "no_api_key_detected")

input = {
    "top_k": 50,
    "top_p": 0.9,
    "prompt": "why llm is usefull? give me answer in one sentence",
    "max_tokens": 512,
    "min_tokens": 0,
    "temperature": 0.6,
    "presence_penalty": 0,
    "frequency_penalty": 0
}

for event in replicate.stream(
    "ibm-granite/granite-3.3-8b-instruct",
    input=input
):
    print(event, end="")