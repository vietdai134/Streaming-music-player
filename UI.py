import tkinter as tk
from function import *
import customtkinter
from PIL import Image, ImageTk
class YouTubeSongPlayerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Streaming Music Player")
        self.geometry("1400x800")
        self.resizable(False,False)
        self.configure(bg="black")
        self.initialize_gui()
        self.initialize_gui_variables()
        self.check_state_previous()
        self.check_state_next()
        self.check_state_pause()
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        self.display_random_songs()
        self.get_all_album()
        
        
    def initialize_gui(self):
       
        
        header_frame = customtkinter.CTkFrame(self)
        header_frame.pack(fill="x")
        

        self.entry = customtkinter.CTkEntry(header_frame,placeholder_text="Search songs",width=500)
        self.entry.pack(side="left",pady=10,padx=10)
        
        search_button = customtkinter.CTkButton(header_frame, text="Search", command=self.search_and_display,width=50)
        search_button.pack(side="left")
        
        self.display_playlist=customtkinter.CTkButton(header_frame,text="Display Playlist",command=self.display_playlist_frame)
        self.display_playlist.pack(side="right")
        
        # Body
        body_frame = customtkinter.CTkFrame(self)
        body_frame.pack(fill="both", expand=True)
        
        
        self.left_frame = customtkinter.CTkFrame(body_frame)
        self.left_frame.pack(side="left", fill="both")
        
        self.album_label = customtkinter.CTkLabel(self.left_frame, text="Album",font=("Arial", 16,"bold"),text_color="white")
        self.album_label.pack()
        
        self.inner_album_frame = customtkinter.CTkScrollableFrame(self.left_frame)
        self.inner_album_frame.pack(side="left", fill="both", expand=True)
        
        
        
        
        result_frame = customtkinter.CTkFrame(body_frame)
        result_frame.pack(side="left", fill="both", expand=True)
        
        self.result_label = customtkinter.CTkLabel(result_frame, text="Search result",font=("Arial", 16,"bold"),text_color="white")
        self.result_label.pack()

        self.inner_frame = customtkinter.CTkScrollableFrame(result_frame)
        self.inner_frame.pack(side="left", fill="both", expand=True)
        
        
        self.right_frame = customtkinter.CTkFrame(body_frame)
        self.right_frame.pack_forget()

        
        self.playlist_label = customtkinter.CTkLabel(self.right_frame, text="Playlist", font=("Arial", 16,"bold"),text_color="white")
        self.playlist_label.pack()
        
        self.inner_playlist_frame = customtkinter.CTkScrollableFrame(self.right_frame)
        self.inner_playlist_frame.pack(fill="both",expand=True)
        
        
        # Footer
        self.footer_frame = customtkinter.CTkFrame(self,border_color="black")
        self.footer_frame.pack_forget()

        self.title_slide_frame=customtkinter.CTkFrame(self.footer_frame)
        self.title_slide_frame.pack(side="left",fill="both",expand=True)
        
        self.image_label = customtkinter.CTkLabel(self.title_slide_frame,text="")
        self.image_label.pack(side="left",padx=10,pady=10)
        
        self.title_label = customtkinter.CTkLabel(self.title_slide_frame,font=("Arial", 13,"bold"))
        self.title_label.pack(side="top",fill="both", padx=10,pady=10)
        
        self.slide_scale = customtkinter.CTkSlider(self.title_slide_frame, from_=0, to=1,width=300)
        self.slide_scale.bind("<ButtonRelease-1>", self.slide_play)
        self.slide_scale.pack(side="bottom",fill="both",padx=10,pady=10)
        
        self.time_label = customtkinter.CTkLabel(self.title_slide_frame, text="",font=("Arial", 12))
        self.time_label.pack(side="bottom",fill="both",padx=5)
        
        self.button_frame=customtkinter.CTkFrame(self.footer_frame)
        self.button_frame.pack(side="right",fill="both",expand=True)
        
        self.volume_scale = customtkinter.CTkSlider(self.button_frame, from_=0, to=100, orientation="vertical",height=100)
        self.volume_scale.set(100)  
        self.volume_scale.bind("<ButtonRelease-1>", self.volume_play)
        self.volume_scale.pack(side="right",padx=5)
        
        icon_next = Image.open("icon/next.png")
        icon_next_photo=customtkinter.CTkImage(icon_next)
        self.next_button = customtkinter.CTkButton(self.button_frame,image=icon_next_photo ,text="", command=self.play_next,font=("Arial", 13,"bold"),width=30)
        self.next_button.pack(side="right",padx=5,pady=10)
        
        
        icon_pause = Image.open("icon/pause.png")
        icon_pause_photo=customtkinter.CTkImage(icon_pause)
        self.pause_resume_button = customtkinter.CTkButton(self.button_frame, image=icon_pause_photo,text="", command=self.pause_resume,font=("Arial", 13,"bold"),width=30)
        self.pause_resume_button.pack(side="right",padx=5,pady=10)
        
        icon_previous = Image.open("icon/previous.png")
        icon_previous_photo=customtkinter.CTkImage(icon_previous)
        self.previous_button = customtkinter.CTkButton(self.button_frame,image=icon_previous_photo, text="", command=self.play_previous,font=("Arial", 13,"bold"),width=30)
        self.previous_button.pack(side="right",padx=5,pady=10)
         
        self.play_video_btn = customtkinter.CTkButton(self.button_frame, text="Play video",font=("Arial", 13,"bold"))
        self.play_video_btn.pack(side="right",padx=5,pady=10)
        self.play_video_btn.configure(state=tk.DISABLED)
        
        
    def initialize_gui_variables(self):
        initialize_gui_variables(self.next_button, self.previous_button, self.pause_resume_button,
                                  self.entry, self.inner_frame,self.footer_frame, 
                                  self.volume_scale,self.slide_scale,self.time_label,
                                  self.image_label,self.title_label,self.inner_playlist_frame,
                                  self.left_frame,self.play_video_btn,self.inner_album_frame)
        

    def check_state_previous(self):
        check_state_previous()

    def check_state_next(self):
        check_state_next()

    def check_state_pause(self):
        check_state_pause()

    def search_and_display(self):
        search_and_display()

    def play_previous(self):
        play_previous()

    def pause_resume(self):
        pause_resume()
    
    def play_next(self):
        play_next()
        
    def get_all_album(self):
        get_all_album()
        
    def volume_play(self,event):
        current_value = self.volume_scale.get()
        volume_play(current_value)
    
    def slide_play(self,event):
        current_value = self.slide_scale.get()
        slide_play(current_value)
    
    def display_playlist_frame(self):
        if self.right_frame.winfo_ismapped(): 
            self.right_frame.pack_forget() 
        else:
            self.right_frame.pack(side="right", fill="both", expand=True)
     
    def display_random_songs(self):
        display_random_songs()     
    def on_close(self):
        os._exit(0)
        
def main():
    app = YouTubeSongPlayerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close) 
    app.mainloop()

if __name__ == "__main__":
    main()