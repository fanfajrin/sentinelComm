import replicate
import pandas as pd
from dotenv import load_dotenv
import os
import time

load_dotenv()


data_train = pd.read_csv(f'./train.csv')
data_train = data_train.head(100)


API_KEY = os.getenv("API_KEY", "no_api_key_detected")



def classify_tweet(text):
    """
    Classify a single tweet using Replicate API to determine if it's about a disaster.
    Returns 1 for disaster, 0 for not disaster.
    """
    try:
        input_data = {
            "prompt": f"Classify this sentence into disaster tweet or not disaster tweet. Output only 1 for disaster and 0 for not disaster. Sentence: '{text}'",
            "temperature": 0.1,
            "max_tokens": 5,
            "min_tokens": 1,
        }

        response = ""
        for event in replicate.stream("ibm-granite/granite-3.3-8b-instruct", input=input_data):
            response += str(event)
            
        return 1 if '1' in response.strip() else 0
    except Exception as e:
        print(f"Error classifying tweet: {e}")
        return 0

def extract_location(text):
    """
    Extracts the location from a disaster tweet using Replicate API.
    Returns the location string or "Not found".
    """
    try:
        input_data = {
            "prompt": f"From the following disaster tweet, what is the specific location mentioned? If no location is found, just output 'Not found'. Tweet: '{text}'",
            "temperature": 0.2,
            "max_tokens": 50,
            "min_tokens": 1,
        }
        location = ""
        for event in replicate.stream("ibm-granite/granite-3.3-8b-instruct", input=input_data):
            location += str(event)
        
        location = location.strip()
        return location if location and "not found" not in location.lower() else "Not found"
    except Exception as e:
        print(f"Error extracting location: {e}")
        return "Error"

def identify_urgency(text):
    """
    Classifies the urgency of a disaster tweet.
    Returns "Immediate Danger," "Urgent Need," or "Information/Update."
    """
    try:
        input_data = {
            "prompt": f"Classify the urgency of this tweet. Respond with only one of the following options: 'Immediate Danger', 'Urgent Need', or 'Information/Update'. Tweet: '{text}'",
            "temperature": 0.1,
            "max_tokens": 20,
            "min_tokens": 1,
        }
        urgency = ""
        for event in replicate.stream("ibm-granite/granite-3.3-8b-instruct", input=input_data):
            urgency += str(event)

        urgency = urgency.strip()
        

        if "immediate danger" in urgency.lower():
            return "Immediate Danger"
        elif "urgent need" in urgency.lower():
            return "Urgent Need"
        elif "information" in urgency.lower() or "update" in urgency.lower():
            return "Information/Update"
        else:
            return "Unclassified"
            
    except Exception as e:
        print(f"Error identifying urgency: {e}")
        return "Error"

def extract_resource_needs(text):
    """
    Pinpoints specific aid requests from a tweet, like "water," "medical," or "rescue."
    Returns a comma-separated list of needs or "None".
    """
    try:
        input_data = {
            "prompt": f"From this tweet, list the specific resources needed (e.g., water, medical, shelter, food, rescue, blood). If no specific resource is requested, output 'None'. Only return the specific resources. Tweet: '{text}'",
            "temperature": 0.2,
            "max_tokens": 50,
            "min_tokens": 1,
        }
 
        needs = ""
        for event in replicate.stream("ibm-granite/granite-3.3-8b-instruct", input=input_data):
            needs += str(event)

        needs = needs.strip()
        return needs if needs else "None"
    except Exception as e:
        print(f"Error extracting resource needs: {e}")
        return "Error"

# --- Main Processing Loop ---

# Initialize the new columns in the DataFrame
data_train['prediction'] = 0
data_train['urgency'] = 'N/A'
data_train['resource_needs'] = 'N/A'
data_train['location'] = 'N/A'


for index, row in data_train.iterrows():
    text = row['text']
    print(f"\nProcessing row {index + 1}/{len(data_train)} | ID: {row['id']}")
    print(f"Text: '{text[:80]}...'")
    

    prediction = classify_tweet(text)
    data_train.at[index, 'prediction'] = prediction
    

    if prediction == 1:
        print("-> Disaster Tweet Identified. Running further analysis...")
        

        time.sleep(1) 
        

        urgency = identify_urgency(text)
        data_train.at[index, 'urgency'] = urgency
        print(f"   - Urgency: {urgency}")
        time.sleep(1)
        

        resources = extract_resource_needs(text)
        data_train.at[index, 'resource_needs'] = resources
        print(f"   - Needs: {resources}")
        time.sleep(1)


        location = extract_location(text)
        data_train.at[index, 'location'] = location
        print(f"   - Location: {location}")

    else:
        print("-> Not a disaster tweet. Skipping further analysis.")
    

    time.sleep(1)


output_filename = './test_with_full_analysis.csv'
data_train.to_csv(output_filename, index=False)
print(f"\n✅ Analysis complete. Results saved to '{output_filename}'")

print("\n--- Final Results Sample ---")
print(data_train[['id', 'prediction', 'urgency', 'resource_needs', 'location']].head(20))