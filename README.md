# Backend Clothing Recommendation System

## Description
This is a backend system for a clothing recommendation app designed for a hackathon. The app allows a user to upload images of clothes, and based on predefined AI rules, it provides clothing recommendations via a GET request.

## Features
- **Image Upload**: Users can upload images of clothes, which are stored in AWS S3.
- **Metadata Storage**: Information such as item ID, type, color, style, material, and image URL is stored in PostgreSQL.
- **Recommendations**: The app generates clothing recommendations based on predefined AI rules when a user clicks a button.
- **API Endpoints**:
  - **POST** `/upload`: Uploads an image and stores metadata.
  - **GET** `/recommendations`: Retrieves clothing recommendations based on the stored items.

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Image Storage**: AWS S3
- **Recommendation Engine**: AI-based rules for generating suggestions

## Setup Instructions

### 1. Install Dependencies
Make sure you have Python 3.8+ and `pip` installed.

### 2. Install Postgresql in local or in an EC2 instance

### 3. Replace AWS secret key with the working ones
Use environment variables

### 4. Run the app
Run it via python3 main.py or if you want it running all the time: use the command `nohup python3 main.py > flask_app.log 2>&1 &`
