import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from MainDisplay import Player

app = QApplication(sys.argv)
player = Player()
monitor = QDesktopWidget().screenGeometry(1)
player.move(monitor.top(),monitor.left())
player.showFullScreen()
sys.exit(app.exec_())
