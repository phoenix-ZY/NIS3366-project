import matplotlib.pyplot as plt
from ultralytics import YOLO
import json
from FaceDetection.utils import *
import cv2
import time


class MyBox:
    def __init__(self, box):
        self.x1 = box['x1']
        self.x2 = box['x2']
        self.y1 = box['y1']
        self.y2 = box['y2']
        self.center = zone2center(box)


class Face:
    def __init__(self, name, frame, data):
        self.name = name
        self.conf = data['confidence']
        self.face_data = frame[int(data['box']['y1']):int(data['box']['y2']), int(data['box']['x1']):int(data['box']['x2'])]

    def update(self, frame, data):
        if data['confidence'] > self.conf:
            self.face_data = frame[int(data['box']['y1']):int(data['box']['y2']), int(data['box']['x1']):int(data['box']['x2'])]

    def showface(self,mode='show'):
        face_data = cv2.cvtColor(self.face_data, cv2.COLOR_BGR2RGB)
        if mode=='show':
            plt.imshow(face_data)
            plt.show()
        elif mode=='return':
            return face_data
        else:
            raise ValueError(mode)



class FrameData:
    def __init__(self, index, boxes):
        self.index = index
        self.face_names = None
        self.boxes = [MyBox(box) for box in boxes]

    def get_center_list(self):
        return [box.center for box in self.boxes]


class TargetVideo:
    def __init__(self, video: cv2.VideoCapture, conf=0.5):
        self.origVideo = video
        self.get_new_name = new_name_func()
        self.model = YOLO('../FaceDetection/yolov8l-face.pt')  # ~1倍
        self.conf = conf
        self.frames_data = {}
        self.faces = {}

        self.frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))  # 视频的宽度
        self.frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 视频的高度
        self.frame_rate = int(video.get(cv2.CAP_PROP_FPS))  # 视频的帧率（FPS）
        self.frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))  # 视频的总帧数

        self.FramePreprocess()

    def FramePreprocess(self):
        pre_center_dict = None
        count = 0
        self.origVideo.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while self.origVideo.isOpened():
            success, frame = self.origVideo.read()
            if success:
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_index = int(self.origVideo.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                result = self.model(frame, conf=self.conf)[0]
                frame_json_data = json.loads(result.tojson())
                co_list = [item['box'] for item in frame_json_data]
                self.frames_data[frame_index] = FrameData(frame_index, co_list)
                indexed_center_dict = MyHungary(pre_center_dict, self.frames_data[frame_index].get_center_list(), self.get_new_name)
                if indexed_center_dict is not None:
                    self.frames_data[frame_index].face_names = list(indexed_center_dict.keys())
                    for idx, name in enumerate(indexed_center_dict):
                        if name not in self.faces:
                            self.faces[name] = Face(name, frame, frame_json_data[idx])
                        else:
                            self.faces[name].update(frame, frame_json_data[idx])
                else:
                    self.frames_data[frame_index].face_names=[]
                pre_center_dict = indexed_center_dict
            else:
                break
            count += 1
            print(count, '/', self.frame_count)

    def show_detected_faces(self):
        for name in self.faces:
            self.faces[name].showface()

    def FrameFaceMosaic(self, frame_range, name_list):

        imgs = []
        self.origVideo.set(cv2.CAP_PROP_POS_FRAMES, frame_range[0])
        count = frame_range[0]
        while count < frame_range[1]:
            ret, frame = self.origVideo.read()
            common_elements = list(set(name_list) & set(self.frames_data[count].face_names))
            if len(common_elements) > 0:
                box_list = []
                for name in common_elements:
                    box_list.append(self.frames_data[count].boxes[self.frames_data[count].face_names.index(name)])
                imgs.append(Mosiac(frame, box_list))
            else:
                imgs.append(frame)
            print('\r',count,'/',frame_range[1],end='')
            count+=1

        return imgs

    def mosaic_save(self, save_path='./runs/tmp.mp4', frame_range=None, face_names=None):
        # frame_range=[0, self.frame_count]
        # face_names=list(self.faces.keys())
        if face_names=="all":
            face_names=list(self.faces.keys())
        if frame_range=='all':
            frame_range=[0, self.frame_count]

        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        video_writer = cv2.VideoWriter(save_path, fourcc, self.frame_rate, (self.frame_width, self.frame_height))
        new_imgs = self.FrameFaceMosaic(frame_range, face_names)
        for img in new_imgs:
            video_writer.write(img)
        video_writer.release()


