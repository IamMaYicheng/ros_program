#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image

class image_converter:
    def __init__(self):
        # 创建cv_bridge，声明图像的发布者和订阅者
        self.image_pub = rospy.Publisher("cv_bridge_image", Image, queue_size=1)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/usb_cam/image_raw", Image, self.callback)

    def callback(self,data):
        # 使用cv_bridge将ROS的图像数据转换成OpenCV的图像格式
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        # 显示Opencv格式的图像
        font = cv2.FONT_HERSHEY_SIMPLEX  # 使用默认字体
        lower_red = np.array([0, 160, 170])  # 红色阈值下界
        higher_red = np.array([10, 235, 240])  # 红色阈值上界
        img_hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)  # RGB颜色空间向HSV颜色空间转变
        mask = cv2.inRange(img_hsv, lower_red, higher_red)  # 过滤出红色部分
        mask = cv2.medianBlur(mask, 5)  # 中值滤波
        #   cv2.imshow('mask', mask)
        #   cv2.waitKey(0)
        #   cv2.destroyAllWindows()
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # 轮廓检测
        (x, y, w, h) = cv2.boundingRect(contours[0])  # 返回矩阵四个点的坐标
        cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 0, 255), 3)  # 绘制矩形
        
        # 再将opencv格式的数据转换成ros image格式的数据发布
        try:
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
        except CvBridgeError as e:
            print(e)

if __name__ == '__main__':
    try:
        # 初始化ros节点
        rospy.init_node("cv_bridge_test")
        rospy.loginfo("Starting cv_bridge_test node")
        image_converter()
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down cv_bridge_test node.")
        cv2.destroyAllWindows()
