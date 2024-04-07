"""
舒飞翔是我们的光！
"""
# from PySide6.QtCore import Qt,QTime,QTimer,QThread,Signal
import os
import random
import time
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import blind_watermark as bw
import core
import cv2
import shutil
import json
import os
import command


recoverdata={}
def initial():
    current_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_path)
    """
    准备相应文件夹与工作环境
    :return:
    """

    if os.path.exists("origin"):
        pass
    else:
        os.mkdir("origin")
    if os.listdir("origin") != []:
        for i in os.listdir("origin"):
            os.remove("origin/" + i)

def process(watermark,
            videoc,
            filename,
            sampletimes=5,
            peroid=1,
            ):
    """
    主处理函数
    :param watermark:水印内容
    :param videoc: 输入视频cv2读取结果
    :param filename: 输出视频路径
    :param sampletimes: 取样次数
    :param peroid: 取样个数增量
    :return:是否成功
    """
    filetype=".png"
    sen = 0
    kbps=10000
    maxkbps=25000
    videotype=".mp4"
    outputtype="video"
    processtype="text"
    watermarkquality=30    ## 水印质量，建议为30，如果视频压制更厉害需要相应提高

    seed=[]
    for tim in range(2):
        seed.append(random.randint(1,9999))
    seed.append(watermarkquality)
    # 生成随机种子用于水印合成
    initial() #初始化

    video = videoc
    frame_count = int(videoc.get(cv2.CAP_PROP_FRAME_COUNT))

    fps = int(videoc.get(cv2.CAP_PROP_FPS))
    # 获取视频的宽度（单位：像素）
    width = videoc.get(cv2.CAP_PROP_FRAME_WIDTH)
    # 获取视频的高度（单位：像素）
    height = videoc.get(cv2.CAP_PROP_FRAME_HEIGHT)
    sen1=str(str(int(width))+"x"+str(int(height)))
    if sen==0: #自动获取分辨率
        sen=sen1

    framelist = []
    for i in range(int(sampletimes)):
        framenumber = random.randint(1, frame_count)
        processfr = framenumber #对视频进行随机抽帧
        for ti in range(int(peroid)):
            if processfr <= frame_count: #加长取样区间，减少解密难度
                framelist.append(processfr) #判断帧号是否超出范围
            processfr = processfr+1
    framelist = list(set(framelist))
    print(framelist)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'

    index = 0
    video.set(cv2.CAP_PROP_POS_FRAMES, index)
    # 遍历每个指定的帧位置
    a = []
    while True:
        ret,frame = video.read()
        if not ret :
            break
        if index in framelist:
            wm_len, frame = core.encodewatermark_text(watermark, frame)
        cv2.imwrite(f'origin/{index}.png', frame)
        a.append(frame)
        index += 1

    comm=r"ffmpeg\bin\ffmpeg.exe -r "+str(fps)+" -f image2 -start_number 0 -i origin/%0d"+str(filetype)+" -c:v libx264 -b:v "+str(kbps)+"k -maxrate "+str(kbps)+"k -bufsize 10000k -pix_fmt yuv420p -c:a copy origin/"+str(filename) + ".mp4 -y"
    sta=os.system(comm)

    # out = cv2.VideoWriter("result/" + str(filename) + "/output.mp4", fourcc, fps, (int(width),int(height)))
    for i in range(frame_count):
        # frame = cv2.imread(f'frame_{i}.png')
        # # frame = a[i]
        # out.write(frame)
        os.remove(f'origin/{i}.png')
    # out.release()

    return wm_len,watermark

def recover(videoc,wm_len,watermark):
    index = 0
    video = videoc
    video.set(cv2.CAP_PROP_POS_FRAMES, index)
    while True:
        

        ret,frame = video.read()
        if not ret :
            break
        resu = core.decodewatermark_text(wm_len, frame)
        print(resu)
        index += 1
        if resu == watermark:
            return True
        print(index)
    return False


# if __name__ == "__main__":
#     initial()

#     ## text
#     process(r"hellozts",r"meeting_02.mp4",filetype=".png",filename="testzts",outputtype="video",processtype="text")
#     recorver(r"result/testzts/testzts.json",r"result/testzts/testzts.mp4","text")
