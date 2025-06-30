import replicate
import pandas as pd
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()

data_train = pd.read_csv(f'./test.csv')

data_train = data_train.head(50)


API_KEY = os.getenv("API_KEY", "no_api_key_detected")

def classify_tweet(text):
    """
    Classify a single tweet using Replicate API
    """
    try:
        input_data = {
            "top_k": 50,
            "top_p": 0.9,
            "prompt": f"Classify this sentence into disaster tweet or not disaster tweet. Output only 1 for disaster and 0 for not disaster. Sentence: '{text}'",
            "max_tokens": 10,  # Reduced since we only need 1 or 0
            "min_tokens": 1,
            "temperature": 0.1,  # Lower temperature for more consistent results
            "presence_penalty": 0,
            "frequency_penalty": 0
        }
        
        # Collect the full response
        response = ""
        for event in replicate.stream(
            "ibm-granite/granite-3.3-8b-instruct",
            input=input_data
        ):
            response += str(event)
        
        # Extract the prediction (look for 0 or 1 in the response)
        response = response.strip()
        if '1' in response:
            return 1
        elif '0' in response:
            return 0
        else:
            # If unclear response, return None or handle as needed
            print(f"Unclear response: {response}")
            return None
            
    except Exception as e:
        print(f"Error classifying text: {e}")
        return None

# Initialize the predictions column
data_train['prediction'] = 0

# Iterate through each row and classify
for index, row in data_train.iterrows():
    print(f"Processing row {index + 1}/{len(data_train)}")
    
    # Get the text to classify
    text = row['text']
    
    # Classify the text
    prediction = classify_tweet(text)
    
    # Store the prediction
    data_train.at[index, 'prediction'] = prediction
    
    print(f"ID: {row['id']}, Text: '{text[:50]}...', Prediction: {prediction}")
    
    # Add a small delay to avoid rate limiting
    time.sleep(1)

# # Display results
# print("\nClassification Results:")
# print(data_train[['id', 'text', 'target', 'prediction']].head(10))

# Save results to CSV
data_train.to_csv('./test_with_predictions.csv', index=False)
print(f"\nResults saved to 'test_with_predictions.csv'")

# # Optional: Calculate accuracy if you have ground truth labels
# if 'target' in data_train.columns:
#     # Remove rows where prediction failed
#     valid_predictions = data_train.dropna(subset=['prediction'])
    
#     if len(valid_predictions) > 0:
#         accuracy = (valid_predictions['target'] == valid_predictions['prediction']).mean()
#         print(f"Accuracy: {accuracy:.2%}")
#     else:
#         print("No valid predictions to calculate accuracy")