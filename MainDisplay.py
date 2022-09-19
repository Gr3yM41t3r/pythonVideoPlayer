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
        self.language_List.hide()




        self.language_List.move(int(monitor.width() / 2 - self.language_List.width() / 2),
                                int(monitor.height() / 2 - self.language_List.height() / 2))
        print(int(monitor.height() / 2 - self.language_List.height() / 2))
        print(int(monitor.width() / 2 - self.language_List.width() / 2))




        #---------------Image----------------------------

        self.messageView = QLabel(self)
        self.messageView.resize(700, 400)
        self.messageView.move(int(monitor.width() / 2 - self.messageView.width() / 2),
                              int(monitor.height() / 2 - self.messageView.height() / 2))
        self.messageView.setStyleSheet("""
                 border-top-left-radius:30px;
                 border-bottom-left-radius:30px;
                 border-top-right-radius:30px;
                 border-bottom-right-radius:30px;
             """)

        self.messageView.hide()


        #----------------Technical informations ------------
        self.tableWidget = QtWidgets.QTableWidget(self)

        self.tableWidget.resize(720,500)
        self.tableWidget.move(int(monitor.width() / 2 - self.tableWidget.width() / 2),
                              int(monitor.height() / 2 - self.tableWidget.height() / 2))
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(4)
        self.tableWidget.setStyleSheet("background-color:grey")



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
        self.a=1
        self.setupInformationTable()
        self.fillInformationTable()
        self.tableWidget.hide()



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
        self.start_time = time.time()
        if event.button()==Qt.RightButton:
            if self.tableWidget.isVisible():
                self.a+=1
                self.fillInformationTable()
            else:
                self.mediaplayer.stop()
                self.tableWidget.show()
        elif event.button()==Qt.LeftButton:
            self.tableWidget.hide()
            self.messageView.hide()
            self.videoframe.show()
            self.OpenFile()
        elif event.button()==Qt.MiddleButton:
            self.showMessage("25")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            exit()

    def wheelEvent(self, event):
        self.start_time = time.time()
        if self.isPlayingTrailer:
            self.showMessage("26")
        else:
            self.showLanguageMenu()
            item = self.language_List.item(self.current_option % len(self.language_option))
            item.setIcon(QtGui.QIcon())
            if event.angleDelta().y() // 120 == 1:
                self.current_option -= 1
            elif event.angleDelta().y() // 120 == -1:
                self.current_option += 1
            item = self.language_List.item(self.current_option % len(self.language_option))
            item.setSelected(True)
            icon = QIcon('assets/icons/checksvg2.svg')
            item.setIcon(icon)

            self.language_List.scrollToItem(item)
        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()



    def Play(self):
        self.media=self.instance.media_new(self.filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.mediaplayer.play()

    def OpenFile(self):
        self.isPlayingTrailer = False
        self.filename = "assets/videos/" + self.selected_language + "_Vin.mp4"
        self.Play()

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

    def showMessage(self,message):
        pixmap = QtGui.QPixmap("assets/ass/"+message+".svg")
        self.messageView.setPixmap(pixmap)
        self.messageView.show()
        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()

    def setupInformationTable(self):
        _translate = QtCore.QCoreApplication.translate
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)
            self.tableWidget.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setItem(i, 0, item)
            print("added")


    def fillInformationTable(self):
        for i in range(4):
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText("Prop"+str(i))
            item = self.tableWidget.item(i, 0)
            item.setText("Value" + str(i)+":"+str(self.a))
        header = self.tableWidget.horizontalHeader()
        header.setDefaultSectionSize(200)
        header = self.tableWidget.verticalHeader()
        header.setDefaultSectionSize(100)


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
