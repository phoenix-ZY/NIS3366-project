from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2

from qfluentwidgets import Action, FluentIcon
import os

from ui.ui_others import Ui_others
from SRT.srt import load_model, srt_create

video_width = 960
video_height = 540

class others(Ui_others, QWidget):
    def __init__(self, parent=None):
        
        super().__init__(parent=parent)
        self.setupUi(self)

        self.add_subtitle.setToolTip('添加字幕')
        self.add_subtitle.clicked.connect(self.__add_subtitle)
        self.play_button.setIcon(FluentIcon.PLAY)
        self.play_button.setToolTip('播放')
        self.play_button.clicked.connect(self.__play_video)
        self.start_frame_button.clicked.connect(self.__get_start_frame)
        self.end_frame_button.clicked.connect(self.__get_end_frame)

        # 菜单栏初始化
        self.commandbar.addActions([Action(FluentIcon.DOCUMENT, '打开文件', triggered=self.__open_file), Action(FluentIcon.SAVE, '保存片段', triggered=self.__save_file)])

        # 视频播放器初始化
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
        self.save_filename = None
        self.frame_index = None
        self.timer = QtCore.QTimer(self)

        self.timer.timeout.connect(self.__next_frame)

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

    # 显示一张图片
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
    
    # 添加字幕
    def __add_subtitle(self):
        model = load_model('small')
        srt_create(input=self.file_name, language='Chinese', output=self.file_name+".srt", model=model)

    def __save_file(self):
        if not self.workable:
            return
        
        self.save_filename = QFileDialog.getSaveFileName(self, "保存文件", "", "视频文件(*.mp4 *.avi *.flv *.mkv *.mov *.wmv)")
        if self.save_filename[0] == '':
            return
        # 删除save_filename文件
        os.system(f'del {self.save_filename[0]}')
        # 获取视频总时长
        duration = self.opencv_cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.opencv_cap.get(cv2.CAP_PROP_FPS)
        # 获取start_frame和end_frame对应的时间点
        start_time = self.start_frame / self.all_frame_nums * duration
        end_time = self.end_frame / self.all_frame_nums * duration
        # 使用ffmpeg进行剪辑
        command = f'ffmpeg -i {self.file_name} -ss {start_time} -to {end_time} -c copy {self.save_filename[0]}'
        os.system(command)
    

    # 获取起始帧
    def __get_start_frame(self):
        if self.workable:
            self.start_frame = self.frame_index - 1
            if self.start_frame and self.end_frame and self.start_frame > self.end_frame:
                self.start_frame, self.end_frame = self.end_frame, self.start_frame
            # print(self.start_frame, self.end_frame)

    # 获取结束帧
    def __get_end_frame(self):
        if self.workable:
            self.end_frame = self.frame_index - 1
            if self.start_frame and self.end_frame and self.start_frame > self.end_frame:
                self.start_frame, self.end_frame = self.end_frame, self.start_frame
            # print(self.start_frame, self.end_frame)