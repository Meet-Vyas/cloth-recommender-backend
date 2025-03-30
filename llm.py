# import boto3
# import json
# import random

# # Initialize the Bedrock client
# bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')

# def generate_llm_response(prompt):
#     """Generate a response using AWS Bedrock and Claude."""
#     # Use the correct model ID format for AWS Bedrock
#     model_id = 'arn:aws:bedrock:us-east-2:785362251004:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'  # Use the actual available model ID
    
#     # Create a message structure for Claude
#     body = {
#         "anthropic_version": "bedrock-2023-05-31",
#         "max_tokens": 500,
#         "temperature": 0.3,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
#     }
    
#     try:
#         # Invoke the model
#         response = bedrock.invoke_model(
#             modelId=model_id,
#             body=json.dumps(body)
#         )
        
#         # Extract the response
#         result = json.loads(response['body'].read())
#         llm_output = result['content'][0]['text']
#         return llm_output
#     except Exception as e:
#         print(f"Error: {e}")
#         return "Failed to generate response."
# print("LLM response generation function initialized.")
# def process_clothing_input(input_json):
#     """Process the input JSON to get clothing recommendations."""
#     weather = input_json.get('weather', 'Unknown weather')
    
#     # Initialize the output JSON structure
#     output_json = {}
    
#     # Process each clothing category (top, bottom, shoes, watch)
#     for category in ['top', 'bottom', 'shoes', 'watch']:
#         items = input_json.get(category, [])
        
#         best_item = None
        
#         # For each item in the category, generate a suggestion
#         for item in items:
#             color = item.get('color', item.get('type', 'Unknown'))
#             image_id = item.get('imageId', 'Unknown imageId')
            
#             # Ultra-efficient prompt (<50 tokens)
                
#             prompt = (
#                 f"Weather: {weather}. Item: {category} ({color}). "
#                 f"In 50 words or less, suggest a stylish color combination for this item. "
#                 f"Be specific and varied in your recommendations."
#             )
            
#             try:
#                 # Generate the LLM response
#                 generate_llm_response(prompt)
#                 # We don't actually need the response, just tracking which items we processed
#                 if not best_item:
#                     best_item = image_id
#             except:
#                 if not best_item:
#                     best_item = image_id
        
#         # Store the selected item for this category
#         if best_item:
#             output_json[category] = best_item
#         elif items:  # Fallback
#             output_json[category] = items[0].get('imageId', 'Unknown')
    
#     return output_json
# print("Clothing input processing function initialized.")
# def main():
#     # Example input JSON
#     input_json = {
#     "weather": "summer",
#     "top": {
#         "casual": [
#             {
#                 "category": "T-shirt",
#                 "color": "#0000ff",
#                 "imageId": "abc123.jpg"
#             },
#             {
#                 "category": "shirt",
#                 "color": "#ff0000",
#                 "imageId": "def456.jpg"
#             }
#         ]
#     },
#     "bottom": {
#         "casual": [
#             {
#                 "category": "jeans",
#                 "color": "#00ff00",
#                 "imageId": "ghi789.jpg"
#             }
#         ]
#     },
#     "shoes": [
#         {
#             "category": "sneakers",
#             "color": "#ff00ff",
#             "imageId": "jkl012.jpg"
#         }
#     ],
#     "watch": [
#         {
#             "category": "digital",
#             "color": "#ffff00",
#             "imageId": "mno345.jpg"
#         }
#     ]
# }
    
#     # Process the input and generate a result
#     result_json = process_clothing_input(input_json)
    
#     # Print the result in JSON format
#     print(json.dumps(result_json, indent=4))

# # Run the script
# if __name__ == "__main__":
#     main()
    





# import boto3
# import json
# import random
# from typing import Dict, List, Optional, Union

# class ClothingRecommender:
#     def __init__(self):
#         self.model_id = 'arn:aws:bedrock:us-east-2:785362251004:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'
#         self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')
    
#     def generate_llm_response(self, prompt: str) -> Optional[str]:
#         """Generate a response using AWS Bedrock and Claude 3."""
#         body = {
#             "anthropic_version": "bedrock-2023-05-31",
#             "max_tokens": 100,
#             "messages": [{"role": "user", "content": prompt}]
#         }
        
#         try:
#             response = self.bedrock.invoke_model(
#                 modelId=self.model_id,
#                 body=json.dumps(body),
#                 contentType='application/json',
#                 accept='application/json'
#             )
#             result = json.loads(response['body'].read())
#             return result['content'][0]['text']
#         except Exception as e:
#             print(f"LLM Error: {str(e)}")
#             return None
    
#     def select_item(self, items: List[Dict], category: str, weather: str) -> Optional[str]:
#         """Select an item either randomly or via LLM recommendation."""
#         if not items:
#             return None
            
#         try:
#             selected = random.choice(items)
#             if random.random() < 0.7:  # 70% chance for random selection
#                 return selected['imageId']
            
#             # LLM-assisted selection
#             prompt = self._build_selection_prompt(selected, category, weather)
#             if self.generate_llm_response(prompt):
#                 return selected['imageId']
#             return random.choice(items)['imageId']
#         except IndexError:
#             return None
    
#     def _build_selection_prompt(self, item: Dict, category: str, weather: str) -> str:
#         """Construct a prompt for item selection."""
#         color = item.get('color', item.get('type', 'unknown'))
#         return (
#             f"Analyze this {category} for {weather} weather:\n"
#             f"Color/Type: {color}\n"
#             "Should this be recommended? Reply only with YES or NO."
#         )
    
#     def _get_items_from_category(self, data: Dict, category: str) -> List[Dict]:
#         """Safely extract items from nested category structure."""
#         try:
#             if category == 'top':
#                 # Handle both top and shirt categories
#                 use_shirt = random.choice([True, False])
#                 if use_shirt and 'shirt' in data and data['shirt'].get('casual'):
#                     return data['shirt']['casual']
#                 elif 'top' in data and data['top'].get('casual'):
#                     return data['top']['casual']
#                 return []
#             elif category == 'bottom':
#                 if 'bottom' in data and data['bottom'].get('casual'):
#                     return data['bottom']['casual']
#                 return []
#             else:  # shoes, watch
#                 return data.get(category, [])
#         except (KeyError, AttributeError):
#             return []
    
#     def process_input(self, input_data: Dict) -> Dict:
#         """Process input JSON to generate outfit recommendations."""
#         weather = input_data.get('weather', 'moderate')
#         output = {
#             "top": None,
#             "bottom": None,
#             "shoes": None,
#             "watch": None
#         }
        
#         # Handle each category
#         for category in output.keys():
#             items = self._get_items_from_category(input_data, category)
#             if items:
#                 output[category] = self.select_item(items, category, weather)
        
#         return {k: v for k, v in output.items() if v is not None}
 
# def main():
#     recommender = ClothingRecommender()
    
#     input_json = {
#         "weather": "summer",
#         "top": {
#             "casual": [
#                 {"category": "T-shirt", "color": "#0000ff", "imageId": "abc123.jpg"},
#                 {"category": "shirt", "color": "#ff0000", "imageId": "def456.jpg"}
#             ]
#         },
#         "bottom": {
#             "casual": [
#                 {"category": "jeans", "color": "#00ff00", "imageId": "ghi789.jpg"}
#             ]
#         },
#         "shoes": [
#             {"category": "sneakers", "color": "#ff00ff", "imageId": "jkl012.jpg"}
#         ],
#         "watch": [
#             {"category": "digital", "color": "#ffff00", "imageId": "mno345.jpg"}
#         ]
#     }
    
#     result = recommender.process_input(input_json)
#     print(json.dumps(result, indent=2))

# if __name__ == "__main__":
#     main()

import boto3
import json
from typing import Dict, Any

class ClothingRecommender:
    def __init__(self):
        self.model_id = 'arn:aws:bedrock:us-east-2:785362251004:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')
    
    def recommend_outfit(self, context_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate a color-coordinated outfit recommendation using Claude."""
        
        prompt = self._build_prompt(context_info)
        response = self._call_llm(prompt)
        
        # If no valid response, implement fallback logic
        if not response:
            return self._fallback_selection(context_info)
            
        return response
    
    def _build_prompt(self, context_info: Dict[str, Any]) -> str:
        """Build a concise prompt for the LLM to select clothing items with best color coordination."""
        
        # Convert the context_info to a formatted string representation
        context_str = json.dumps(context_info, indent=2)
        
        prompt = f"""
    As a fashion advisor, select ONE item from each category (top, bottom, shoes, watch) that creates the most harmonious color combination for the given weather.

    Wardrobe information:
    {context_str}

    Return ONLY a JSON object with these keys: "top", "bottom", "shoes", "watch". For each key, provide ONLY the imageId.
    Your response must be EXACTLY in this format: {{"top": "imageId", "bottom": "imageId", "shoes": "imageId", "watch": "imageId"}}
    """
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict[str, str]:
        """Call the LLM model and parse the response."""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 150,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            result = json.loads(response['body'].read())
            response_text = result['content'][0]['text'].strip()
            
            # Parse the JSON response
            return json.loads(response_text)
        except Exception as e:
            print(f"Error with LLM call: {str(e)}")
            return {}
    
    def _fallback_selection(self, context_info: Dict[str, Any]) -> Dict[str, str]:
        """Simple fallback selection if LLM fails."""
        result = {}
        
        # Select first item from each category
        if "top" in context_info and context_info["top"].get("casual"):
            result["top"] = context_info["top"]["casual"][0]["imageId"]
            
        if "bottom" in context_info and context_info["bottom"].get("casual"):
            result["bottom"] = context_info["bottom"]["casual"][0]["imageId"]
            
        if "shoes" in context_info and context_info["shoes"]:
            result["shoes"] = context_info["shoes"][0]["imageId"]
            
        if "watch" in context_info and context_info["watch"]:
            result["watch"] = context_info["watch"][0]["imageId"]
            
        return result

def main():
    recommender = ClothingRecommender()
    
    # Example context_info
    context_info = {
        "weather": "summer",
        "top": {
            "casual": [
                {"category": "T-shirt", "color": "#0000ff", "imageId": "abc123.jpg"},
                {"category": "shirt", "color": "#ff0000", "imageId": "def456.jpg"}
            ]
        },
        "bottom": {
            "casual": [
                {"category": "jeans", "color": "#00ff00", "imageId": "ghi789.jpg"},
                {"category": "shorts", "color": "#00ff00", "imageId": "ghi789647675.jpg"}
            ]
        },
        "shoes": [
            {"category": "sneakers", "color": "#ff00ff", "imageId": "jkl012.jpg"},
            {"category": "formal", "color": "#ff00ff", "imageId": "jkl0165762.jpg"},
            {"category": "casual", "color": "#ff0012", "imageId": "formal123.jpg"}
        ],
        "watch": [
            {"category": "digital", "color": "#ffff00", "imageId": "mno345.jpg"},
            {"category": "smart", "color": "#ff0000", "imageId": "def456.jpg"},
            {"category": "analogue", "color": "#ff0000", "imageId": "def4568766.jpg"}
        ]
    }
    
    result = recommender.recommend_outfit(context_info)
    print(json.dumps(result))

if __name__ == "__main__":
    main()