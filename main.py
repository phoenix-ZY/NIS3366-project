import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from ui.mosaic import mosaic
from ui.watermark import watermark
from ui.remove_watermark import remove_watermark
from ui.others import others

from qfluentwidgets import FluentIcon, MSFluentWindow

class MainWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()

        self.mosaic = mosaic(self)
        self.watermark = watermark(self)
        self.remove_watermark = remove_watermark(self)
        self.others = others(self)
        self.addSubInterface(self.mosaic, FluentIcon.HOME, '添加马赛克')
        self.addSubInterface(self.watermark, FluentIcon.MOVIE, '添加水印')
        self.addSubInterface(self.remove_watermark, FluentIcon.TAG, '去除水印')
        self.addSubInterface(self.others, FluentIcon.IOT, '其他')
        self.initWindow()
        # self.navigationInterface.addSeparator()

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
