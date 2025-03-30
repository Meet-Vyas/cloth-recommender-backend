import json
import os
import uuid

import boto3
import psycopg2
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from llm import ClothingRecommender

app = Flask(__name__)

# Database connection settings (local PostgreSQL)
DB_HOST = 'localhost'
DB_NAME = 'myappdb'
DB_USER = 'meet'
DB_PASS = '123'

# S3 Bucket name placeholder (Replace when deploying)
BUCKET_NAME = "wics-cloth-recommender-images"

# AWS Credentials (for development purposes, replace with your actual keys)
AWS_ACCESS_KEY_ID = 'AKIA4FRMG5HUOC65OWNV'
AWS_SECRET_ACCESS_KEY = 'lb1ZJkk6qbTAzTEsXhkjW5Qet5Rj7hu/JcItTs/x'

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("Database connection established")
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def check_s3_connection():
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"Successfully connected to S3 bucket: {BUCKET_NAME}")
        return True
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"S3 credentials error: {e}")
        return False
    except Exception as e:
        print(f"Error connecting to S3: {e}")
        return False

# Check PostgreSQL connection
db_connection = connect_to_db()
if not db_connection:
    print("Failed to connect to PostgreSQL database. Exiting...")
    exit(1)

# Check S3 connection
if not check_s3_connection():
    print("Failed to connect to S3 storage. Exiting...")
    exit(1)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Extract form data
        style = request.form['style']
        type_ = request.form['type']
        weather = request.form['weather']
        user_id = request.form['userId']
        category = request.form['category']
        color = request.form['color']
        image = request.files['image']

        # Generate unique image ID
        image_id = str(uuid.uuid4())
        filename = secure_filename(image_id)  # No extension restriction

        # Define storage path
        image_path = f"{BUCKET_NAME}/{user_id}/{style}/{type_}/{category}/{filename}"

        # Save the file locally (for now)
        local_folder = f"uploads/{user_id}/{style}/{type_}/{category}"
        os.makedirs(local_folder, exist_ok=True)
        image.save(os.path.join(local_folder, filename))

        # Store in PostgreSQL
        conn = connect_to_db()
        if conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO clothing_items (image_id, style, type, weather, user_id, category, color, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (image_id, style, type_, weather, user_id, category, color, image_path)
            )
            conn.commit()
            cur.close()
            conn.close()
        else:
            return jsonify({"error": "Database connection failed"}), 500

        return jsonify({"message": "Image uploaded successfully", "image_id": image_id, "image_url": image_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/recommend', methods=['GET'])
def get_recommendations():
    try:
        # Extract query parameters
        weather = request.args.get('weather')
        user_id = request.args.get('userId')
        style = request.args.get('style', None)  # Optional style parameter

        if user_id != "123":
            return jsonify({"error": "Invalid user"}), 400

        # Check if required parameters are present
        if not weather or not user_id:
            return jsonify({"error": "Missing required parameters"}), 400

        # Connect to the database
        conn = connect_to_db()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cur = conn.cursor()

        # Query clothing items for the given weather, user and optional style
        query = """
        SELECT style, type, category, color, image_id
        FROM clothing_items
        WHERE weather = %s AND user_id = %s
        """

        if style:
            query += " AND style = %s"
            cur.execute(query, (weather, user_id, style))
        else:
            cur.execute(query, (weather, user_id))

        rows = cur.fetchall()
        conn.close()

        # Generate recommendations JSON
        recommendations = {
            "weather": weather,
            "top": {},
            "bottom": {},
            "shoes": [],
            "watch": []
        }

        # Organize clothing items into the appropriate categories
        for row in rows:
            style = row[0]
            item_type = row[1]
            category = row[2]
            color = row[3]
            image_id = row[4]

            # Add items to the appropriate category
            if item_type == "top":
                if style not in recommendations["top"]:
                    recommendations["top"][style] = []
                recommendations["top"][style].append({
                    "category": category,
                    "color": color,
                    "imageId": image_id
                })
            elif item_type == "bottom":
                if style not in recommendations["bottom"]:
                    recommendations["bottom"][style] = []
                recommendations["bottom"][style].append({
                    "category": category,
                    "color": color,
                    "imageId": image_id
                })
            elif item_type == "shoes":
                recommendations["shoes"].append({
                    "category": category,
                    "color": color,
                    "imageId": image_id
                })
            elif item_type == "watch":
                recommendations["watch"].append({
                    "category": category,
                    "color": color,
                    "imageId": image_id
                })

        recommender = ClothingRecommender()
        result = recommender.recommend_outfit(recommendations)
        print(json.dumps(result))

        # Return the recommendations as JSON
        return jsonify(recommendations)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
