import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ui.mosaic import mosaic

from PyQt5.QtMultimedia import *

from qfluentwidgets import FluentIcon, SplitFluentWindow, FluentTranslator, setFont, SubtitleLabel

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))

class MainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        self.mosaic = mosaic(self)
        self.test = Widget('123')
        self.addSubInterface(self.mosaic, FluentIcon.HOME, '自动添加马赛克')
        # self.navigationInterface.addSeparator()
        self.addSubInterface(self.test, FluentIcon.ACCEPT, '为什么啊')
        self.initWindow()

    def initWindow(self):
        self.resize(1160, 810)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('视频处理器')

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.navigationInterface.setExpandWidth(200)

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)

    translator = FluentTranslator()
    app.installTranslator(translator)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
