import boto3
import json
import random
from typing import Dict, Any, List


class ClothingRecommender:

    def __init__(self):
        self.model_id = 'arn:aws:bedrock:us-east-1:836537608680:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0'
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name='us-east-1',
            aws_access_key_id='AKIA4FRMG5HUOC65OWNV',
            aws_secret_access_key='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'
        )
        self.previous_outfits = []
        self.max_history = 3

    def recommend_outfit(self, context_info: Dict[str, Any]) -> Dict[str, str]:
        prompt = self._build_prompt(context_info)
        response = self._call_llm(prompt)

        if not response:
            return self._fallback_selection(context_info)

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

Return ONLY a JSON object with these keys: "top", "bottom", "shoes", "watch". For each key, provide ONLY the imageUrl.
Your response must be EXACTLY in this format: {{"top": "imageUrl", "bottom": "imageUrl", "shoes": "imageUrl", "watch": "imageUrl"}}
"""
        return prompt

    def _call_llm(self, prompt: str) -> Dict[str, str]:
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
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

            print(f"Raw LLM response: {response_text}")

            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                json_text = response_text[json_start:json_end]
                llm_response = json.loads(json_text)
            else:
                raise ValueError("No JSON object found in response")

            return {
                "top": llm_response.get("top"),
                "bottom": llm_response.get("bottom"),
                "shoes": llm_response.get("shoes"),
                "watch": llm_response.get("watch")
            }
        except Exception as e:
            print(f"Error with LLM call: {str(e)}")
            print(f"Failed to parse response: {response_text if 'response_text' in locals() else 'No response'}")
            return {
                "top": None,
                "bottom": None,
                "shoes": None,
                "watch": None
            }

    def _fallback_selection(self, context_info: Dict[str, Any]) -> Dict[str, str]:
        result = {
            "top": None,
            "bottom": None,
            "shoes": None,
            "watch": None
        }

        if "top" in context_info:
            if "casual" in context_info["top"]:
                result["top"] = context_info["top"]["casual"][0]["imageUrl"]
            elif "formal" in context_info["top"]:
                result["top"] = context_info["top"]["formal"][0]["imageUrl"]

        if "bottom" in context_info:
            if "casual" in context_info["bottom"]:
                result["bottom"] = context_info["bottom"]["casual"][0]["imageUrl"]
            elif "formal" in context_info["bottom"]:
                result["bottom"] = context_info["bottom"]["formal"][0]["imageUrl"]

        if "shoes" in context_info and context_info["shoes"]:
            result["shoes"] = context_info["shoes"][0]["imageUrl"]

        if "watch" in context_info and context_info["watch"]:
            result["watch"] = context_info["watch"][0]["imageUrl"]

        return result

    def generate_alternative_outfit(self, context_info: Dict[str, Any], current_outfit: Dict[str, str]) -> Dict[
        str, str]:
        """Generate an alternative outfit by randomly selecting from available options."""
        categories = ["top", "bottom", "shoes", "watch"]
        alt_outfit = current_outfit.copy()

        for category in categories:
            available_items = self.get_items_for_category(context_info, category)

            alternative_items = [item for item in available_items if item != alt_outfit.get(category)]

            if alternative_items:
                alt_outfit[category] = random.choice(alternative_items)
            else:
                print(f"No alternatives available for {category}")

        return alt_outfit

    def get_items_for_category(self, context_info: Dict[str, Any], category: str) -> List[str]:
        items = []

        if category in context_info:
            if isinstance(context_info[category], list):
                items = [item["imageUrl"] for item in context_info[category] if
                         isinstance(item, dict) and "imageUrl" in item]
            else:
                print(f"Warning: Expected a list for category '{category}', but got {type(context_info[category])}")

        return items

# AI help taken from perplexity.ai