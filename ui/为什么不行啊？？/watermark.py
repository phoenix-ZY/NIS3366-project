from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect

from ui.ui_watermark import Ui_watermark

import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QUrl
import cv2

from qfluentwidgets import Action, FluentIcon
from qfluentwidgets.multimedia import VideoWidget


class watermark(Ui_watermark, QWidget):
    def __init__(self, parent=None):
        
        super().__init__(parent=parent)
        self.setupUi(self)

        self.work_button.setIcon(FluentIcon.CUT)
        self.work_button.setToolTip('添加水印')

        # 菜单栏初始化
        self.commandbar.addAction(Action(FluentIcon.DOCUMENT, '打开文件', triggered=self.__open_file))

        self.player = VideoWidget()
        self.video.addWidget(self.player)

    def __open_file(self):
        self.workable = False
        filename, _ = QFileDialog.getOpenFileName(self, "打开视频", "", "视频文件(*.mp4 *.avi *.flv *.mkv *.mov *.wmv)")
        if filename == '':
            return
        self.player.setVideo(QUrl.fromLocalFile(filename))
        self.player.play()
