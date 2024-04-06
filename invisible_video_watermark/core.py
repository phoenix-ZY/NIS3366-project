import os.path
import random

import blind_watermark as bw
from PIL import Image

bw.bw_notes.close()
# from algorithm.firekepper.BlindWatermark import watermark as fwatermark


def encodewatermark_text(text,
                         input,
                         ):
    
    watermark = bw.WaterMark(password_img=1, password_wm=1, processes=None)
    watermark.read_img(img = input)
    watermark.read_wm(text, mode='str')
    watermarked_image = watermark.embed()
    len_wm = len(watermark.wm_bit)
    return len_wm, watermarked_image


def decodewatermark_text(
        len_wm,
        input,
):
    """
    对输入内容进行解水印
    :param input: 输入图片
    :param len_wm: 水印长度，程序生成值
    :return: 水印文字或者图片
    """
    extract = bw.WaterMark(password_img=1, password_wm=1, processes=None)
    result = extract.extract(embed_img = input, wm_shape=int(len_wm), mode="str")
    return result
