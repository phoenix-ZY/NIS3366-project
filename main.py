import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ui.mosaic import mosaic
from ui.watermark import watermark

from PyQt5.QtMultimedia import *

from qfluentwidgets import FluentIcon, MSFluentWindow

class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.mosaic = mosaic(self)
        self.watermark = watermark(self)
        self.addSubInterface(self.mosaic, FluentIcon.HOME, '添加马赛克')
        # self.navigationInterface.addSeparator()
        self.addSubInterface(self.watermark, FluentIcon.MOVIE, '添加水印')
        self.initWindow()

    def initWindow(self):
        self.resize(1350, 810)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('视频处理器')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
