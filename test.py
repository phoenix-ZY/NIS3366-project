import cv2
import os

# Read the video
video = cv2.VideoCapture('../test.mp4')
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))



# Create a VideoWriter for the output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = video.get(cv2.CAP_PROP_FPS)
frame_size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

video.release()
out = cv2.VideoWriter('output_video.mp4', fourcc, fps, frame_size)

# Read the saved frames and write them to the new video
for i in range(frame_count):
    frame = cv2.imread(f'invisible_video_watermark\output_frame_{i}.png')
    if frame is None:
        break
    out.write(frame)
out.release()