# YouTube Data Harvesting and Warehousing

A full-stack data engineering and analytics application that harvests YouTube channel, video, playlist, and comment data via the YouTube Data API v3, stores it in a structured MySQL data warehouse, and provides an interactive Streamlit dashboard for querying and analysis.

## Table of Contents

- [Project Overview](#project-overview)
- [Technologies Used](#technologies-used)
- [Features](#features)
- [Database Schema](#database-schema)
- [Screenshots](#screenshots)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [SQL Queries Supported](#sql-queries-supported)
- [Ethical Considerations](#ethical-considerations)
- [References](#references)

## Project Overview

This project provides users with the ability to access and analyse data from multiple YouTube channels through a single unified interface. By entering a Channel ID, users can:
- Extract complete channel metadata, video statistics, playlists, and comments
- Store all data in a relational MySQL database
- Run 10 predefined analytical SQL queries via a Streamlit UI
- View results as formatted Pandas DataFrames in the browser

## Technologies Used
Technology                        Version         Purpose
1. **Python**                       3.9+          Core application language

| Technology                   | Version | Purpose |
| **Python**                   | 3.9+    | Core application language |
| **Streamlit**                | 1.x     | Interactive web UI |
| **YouTube Data API v3**      | v3      | Channel, video, playlist & comment extraction |
| **google-api-python-client** | latest  | Python client for Google APIs |
| **MySQL**                    | 8.0     | Relational data warehouse |
| **mysql-connector-python**   | latest  | Python–MySQL bridge |
| **Pandas**                   | 2.x     | Data manipulation and DataFrame display |

### Python Libraries Used (from source code)
```python
import streamlit as st
from googleapiclient.discovery import build
import mysql.connector
import pandas as pd
```
## Features
- **Channel Data Extraction** — Retrieves channel ID, name, description, upload playlist, video count, view count, and subscriber count
- **Video Data Extraction** — Fetches up to 50 videos per API call with full metadata: title, description, publish date, tags, views, likes, favourites,   comment count, duration, and caption status
- **Comment Extraction** — Collects top-level comments (up to 100 per video) with author name, text, and publish date
- **Playlist Extraction** — Retrieves all playlists for a channel with title, video count, and publish date
- **MySQL Data Warehouse** — Stores all data in 4 normalized, relational tables with foreign key constraints
- **Duplicate Detection** — Checks if a channel already exists in the database before inserting
- **10 Analytical SQL Queries** — Predefined queries answerable directly from the Streamlit dropdown
- **Multi-channel Support** — Batch-insert data for up to 10+ channels simultaneously

## Database Schema
```Youtube_Harvesting_Project
│
├── Channels
│   ├── channel_id (PK)
│   ├── channel_name
│   ├── channel_des
│   ├── Playlist_Ids
│   ├── channel_vc
│   ├── channel_viewc
│   └── channel_sub
│
├── Playlist
│   ├── Playlist_Ids (PK)
│   ├── Title
│   ├── channel_id (FK → Channels)
│   ├── channel_name
│   ├── PublishedAt
│   └── Video_Count
│
├── Videos
│   ├── video_id (PK)
│   ├── channel_id (FK → Channels)
│   ├── video_name
│   ├── video_description
│   ├── video_publishedAt
│   ├── video_thumbnails
│   ├── video_tags
│   ├── video_views
│   ├── video_likes
│   ├── video_favorite
│   ├── comment_count
│   ├── video_duration
│   └── video_caption
│
└── Comment
    ├── comment_id (PK)
    ├── video_id (FK → Videos)
    ├── author_name
    ├── text
    └── comment_publishedAt
```
## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- MySQL Server 8.0+
- A Google Cloud account with YouTube Data API v3 enabled

### Step 1 — Clone the Repository
```bash
git clone https://github.com/abhi-1009/YouTube-Data-Harvesting.git
cd YouTube-Data-Harvesting
```
### Step 2 — Install Required Libraries
```bash
pip install streamlit pandas google-api-python-client mysql-connector-python
```
### Step 3 — Set Up Google API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → Enable **YouTube Data API v3**
3. Generate an **API Key** under Credentials
4. Replace the placeholder in the code:
```python
Api_Id = "YOUR_YOUTUBE_API_KEY_HERE"
```
### Step 4 — Configure MySQL
1. Start your MySQL server
2. Update the connection credentials in the code:
```python
mydb = mysql.connector.connect(
    host='localhost',
    user='your_username',
    password='your_password'
)
```
3. The database `Youtube_Harvesting_Project` and all 4 tables are created automatically on first run

### Step 5 — Run the Application
```bash
streamlit run youtube_harvesting.py
```

Open your browser at `http://localhost:8501`

## Usage
1. **Enter a YouTube Channel ID** in the text input field
2. Click **Migrate to SQL** to extract and store all channel data
3. Use the **Radio button** to select which table to view (Channels / Playlists / Videos / Comments)
4. Click **Collect & Show Data** to display the table for that channel
5. Select any question from the **dropdown** to run a predefined SQL analytical query

## SQL Queries Supported

| Q1   | Names of all videos and their corresponding channels |
| Q2   | Channels with the most number of videos |
| Q3   | Top 10 most viewed videos and their channels |
| Q4   | Number of comments on each video |
| Q5   | Videos with the highest number of likes |
| Q6   | Total likes for each video |
| Q7   | Total views for each channel |
| Q8   | Channels that published videos in a specific year |
| Q9   | Average duration of videos per channel |
| Q10  | Videos with the highest number of comments |

## Ethical Considerations
This project follows responsible data collection practices:
- Uses the **official YouTube Data API v3** — no scraping of HTML/DOM
- Respects YouTube's **Terms of Service** and API usage quotas
- Collected data is used **purely for analytical purposes**
- No personally identifiable information (PII) is stored beyond what the public YouTube API returns
- API keys are not hardcoded in production — use environment variables
```python
import os
Api_Id = os.environ.get("YOUTUBE_API_KEY")
```

## References
- [Streamlit Documentation](https://docs.streamlit.io/)
- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Python Documentation](https://docs.python.org/)
- [MySQL Connector Python](https://dev.mysql.com/doc/connector-python/en/)

## Author
**Abhijit Sinha**
- GitHub: [@abhi-1009](https://github.com/abhi-1009)
- LinkedIn: [abhijit-sinha-053b159a](https://linkedin.com/in/abhijit-sinha-053b159a)
- Email: sinhaabhijit12@yahoo.com
