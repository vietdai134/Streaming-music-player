from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
ytb_api=os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=ytb_api)



class AppStatus:
    selected_songs = []
    history_songs = []
    select=False
    next = False
    previous = False
    start_time = None
    time_song = None
    audio = None
    pause = False
    volume=False
    volume_audio=None
    volume_value=100
    slide=False
    current_value=0
    stop_threads = False
    
    stop_video=False
    
    right_frame=False
    
    song_select=None