import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import chromadb
import boto3
import uuid
from botocore.exceptions import NoCredentialsError

app = FastAPI()

# Ensure the directory exists
CHROMA_DB_PATH = "./data/chromadb"
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="clothing")

# Initialize S3 client
s3_client = boto3.client("s3")
BUCKET_NAME = "wics-cloth-recommender-images"


def upload_to_s3(file: UploadFile, file_name: str) -> str:
    """Uploads an image file to S3 and returns the image URL"""
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file_name, ExtraArgs={"ACL": "public-read"})
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found")


@app.post("/add_clothing")
async def add_clothing(
        file: UploadFile = File(...),
        type: str = Form(...),
        color: str = Form(...),
        style: str = Form(...),
        material: str = Form(None)  # Optional field
):
    """Uploads an image, stores metadata in ChromaDB"""
    item_id = str(uuid.uuid4())
    file_name = f"{item_id}_{file.filename}"

    # Upload image to S3
    image_url = upload_to_s3(file, file_name)

    # Store metadata in ChromaDB
    collection.add(
        ids=[item_id],
        metadatas=[{
            "type": type,
            "color": color,
            "style": style,
            "material": material if material else "",
            "image_url": image_url
        }]
    )

    return {"message": "Clothing item added successfully", "id": item_id, "image_url": image_url}


@app.get("/recommend")
def recommend():
    """Returns clothing recommendations based on predefined AI rules"""

    # Simulate AI-based filtering logic (modify as needed)
    results = collection.query(
        query_texts=["casual outfit suggestion"],  # Replace with actual AI-driven prompts
        n_results=3
    )

    recommendations = results.get("metadatas", [])
    return {"recommendations": recommendations}

@app.get("/list_clothing")
def list_clothing():
    """Fetch all clothing items stored in ChromaDB"""
    results = collection.get()
    return {"items": results}


# Run the app using the below command:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload