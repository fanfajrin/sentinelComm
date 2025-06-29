import replicate
import pandas as pd
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY", "no_api_key_detected")

input = {
    "prompt": "why llm is usefull? give me answer in one sentence"
}

for event in replicate.stream(
    "ibm-granite/granite-3.3-8b-instruct",
    input=input
):
    print(event, end="")