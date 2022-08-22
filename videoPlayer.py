import vlc
import time

# creating vlc media player object
media_player = vlc.MediaPlayer()

# media object
media = vlc.Media("assets/videos/test.mp4")

# setting media to the media player
media_player.set_media(media)

# start playing video


def playVideo():
    media_player.play()
    while True:
        pass


