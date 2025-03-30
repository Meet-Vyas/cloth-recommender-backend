from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import chromadb
import boto3
import uuid
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
from typing import Optional
from llm import ClothingRecommender

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
chroma_client = chromadb.PersistentClient(path=os.getenv("CHROMA_DB_PATH", "/tmp/chroma"))
collection = chroma_client.get_or_create_collection(name="clothing")

# Initialize AWS clients
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-2")
)
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "wics-cloth-recommender-images")

# Initialize recommender
recommender = ClothingRecommender()

# Models
class RecommendationRequest(BaseModel):
    weather: str
    style: Optional[str] = None
    occasion: Optional[str] = None

class ClothingItem(BaseModel):
    type: str
    color: str
    style: str
    material: Optional[str] = None
    image_url: str

def upload_to_s3(file: UploadFile, file_name: str) -> str:
    """Uploads an image file to S3 and returns the image URL"""
    try:
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file_name,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_clothing")
async def add_clothing(
    file: UploadFile = File(...),
    type: str = Form(...),
    color: str = Form(...),
    style: str = Form(...),
    material: str = Form(None)
):
    """Uploads an image, stores metadata in ChromaDB"""
    try:
        item_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_name = f"{item_id}{file_extension}"

        # Upload image to S3
        image_url = upload_to_s3(file, file_name)

        # Store metadata in ChromaDB
        collection.add(
            ids=[item_id],
            documents=[f"{type} {color} {style}"],
            metadatas=[{
                "type": type,
                "color": color,
                "style": style,
                "material": material or "",
                "image_url": image_url
            }]
        )

        return {
            "message": "Clothing item added successfully",
            "id": item_id,
            "image_url": image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend")
async def recommend_outfit(request: RecommendationRequest):
    """Generate outfit recommendations based on weather and preferences"""
    try:
        # Create input data structure for the recommender
        input_data = {
            "weather": request.weather,
            "style": request.style,
            "occasion": request.occasion
        }

        # Get recommendations from the LLM
        recommendation = recommender.process_request(input_data)

        # Get full item details from ChromaDB
        full_recommendations = {}
        for category, image_id in recommendation.items():
            if image_id:
                # Extract ID from image URL (assuming format "https://.../ID.jpg")
                item_id = os.path.splitext(os.path.basename(image_id))[0].split('_')[0]
                item = collection.get(ids=[item_id])
                if item and len(item['metadatas']) > 0:
                    full_recommendations[category] = item['metadatas'][0]

        return {
            "status": "success",
            "data": full_recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_clothing")
async def list_clothing():
    """Fetch all clothing items stored in ChromaDB"""
    try:
        results = collection.get()
        return {"items": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))