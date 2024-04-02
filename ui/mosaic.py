# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect

from ui.ui_mosaic import Ui_mosaic
from FaceDetection.API import *
import sys
from PyQt5.QtCore import Qt, QThreadPool, QRunnable
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
import numpy as np

from PyQt5.QtMultimedia import *

from qfluentwidgets import CommandBar, Action, FluentIcon, SplitFluentWindow, FluentTranslator

video_width = 960
video_height = 540


class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)


class mosaic(Ui_mosaic, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.threadPool = QThreadPool()

        # 按钮初始化
        self.play_button.setIcon(FluentIcon.PLAY)
        self.play_button.setToolTip('播放')
        self.cut_button.setToolTip('获取起始帧')
        self.cut_button.setIcon(FluentIcon.CUT)
        self.last_frame.setToolTip('上一帧')
        self.last_frame.setIcon(FluentIcon.CARE_LEFT_SOLID)
        self.next_frame.setToolTip('下一帧')
        self.next_frame.setIcon(FluentIcon.CARE_RIGHT_SOLID)
        self.choose_face.setToolTip('确定选择要打码的人脸')
        self.choose_face.setIcon(FluentIcon.ACCEPT)
        self.detect_face.setToolTip('开始检测人脸')
        self.detect_face.setIcon(FluentIcon.CAMERA)

        self.play_button.clicked.connect(self.__play_video)
        self.cut_button.clicked.connect(self.__get_start_frame)
        self.last_frame.clicked.connect(self.__set_last_frame)
        self.next_frame.clicked.connect(self.__set_next_frame)
        self.choose_face.clicked.connect(self.check_status)
        self.detect_face.clicked.connect(self.face_detect)

        # 菜单栏初始化
        self.commandbar.addActions([Action(FluentIcon.DOCUMENT, '打开文件', triggered=self.__open_file), Action(FluentIcon.SAVE, '保存', triggered=self.__save_file)])

        # 播放窗口设置
        self.video.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.video.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.video.setMouseTracking(False)
        self.video.setFocusPolicy(Qt.NoFocus)
        self.video.setPalette(QPalette(Qt.black))

        # 进度条初始化
        self.video_slider.sliderMoved.connect(self.__set_video)  # 进度条拖拽跳转
        self.video_slider.clicked.connect(self.__click_set_video)  # 进度条点击跳转
        self.video_slider.sliderReleased.connect(lambda: setattr(self, 'slider_pressed', False))  # 进度条释放时允许视频更新slider

        # 变量初始化
        self.slider_pressed = False
        self.all_frame_nums = None
        self.opencv_cap = None
        self.start_frame = None
        self.fps = None
        self.end_frame = None
        self.workable = False
        self.file_name = None
        self.frame_index = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.__next_frame)

    # 获取起始帧
    def __get_start_frame(self):
        self.start_frame = None
        self.end_frame = None
        if self.workable:
            self.start_frame = self.frame_index - 1
            self.cut_button.setToolTip('获取结束帧')
            self.cut_button.disconnect()
            self.cut_button.clicked.connect(self.__get_end_frame)

    # 获取结束帧
    def __get_end_frame(self):
        if self.workable:
            self.end_frame = self.frame_index - 1
            self.cut_button.setToolTip('获取起始帧')
            self.cut_button.disconnect()
            self.cut_button.clicked.connect(self.__get_start_frame)
            self.start_frame, self.end_frame = self.end_frame, self.start_frame if self.start_frame > self.end_frame else (self.start_frame, self.end_frame)

    def __img_resize(self, img):
        height, width = img.shape[0], img.shape[1]
        ratio = min(video_width / width, video_height / height)
        img = cv2.resize(img, (int(width * ratio), int(height * ratio)))
        # 图片背景填充黑色
        top = (video_height - img.shape[0]) >> 1
        bottom = video_height - img.shape[0] - top
        left = (video_width - img.shape[1]) >> 1
        right = video_width - img.shape[1] - left
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        return img

    def __open_file(self):
        self.workable = False
        filename, _ = QFileDialog.getOpenFileName(self, "打开视频", "", "视频文件(*.mp4 *.avi *.flv *.mkv *.mov *.wmv)")
        if filename == '':
            return

        self.file_name = filename
        self.start_frame = None
        self.end_frame = None

        # 使用opencv打开文件，获取总帧数
        self.opencv_cap = cv2.VideoCapture(filename)
        self.all_frame_nums = int(self.opencv_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(1000 / self.opencv_cap.get(cv2.CAP_PROP_FPS))
        self.frame_index = 1  # 这是当前显示的为第x帧，base 1

        # 显示第一帧图片
        self.__show_img(self.opencv_cap.read()[1])

        self.workable = True

    def __show_img(self, img):
        if img is None:
            return
        frame = self.__img_resize(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (video_width, video_height))
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap.fromImage(QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)))
        self.video.setScene(scene)

    def __play_video(self):
        if self.workable:
            if self.timer.isActive():
                self.play_button.setIcon(FluentIcon.PLAY)
                self.play_button.setToolTip('播放')
                self.timer.stop()
            else:
                self.play_button.setIcon(FluentIcon.PAUSE)
                self.play_button.setToolTip('暂停')
                self.timer.start(self.fps)

    def __set_last_frame(self):
        if self.workable:
            if self.timer.isActive():
                self.__play_video()
            if self.frame_index == 1:
                return
            self.frame_index -= 1
            self.opencv_cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index - 1)
            self.__show_img(self.opencv_cap.read()[1])
            self.__change_slide(self.frame_index)

    def __set_next_frame(self):
        if self.workable:
            if self.timer.isActive():
                self.__play_video()
            if self.frame_index == self.all_frame_nums:
                return
            self.frame_index += 1
            self.opencv_cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index - 1)
            self.__show_img(self.opencv_cap.read()[1])
            self.__change_slide(self.frame_index)

    # 结束时按钮变为播放
    def __video_stop(self):
        self.play_button.setIcon(FluentIcon.PLAY)
        self.play_button.setToolTip('播放')
        self.timer.stop()
        self.frame_index = 1
        self.opencv_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # 播放下一帧
    def __next_frame(self):
        self.frame_index += 1
        if self.frame_index >= self.all_frame_nums:
            self.__video_stop()
            return
        self.__show_img(self.opencv_cap.read()[1])
        self.__change_slide(self.frame_index)

    def __save_file(self):
        pass

    # 滑动条跟随视频播放更改
    def __change_slide(self, v):
        if self.workable and not self.slider_pressed:
            self.video_slider.setValue(int(v * 1000 // self.all_frame_nums))

    def __set_video(self, v):
        if self.workable:
            self.slider_pressed = True
            self.frame_index = int(v * self.all_frame_nums / 1000)
            self.opencv_cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
            self.__show_img(self.opencv_cap.read()[1])

    def __click_set_video(self, v):
        if self.workable:
            self.slider_pressed = False
            self.frame_index = int(v * self.all_frame_nums / 1000)
            self.opencv_cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_index)
            self.__show_img(self.opencv_cap.read()[1])

    def face_detect(self):
        self.target_video = VideoInitialize(self.opencv_cap, 0.5)
        detected_faces = self.target_video.faces
        face_dict = {}
        for name in detected_faces:
            data = detected_faces[name].showface(mode='return')
            height, width, channel = data.shape
            q_image = QtGui.QImage(data, width, height, 3 * width, QtGui.QImage.Format_RGB888)
            face_dict[name] = q_image

        list_widget_width = self.image_list.width()
        for name in face_dict:
            item = QtWidgets.QListWidgetItem(self.image_list)
            widget = QtWidgets.QWidget()
            widget.setMaximumWidth(list_widget_width)
            layout = QtWidgets.QHBoxLayout(widget)
            label = QtWidgets.QLabel()
            label.setObjectName(str(name))
            pixmap = QtGui.QPixmap.fromImage(face_dict[name])
            scaled_pixmap = pixmap.scaled(list_widget_width - 40, 100, QtCore.Qt.KeepAspectRatio)
            label.setPixmap(scaled_pixmap)
            layout.addWidget(label)
            layout.addStretch()

            checkbox = QtWidgets.QCheckBox()
            layout.addWidget(checkbox, 0, QtCore.Qt.AlignRight)
            layout.setSpacing(2)
            layout.setAlignment(QtCore.Qt.AlignVCenter)

            widget.setLayout(layout)

            item.setSizeHint(widget.sizeHint())
            self.image_list.setItemWidget(item, widget)

    def check_status(self):
        checked_items = []

        for index in range(self.image_list.count()):
            item = self.image_list.item(index)
            widget = self.image_list.itemWidget(item)
            checkbox = widget.layout().itemAt(2).widget()
            if checkbox.isChecked():
                label = widget.layout().itemAt(0).widget().objectName()
                checked_items.append(int(label))
        if len(checked_items)==0:
            checked_items='all'

        working_path = './runs/tmp.mp4'
        VideoMosaic(self.target_video, working_path, frame_range='all', names=checked_items)
        self.opencv_cap = cv2.VideoCapture(working_path)
        self.all_frame_nums = int(self.opencv_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(1000 / self.opencv_cap.get(cv2.CAP_PROP_FPS))
        self.frame_index = 1  # 这是当前显示的为第x帧，base 1

        # 显示第一帧图片
        self.__show_img(self.opencv_cap.read()[1])
