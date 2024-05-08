import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
from pydub import AudioSegment
import sounddevice as sd
import threading
import io
import numpy as np
import urllib.request
from PIL import Image
import time 
from datetime import datetime
from appStatus import *
import vlc
from pynput.keyboard import Key, Listener 
import customtkinter
import random

def initialize_gui_variables(next_btn, prev_btn, pause_resume_btn,
                             entry_field, inner_frm,footer_frm, 
                             vlume_scale,sld_scale,tme_label,
                             img_label,titl_label,iner_playlist_frame,lft_frame,ply_video_btn,iner_album_frame):
    global next_button, previous_button, pause_resume_button
    global entry, inner_frame,footer_frame ,volume_scale,slide_scale,time_label
    global image_label,title_label,inner_playlist_frame,left_frame,play_video_btn,inner_album_frame
    next_button = next_btn
    previous_button = prev_btn
    pause_resume_button = pause_resume_btn
    entry = entry_field
    inner_frame = inner_frm
    footer_frame=footer_frm

    volume_scale=vlume_scale
    slide_scale=sld_scale
    time_label=tme_label
    image_label=img_label
    title_label=titl_label
    inner_playlist_frame=iner_playlist_frame
    left_frame=lft_frame
    play_video_btn=ply_video_btn
    inner_album_frame=iner_album_frame

    
def time_to_seconds(time_string):
    time_obj = datetime.strptime(time_string, "%H:%M:%S")
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    return total_seconds

def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
    else:
        return "{:02d}:{:02d}".format(int(minutes), int(seconds))

def get_duration_play():
    elapsed_time = time.time() - AppStatus.start_time
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    return formatted_time

def check_state_pause():
    if len(AppStatus.selected_songs)==0:
        pause_resume_button.configure(state=tk.DISABLED)
    else:
        pause_resume_button.configure(state=tk.NORMAL)
        
def check_state_next():
    if len(AppStatus.selected_songs)<2 or len(AppStatus.history_songs)==len(AppStatus.selected_songs)-1:
        next_button.configure(state=tk.DISABLED)
    else:
        next_button.configure(state=tk.NORMAL)
            
def check_state_previous():
    if len(AppStatus.history_songs)==0:
        previous_button.configure(state=tk.DISABLED)
    else:
        previous_button.configure(state=tk.NORMAL)
               
def check_thread_by_name(thread_name):
    for thread in threading.enumerate():
        if thread.name == thread_name:
            return True
    return False

def check_song_url(song_url):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "audio_info.txt"
    file_path = os.path.join(current_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if song_url in line:
                return True
    return False


def check_file_txt(album_name):
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
    txt_files = [file for file in os.listdir(current_dir) if file.endswith(".txt")]
    for file in txt_files:
        if album_name.lower() == file.replace("_album.txt", "").lower():
            return True
    return False

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def display_random_songs():
    list_songs = get_random_song()
    for widget in inner_frame.winfo_children():
            widget.destroy() 
    for song_info in list_songs:
        song_url, video_title, thumbnail_url = song_info
        with urllib.request.urlopen(thumbnail_url) as response:
            image_data = response.read()
        image = Image.open(io.BytesIO(image_data))
        thumbnail_image = customtkinter.CTkImage(image,size=(120,90))
        
        button_frame = customtkinter.CTkFrame(inner_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        sub_button = customtkinter.CTkButton(button_frame,text="+", compound=tk.LEFT, width=30)
        sub_button.pack(side="left")
        sub_button.configure(command=lambda url=song_url,title=video_title, thumbnail=thumbnail_url: add_to_album(url,title,thumbnail) )
        
        song_button = customtkinter.CTkButton(button_frame, compound=tk.LEFT)
        song_button.pack(side="left",fill="x",expand=True)
        song_button.image = thumbnail_image
        
        song_button.configure(image=thumbnail_image,font=("Arial", 13,"bold"), anchor="w", text=video_title, command=lambda url=song_url: add_to_playlist(url))      
    inner_frame.update_idletasks()

def get_random_song():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "audio_info.txt"
    file_path = os.path.join(current_dir, file_name)
    
    random_songs=[]
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        
        # Check if there are at least 10 lines in the file
        if len(lines) >= 10:
            # Select 10 random lines
            random_lines = random.sample(lines, 10)
        else:
            # If there are less than 10 lines, select all lines
            random_lines = lines
            
        for line in random_lines:
            parts = line.strip().split(" **** ") 
            song_url=parts[0]
            video_title = parts[1]  
            thumbnail_url = parts[2]  
            random_songs.append((song_url,video_title, thumbnail_url))  
    return random_songs

def on_press(key):
    if key == Key.esc:
        AppStatus.stop_video=True
        AppStatus.pause=False
        pause_resume()
        AppStatus.current_value = slide_scale.get()
        start_position_ms = slide_scale.get() * 1000 
        trimmed_audio_segment = AppStatus.volume_audio[start_position_ms:]
        AppStatus.audio = trimmed_audio_segment
     
def key_listener():
    while not AppStatus.stop_threads:
        if AppStatus.stop_threads:
            break
        with Listener(on_press=on_press) as listener:
            listener.join()
            
        
def play_video_vlc(song_url):
    while not AppStatus.stop_threads:
        if AppStatus.stop_threads:
            AppStatus.pause=False
            break
        yt = YouTube(song_url)
        mp4_streams=yt.streams.filter(file_extension='mp4',progressive=True).order_by('resolution').desc()
        
        selected_stream = None
        for stream in mp4_streams:
            if stream.resolution >= "1080p":
                selected_stream = stream
                break
            elif stream.resolution >= "720p":
                selected_stream = stream 
            elif not selected_stream:
                selected_stream = stream
        if selected_stream:
            if not check_thread_by_name("key_thread"):
                AppStatus.stop_threads=False
                listener_thread = threading.Thread(target=key_listener,name="key_thread")
                listener_thread.start()
                
            vlc_instance = vlc.Instance("--no-xlib")
            player = vlc_instance.media_player_new()
            media = vlc_instance.media_new(selected_stream.url)
            media.add_option(':aspect-ratio=16:9')
            media.add_option(f'start-time={slide_scale.get()}')
            volume_value = int(volume_scale.get()) 
           
            player.audio_set_volume(volume_value)
            
            player.set_media(media)
            player.set_fullscreen(False)
            player.play()   
            
            value=slide_scale.get()
            while value<AppStatus.volume_audio.duration_seconds-1:
                if AppStatus.stop_video  or AppStatus.previous or AppStatus.next :
                    AppStatus.stop_threads=True
                    
                    break
                value=value+1
                slide_scale.set(value)
                time_label.configure(text=format_duration(value)+"/"+format_duration(AppStatus.volume_audio.duration_seconds))
                time.sleep(1)
            if not AppStatus.stop_video:
                play_next()
            player.stop()
            
def play_video(song_url):
    try:
        if AppStatus.pause == True:
            AppStatus.pause = False
        pause_resume() 
        if check_thread_by_name("video_thread"):
            AppStatus.stop_threads = True
            time.sleep(1)

        AppStatus.stop_threads=False
        AppStatus.stop_video=False
        if not check_thread_by_name("video_thread"):
            video_thread = threading.Thread(target=play_video_vlc, args=(song_url,),name="video_thread")
            video_thread.start() 
        
        AppStatus.stop_threads=True 
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def get_album_name(album_name):
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
    file_name = f"{album_name}_album.txt"
    file_path = os.path.join(current_dir, file_name)
    album_songs=[]
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" **** ") 
            song_url=parts[0]
            video_title = parts[1]  
            thumbnail_url = parts[2]  
            album_songs.append((song_url,video_title, thumbnail_url))  
    return album_songs

def remove_album(album_name,album_window):
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa album này không?")
    if confirm:
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
        file_name = f"{album_name}_album.txt"
        file_path = os.path.join(current_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            get_all_album()
            album_window.destroy()
        else:
            print("File not found.")

def display_list_album():    
    album_window = customtkinter.CTkToplevel()
    album_window.title("Xóa Album")
    center_window(album_window)
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
    album_files = [file for file in os.listdir(current_dir) if file.endswith(".txt") and "album" in file.lower()]
    if album_files:
        for album_file in album_files:
            album_name = album_file.replace("_album.txt", "")
            album_button = customtkinter.CTkButton(album_window, font=("Arial", 13,"bold"),text=album_name, command=lambda name=album_name:remove_album(name,album_window))
            album_button.pack(fill="x")
            
    else:
        print("Không có file album nào trong thư mục hiện tại.")
    
def remove_song_album(album_name,song_url):
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa bài hát này không?")
    if confirm:
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
        file_name = f"{album_name}_album.txt"
        file_path = os.path.join(current_dir, file_name)
        with open(file_path, 'r') as file:
                lines = file.readlines()
        with open(file_path, 'w') as file:
            for line in lines:
                parts = line.strip().split(" **** ") 
                if parts[0] != song_url:
                    file.write(line)
        display_songs_in_album(album_name)
    
def display_songs_in_album(album_name):
    album_songs = get_album_name(album_name)
    for widget in inner_frame.winfo_children():
            widget.destroy() 
    for song_info in album_songs:
        song_url, video_title, thumbnail_url = song_info
        with urllib.request.urlopen(thumbnail_url) as response:
            image_data = response.read()
        image = Image.open(io.BytesIO(image_data))
        thumbnail_image = customtkinter.CTkImage(image,size=(120,90))
        
        button_frame = customtkinter.CTkFrame(inner_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        sub_button = customtkinter.CTkButton(button_frame,text=" - ", compound=tk.LEFT,width=30,command=lambda url=song_url,name=album_name:remove_song_album(name,url))
        sub_button.pack(side="left")
        
        song_button = customtkinter.CTkButton(button_frame, compound=tk.LEFT)
        song_button.pack(side="left",fill="x",expand=True)
        song_button.image = thumbnail_image
        
        song_button.configure(image=thumbnail_image,font=("Arial", 13,"bold"), anchor="w", text=video_title, command=lambda url=song_url: add_to_playlist(url))      
    inner_frame.update_idletasks()
    
    
def get_all_album():
    for widget in inner_album_frame.winfo_children():
        if isinstance(widget, customtkinter.CTkButton):
            widget.destroy()
    remove_button=customtkinter.CTkButton(inner_album_frame,text="Delete Album",command=display_list_album,font=("Arial", 13,"bold"))
    remove_button.pack(side="top")
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
    album_files = [file for file in os.listdir(current_dir) if file.endswith(".txt") and "album" in file.lower()]
    if album_files:
        for album_file in album_files:
            album_name = album_file.replace("_album.txt", "")
            album_button = customtkinter.CTkButton(inner_album_frame,font=("Arial", 13,"bold"), text=album_name, width=100,command=lambda name=album_name:display_songs_in_album(name))
            album_button.pack(fill="x",pady=5)
        
    else:
        print("Không có file album nào trong thư mục hiện tại.")
    

def write_album_to_txt(album_name,song_url, video_title, thumbnail_url):
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
    file_name = f"{album_name}_album.txt"
    file_path = os.path.join(current_dir, file_name)
    exists = False
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if song_url in line:
                    exists = True
                    messagebox.showinfo("Thông báo", f"Đã có bài hát trong {album_name}")
                    break
    if not exists:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{song_url} **** ")
            file.write(f"{video_title} **** ")
            file.write(f"{thumbnail_url}\n")
        get_all_album()  
         
         
def create_album(song_url,video_title,thumbnail_url,album_window):
    album_name = customtkinter.CTkInputDialog(title="Tạo Album",text= "Nhập tên album:")
    name=album_name.get_input()
    if check_file_txt(name)==False:
        write_album_to_txt(name,song_url, video_title, thumbnail_url)
        destroy_album_window(album_window)
    else:
        messagebox.showinfo("Thông báo", f"{album_name} đã tồn tại. Vui lòng nhập một tên khác.")
        
def destroy_album_window(album_window):
    album_window.destroy()     
    
def add_to_album(song_url,video_title,thumbnail_url):
    album_window = customtkinter.CTkToplevel()
    album_window.title("Chọn Album")
    center_window(album_window)
    create_button = customtkinter.CTkButton(album_window,font=("Arial", 13,"bold"), text="Create Album", command=lambda url=song_url,title=video_title,thumbnail=thumbnail_url:create_album(url,title,thumbnail,album_window))
    create_button.pack(side="top")
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album")
    album_files = [file for file in os.listdir(current_dir) if file.endswith(".txt") and "album" in file.lower()]
    if album_files:
        for album_file in album_files:
            album_name = album_file.replace("_album.txt", "")
            album_button = customtkinter.CTkButton(album_window, font=("Arial", 13,"bold"),text=album_name, width=100,command=lambda name=album_name, url=song_url,title=video_title,thumbnail=thumbnail_url:(write_album_to_txt(name,url, title, thumbnail),destroy_album_window(album_window)))
            album_button.pack(fill="x",pady=10)
    else:
        print("Không có file album nào trong thư mục hiện tại.")
    
    
def get_txt(song_url):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "audio_info.txt"
    file_path = os.path.join(current_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if song_url in line:
                parts = line.strip().split(" **** ") 
                video_title = parts[1]  
                thumbnail_url = parts[2]  
                return  video_title, thumbnail_url
    return  None, None

def write_to_txt(song_url, video_title, thumbnail_url):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "audio_info.txt"
    file_path = os.path.join(current_dir, file_name)
    if not check_song_url(song_url):
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(f"{song_url} **** ")
            file.write(f"{video_title} **** ")
            file.write(f"{thumbnail_url}\n")
        
def remove_song_playlist(song_url):
    confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa bài hát này không?")
    if confirm:
        value=0
        for i in range(len(AppStatus.selected_songs)):
            if AppStatus.selected_songs[i]==song_url:
                value=i
                break
        if len(AppStatus.selected_songs) ==1:
            sd.stop()
            footer_frame.pack_forget()
            AppStatus.selected_songs.pop(0)   
        elif value-len(AppStatus.history_songs)>=1:
            AppStatus.selected_songs.pop(value)
        elif value==len(AppStatus.history_songs):
            sd.stop()
            AppStatus.selected_songs.pop(value)
            if len(AppStatus.selected_songs)==len(AppStatus.history_songs):
                AppStatus.history_songs.pop(len(AppStatus.history_songs)-1)
            else:
                AppStatus.next=True
                play_song(AppStatus.selected_songs[len(AppStatus.history_songs)])
        elif value<len(AppStatus.history_songs):
            AppStatus.selected_songs.pop(value)
            AppStatus.history_songs.pop(value)        

        for widget in inner_playlist_frame.winfo_children():
            if isinstance(widget, customtkinter.CTkFrame):
                widget.destroy()

        for url in AppStatus.selected_songs:
            video_title, thumbnail_url = get_txt(url)
            update_selected_songs_listbox(video_title, thumbnail_url, url)

        
    
 
def update_selected_songs_listbox(video_title,thumbnail_url,song_url):
    with urllib.request.urlopen(thumbnail_url) as response:
        image_data = response.read()
    image = Image.open(io.BytesIO(image_data))
    thumbnail_image = customtkinter.CTkImage(image,size=(120,90))
    
    button_frame = customtkinter.CTkFrame(inner_playlist_frame)
    button_frame.pack(fill="x", padx=5, pady=5)
    
    sub_button = customtkinter.CTkButton(button_frame,text=" - ", compound=tk.LEFT,width=30,command=lambda url=song_url:remove_song_playlist(url))
    sub_button.pack(side="left")
    
    song_button = customtkinter.CTkButton(button_frame, compound=tk.LEFT)
    song_button.pack(fill="x", padx=5, pady=5)
    song_button.image = thumbnail_image
    song_button.configure( image=thumbnail_image,anchor="w", text=video_title,command=lambda url=song_url: play_selected_song_from_playlist(url),font=("Arial", 13,"bold"))
    inner_playlist_frame.update_idletasks()

    
def play_selected_song_from_playlist(song_url):
    AppStatus.select=True
    AppStatus.stop_threads=True
    sd.stop()
    number=0
    for i in range(len(AppStatus.selected_songs)):
        if AppStatus.selected_songs[i]==song_url:
            number=i    
    if number==0:
        while len(AppStatus.history_songs)!=0:
            AppStatus.history_songs.pop(len(AppStatus.history_songs)-1) 
    elif number<len(AppStatus.history_songs):
        while number<len(AppStatus.history_songs):
            AppStatus.history_songs.pop(len(AppStatus.history_songs)-1)
    elif number>len(AppStatus.history_songs):
        while number>len(AppStatus.history_songs):
            AppStatus.history_songs.append(AppStatus.selected_songs[len(AppStatus.history_songs)])
    play_song(AppStatus.selected_songs[len(AppStatus.history_songs)])
   
        

def update_time_play():
    while not AppStatus.stop_threads:
        if AppStatus.current_value<AppStatus.volume_audio.duration_seconds-1:
            if AppStatus.pause :
                threading.Event().wait()
            AppStatus.current_value=AppStatus.current_value+1
            slide_scale.set(AppStatus.current_value)
            time_label.configure(text=format_duration(AppStatus.current_value)+"/"+format_duration(AppStatus.volume_audio.duration_seconds))
            time.sleep(1)
        if AppStatus.stop_threads :
            break
           
def slide_play(value):
    if AppStatus.stop_video==False:
        AppStatus.stop_video=True
    if AppStatus.pause == True:
        AppStatus.pause = False
    if AppStatus.slide == False:
        pause_resume()   
    AppStatus.slide = True
    AppStatus.current_value = value
    start_position_ms = value * 1000 
    trimmed_audio_segment = AppStatus.volume_audio[start_position_ms:]
    if AppStatus.volume_value == 100:
        trimmed_audio_segment = trimmed_audio_segment.apply_gain(0)     
    elif AppStatus.volume_value == 0:
        trimmed_audio_segment = trimmed_audio_segment.apply_gain(-50)
    else:
        trimmed_audio_segment = trimmed_audio_segment.apply_gain(trimmed_audio_segment.dBFS * (100 - AppStatus.volume_value) / 100)
    AppStatus.audio = trimmed_audio_segment
    pause_resume()
    AppStatus.stop_threads = False

def volume_play(value):
    if AppStatus.pause == True:
        AppStatus.pause = False
    if AppStatus.slide == False:
        pause_resume() 
    AppStatus.volume=True 
    AppStatus.volume_value=value
    difference_db = AppStatus.volume_audio.dBFS - AppStatus.audio.dBFS
    if difference_db!=0:
        AppStatus.audio = AppStatus.audio.apply_gain(difference_db) 
    if value==100:
        AppStatus.audio=AppStatus.audio.apply_gain(0)     
    elif value==0:
        AppStatus.audio=AppStatus.audio.apply_gain(-50)
    else:
        AppStatus.audio=AppStatus.audio.apply_gain(AppStatus.volume_audio.dBFS * (100-value) / 100) 
    pause_resume()
    AppStatus.stop_threads = False
                
def pause_resume():
    if AppStatus.pause==False:
        AppStatus.pause=True
        icon_play = Image.open("icon/play-button.png")
        icon_play_photo=customtkinter.CTkImage(icon_play)
        pause_resume_button.configure(image=icon_play_photo)
        timeplay = get_duration_play()
        timeplay = time_to_seconds(timeplay)
        start_position_ms = timeplay * 1000 
        trimmed_audio_segment = AppStatus.audio[start_position_ms:]
        AppStatus.audio=trimmed_audio_segment
        AppStatus.stop_threads=True
        sd.stop()
    else:
        AppStatus.stop_threads=False 
        icon_pause = Image.open("icon/pause.png")
        icon_pause_photo=customtkinter.CTkImage(icon_pause)
        pause_resume_button.configure(image=icon_pause_photo)
        if check_thread_by_name("resume_thread")==False:
            audio_thread = threading.Thread(target=resume_audio,name="resume_thread")
            audio_thread.start()   
        AppStatus.stop_threads=True  

def resume_audio():
    while not AppStatus.stop_threads:
        AppStatus.pause=False
        audio_array = np.array(AppStatus.audio.get_array_of_samples())
        AppStatus.start_time = 0
        play_audio(audio_array, AppStatus.audio)   
        if AppStatus.stop_threads:
            break

def play_previous():
    AppStatus.stop_video=True
    AppStatus.pause=False
    AppStatus.previous=True
    sd.stop() 
    AppStatus.stop_threads = True
    AppStatus.history_songs.pop(len(AppStatus.history_songs)-1)
    play_song(AppStatus.selected_songs[len(AppStatus.history_songs)])
    
def play_next():
    AppStatus.stop_video=True
    AppStatus.pause=False
    AppStatus.next=True
    sd.stop()
    play_playlist()
    check_state_previous()
    check_state_next()   
    
def play_playlist():  
    AppStatus.stop_threads = True
    if len(AppStatus.history_songs)<len(AppStatus.selected_songs)-1:
        AppStatus.history_songs.append(AppStatus.selected_songs[len(AppStatus.history_songs)])        
        play_song(AppStatus.selected_songs[len(AppStatus.history_songs)])
    else: 
        pause_resume_button.configure(state=tk.DISABLED)
        messagebox.showinfo("Fail","Không có bài hát kế tiếp")
                  
def add_to_playlist(song_url):
    AppStatus.selected_songs.append(song_url)
    if check_song_url(song_url):
        video_title,thumbnail = get_txt(song_url)
        update_selected_songs_listbox(video_title,thumbnail,song_url)
    else: 
        print("false")
    check_state_next()
    if len(AppStatus.selected_songs)==1:
        play_song(AppStatus.selected_songs[0])

  
def play_audio(audio_data, audio_segment):
    check_state_pause()
    footer_frame.pack(side="bottom", fill="x")
    play_video_btn.configure(state=tk.NORMAL)
    AppStatus.time_song=audio_segment.duration_seconds
    AppStatus.time_song=format_duration(AppStatus.time_song)
    AppStatus.audio=audio_segment
    AppStatus.start_time = time.time()
    frame_rate = audio_segment.frame_rate
    if check_thread_by_name("time_thread")==False:
        AppStatus.stop_threads=False
        update_time_thread  = threading.Thread(target=update_time_play,name="time_thread") 
        update_time_thread.start()   
    sd.play(audio_data, frame_rate * 2)
    sd.wait()


    if AppStatus.next==False and AppStatus.previous==False and AppStatus.pause==False and AppStatus.volume==False and AppStatus.slide==False and AppStatus.select==False:
        AppStatus.current_value=0
        play_playlist()
    check_state_previous()
    check_state_next()
    AppStatus.next=False
    AppStatus.previous=False
    AppStatus.volume=False
    AppStatus.slide=False
    AppStatus.select=False
    

def play_song(song_url):
    def play_song_thread():
        try:
            yt = YouTube(song_url)  

            play_video_btn.configure(command=lambda url=song_url: play_video(url),font=("Arial", 13,"bold"))
            
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            video_title, thumbnail_url = get_txt(song_url)
            
            with urllib.request.urlopen(thumbnail_url) as response:
                image_data = response.read()
            image = Image.open(io.BytesIO(image_data))
            image_song = customtkinter.CTkImage(light_image=image,dark_image=image,size=(120, 90))
            image_label.configure(image=image_song)
            title_label.configure(text=video_title,font=("Arial", 13,"bold"))
            with io.BytesIO() as buffer:
                audio_stream.stream_to_buffer(buffer)
                audio_data = buffer.getvalue()
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
                AppStatus.volume_audio=audio_segment
                slide_scale.configure(from_=0, to=AppStatus.volume_audio.duration_seconds)
                time_label.configure(text="00:00:00/"+format_duration(AppStatus.volume_audio.duration_seconds))
                if AppStatus.volume_value==100:
                    audio_segment=audio_segment.apply_gain(0)     
                elif AppStatus.volume_value==0:
                    audio_segment=audio_segment.apply_gain(-50)
                else:
                    audio_segment=audio_segment.apply_gain(audio_segment.dBFS * (100-AppStatus.volume_value) / 100)
                audio_array = np.array(audio_segment.get_array_of_samples())
                AppStatus.current_value=0
                play_audio(audio_array, audio_segment)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    thread = threading.Thread(target=play_song_thread,name="play_thread")
    thread.start()

def search_and_display():
    query = entry.get()
    try:
        for widget in inner_frame.winfo_children():
            widget.destroy() 
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=5
        ).execute()
        items = search_response.get('items', [])
        if items:
            for item in items:
                video_id = item['id']['videoId']   
                video_title = item['snippet']['title']
                thumbnail_url = item['snippet']['thumbnails']['default']['url']
                song_url = f"https://www.youtube.com/watch?v={video_id}"
                with urllib.request.urlopen(thumbnail_url) as response:
                    image_data = response.read()
                image = Image.open(io.BytesIO(image_data))
                thumbnail_image = customtkinter.CTkImage(image,size=(120, 90))
                button_frame = customtkinter.CTkFrame(inner_frame)
                button_frame.pack(fill="x", padx=5, pady=5)
                
                sub_button = customtkinter.CTkButton(button_frame,text="+", compound=tk.LEFT, width=30)
                sub_button.pack(side="left")
                
                song_button = customtkinter.CTkButton(button_frame, compound=tk.LEFT)
                song_button.pack(side="left",fill="x",expand=True)
                song_button.image = thumbnail_image
                
                 
                write_to_txt(song_url,video_title,thumbnail_url)
                song_button.configure(image=thumbnail_image, anchor="w", text=video_title,font=("Arial", 13,"bold"),command=lambda url=song_url: add_to_playlist(url)) 
                sub_button.configure(command=lambda url=song_url,title=video_title, thumbnail=thumbnail_url: add_to_album(url,title,thumbnail) )      
            inner_frame.update_idletasks()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")