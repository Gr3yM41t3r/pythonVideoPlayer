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

    def __init__(self, mntr, master=None):
        QMainWindow.__init__(self, master)
        self.filename = "assets/videos/placeholder.mp4"
        self.setWindowTitle("Media Player")
        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.monitor = mntr

        # black screen
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

        # ---------------Image----------------------------

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

        # ----------------Technical informations -----------
        self.tableInfo = QtWidgets.QTableWidget(self)

        self.headerFont = QtGui.QFont()
        self.headerFont.setPointSize(40)
        self.infoFont = QtGui.QFont()
        self.infoFont.setPointSize(40)
        self.tableInfo.resizeRowsToContents()
        self.tableInfo.resizeColumnsToContents()
        self.a = 1
        self.TableHeight = 500
        self.TableWidth = 2 * self.TableHeight
        self.tableInfo.setColumnCount(1)
        self.tableInfo.setRowCount(4)
        self.setupInformationTable()
        self.fillInformationTable()
        self.tableInfo.resize(self.TableWidth, self.TableHeight * 2)
        self.tableInfo.move(int(monitor.width() / 2 - self.tableInfo.width() / 2),
                            int(monitor.height() / 2 - self.tableInfo.height() / 2))

        self.tableInfo.setStyleSheet("background:rgb(255,255,255);color:black;"
                                     "selection-background-color:white;selection-color:black")

        # thread watcher for mouse input inactivity
        self.Play()
        self.thread = Thread(target=self.inactivityDetector)
        self.current_option = 0
        self.shouldWait = True
        self.isPlayingTrailer = True
        self.counter = 0
        self.checkThreadTimer = QtCore.QTimer(self)
        self.checkThreadTimer.setInterval(1000)
        self.checkThreadTimer.timeout.connect(self.readListValues)
        self.checkThreadTimer.start()

        self.tableInfo.hide()

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
        exit_option = menu.addAction('Exit')
        play_option = menu.addAction('play')
        exit_option.triggered.connect(lambda: exit())
        play_option.triggered.connect(self.OpenFile)
        menu.exec_(self.mapToGlobal(pos))

    # ----------------mouse and keyboard events---------------------------

    def mousePressEvent(self, event):
        self.start_time=time.time()
        if event.button() == Qt.RightButton:
            self.isPlayingTrailer=False
            if not self.thread.is_alive():
                self.thread = Thread(target=self.inactivityDetector)
                self.thread.start()
            if self.tableInfo.isVisible():
                self.a += 1
                self.fillInformationTable()
            else:
                self.mediaplayer.stop()
                self.tableInfo.show()
        elif event.button() == Qt.LeftButton:
            self.tableInfo.hide()
            self.messageView.hide()
            self.videoframe.show()
            self.OpenFile()
        elif event.button() == Qt.MiddleButton:
            self.showMessage("25")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            exit()

    def wheelEvent(self, event):
        self.start_time = time.time()
        if self.isPlayingTrailer and not self.tableInfo.isVisible():
            self.showMessage("26")
        else:
            self.tableInfo.hide()
            self.displaylanguagemenu(event)
        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()

    def displaylanguagemenu(self, event):
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

    # ------- inactivity---------
    def inactivityDetector(self):
        while True:
            if time.time() - self.start_time > 3:
                if self.messageView.isVisible():
                    self.messageView.hide()
                    print('hekjazhkjehazkehjaz')
                    self.language_List.hide()
                    break
                print("chosiing language" + self.language_option[self.current_option % len(self.language_option)])
                self.selected_language = self.language_option[self.current_option % len(self.language_option)]
                self.resumePlayBack()
                break
        while True:
            print("test")
            print(time.time())
            print(self.start_time)
            print(self.tableInfo.isVisible())
            print( time.time()-self.start_time)

            if time.time()-self.start_time > 30 and self.tableInfo.isVisible():
                print("reddd baleek hadi bladek")
            if time.time()-self.start_time > 40 and self.tableInfo.isVisible():
                print("khreeej t9owed")
                self.tableInfo.hide()
                break


    def messagewatch(self):
        while True:
            if time.time()-self.start_time>30:
                pass

    def readListValues(self):
        if self.shouldWait:
            while self.shouldWait and not self.mediaplayer.is_playing():
                self.counter += 1
                print("hiding")
                self.videoframe.hide()
                if self.counter < 5:
                    print("returning")
                    return
                else:
                    self.shouldWait = False
                    self.videoframe.show()
                    print("showing")
        else:
            if not self.mediaplayer.is_playing() and not self.shouldWait:
                print("start")
                self.filename = "assets/videos/placeholder.mp4"
                self.Play()
                self.isPlayingTrailer = True
                self.shouldWait = True
                self.counter = 0

    def showLanguageMenu(self):
        self.language_List.show()

    def showMessage(self, message):
        pixmap = QtGui.QPixmap("assets/ass/" + message + ".svg")
        self.messageView.setPixmap(pixmap)
        self.messageView.show()
        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()

    # --------------Fiche technique--------------------------------

    def setupInformationTable(self):
        _translate = QtCore.QCoreApplication.translate
        item = QtWidgets.QTableWidgetItem()
        self.tableInfo.setHorizontalHeaderItem(0, item)
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            self.tableInfo.setVerticalHeaderItem(i, item)
            self.tableInfo.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem()
            self.tableInfo.setItem(i, 0, item)
            print("added")

    def fillInformationTable(self):
        for i in range(4):
            item = self.tableInfo.verticalHeaderItem(i)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(self.headerFont)
            item.setText("Prop" + str(i))
            item = self.tableInfo.item(i, 0)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(self.infoFont)
            item.setText("Value" + str(i) + ":" + str(self.a))

        header = self.tableInfo.horizontalHeader()
        header.setDefaultSectionSize(int(self.TableWidth / 2))
        header = self.tableInfo.verticalHeader()
        header.setDefaultSectionSize(int(self.TableHeight / 2))
        header.setMinimumWidth(self.TableHeight)
        self.tableInfo.horizontalHeader().hide()
        self.tableInfo.verticalScrollBar().hide()

    # --------------play back --------------------------
    def Play(self):
        self.media = self.instance.media_new(self.filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.mediaplayer.play()

    def OpenFile(self):
        self.isPlayingTrailer = False
        self.filename = "assets/videos/" + self.selected_language + "_Vin.mp4"
        self.Play()

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
