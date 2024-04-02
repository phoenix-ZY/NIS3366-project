import numpy as np
from scipy.optimize import linear_sum_assignment
import cv2
import matplotlib.pyplot as plt


def new_name_func(initial_value=0):
    def inner():
        nonlocal initial_value
        initial_value += 1
        return initial_value

    return inner


def zone2center(co_dict):
    return [(co_dict['x1'] + co_dict['x2']) / 2, (co_dict['y1'] + co_dict['y2']) / 2]


def MyHungary(previous_objs, current_objs, get_new_name):
    """
    previous_objs若非None则含序号，current_objs一定不含序号

    :param previous_objs:
    :param current_objs:
    :param get_new_name:
    :return:
    """

    if len(current_objs) == 0:
        return None
    if previous_objs is None:
        return {get_new_name(): obj for obj in current_objs}

    rectified_current_objs = current_objs.copy()

    indexes = list(previous_objs.keys())
    previous_objs_np = np.array(list(previous_objs.values()))
    current_objs_np = np.array(rectified_current_objs)

    try:
        diff = current_objs_np[:, np.newaxis, :] - previous_objs_np[np.newaxis, :, :]
    except:
        print(current_objs)
        print(previous_objs)

    dist_matrix = np.sqrt(np.sum(diff ** 2, axis=2))
    size = max(dist_matrix.shape)
    square_array = np.zeros((size, size))
    square_array[:dist_matrix.shape[0], :dist_matrix.shape[1]] = dist_matrix

    if len(previous_objs) < len(current_objs):
        for i in range(len(current_objs) - len(previous_objs)):
            indexes.append(-1 - i)

    # row是当前，col是之前
    row_ind, col_ind = linear_sum_assignment(square_array)
    rst = {}
    for i in range(len(current_objs)):
        name = indexes[col_ind[i]]
        if name < 0 or (current_objs[i][0] - previous_objs[name][0]) ** 2 + (current_objs[i][1] - previous_objs[name][1]) ** 2 > 10000:
            name = get_new_name()

        rst[name] = current_objs[i]

    return rst


def Mosiac(data, box_list):
    try:
        for box in box_list:
            data[int(box.y1):int(box.y2), int(box.x1):int(box.x2)] = cv2.blur(data[int(box.y1):int(box.y2), int(box.x1):int(box.x2)], (175, 175))
    except:
        print(data)
        print(box_list)
        exit(888)
    # cv2.imshow('Blurred Image', data)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # array_to_image_with_text(data)
    return data


def array_to_image_with_text(array, co_dict=None):
    plt.clf()
    plt.imshow(array)  # 仍然是显示灰度图
    if co_dict is not None:
        for name in co_dict.keys():
            plt.text(co_dict[name][0], co_dict[name][1], str(name), color='red', fontsize=12)  # 在指定坐标添加文字
    plt.show()
