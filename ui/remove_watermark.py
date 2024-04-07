from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect

from ui.ui_remove_watermark import Ui_remove

import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QUrl
import cv2
import os
from tqdm import tqdm

import glob
import numpy as np
from moviepy.editor import VideoFileClip
from qfluentwidgets import Action, FluentIcon
from qfluentwidgets.multimedia import VideoWidget

video_width = 960
video_height = 540

class remove_watermark(Ui_remove, QWidget):
    def __init__(self, parent=None):

        super().__init__(parent=parent)
        self.setupUi(self)

        self.work_button.setIcon(FluentIcon.PALETTE)
        self.work_button.setToolTip('去除水印')
        self.work_button.clicked.connect(self.__remove_watermark)
        self.play_button.setIcon(FluentIcon.PLAY)
        self.play_button.setToolTip('播放')
        self.play_button.clicked.connect(self.__play_video)
        self.addwater_button.setIcon(FluentIcon.PALETTE)
        self.addwater_button.setToolTip('添加水印')
        self.addwater_button.clicked.connect(self.__adda_watermark)

        # 菜单栏初始化
        self.commandbar.addAction(Action(FluentIcon.DOCUMENT, '打开文件', triggered=self.__open_file))

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

    def __remove_watermark(self):
        def ensure_directory_exists(directory):
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    print(f"创建目录: {directory}")
                except OSError as error:
                    print(f"创建目录 {directory} 时出错: {error}")
                    raise

        def is_valid_video_file(file):
            try:
                with VideoFileClip(file) as video_clip:
                    return True
            except Exception as e:
                print(f"无效的视频文件: {file}, 错误: {e}")
                return False

        def get_first_valid_frame(video_clip, threshold=10, num_frames=10):
            total_frames = int(video_clip.fps * video_clip.duration)
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

            for idx in frame_indices:
                frame = video_clip.get_frame(idx / video_clip.fps)
                if frame.mean() > threshold:
                    return frame

            return video_clip.get_frame(0)

        def select_roi_for_mask(video_clip):
            frame = get_first_valid_frame(video_clip)

            # 将视频帧调整为720p显示
            display_height = 720
            scale_factor = display_height / frame.shape[0]
            display_width = int(frame.shape[1] * scale_factor)
            display_frame = cv2.resize(frame, (display_width, display_height))
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            # instructions = ""
            font = cv2.FONT_HERSHEY_SIMPLEX
            # cv2.putText(display_frame, instructions, (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

            r = cv2.selectROI(display_frame)
            cv2.destroyAllWindows()

            r_original = (
                int(r[0] / scale_factor), int(r[1] / scale_factor), int(r[2] / scale_factor), int(r[3] / scale_factor))

            return r_original

        def detect_watermark_adaptive(frame, roi):
            roi_frame = frame[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
            gray_frame = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
            _, binary_frame = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            mask = np.zeros_like(frame[:, :, 0], dtype=np.uint8)
            mask[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]] = binary_frame

            return mask

        def generate_watermark_mask(video_clip, num_frames=10, min_frame_count=7):
            total_frames = int(video_clip.duration * video_clip.fps)
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

            frames = [video_clip.get_frame(idx / video_clip.fps) for idx in frame_indices]
            r_original = select_roi_for_mask(video_clip)

            masks = [detect_watermark_adaptive(frame, r_original) for frame in frames]

            final_mask = sum((mask == 255).astype(np.uint8) for mask in masks)
            # 根据像素点在至少min_frame_count张以上的帧中的出现来生成最终的遮罩
            final_mask = np.where(final_mask >= min_frame_count, 255, 0).astype(np.uint8)

            kernel = np.ones((5, 5), np.uint8)
            return cv2.dilate(final_mask, kernel)

        def process_video(video_clip, output_path, apply_mask_func):
            total_frames = int(video_clip.duration * video_clip.fps)
            progress_bar = tqdm(total=total_frames, desc="正在处理帧", unit="帧")

            def process_frame(frame):
                result = apply_mask_func(frame)
                progress_bar.update(1000)
                return result

            processed_video = video_clip.fl_image(process_frame, apply_to=["each"])
            processed_video.write_videofile(f"{output_path}.mp4", codec="libx264")

        # 主代码
        output_dir = "output"
        ensure_directory_exists(output_dir)

        if is_valid_video_file(self.file_name):
            video_clip = VideoFileClip(self.file_name)
            watermark_mask = generate_watermark_mask(video_clip)

            mask_func = lambda frame: cv2.inpaint(frame, watermark_mask, 3, cv2.INPAINT_NS)
            video_name = os.path.basename(self.file_name)
            output_video_path = os.path.join(output_dir, os.path.splitext(video_name)[0])
            process_video(video_clip, output_video_path, mask_func)
            print(f"成功处理视频文件: {video_name}")
        else:
            print("无效的视频文件")


    def __adda_watermark(self):
        def ensure_directory_exists(directory):
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    print(f"Created directory: {directory}")
                except OSError as error:
                    print(f"Error creating directory {directory}: {error}")
                    raise


        def is_valid_video_file(file):
            try:
                with VideoFileClip(file) as video_clip:
                    return True
            except Exception as e:
                print(f"Invalid video file: {file}, Error: {e}")
                return False


        def get_first_valid_frame(video_clip, threshold=10, num_frames=10):
            total_frames = int(video_clip.fps * video_clip.duration)
            frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

            for idx in frame_indices:
                frame = video_clip.get_frame(idx / video_clip.fps)
                if frame.mean() > threshold:
                    return frame

            return video_clip.get_frame(0)


        def select_watermark_position(video_clip):
            frame = get_first_valid_frame(video_clip)

            # 将视频帧调整为720p显示
            display_height = 720
            scale_factor = display_height / frame.shape[0]
            display_width = int(frame.shape[1] * scale_factor)
            display_frame = cv2.resize(frame, (display_width, display_height))
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            instructions = ""
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(
                display_frame, instructions, (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA
            )

            r = cv2.selectROI(display_frame)
            cv2.destroyAllWindows()

            position = (int(r[0] / scale_factor), int(r[1] / scale_factor))

            return position


        def add_watermark(video_clip, watermark_path, watermark_position):
            watermark = cv2.imread(watermark_path, cv2.IMREAD_UNCHANGED)
            watermark_height, watermark_width, _ = watermark.shape

            def add_watermark_to_frame(frame):
                frame_height, frame_width, _ = frame.shape
                x, y = watermark_position

                # 创建一个与视频帧大小相同的全黑图像
                watermarked_frame = np.zeros_like(frame)

                # 将视频帧复制到新图像
                watermarked_frame[:] = frame

                # # 检查水印是否超出视频帧边界
                # if x + watermark_width > frame_width:
                #     watermark = watermark[:, :frame_width - x]
                # if y + watermark_height > frame_height:
                #     watermark = watermark[:frame_height - y, :]

                # 将水印图片直接叠加到指定位置
                watermarked_frame[y : y + watermark.shape[0], x : x + watermark.shape[1]] = (
                    cv2.addWeighted(
                        watermarked_frame[
                            y : y + watermark.shape[0], x : x + watermark.shape[1]
                        ],
                        1,
                        watermark,
                        1,
                        0,
                    )
                )

                return watermarked_frame

            return video_clip.fl_image(add_watermark_to_frame)


        def process_video(video_clip, output_path, watermark_path, watermark_position):
            watermarked_clip = add_watermark(video_clip, watermark_path, watermark_position)
            watermarked_clip.write_videofile(f"{output_path}.mp4", codec="libx264")


        input_video = self.file_name
        watermark_path = "logo.jpg"
        output_dir = "output"

        ensure_directory_exists(output_dir)

        if is_valid_video_file(input_video):
            video_clip = VideoFileClip(input_video)
            watermark_position = select_watermark_position(video_clip)

            video_name = os.path.basename(input_video)
            output_video_path = os.path.join(output_dir, os.path.splitext(video_name)[0])
            process_video(video_clip, output_video_path, watermark_path, watermark_position)
            print(f"Successfully processed {video_name}")
        else:
            print("Invalid video file")