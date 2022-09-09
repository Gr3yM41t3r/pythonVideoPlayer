#! /usr/bin/python

#
# Qt example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#

import sys
import os.path
import time
from threading import Thread

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QSlider, QHBoxLayout, QPushButton, \
    QVBoxLayout, QAction, QFileDialog, QApplication, QMenu, QDesktopWidget, QStyle, QLabel
import vlc



class Player(QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    language_option = ['English', 'French', 'Chinese', 'Arabic', 'German', 'Spanish', 'Italien']
    selected_language = 'French'


    def __init__(self,mntr, master=None):
        QMainWindow.__init__(self, master)
        self.filename = "assets/videos/placeholder.mp4"
        self.setWindowTitle("Media Player")
        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_menu)
        self.monitor = mntr

        #black screen
        self.setStyleSheet("background:rgb(0,0,0);")


        # creating video frame
        self.videoframe = QWidget(self)
        self.setStyleSheet("background:rgb(0,0,0);")
        self.videoframe.setWindowOpacity(0.5)
        self.videoframe.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(self.videoframe)
        self.isPaused = False
        self.mediaplayer.set_xwindow(self.videoframe.winId())

        # creating language options list
        self.language_List = QtWidgets.QListWidget(self)
        self.language_List.setStyleSheet("background:rgba(38,38,38,255);"
                                         "selection-background-color: rgb(90, 90, 90);"
                                         )

        self.retranslateUi()
        self.language_List.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.language_List.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.language_List.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # set up language options
        self.language_List.setMaximumHeight(self.language_List.sizeHintForRow(0) * self.language_List.count())
        self.language_List.setMinimumHeight(self.language_List.sizeHintForRow(0) * 3)
        self.language_List.setMinimumWidth(self.language_List.sizeHintForColumn(0) + 100)
        self.language_List.setAutoScroll(True)
        self.language_List.hide()




        self.language_List.move(int(monitor.width() / 2 - self.language_List.width() / 2),
                                int(monitor.height() / 2 - self.language_List.height() / 2))
        print(int(monitor.height() / 2 - self.language_List.height() / 2))
        print(int(monitor.width() / 2 - self.language_List.width() / 2))




        #---------------Image
        self.messageView = QLabel(self)
        self.messageView.resize(500, 250)
        pixmap = QtGui.QPixmap("assets/ass/25.svg")
        self.messageView.move(int(monitor.width() / 2 - self.messageView.width() / 2),
                              int(monitor.height() / 2 - self.messageView.height() / 2))
        self.messageView.setPixmap(pixmap)
        self.messageView.hide()
        # thread watcher for mouse input inactivity
        self.Play()
        self.thread = Thread(target=self.inactivityDetector)

        self.current_option = 0
        self.shouldWait=True
        self.isPlayingTrailer=True
        self.counter=0
        self.checkThreadTimer = QtCore.QTimer(self)
        self.checkThreadTimer.setInterval(1000)
        self.checkThreadTimer.timeout.connect(self.readListValues)
        self.checkThreadTimer.start()


    def get_end_callback(mediaplayer):
        def end_callback(event):
            print("End of playing reached")
        return end_callback


    def retranslateUi(self):
        font = QtGui.QFont()
        font.setFamily("P052 [UKWN]")
        font.setPointSize(80)
        for i in range(len(self.language_option)):
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            self.language_List.addItem(item)
            item = self.language_List.item(i)
            item.setText(self.language_option[i])

    def right_menu(self, pos):
        menu = QMenu()
        # Add menu options
        exit_option = menu.addAction('Exit')
        play_option = menu.addAction('play')
        # Menu option events
        exit_option.triggered.connect(lambda: exit())
        play_option.triggered.connect(self.OpenFile)
        # Position
        menu.exec_(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        if event.button()==Qt.RightButton:
            sys.exit(app.exec_())
        elif event.button()==Qt.LeftButton:
            self.OpenFile()

    def wheelEvent(self, event):
        self.start_time = time.time()
        if self.isPlayingTrailer:
            self.messageView.show()
        else:
            item = self.language_List.item(self.current_option % len(self.language_option))
            item.setIcon(QtGui.QIcon())
            self.showLanguageMenu()
            if event.angleDelta().y() // 120 == 1:
                self.current_option -= 1
            elif event.angleDelta().y() // 120 == -1:
                self.current_option += 1
            item = self.language_List.item(self.current_option % len(self.language_option))
            item.setSelected(True)
            self.language_List.scrollToItem(item)
            icon = QIcon('assets/icons/check.png')
            item.setIcon(icon)
        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()

    def PlayPause(self):
        # Toggle play/pause status
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.isPaused = False


    def Play(self):
        self.media=self.instance.media_new(self.filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.mediaplayer.play()

    def OpenFile(self):
        self.isPlayingTrailer = False
        """Open a media file in a MediaPlayer
        """
        filename = "assets/videos/" + self.selected_language + "_Vin.mp4"
        if sys.version < '3':
            filename = vlc.unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title


        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
        self.PlayPause()



    def inactivityDetector(self):
        while True:
            if time.time() - self.start_time > 3:
                if self.messageView.isVisible():
                    self.messageView.hide()
                    break
                print("chosiing language" + self.language_option[self.current_option % len(self.language_option)])
                self.selected_language = self.language_option[self.current_option % len(self.language_option)]
                self.resumePlayBack()
                break



    def readListValues(self):
        if self.shouldWait:
            while self.shouldWait and not self.mediaplayer.is_playing():
                self.counter += 1
                print("hiding")
                self.videoframe.hide()
                if self.counter<5:
                    print("returning")
                    return
                else:
                    self.shouldWait=False
                    self.videoframe.show()
                    print("showing")
        else:
            if not self.mediaplayer.is_playing() and not self.shouldWait:
                print("start")
                self.filename="assets/videos/placeholder.mp4"
                self.Play()
                self.isPlayingTrailer=True
                self.shouldWait=True
                self.counter=0




    def showLanguageMenu(self):
        self.language_List.show()

    def resumePlayBack(self):
        self.OpenFile()
        self.language_List.hide()
        self.isPaused = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = QDesktopWidget().screenGeometry(2)

    player = Player(monitor)
    player.move(monitor.center())
    player.showFullScreen()
    sys.exit(app.exec_())
