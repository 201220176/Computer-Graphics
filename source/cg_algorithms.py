#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math
from unittest import result


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        #DDA画线算法
        if x0 == x1:
            #垂直于x轴的直线
            step = 1 if y0 <= y1 else -1
            for y in range(y0, y1 + step,step):
                result.append((x0, y))
        else:
            k = (y1 - y0) / (x1 - x0)
            if abs(k)>=1:   #斜率大于1,y每增加1,x增加(1/k)取整
                step = 1 if y0 <= y1 else -1
                x = x0
                for y in range (y0,y1+step,step):
                    result.append((round(x),y))
                    x = x + (1/k)*step
            else:           #斜率小于等于1，x每增加1，y增加k取整
                step = 1 if x0 <= x1 else -1
                y = y0
                for x in range (x0,x1+step,step):
                    result.append((x,round(y)))
                    y = y + k*step
    elif algorithm == 'Bresenham':
        #Brasenham画线算法
        dx = abs(x1-x0)
        dy = abs(y1-y0)
        xstep = 1 if x0 <= x1 else -1
        ystep = 1 if y0 <= y1 else -1
        if abs(dy)<=abs(dx):     #斜率小于1
            p = 2*abs(dy) - abs(dx)   #引入决策变量，为了提高精度，将小数与除法转化为整数与减法
            y = y0
            for x in range(x0,x1+xstep,xstep):
                result.append((x,y))
                if p >= 0:
                    p = p-2*dx
                    y = y+ystep
                p = p+2*dy
        else:                   #斜率大于一
            p = 2*abs(dx) - abs(dy)   #引入决策变量，为了提高精度，将小数与除法转化为整数与减法
            x = x0
            for y in range(y0,y1+ystep,ystep):
                result.append((x,y))
                if p >= 0:
                    p = p-2*dy
                    x = x+xstep
                p = p+2*dx

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """

    #x^2 / a^2 + y^2 / b^2 = 1,F(x,y)= b^2 * x^2 + a^2 * y^2 - a^2 * b^2 = 0

    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    a = round(abs(x1-x0)/2)
    b = round(abs(y1-y0)/2)
    xc = round((x1+x0)/2)
    yc = round((y1+y0)/2)
    sqa = a**2
    sqb = b**2
    
    if a==0 or b==0:
        return draw_line(p_list,'DDA')
    
    x,y = 0,b
    d = sqb + sqa*(-b+0.25)     #决策变量，从(0,b)点开始。di = F(xi+1, yi-0.5)
    while sqb*(x)< sqa*(y):     #上半部分，dx>dy，即2xb^2>2ya^2
        result.append((x+xc,y+yc))
        result.append((x+xc,-y+yc))
        result.append((-x+xc,y+yc))
        result.append((-x+xc,-y+yc))
        if d < 0:
            d += sqb*(2*x+3)    #增量 di+1-di
        else:
            d += (sqb*(2*x+3)+sqa*(-2*y+2))
            y-=1
        x+=1   
    
    d = sqb*(x+0.5)**2 + sqa*(y-1)**2 -sqa*sqb
    while y>=0:                 #下半部分，dx<dy，即2xb^2<2ya^2
        result.append((x+xc,y+yc))
        result.append((x+xc,-y+yc))
        result.append((-x+xc,y+yc))
        result.append((-x+xc,-y+yc))
        if d < 0:
            d += (sqb*(2*x+2)+sqa*(3-2*y))
            x += 1
        else:
            d += sqa*(3-2*y)
        y-=1

    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    n = len(p_list)     #控制点个数
    result.append((round(p_list[0][0]), round(p_list[0][1])))
    if algorithm == 'Bezier':
        t=0.001
        while t<1:                          #取1000次比例系数t 
            temp = []
            for j in range(n-1):            #首先将控制点进行一轮递归，得到n-1个新的控制点，存在temp中
                    x0,y0=p_list[j]
                    x1,y1=p_list[j+1]
                    x,y=(1-t)*x0+t*x1,(1-t)*y0+t*y1
                    temp.append((x,y))
            for i in range(n-2):            #再进行n-2次控制点递归，即可得到一个曲线上的点
                for j in range(n-i-2):      #每次开始内层循环，都剩余n-i-1个控制点，故需要循环n-i-2次以得到最终点
                    x0,y0=temp[j]
                    x1,y1=temp[j+1]
                    x,y=(1-t)*x0+t*x1,(1-t)*y0+t*y1
                    temp[j]=(x,y)
            x,y=round(temp[0][0]),round(temp[0][1])
            result.append((x,y))
            t+=0.001
    elif algorithm == 'B-spline':
        pass
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for i in p_list:
        result.append([i[0] + dx, i[1] + dy])
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    pass
