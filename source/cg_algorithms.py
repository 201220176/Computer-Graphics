#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math
from pydoc import plain
from re import X
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
    result = []
    for p in p_list:
        x1 , y1 = p[0],p[1]
        d=math.radians(r)
        x2 = (x1-x)*math.cos(d)-(y1-y)*math.sin(d) + x
        y2 = (x1-x)*math.sin(d)+(y1-y)*math.cos(d) + y
        result.append((round(x2),round(y2)))

    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """

    result = []
    for p in p_list:
        x1 , y1 = p[0],p[1]
        x2 = (x1-x)*s+ x
        y2 = (y1-y)*s+ y
        result.append((round(x2),round(y2)))

    return result


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
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if algorithm == "Cohen-Sutherland":     #编码裁剪算法
         while True:
            #计算区域码
            code0,code1 = 0,0
            code0 += 1 if x0 < x_min else 0
            code0 += 2 if x0 > x_max else 0
            code0 += 4 if y0 < y_min else 0
            code0 += 8 if y0 > y_max else 0
            code1 += 1 if x1 < x_min else 0
            code1 += 2 if x1 > x_max else 0
            code1 += 4 if y1 < y_min else 0
            code1 += 8 if y1 > y_max else 0
            if code0 == 0 and code1 == 0:
                return [[round(x0), round(y0 )], [round(x1), round(y1 )]]
            elif code0 & code1 != 0:
                return []
            else:
                if code0 == 0:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                    code0, code1 = code1, code0
                if code0 & 1 == 1:
                    u = (x_min - x0) / (x1 - x0)
                    x0,y0 = x_min,y0 + u * (y1 - y0)
                elif code0 & 2 == 2:
                    u = (x_max - x0) / (x1 - x0)
                    x0, y0 = x_max,y0 + u*(y1 - y0)                
                elif code0 & 4 == 4:
                    u = (y_min - y0) / (y1 - y0)
                    x0 ,y0 = x0+u * (x1 - x0),y_min                
                elif code0 & 8 == 8:
                    u = (y_max - y0) / (y1 - y0)
                    x0 , y0 = x0+u * (x1 - x0),y_max
    elif algorithm == "Liang-Barsky":   #梁友栋-Barsky裁剪算法
        dx, dy = x1 - x0, y1 - y0
        p = [-dx, dx, -dy, dy]
        q = [x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
        u1 = 0
        u2 = 1
        if dx == 0:             #平行于y轴
            if q[0]<0 or q[1]<0:    #完全在窗口外
                return []
            else:
                for i in range(2):
                    if p[i+2]<0:    #线段(及其延长线)从边界外部进入内部，3为下边界，4为上边界
                        u1 = max(u1, q[i+2] / p[i+2])   
                    else:           #线段(及其延长线)从边界内部进入外部
                        u2 = min(u2, q[i+2] / p[i+2])   
        elif dy == 0:           #平行于x轴
            if q[2]<0 or q[3]<0:    #完全在窗口外
                return []
            else:
                for i in range(2):
                    if p[i]<0:
                        u1 = max(u1, q[i] / p[i])
                    else:
                        u2 = min(u2, q[i] / p[i])
        else:                   #不平行于边界
            for i in range(4):
                if p[i] < 0:
                    u1 = max(u1, q[i] / p[i])
                else:
                    u2 = min(u2, q[i] / p[i])
        #u1为截点1关于原直线的比例，u2为截点2关于原直线的比例
        if u1>u2:               #舍弃该线段
            return []
        else:
            x_new1,y_new1=x0 + u1 * (x1 - x0),y0 + u1 * (y1 - y0)
            x_new2,y_new2=x0 + u2 * (x1 - x0),y0 + u2 * (y1 - y0)
            return [[round(x_new1), round(y_new1 )], [round(x_new2), round(y_new2 )]]
