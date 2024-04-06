import whisper
import os
import imageio
from zhconv import convert

def load_video(file_path:str):
    """
    加载视频
    @params:
        file_path   - Required  : 视频路径 (str)
    """
    if os.path.exists(file_path):
        return imageio.get_reader(file_path)
    else:
        raise FileNotFoundError("File not found")

def load_model(model:str='large'):
    """
    加载模型
    @params:
        model   - Required  : 模型大小 (str). Must be one of ['tiny','small','medium','large','base']
    """
    assert model in ['tiny','small','medium','large','base'], 'model must be in ["tiny","small","medium","large","base"]'
    return whisper.load_model(model)


    
def seconds_to_hmsm(seconds:float):
    """
    输入一个秒数，输出为H:M:S:M时间格式
    @params:
        seconds   - Required  : 秒 (float)
    """
    hours = str(int(seconds // 3600))
    minutes = str(int((seconds % 3600) // 60))
    seconds = seconds % 60
    milliseconds = str(int(int((seconds - int(seconds)) * 1000))) # 毫秒留三位
    seconds = str(int(seconds))
    # 补0
    if len(hours) < 2:
        hours = '0' + hours
    if len(minutes) < 2:
        minutes = '0' + minutes
    if len(seconds) < 2:
        seconds = '0' + seconds
    if len(milliseconds) < 3:
        milliseconds = '0'*(3-len(milliseconds)) + milliseconds
    return f"{hours}:{minutes}:{seconds},{milliseconds}"

def srt_create(input:str,language:str,output:str,model:whisper.model):
    """
    创建srt文件
    @params:
        video   - Required  : 视频 
        language   - Required  : 语言 (str)
        output   - Required  : 输出路径 (str)
        model   - Required  : 模型 (whisper.model)
    """
    video=load_video(input)

    duration=seconds_to_hmsm(video.get_meta_data()['duration'])
    res=model.transcribe(input,fp16=False,language=language)
    with open(output,'w',encoding='utf-8') as f:
        i = 1
        for r in res['segments']:
            f.write(str(i)+'\n')
            f.write(seconds_to_hmsm(float(r['start']))+' --> '+seconds_to_hmsm(float(r['end']))+'\n')
            i += 1
            f.write(convert(r['text'], 'zh-cn')) # 结果可能是繁体，转为简体zh-cn
            f.write('\n')

if __name__=="__main__":
    model=load_model('small')
    srt_create(input=r'./1.mp4',language='Chinese',output=r'./1.srt',model=model)
