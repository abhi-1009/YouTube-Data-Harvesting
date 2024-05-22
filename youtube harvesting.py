import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import mysql.connector
import datetime

# API key connection
def Api_connect():
    Api_Id = "-----------"
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=Api_Id)
    return youtube

youtube = Api_connect()

def get_channel_info(youtube, channel_Ids):
    data_list = []
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_Ids)
    )
    response = request.execute()
    for item in response['items']:
        try:
            data = {
                'channel_id': item['id'],
                'channel_name': item['snippet']['title'],
                'channel_des': item['snippet']['description'],
                'Playlist_Ids': item['contentDetails']['relatedPlaylists']['uploads'],
                'channel_vc': item['statistics']['videoCount'],
                'channel_viewc': item['statistics']['viewCount'],
                'channel_sub': item['statistics']['subscriberCount']
            }
            data_list.append(data)
        except Exception as e:
            st.error(f"An error occurred while processing channel {item['id']}: {e}")
    return data_list

def get_video_ids(youtube, channel_Id):
    video_ids = []
    try:
        response = youtube.channels().list(id=channel_Id, part='contentDetails').execute()
        playlist_Ids = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        next_page_token = None
        while True:
            try:
                response1 = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_Ids,
                    maxResults=50,
                    pageToken=next_page_token).execute()
                for i in range(len(response1['items'])):
                    video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
                next_page_token = response1.get('nextPageToken')
                if next_page_token is None:
                    break
            except Exception as e:
                print(f"An error occurred while processing playlist items: {e}")
                break
    except Exception as e:
        print(f"An error occurred while processing channel {channel_Id}: {e}")
    return video_ids

def get_video_details(youtube, video_Ids, channel_Id):
    all_video_stats = []
    for i in range(0, len(video_Ids), 50):
        try:
            request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_Ids[i:i+50])
            )
            response = request.execute()
            for video in response['items']:
                try:
                    video_stats = {
                        'video_id': video['id'],
                        'channel_id': channel_Id,
                        'video_name': video['snippet']['title'],
                        'video_description': video['snippet']['description'],
                        'video_publishedAt': video['snippet']['publishedAt'].split('T')[0],
                        'video_thumbnails': video['snippet']['thumbnails']['default']['url'],
                        'video_tags': ','.join(video['snippet'].get('tags', [])),
                        'video_views': int(video['statistics'].get('viewCount', 0)),
                        'video_likes': int(video['statistics'].get('likeCount', 0)),
                        'video_favorite': int(video['statistics'].get('favoriteCount', 0)),
                        'comment_count': int(video['statistics'].get('commentCount', 0)),
                        'video_duration': video['contentDetails']['duration'],
                        'video_caption': video['contentDetails'].get('caption', '')
                    }
                    all_video_stats.append(video_stats)
                except Exception as e:
                    print(f"An error occurred while processing video {video['id']}: {e}")
        except Exception as e:
            print(f"An error occurred while retrieving video details: {e}")
    return all_video_stats

def get_comments(youtube, video_Ids):
    all_comment_stats = []
    for video_id in video_Ids:
        try:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100
            )
            response = request.execute()
            for item in response['items']:
                try:
                    topLevelComment = item['snippet']['topLevelComment']
                    comment = {
                        "comment_id": topLevelComment['id'],
                        "video_id": video_id,
                        "author_name": topLevelComment['snippet']['authorDisplayName'],
                        "text": topLevelComment['snippet']['textOriginal'],
                        "comment_publishedAt": topLevelComment['snippet']['publishedAt'].split('T')[0]
                    }
                    all_comment_stats.append(comment)
                except Exception as e:
                    print(f"An error occurred while processing comment {item['id']}: {e}")
        except Exception as e:
            print(f"An error occurred while retrieving comments for video {video_id}: {e}")
    return all_comment_stats

def get_playlist_details(youtube, channel_Id):
    next_page_token = None
    Playlist = []
    while True:
        try:
            request = youtube.playlists().list(
                part='snippet,contentDetails',
                channelId=channel_Id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response['items']:
                try:
                    data = {
                        'Playlist_Ids': item['id'],
                        'Title': item['snippet']['title'],
                        'channel_id': item['snippet']['channelId'],
                        'channel_name': item['snippet']['channelTitle'],
                        'PublishedAt': item['snippet']['publishedAt'].split('T')[0],
                        'Video_Count': item['contentDetails']['itemCount']
                    }
                    Playlist.append(data)
                except Exception as e:
                    print(f"An error occurred while processing playlist {item['id']}: {e}")
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
        except Exception as e:
            print(f"An error occurred while retrieving playlists for channel {channel_Id}: {e}")
            break
    return Playlist

def create_tables():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abhi@100982',
        database='Youtube_Project'
    )
    mycursor = mydb.cursor()
    
    # Create Channels table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Channels (
                        channel_id VARCHAR(255) PRIMARY KEY,
                        channel_name VARCHAR(255),
                        channel_des TEXT,
                        Playlist_Ids VARCHAR(255),
                        channel_vc INT,
                        channel_viewc INT,
                        channel_sub INT
                        )""")
    
    # Create Playlist table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Playlist (
                        Playlist_Ids VARCHAR(255) PRIMARY KEY,
                        Title VARCHAR(255),
                        channel_id VARCHAR(255),
                        channel_name VARCHAR(255),
                        PublishedAt DATE,
                        Video_Count INT,
                        FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
                        )""")
    
    # Create Videos table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Videos (
                        video_id VARCHAR(255) PRIMARY KEY,
                        channel_id VARCHAR(255),
                        video_name VARCHAR(255),
                        video_description TEXT,
                        video_publishedAt DATE,
                        video_thumbnails VARCHAR(255),
                        video_tags TEXT,
                        video_views INT,
                        video_likes INT,
                        video_favorite INT,
                        comment_count INT,
                        video_duration VARCHAR(255),
                        video_caption VARCHAR(255),
                        FOREIGN KEY (channel_id) REFERENCES Channels(channel_id)
                        )""")
    
    # Create Comments table
    mycursor.execute("""CREATE TABLE IF NOT EXISTS Comment (
                        comment_id VARCHAR(255) PRIMARY KEY,
                        video_id VARCHAR(255),
                        author_name VARCHAR(255),
                        text TEXT,
                        comment_publishedAt DATE,
                        FOREIGN KEY (video_id) REFERENCES Videos(video_id)
                        )""")
    
    mydb.commit()
    mydb.close()

def store_channel_data(channels):
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Abhi@100982',
            database='Youtube_Project'
        )
        mycursor = mydb.cursor()
        
        insert_query = """INSERT INTO Channels (channel_id, channel_name, channel_des, Playlist_Ids, channel_vc, channel_viewc, channel_sub) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values_list = []
        for channel in channels:
            values = (
                channel['channel_id'],
                channel['channel_name'],
                channel['channel_des'],
                channel['Playlist_Ids'],
                channel['channel_vc'],
                channel['channel_viewc'],
                channel['channel_sub']
            )
            values_list.append(values)
        
        mycursor.executemany(insert_query, values_list)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"An error occurred while storing channel data: {err}")
    finally:
        mydb.close()

def store_playlist_data(playlists):
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Abhi@100982',
            database='Youtube_Project'
        )
        mycursor = mydb.cursor()
        
        insert_query = """INSERT INTO Playlist (Playlist_Ids, Title, channel_id, channel_name, PublishedAt, Video_Count) 
                          VALUES (%s, %s, %s, %s, %s, %s)"""
        values_list = []
        for playlist in playlists:
            values = (
                playlist['Playlist_Ids'],
                playlist['Title'],
                playlist['channel_id'],
                playlist['channel_name'],
                playlist['PublishedAt'],
                playlist['Video_Count']
            )
            values_list.append(values)
        
        mycursor.executemany(insert_query, values_list)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"An error occurred while storing playlist data: {err}")
    finally:
        mydb.close()

def store_video_data(videos):
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Abhi@100982',
            database='Youtube_Project'
        )
        mycursor = mydb.cursor()
        
        insert_query = """INSERT INTO Videos (video_id, channel_id, video_name, video_description, video_publishedAt, video_thumbnails, video_tags, video_views, video_likes, video_favorite, comment_count, video_duration, video_caption) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values_list = []
        for video in videos:
            values = (
                video['video_id'],
                video['channel_id'],
                video['video_name'],
                video['video_description'],
                video['video_publishedAt'],
                video['video_thumbnails'],
                video['video_tags'],
                video['video_views'],
                video['video_likes'],
                video['video_favorite'],
                video['comment_count'],
                video['video_duration'],
                video['video_caption']
            )
            values_list.append(values)
        
        mycursor.executemany(insert_query, values_list)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"An error occurred while storing video data: {err}")
    finally:
        mydb.close()

def store_comment_data(comments):
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Abhi@100982',
            database='Youtube_Project'
        )
        mycursor = mydb.cursor()
        
        insert_query = """INSERT INTO Comment (comment_id, video_id, author_name, text, comment_publishedAt) 
                          VALUES (%s, %s, %s, %s, %s)"""
        values_list = []
        for comment in comments:
            values = (
                comment['comment_id'],
                comment['video_id'],
                comment['author_name'],
                comment['text'],
                comment['comment_publishedAt']
            )
            values_list.append(values)
        
        mycursor.executemany(insert_query, values_list)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"An error occurred while storing comment data: {err}")
    finally:
        mydb.close()
        
def insert_data(channel_ids):
    if channel_ids:
        create_tables()
        
        # Get and store channel data
        try:
            channel_data = get_channel_info(youtube, channel_ids)
            store_channel_data(channel_data)
        except Exception as e:
            print(f"An error occurred while retrieving or storing channel data: {e}")
        
        # Get and store playlist data for each channel
        for channel_id in channel_ids:
            try:
                playlist_data = get_playlist_details(youtube, channel_id)
                store_playlist_data(playlist_data)
            except Exception as e:
                print(f"An error occurred while retrieving or storing playlist data for channel {channel_id}: {e}")
        
        # Get and store video and comment data for each channel
        for channel_id in channel_ids:
            try:
                video_ids = get_video_ids(youtube, channel_id)
                video_data = get_video_details(youtube, video_ids, channel_id)
                store_video_data(video_data)
                
                comment_data = get_comments(youtube, video_ids)
                store_comment_data(comment_data)
            except Exception as e:
                print(f"An error occurred while retrieving or storing video/comment data for channel {channel_id}: {e}")
    else:
        print('Please enter valid YouTube Channel IDs.')
def view_channel_details(channel_ids):
    channel_data = get_channel_info(youtube, channel_ids)
    return channel_data
insert_data(["UCxTFPM1NYtPVk1jBwUMJcnw","UCEz0tA0xcXp-XRvRu-ZP0tA","UCxC5Ls6DwqV0e-CYcAKkExQ","UCQP57evqzgtzEcEq8neFOiw",
               "UCOnF_609TSdgcXurRRrJXIg","UClga3ybuyyjpvqsh-cf3DvQ","UCqaFXphJatlJEv2WfLtC-eg","UCmpQxK37UZ5TuDa61AZL8Yw",
               "UCn1XnDWhsLS5URXTi5wtFTA","UC5eAy9_AKthxQT7qafKcgCQ"])

 
# Streamlit UI
def tables():
    return
import streamlit as st
with st.sidebar:
    st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("Skill Take Away")
    st.caption("Python Scripting")
    st.caption("Data Collection")
    st.caption("API Integration")
    st.caption("Data Management using SQL")

st.title("YOUTUBE DATA HARVESTING AND WAREHOUSING")
channel_id = st.text_input("Enter the channel ID")


if st.button("Collect & Show Data"):
    if channel_id:
        channel_ids = [id.strip() for id in channel_id.split(",")]
        all_channel_data = []
        for cid in channel_ids:
            channel_data = view_channel_details([cid])
            all_channel_data.extend(channel_data)
        if all_channel_data:
            st.success("Channel data retrieved successfully")
            st.write("Channel Data:")
            st.write(all_channel_data)
    else:
        st.error("Please enter a channel ID")
    st.success("Table created successfully")

if st.button("Migrate to SQL"):
    if channel_id:
        channel_ids = [id.strip() for id in channel_id.split(",")]
        for cid in channel_ids:
            insert_data([cid])
        st.success("Channel data migrated successfully")
    else:
        st.error("Please enter a channel ID")
try:
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abhi@100982',
        database='Youtube_Project'
    )
    mycursor = mydb.cursor()

    question = st.selectbox("Select your question", (
        "Q1-What are the names of all the videos and their corresponding channels",
        "Q2-Which channels have the most number of videos, and how many videos do they have",
        "Q3-What are the top 10 most viewed videos and their respective channels",
        "Q4-How many comments were made on each video with their corresponding video names",
        "Q5-Which videos have the highest number of likes with their corresponding channel names",
        "Q6-What is the total number of likes for each video with their corresponding video names",
        "Q7-What is the total number of views for each channel with their corresponding channel names",
        "Q8-What are the names of all the channels that have published videos in the particular year",
        "Q9-What is the average duration of all videos in each channel with corresponding channel names",
        "Q10-Which videos have the highest number of comments with their corresponding channel names"
    ))

    if question == "Q1-What are the names of all the videos and their corresponding channels":
        query1 = '''
        SELECT v.video_name AS video_title, c.channel_name AS channel_name
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        '''
        mycursor.execute(query1)
        t1 = mycursor.fetchall()
        df = pd.DataFrame(t1, columns=["video title", "channel name"])
        st.write(df)

    elif question == "Q2-Which channels have the most number of videos, and how many videos do they have":
        query2 = '''
        SELECT c.channel_name AS channel_name, COUNT(v.video_id) AS no_videos
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        GROUP BY c.channel_name
        ORDER BY no_videos DESC
        '''
        mycursor.execute(query2)
        t2 = mycursor.fetchall()
        df2 = pd.DataFrame(t2, columns=["channel name", "No of videos"])
        st.write(df2)

    elif question == "Q3-What are the top 10 most viewed videos and their respective channels":
        query3 = '''
        SELECT v.video_views AS views, c.channel_name AS channel_name, v.video_name AS video_title
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        WHERE v.video_views IS NOT NULL
        ORDER BY v.video_views DESC
        LIMIT 10
        '''
        mycursor.execute(query3)
        t3 = mycursor.fetchall()
        df3 = pd.DataFrame(t3, columns=["views", "channel name", "video title"])
        st.write(df3)

    elif question == "Q4-How many comments were made on each video with their corresponding video names":
        query4 = '''
        SELECT v.comment_count AS no_comments, v.video_name AS video_title
        FROM Videos v
        WHERE v.comment_count IS NOT NULL
        '''
        mycursor.execute(query4)
        t4 = mycursor.fetchall()
        df4 = pd.DataFrame(t4, columns=["no of comments", "video title"])
        st.write(df4)

    elif question == "Q5-Which videos have the highest number of likes with their corresponding channel names":
        query5 = '''
        SELECT v.video_name AS video_title, c.channel_name AS channel_name, v.video_likes AS like_count
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        WHERE v.video_likes IS NOT NULL
        ORDER BY v.video_likes DESC
        '''
        mycursor.execute(query5)
        t5 = mycursor.fetchall()
        df5 = pd.DataFrame(t5, columns=["video title", "channel name", "like count"])
        st.write(df5)

    elif question == "Q6-What is the total number of likes for each video with their corresponding video names":
        query6 = '''
        SELECT v.video_likes AS like_count, v.video_name AS video_title
        FROM Videos v
        '''
        mycursor.execute(query6)
        t6 = mycursor.fetchall()
        df6 = pd.DataFrame(t6, columns=["like count", "video title"])
        st.write(df6)

    elif question == "Q7-What is the total number of views for each channel with their corresponding channel names":
        query7 = '''
        SELECT c.channel_name AS channel_name, SUM(v.video_views) AS total_views
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        GROUP BY c.channel_name
        '''
        mycursor.execute(query7)
        t7 = mycursor.fetchall()
        df7 = pd.DataFrame(t7, columns=["channel name", "total views"])
        st.write(df7)

    elif question == "Q8-What are the names of all the channels that have published videos in the particular year":
        query8 = '''
        SELECT c.channel_name AS channel_name
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        WHERE EXTRACT(YEAR FROM v.video_publishedAt) = 2023
        '''
        mycursor.execute(query8)
        t8 = mycursor.fetchall()
        df8 = pd.DataFrame(t8, columns=["channel name"])
        st.write(df8)

    elif question == "Q9-What is the average duration of all videos in each channel with corresponding channel names":
        query9 = '''
        SELECT c.channel_name AS channel_name, AVG(v.video_duration) AS average_duration
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        GROUP BY c.channel_name
        '''
        mycursor.execute(query9)
        t9 = mycursor.fetchall()
        df9 = pd.DataFrame(t9, columns=["channel name", "average duration"])
        st.write(df9)

    elif question == "Q10-Which videos have the highest number of comments with their corresponding channel names":
        query10 = '''
        SELECT v.video_name AS video_title, c.channel_name AS channel_name, v.comment_count AS comments
        FROM Videos v
        JOIN Channels c ON v.channel_id = c.channel_id
        WHERE v.comment_count IS NOT NULL
        ORDER BY v.comment_count DESC
        '''
        mycursor.execute(query10)
        t10 = mycursor.fetchall()
        df10 = pd.DataFrame(t10, columns=["video title", "channel name", "comments"])
        st.write(df10)

except mysql.connector.Error as err:
    st.error(f"Error connecting to MySQL Platform: {err}")
finally:
    if mydb.is_connected():
        mycursor.close()
        mydb.close()
        st.info("MySQL connection is closed")
