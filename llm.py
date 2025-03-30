# import boto3
# import json
# import random
# from typing import Dict, Any, List

# class ClothingRecommender:
#     def __init__(self):
#         self.model_id = 'arn:aws:bedrock:us-east-2:785362251004:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'
#         self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')
#         self.previous_outfits = []  # Store previous outfit recommendations
#         self.max_history = 3  # Remember last 3 outfits to avoid repetition
    
#     def recommend_outfit(self, context_info: Dict[str, Any]) -> Dict[str, str]:
#         """Generate a color-coordinated outfit recommendation using Claude."""
        
#         prompt = self._build_prompt(context_info)
#         response = self._call_llm(prompt)
        
#         # If no valid response, implement fallback logic
#         if not response:
#             return self._fallback_selection(context_info)
        
#         # If we have previous outfits and the current one is too similar
#         if self.previous_outfits and self._is_too_similar(response, self.previous_outfits[-1]):
#             # Try to get an alternative outfit
#             alt_outfit = self._generate_alternative_outfit(context_info, response)
#             if alt_outfit:
#                 response = alt_outfit
        
#         # Update outfit history
#         self.previous_outfits.append(response)
#         if len(self.previous_outfits) > self.max_history:
#             self.previous_outfits.pop(0)
            
#         return response
    
#     def _build_prompt(self, context_info: Dict[str, Any]) -> str:
#         """Build a concise prompt for the LLM to select clothing items with best color coordination."""
        
#         # Convert the context_info to a formatted string representation
#         context_str = json.dumps(context_info, indent=2)
        
#         # If we have previous outfits, tell the model to avoid them
#         avoid_str = ""
#         if self.previous_outfits:
#             avoid_str = f"Previously recommended outfits (avoid exact matches): {json.dumps(self.previous_outfits)}"
        
#         prompt = f"""
# As a fashion advisor, select ONE item from each category (top, bottom, shoes, watch) that creates the most harmonious color combination for the given weather.

# Wardrobe information:
# {context_str}

# {avoid_str}

# Return ONLY a JSON object with these keys: "top", "bottom", "shoes", "watch". For each key, provide ONLY the imageId.
# Your response must be EXACTLY in this format: {{"top": "imageId", "bottom": "imageId", "shoes": "imageId", "watch": "imageId"}}
# """
#         return prompt
    
#     def _call_llm(self, prompt: str) -> Dict[str, str]:
#         """Call the LLM model and parse the response."""
#         try:
#             body = {
#                 "anthropic_version": "bedrock-2023-05-31",
#                 "max_tokens": 150,
#                 "messages": [{"role": "user", "content": prompt}]
#             }
            
#             response = self.bedrock.invoke_model(
#                 modelId=self.model_id,
#                 body=json.dumps(body),
#                 contentType='application/json',
#                 accept='application/json'
#             )
            
#             result = json.loads(response['body'].read())
#             response_text = result['content'][0]['text'].strip()
            
#             # Parse the JSON response
#             return json.loads(response_text)
#         except Exception as e:
#             print(f"Error with LLM call: {str(e)}")
#             return {}
    
#     def _is_too_similar(self, current_outfit: Dict[str, str], previous_outfit: Dict[str, str]) -> bool:
#         """Check if the current outfit is too similar to the previous one."""
#         # Count how many items are the same
#         same_items = sum(1 for k in current_outfit if k in previous_outfit and current_outfit[k] == previous_outfit[k])
#         # If 3 or more items are the same, it's too similar
#         return same_items >= 3
    
#     def _generate_alternative_outfit(self, context_info: Dict[str, Any], current_outfit: Dict[str, str]) -> Dict[str, str]:
#         """Generate an alternative outfit that's different enough from the current one."""
#         # Create a copy of the current outfit
#         alt_outfit = current_outfit.copy()
        
#         # Decide which items to change (at least 2)
#         categories = ["top", "bottom", "shoes", "watch"]
#         items_to_change = random.sample(categories, random.randint(2, 3))
        
#         # Change selected items
#         for category in items_to_change:
#             # Get available items for this category
#             available_items = self._get_items_for_category(context_info, category)
#             if not available_items:
#                 continue
                
#             # Filter out the current item
#             alternative_items = [item for item in available_items if item != alt_outfit.get(category)]
#             if not alternative_items:
#                 continue
                
#             # Select an alternative that works well with the rest of the outfit
#             alt_outfit[category] = self._select_harmonious_alternative(alternative_items, alt_outfit, category)
        
#         return alt_outfit
    
#     def _get_items_for_category(self, context_info: Dict[str, Any], category: str) -> List[str]:
#         """Get all available items for a specific category."""
#         items = []
        
#         if category in ["top", "bottom"]:
#             for style_type in ["casual", "formal"]:
#                 if style_type in context_info[category]:
#                     items.extend([item["imageId"] for item in context_info[category][style_type]])
#         elif category in context_info:
#             items = [item["imageId"] for item in context_info[category]]
            
#         return items
    
#     def _select_harmonious_alternative(self, alternatives: List[str], outfit: Dict[str, str], category: str) -> str:
#         """Select an alternative item that harmonizes with the rest of the outfit."""
#         # For simplicity, just choose a random alternative
#         # In a real implementation, this could use color theory to ensure good coordination
#         return random.choice(alternatives)
    
#     def _fallback_selection(self, context_info: Dict[str, Any]) -> Dict[str, str]:
#         """Simple fallback selection if LLM fails."""
#         result = {}
        
#         # Select first item from each category
#         if "top" in context_info:
#             if "casual" in context_info["top"]:
#                 result["top"] = context_info["top"]["casual"][0]["imageId"]
#             elif "formal" in context_info["top"]:
#                 result["top"] = context_info["top"]["formal"][0]["imageId"]
            
#         if "bottom" in context_info:
#             if "casual" in context_info["bottom"]:
#                 result["bottom"] = context_info["bottom"]["casual"][0]["imageId"]
#             elif "formal" in context_info["bottom"]:
#                 result["bottom"] = context_info["bottom"]["formal"][0]["imageId"]
            
#         if "shoes" in context_info and context_info["shoes"]:
#             result["shoes"] = context_info["shoes"][0]["imageId"]
            
#         if "watch" in context_info and context_info["watch"]:
#             result["watch"] = context_info["watch"][0]["imageId"]
            
#         return result

# def main():
#     recommender = ClothingRecommender()
    
#     # Example context_info
    # context_info = {
    #     "weather": "summer",
    #     "top": {
    #         "casual": [
    #             {"category": "T-shirt", "color": "#000000", "imageId": "abc123.jpg"},
    #             {"category": "shirt", "color": "#ffffff", "imageId": "def456.jpg"},
    #             {"category": "polo", "color": "#0073cf", "imageId": "polo789.jpg"},
    #             {"category": "T-shirt", "color": "#f5f5dc", "imageId": "beige123.jpg"},
    #             {"category": "shirt", "color": "#87ceeb", "imageId": "skyblue456.jpg"}
    #         ],
    #         "formal": [
    #             {"category": "shirt", "color": "#ffffff", "imageId": "whitedress123.jpg"},
    #             {"category": "shirt", "color": "#87ceeb", "imageId": "bluedress456.jpg"},
    #             {"category": "shirt", "color": "#f5f5dc", "imageId": "beigedress789.jpg"},
    #         ]
    #     },
    #     "bottom": {
    #         "casual": [
    #             {"category": "jeans", "color": "#000080", "imageId": "navy789.jpg"},
    #             {"category": "shorts", "color": "#f5f5dc", "imageId": "beige567.jpg"},
    #             {"category": "pants", "color": "#808080", "imageId": "grey123.jpg"},
    #             {"category": "jeans", "color": "#000000", "imageId": "black456.jpg"},
    #             {"category": "shorts", "color": "#ffffff", "imageId": "white789.jpg"}
    #         ],
    #         "formal": [
    #             {"category": "pants", "color": "#000000", "imageId": "blackdress123.jpg"},
    #             {"category": "pants", "color": "#000080", "imageId": "navydress456.jpg"},
    #             {"category": "pants", "color": "#808080", "imageId": "greydress789.jpg"},
    #             {"category": "pants", "color": "#f5f5dc", "imageId": "beigedress012.jpg"},
    #             {"category": "pants", "color": "#8b4513", "imageId": "browndress345.jpg"}
    #         ]
    #     },
    #     "shoes": [
    #         {"category": "sneakers", "color": "#000000", "imageId": "blacksneakers.jpg"},
    #         {"category": "formal", "color": "#8b4513", "imageId": "brownformal.jpg"},
    #         {"category": "casual", "color": "#ffffff", "imageId": "whitecasual.jpg"},
    #         {"category": "sneakers", "color": "#0073cf", "imageId": "bluesneakers.jpg"},
    #         {"category": "sandals", "color": "#f5f5dc", "imageId": "beigesandals.jpg"},
    #         {"category": "formal", "color": "#000000", "imageId": "blackformal.jpg"},
    #         {"category": "loafers", "color": "#000080", "imageId": "navyloafers.jpg"}
    #     ],
    #     "watch": [
    #         {"category": "digital", "color": "#000000", "imageId": "blackdigital.jpg"},
    #         {"category": "smart", "color": "#c0c0c0", "imageId": "silverwatch.jpg"},
    #         {"category": "analogue", "color": "#8b4513", "imageId": "brownwatch.jpg"},
    #         {"category": "smart", "color": "#ffffff", "imageId": "whitewatch.jpg"},
    #         {"category": "sports", "color": "#0073cf", "imageId": "bluewatch.jpg"},
    #         {"category": "luxury", "color": "#ffd700", "imageId": "goldwatch.jpg"},
    #         {"category": "dress", "color": "#000000", "imageId": "blackdresswatch.jpg"}
    #     ]
    # }
    
#     # Test multiple recommendations to see variation
#     for i in range(3):
#         result = recommender.recommend_outfit(context_info)
#         print(f"Outfit {i+1}: {json.dumps(result)}")

# if __name__ == "__main__":
#     main()

# import boto3
# import json
# import random
# from typing import Dict, Any, List

# class ClothingRecommender:
    
#     def _is_too_similar(self, item1, item2):
#         """Checks if two clothing items are too similar based on their color or category."""
#         return item1["category"] == item2["category"] and item1["color"] == item2["color"]

#     def __init__(self):
#         self.model_id = 'arn:aws:bedrock:us-east-2:785362251004:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'
#         self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')
#         self.previous_outfits = []  # Store previous outfit recommendations
#         self.max_history = 3  # Remember last 3 outfits to avoid repetition
    
#     def recommend_outfit(self, context_info: Dict[str, Any]) -> Dict[str, str]:
#         """Generate a color-coordinated outfit recommendation using Claude."""
        
#         prompt = self._build_prompt(context_info)
#         response = self._call_llm(prompt)
        
#         if not response:
#             return self._fallback_selection(context_info)
        
#         if self.previous_outfits and self._is_too_similar(response, self.previous_outfits[-1]):
#             alt_outfit = self._generate_alternative_outfit(context_info, response)
#             if alt_outfit:
#                 response = alt_outfit
        
#         self.previous_outfits.append(response)
#         if len(self.previous_outfits) > self.max_history:
#             self.previous_outfits.pop(0)
            
#         return response
    
#     def _build_prompt(self, context_info: Dict[str, Any]) -> str:
#         context_str = json.dumps(context_info, indent=2)
        
#         avoid_str = ""
#         if self.previous_outfits:
#             avoid_str = f"Previously recommended outfits (avoid exact matches): {json.dumps(self.previous_outfits)}"
        
#         prompt = f"""
# As a fashion advisor, select ONE item from each category (top, bottom, shoes, watch) that creates the most harmonious color combination for the given weather.

# Wardrobe information:
# {context_str}

# {avoid_str}

# Return ONLY a JSON object with these keys: "top", "bottom", "shoes", "watch". For each key, provide ONLY the imageId.
# Your response must be EXACTLY in this format: {{"top": "imageId", "bottom": "imageId", "shoes": "imageId", "watch": "imageId"}}
# """
#         return prompt
    
#     def _call_llm(self, prompt: str) -> Dict[str, str]:
#         try:
#             body = {
#                 "anthropic_version": "bedrock-2023-05-31",
#                 "max_tokens": 150,
#                 "messages": [{"role": "user", "content": prompt}]
#             }
            
#             response = self.bedrock.invoke_model(
#                 modelId=self.model_id,
#                 body=json.dumps(body),
#                 contentType='application/json',
#                 accept='application/json'
#             )
            
#             result = json.loads(response['body'].read())
#             response_text = result['content'][0]['text'].strip()
            
#             return json.loads(response_text)
#         except Exception as e:
#             print(f"Error with LLM call: {str(e)}")
#             return {}
    
#     def _fallback_selection(self, context_info: Dict[str, Any]) -> Dict[str, str]:
#         result = {}
        
#         if "top" in context_info:
#             if "casual" in context_info["top"]:
#                 result["top"] = context_info["top"]["casual"][0]["imageId"]
#             elif "formal" in context_info["top"]:
#                 result["top"] = context_info["top"]["formal"][0]["imageId"]
            
#         if "bottom" in context_info:
#             if "casual" in context_info["bottom"]:
#                 result["bottom"] = context_info["bottom"]["casual"][0]["imageId"]
#             elif "formal" in context_info["bottom"]:
#                 result["bottom"] = context_info["bottom"]["formal"][0]["imageId"]
            
#         if "shoes" in context_info and context_info["shoes"]:
#             result["shoes"] = context_info["shoes"][0]["imageId"]
            
#         if "watch" in context_info and context_info["watch"]:
#             result["watch"] = context_info["watch"][0]["imageId"]
            
#         return result

# def load_json_file(filename: str) -> Dict[str, Any]:
#     """Load JSON data from a file."""
#     try:
#         with open(filename, 'r', encoding='utf-8') as file:
#             return json.load(file)
#     except Exception as e:
#         print(f"Error reading JSON file: {str(e)}")
#         return {}

# def main():
#     recommender = ClothingRecommender()
    
#     # Load wardrobe data from a JSON file
#     context_info = load_json_file('wardrobe.json')
    
#     if not context_info:
#         print("Failed to load wardrobe data.")
#         return
    
#     # Test multiple recommendations to see variation
#     for i in range(3):
#         result = recommender.recommend_outfit(context_info)
#         print(f"Outfit {i+1}: {json.dumps(result, indent=2)}")

# if __name__ == "__main__":
#     main()


import boto3
import json
import random
from typing import Dict, Any, List

class ClothingRecommender:
    
    def __init__(self):
        self.model_id = 'arn:aws:bedrock:us-east-2:785362251004:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-2')
        self.previous_outfits = []  # Store previous outfit recommendations
        self.max_history = 3  # Remember last 3 outfits to avoid repetition
    
    def recommend_outfit(self, context_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate a color-coordinated outfit recommendation using Claude."""
        
        prompt = self._build_prompt(context_info)
        response = self._call_llm(prompt)
        
        if not response:
            return self._fallback_selection(context_info)
        
        # Remove check for "too similar" since we are not using it anymore
        
        self.previous_outfits.append(response)
        if len(self.previous_outfits) > self.max_history:
            self.previous_outfits.pop(0)
            
        return response
    
    def _build_prompt(self, context_info: Dict[str, Any]) -> str:
        context_str = json.dumps(context_info, indent=2)
        
        avoid_str = ""
        if self.previous_outfits:
            avoid_str = f"Previously recommended outfits (avoid exact matches): {json.dumps(self.previous_outfits)}"
        
        prompt = f"""
As a fashion advisor, select ONE item from each category (top, bottom, shoes, watch) that creates the most harmonious color combination for the given weather.

Wardrobe information:
{context_str}

{avoid_str}

Return ONLY a JSON object with these keys: "top", "bottom", "shoes", "watch". For each key, provide ONLY the imageId.
Your response must be EXACTLY in this format: {{"top": "imageId", "bottom": "imageId", "shoes": "imageId", "watch": "imageId"}}
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict[str, str]:
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
            
            return json.loads(response_text)
        except Exception as e:
            print(f"Error with LLM call: {str(e)}")
            return {}
    
    def _fallback_selection(self, context_info: Dict[str, Any]) -> Dict[str, str]:
        result = {}
        
        if "top" in context_info:
            if "casual" in context_info["top"]:
                result["top"] = context_info["top"]["casual"][0]["imageId"]
            elif "formal" in context_info["top"]:
                result["top"] = context_info["top"]["formal"][0]["imageId"]
            
        if "bottom" in context_info:
            if "casual" in context_info["bottom"]:
                result["bottom"] = context_info["bottom"]["casual"][0]["imageId"]
            elif "formal" in context_info["bottom"]:
                result["bottom"] = context_info["bottom"]["formal"][0]["imageId"]
            
        if "shoes" in context_info and context_info["shoes"]:
            result["shoes"] = context_info["shoes"][0]["imageId"]
            
        if "watch" in context_info and context_info["watch"]:
            result["watch"] = context_info["watch"][0]["imageId"]
            
        return result

    def generate_alternative_outfit(self, context_info: Dict[str, Any], current_outfit: Dict[str, str]) -> Dict[str, str]:
        """Generate an alternative outfit by randomly selecting from available options."""
        categories = ["top", "bottom", "shoes", "watch"]
        alt_outfit = current_outfit.copy()
    
        for category in categories:
             # Get available items for the category
            available_items = self.get_items_for_category(context_info, category)
        
            # Filter out the current item in the outfit
            alternative_items = [item for item in available_items if item != alt_outfit.get(category)]
        
            if alternative_items:
                # Randomly select an alternative item
                alt_outfit[category] = random.choice(alternative_items)
            else:
                print(f"No alternatives available for {category}")
    
        return alt_outfit

    def get_items_for_category(self, context_info: Dict[str, Any], category: str) -> List[str]:
        """Get all items available for a specific category."""
        items = []
    
        # Check if the category exists in context_info and it's a list
        if category in context_info:
            # Make sure it's a list and then extract the "imageId"
            if isinstance(context_info[category], list):
                items = [item["imageId"] for item in context_info[category] if isinstance(item, dict) and "imageId" in item]
            else:
                print(f"Warning: Expected a list for category '{category}', but got {type(context_info[category])}")
    
        return items


def load_json_file(filename: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return {}

def main():
    recommender = ClothingRecommender()
    
    # Load wardrobe data from a JSON file
    context_info = load_json_file('wardrobe.json')
    
    if not context_info:
        print("Failed to load wardrobe data.")
        return
    
    # Test multiple recommendations to see variation
    for i in range(3):
        result = recommender.recommend_outfit(context_info)
        print(f"Outfit {i+1}: {json.dumps(result, indent=2)}")
        
        # Generate alternative outfit for the current recommendation
        alt_outfit = recommender.generate_alternative_outfit(context_info, result)
        print(f"Alternative Outfit {i+1}: {json.dumps(alt_outfit, indent=2)}")

if __name__ == "__main__":
    main()
