# coding: utf-8
import sys
import time

from PyQt5 import QtCore
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCursor

from MainDisplay import Player


class MainWindow(QMainWindow):
    control_options = ['play', 'language', 'specs']
    default_selection = "play"

    def __init__(self,mntr, videoPLayer):
        super(MainWindow, self).__init__()
        self.monitor=mntr
        # Window size
        self.WIDTH = 480
        self.HEIGHT = 480
        self.resize(self.WIDTH, self.HEIGHT)
        # Widget
        self.centralwidget = QWidget(self)
        self.centralwidget.resize(self.WIDTH, self.HEIGHT)
        # Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_menu)
        # Initial
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(1)
        self.centralwidget.move(int(monitor.width() / 2 - self.width() / 2),
                                int(monitor.height() / 2 - self.height() / 2))
        self.radius = 240
        self.videoPlayer = videoPLayer
        self.centralwidget.setStyleSheet(
            """
            background:rgb(255, 255, 255);
            border-top-left-radius:{0}px;
            border-bottom-left-radius:{0}px;
            border-top-right-radius:{0}px;
            border-bottom-right-radius:{0}px;
            background-repeat:no-repeat;
            background-position: center;
            background-image:url({1})
            """.format(self.radius, "assets/icons/" + self.default_selection)
        )

    def right_menu(self, pos):
        menu = QMenu()

        # Add menu options
        exit_option = menu.addAction('Exit')

        # Menu option events
        exit_option.triggered.connect(lambda: exit())

        # Position
        menu.exec_(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        self.initialPos = QCursor().pos().x()
        print(QCursor().pos().x())

    def mouseReleaseEvent(self, event):
        '''
        mm = Player()
        self.moveFlag = False
        self.setCursor(Qt.CrossCursor)
        self.endPos = QCursor().pos().x()
        print(self.endPos - self.initialPos)
        if self.endPos - self.initialPos > 180:
            self.changeImage(1)
        elif self.endPos - self.initialPos < -180:
            self.changeImage(-1)
        elif event.button() == Qt.LeftButton and abs(QCursor().pos().x() - self.initialPos) < 20:
            if self.default_selection == "play":
                mm.OpenFile()

        else:
            pass'''

    def mouseMoveEvent(self, event):
        print(QCursor().pos().x())




    def wheelEvent(self, QWheelEvent):
        if(self.centralwidget.isHidden()):
            self.centralwidget.show()
        else:self.centralwidget.hide()


    def changeImage(self, i):
        self.default_selection = self.control_options[(self.control_options.index(self.default_selection) + i) % 3]
        self.centralwidget.setStyleSheet(
            """
            background:rgb(255, 255, 255);
            border-top-left-radius:{0}px;
            border-bottom-left-radius:{0}px;
            border-top-right-radius:{0}px;
            border-bottom-right-radius:{0}px;
            background-repeat:no-repeat;
            background-position: center;
            background-image:url({1});

            """.format(self.radius, "assets/icons/" + self.default_selection)
        )


if __name__ == '__main__':
    app = QApplication([])
    monitor = QDesktopWidget().screenGeometry(0)
    window = MainWindow(None,monitor)

    window.move(monitor.center())
    window.showFullScreen()
    sys.exit(app.exec_())