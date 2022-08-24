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
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QSlider, QHBoxLayout, QPushButton, \
    QVBoxLayout, QAction, QFileDialog, QApplication, QMenu, QDesktopWidget
import vlc


class Player(QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    language_option=['English','French','Chinese','French','Chinese','French','Chinese']
    def __init__(self, master=None):
        QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")
        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_menu)



        self.videoframe = QWidget(self)
        self.setCentralWidget(self.videoframe)
        self.isPaused = False
        self.current_option=0
        self.s=0


        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(680, 415, 380, 250))
        self.listWidget.setStyleSheet("background-color: rgba(190, 206, 255, 0.08);")
        self.listWidget.setAutoScroll(True)
        self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.current_option = 0
        self.retranslateUi()
        self.listWidget.hide()
        self.thread = Thread(target=self.inactivityDetector)





    def retranslateUi(self):
        font = QtGui.QFont()
        font.setFamily("P052 [UKWN]")
        font.setPointSize(30)
        for i in range(len(self.language_option)):
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            self.listWidget.addItem(item)
            item = self.listWidget.item(i)
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

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()

    def OpenFile(self):
        """Open a media file in a MediaPlayer
        """
        filename = "assets/videos/test.mp4"
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
        self.PlayPause()


    def wheelEvent(self, QWheelEvent):
        self.stopPlayBack()
        self.start_time = time.time()
        self.current_option += 1
        print(self.current_option)
        self.listWidget.item(self.current_option % len(self.language_option)).setSelected(True)


        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()

    def inactivityDetector(self):
        while True:
            if time.time()-self.start_time>3:
                print("chosiing language"+ self.language_option[self.current_option%len(self.language_option)])
                self.resumePlayBack()
                return




    def stopPlayBack(self):
        self.listWidget.show()
        self.isPaused = True

    def resumePlayBack(self):
        self.videoframe.show()
        self.OpenFile()
        self.listWidget.hide()
        self.isPaused=False


    def choseLanguage(self):
        pass






if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    monitor = QDesktopWidget().screenGeometry(1)
    player.move(monitor.top(),monitor.left())
    player.showFullScreen()

    sys.exit(app.exec_())
