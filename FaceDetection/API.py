from FaceDetection.main import *


def VideoInitialize(video: cv2.VideoCapture, conf=0.5):
    # 初始化对象并完成初始化加载
    VideoObject = TargetVideo(video, conf)

    return VideoObject


def VideoShowFaces(VideoObject: TargetVideo):
    # 将检测到的人脸返回，格式为字典，键为人脸对应名称，值为数组
    faces = {}
    for name in VideoObject.faces:
        faces[name] = VideoObject.faces[name].showface(mode='return')

    return faces


def VideoMosaic(VideoObject: TargetVideo, save_path='./runs/tmp.mp4', frame_range: list = 'all', names: list = 'all'):
    """
    frame_range对应视频对象中的帧数下标范围，形如[123,456]
    names为一个列表，其中元素为视频对象中的人脸名
    以上两者均支持设定值为’all'来选取全部
    """
    # 对连续若干帧执行打码并保存打码后视频
    VideoObject.mosaic_save(save_path=save_path, frame_range=frame_range, face_names=names)



def FrameMosaic(VideoObject: TargetVideo, frame_range: list, names: list):
    """
    frame_range和names的定义与上同，但不支持‘all'
    """
    # 对连续若干帧执行打码并返回打码后图片的集合
    new_imgs = VideoObject.FrameFaceMosaic(frame_range, names)
    return new_imgs


if __name__ == '__main__':
    cap = cv2.VideoCapture("./debug_video.mp4")
    target = VideoInitialize(cap, 0.45)
    faces = VideoShowFaces(target)
    '''
    与用户交互获取指定要打码的人脸
    '''
    VideoMosaic(target,save_path='./111.mp4')

    # new_imgs=FrameMosaic(target,[0,1000],[1,2,3])
