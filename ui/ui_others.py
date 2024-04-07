# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_others.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_others(object):
    def setupUi(self, others):
        others.setObjectName("others")
        others.resize(1160, 810)
        self.commandbar = CommandBar(others)
        self.commandbar.setGeometry(QtCore.QRect(0, 0, 541, 34))
        self.commandbar.setObjectName("commandbar")
        self.video = QtWidgets.QGraphicsView(others)
        self.video.setGeometry(QtCore.QRect(10, 40, 960, 540))
        self.video.setObjectName("video")
        self.video_slider = Slider(others)
        self.video_slider.setGeometry(QtCore.QRect(10, 580, 961, 21))
        self.video_slider.setOrientation(QtCore.Qt.Horizontal)
        self.video_slider.setObjectName("video_slider")
        self.play_button = ToolButton(others)
        self.play_button.setGeometry(QtCore.QRect(410, 610, 38, 32))
        self.play_button.setObjectName("play_button")
        self.add_subtitle = PushButton(others)
        self.add_subtitle.setGeometry(QtCore.QRect(260, 660, 102, 32))
        self.add_subtitle.setObjectName("add_subtitle")
        self.start_frame_button = PushButton(others)
        self.start_frame_button.setGeometry(QtCore.QRect(370, 660, 102, 32))
        self.start_frame_button.setObjectName("start_frame_button")
        self.end_frame_button = PushButton(others)
        self.end_frame_button.setGeometry(QtCore.QRect(490, 660, 102, 32))
        self.end_frame_button.setObjectName("end_frame_button")

        self.retranslateUi(others)
        QtCore.QMetaObject.connectSlotsByName(others)

    def retranslateUi(self, others):
        _translate = QtCore.QCoreApplication.translate
        others.setWindowTitle(_translate("others", "Form"))
        self.add_subtitle.setText(_translate("others", "添加字幕"))
        self.start_frame_button.setText(_translate("others", "获取起始帧"))
        self.end_frame_button.setText(_translate("others", "获取终止帧"))
from qfluentwidgets import CommandBar, PushButton, Slider, ToolButton
