#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-09-26 16:13
# @Author  : Stardustsky
# @File    : core.py
# @Software: PyCharm


import cv2
import numpy as np
import math
from keras.models import Sequential,load_model


alphabet = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
num_model = load_model("model/num.model")
letter_model = load_model("model/letter.model")

def Euclidean(vec1, vec2):
    """
    Euclidean_Distance,欧式距离
    :param vec1:
    :param vec2:
    :return:
    """
    npvec1, npvec2 = np.array(vec1), np.array(vec2)
    return math.sqrt(((npvec1 - npvec2) ** 2).sum())


def img_mser(img):
    """
    图像切割算法
    :param img:
    :return:
    """
    # 图像预处理
    img = img_resize(img)
    box_content = list()
    box_mser = list()
    mser = cv2.MSER_create(_min_area=50, _max_area=350)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

    # 连通域划分及去重
    regions, boxes = mser.detectRegions(img)
    boxes = boxes.tolist()
    for i in boxes:
        if i not in box_content:
            box_content.append(i)

    # 使用欧氏距离算法去除近似连通域
    for j in box_content:
        if box_mser:
            for k in xrange(len(box_mser)):
                if Euclidean(j, box_mser[k]) > 12 and k == len(box_mser) - 1:
                    box_mser.append(j)
        else:
            box_mser.append(j)

    # 去除多余连通域
    box_mser_len = len(box_mser)
    if box_mser_len != 4:
        if box_mser_len > 4:
            for i in box_mser:
                area = list()
                area.append(i[2] * i[3])
            for j in xrange(box_mser_len - 4):
                pos = area.index(min(area)) - 1
                box_mser.remove(box_mser[pos])
        else:
            print u'切割出现问题，请改变设置值'
            return 0

    # print box_mser
    cut_img = list()
    box_mser.sort()
    for z in xrange(len(box_mser)):
        k = box_mser[z]
        slice_img = img[k[1]-2:k[1] + k[3]+2, k[0]-2:k[0] + k[2] + 2]
        cut_img.append(cv2.resize(slice_img, (30, 40)))
    return cut_img


def img_solve(img):
    """
    图像灰度及改变大小
    :param img:
    :return:
    """
    # img_show(img)
    GraImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, GraImage = cv2.threshold(GraImage, 180, 255, cv2.THRESH_BINARY)
    GraImage = cv2.resize(GraImage, (100, 40))
    # print GraImage.shape
    # ret, GraImage = cv2.threshold(GraImage, 127, 255, cv2.THRESH_BINARY)

    return GraImage


def img_to_RGB(img):
    GraImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return GraImage


def img_resize(img):
    img = cv2.resize(img, (100, 40))
    return img


def img_threshold_filter(img, th=180):
    ret, img = cv2.threshold(img, th, 255, cv2.THRESH_BINARY)
    return img


def img_salt_filter(img):
    """
    去除椒盐类干扰
    :param img:
    :return:
    """
    newIMG = cv2.medianBlur(img, 5)
    return newIMG


def img_open_filter(img):
    """
    图像开运算，去除噪点类干扰以及补全验证码缺口
    :param img:
    :return:
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
    # closed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    # newImg = cv2.erode(closed, kernel2, iterations=1)
    newImg = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    newImg = cv2.dilate(newImg, kernel2)
    return newImg


def img_close_filter(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, 1))
    closed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    newImg = cv2.erode(closed, kernel2, iterations=1)
    return newImg


def main(img, cap_type="401"):

    if cap_type == "401":
        model = num_model
    elif cap_type == "402":
        model = letter_model
    cut_img = img_mser(img)
    captcha = ""

    for i in cut_img:
        i = cv2.cvtColor(i, cv2.COLOR_GRAY2RGB)
        i = np.array(i, dtype='float32')/255
        i = np.expand_dims(i, axis=0)
        res = model.predict(i).tolist()[0]
        captcha += alphabet[res.index(max(res))]
    return captcha
