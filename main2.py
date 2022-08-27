import time
from threading import Thread

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QDir, Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QDesktopWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys

class VideoWindow(QMainWindow):
    language_option = ['English', 'French', 'Chinese', 'Arabic', 'German', 'Spanish', 'Italien']
    selected_language = 'French'

    def __init__(self,mntr, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.setWindowFlag(Qt.FramelessWindowHint)
        videoWidget = QVideoWidget()
        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(videoWidget)

        self.language_List = QtWidgets.QListWidget(self)
        self.language_List.setAttribute(Qt.WA_TranslucentBackground)

        self.monitor = mntr
        self.retranslateUi()
        self.language_List.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.language_List.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.language_List.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # set up language options
        self.language_List.setMaximumHeight(self.language_List.sizeHintForRow(0) * self.language_List.count())
        self.language_List.setMinimumHeight(self.language_List.sizeHintForRow(0) * 3)
        self.language_List.setAutoScroll(True)
        self.language_List.setMinimumWidth(self.language_List.sizeHintForColumn(0) + 100)
        self.language_List.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.language_List.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.language_List.hide()
        self.language_List.move(int(monitor.width()/2-self.language_List.width()/2),int(monitor.height()/2-self.language_List.height()/2))
        print(int(monitor.height()/2-self.language_List.height()/2))
        print(int(monitor.width()/2-self.language_List.width()/2))

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.mediaPlayer.mediaStatusChanged.connect(self.statusChanged)
        self.thread = Thread(target=self.inactivityDetector)
        self.shouldIdle = True
        self.openFile()
        self.current_option = 0



        print(self.monitor)


    def retranslateUi(self):
        font = QtGui.QFont()
        font.setFamily("P052 [UKWN]")
        font.setPointSize(90)
        for i in range(len(self.language_option)):
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setFont(font)
            self.language_List.addItem(item)
            item = self.language_List.item(i)
            item.setText(self.language_option[i])

    def openFile(self):
        self.shouldIdle = False
        fileName="/home/amine/Desktop/pythonVideoPlayer/assets/videos/French_Vin.mp4"
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
        self.mediaPlayer.play()
    def exitCall(self):
        sys.exit(app.exec_())


    def mousePressEvent(self, event):
        if event.button()==Qt.RightButton:
            self.exitCall()
        elif event.button()==Qt.LeftButton:
            self.openFile()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        pass

    def positionChanged(self, position):
        pass

    def durationChanged(self, duration):
        pass

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def wheelEvent(self, QWheelEvent):
        self.showLanguageMenu()
        self.start_time = time.time()
        if QWheelEvent.angleDelta().y() // 120 == 1:
            self.current_option -= 1
        elif QWheelEvent.angleDelta().y() // 120 == -1:
            self.current_option += 1
            print(self.current_option)
        item = self.language_List.item(self.current_option % len(self.language_option))
        item.setSelected(True)
        self.language_List.scrollToItem(item)
        if not self.thread.is_alive():
            self.thread = Thread(target=self.inactivityDetector)
            self.thread.start()

    def inactivityDetector(self):
        while True:
            if time.time() - self.start_time > 1.5:
                print("chosiing language" + self.language_option[self.current_option % len(self.language_option)])
                self.selected_language = self.language_option[self.current_option % len(self.language_option)]
                self.resumePlayBack()
                break
    def resumePlayBack(self):
        self.openFile()
        self.language_List.hide()
        self.isPaused = False

    def showLanguageMenu(self):
        self.language_List.show()

    def playIdlingVideo(self):
        fileName = "/home/amine/Desktop/pythonVideoPlayer/assets/videos/placeholder.mp4"
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            self.mediaPlayer.play()



    def statusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia and not self.shouldIdle:
            print('playback ended!')
            self.shouldIdle=True
            self.playIdlingVideo()
        elif status == QMediaPlayer.EndOfMedia and self.shouldIdle:
            print('idling')

            self.mediaPlayer.play()




    def handleError(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = QDesktopWidget().screenGeometry(2)

    player = VideoWindow(monitor)
    print(monitor.height())
    player.move(monitor.center())
    player.showFullScreen()
    sys.exit(app.exec_())