from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class FileMonitor(QObject):

    image_signal = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def monitor_images(self):
        # I'm guessing this is an infinite while loop that monitors files
        while True:
            if time.time() - self.start_time > 3:
                print("chosiing language" + self.language_option[self.current_option % len(self.language_option)])
                self.selected_language = self.language_option[self.current_option % len(self.language_option)]
                self.resumePlayBack()
                break