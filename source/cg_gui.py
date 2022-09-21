#!/usr/bin/env python
# -*- coding:utf-8 -*-

import math
import numpy as np

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QMessageBox,
    QInputDialog,
    QColorDialog,
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem
    )
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF, Qt


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_color = QColor(0,0,0)

    def reset(self, height,width):
        self.list_widget.clearSelection()
        self.list_widget.clear()
        self.item_dict = {}
        self.selected_id = ''
        self.scene().clear()

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.setFixedSize(height, width)

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None
    
    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None
    
    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_translate(self):
        self.status = 'translate'
        self.temp_item = None

    def start_draw_rotate(self):
        self.status = 'rotate'
        self.temp_item = None

    def start_draw_scale(self):
        self.status = 'scale'
        self.temp_item = None
    
    def start_draw_clip(self,algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_item = None

    def start_delete(self):
        self.status = 'delete'
        self.temp_item = None
        self.delete_item(self.selected_id)

    def delete_item(self,target_id):
        if target_id not in self.item_dict.keys():
            self.main_window.statusBar().showMessage('对象不存在')
        else:
            #清除状态
            self.removeState()            
            #删除scene中的记录
            self.scene().removeItem(self.item_dict[target_id])   
            #删除画布item字典中的记录
            del self.item_dict[target_id]
            #删除画布list_widget中的记录
            target_list=self.list_widget.findItems(target_id, Qt.MatchFlag.MatchExactly)
            target = target_list[0]
            row=self.list_widget.row(target)
            self.list_widget.takeItem(row)
            del target
            #删除mainwindows中的相关记录
            self.main_window.list_widget.clearSelection()

    def removeState(self):#清空当前的所有状态
        self.list_widget.clearSelection()
        self.clear_selection()
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None


    def finish_draw(self):
        self.main_window.inc_id()
        self.temp_id = self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        if selected !='' and self.item_dict:
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.status = ''
            self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,self.temp_color)
            self.scene().addItem(self.temp_item)
        elif self.status in ['polygon', 'curve']:
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,self.temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x, y])
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], '',self.temp_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'translate':
            if self.selected_id != '':
                self.old_pos = pos
                self.old_p_list = self.item_dict[self.selected_id].p_list
        elif self.status == 'rotate':
            if self.selected_id != '':
                self.centerPoint = self.item_dict[self.selected_id].getCenterPoint()
                self.old_pos = pos
                self.old_p_list = self.item_dict[self.selected_id].p_list
        elif self.status == 'scale':
            if self.selected_id != '':
                self.centerPoint = self.item_dict[self.selected_id].getCenterPoint()
                self.old_pos = pos
                self.old_p_list = self.item_dict[self.selected_id].p_list
        elif self.status == 'clip':
            if self.selected_id != '':
                self.old_pos = pos
                self.old_p_list = self.item_dict[self.selected_id].p_list
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        self.now_pos = pos
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status in ['polygon','curve']:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'translate':
            if self.selected_id != '':
                self.item_dict[self.selected_id].p_list = alg.translate(self.old_p_list, x - int(self.old_pos.x()), dy = y - int(self.old_pos.y()))
        elif self.status == 'rotate':
            if self.selected_id != '':
                x0,y0=self.centerPoint[0],self.centerPoint[1]       #中心点
                x1,y1=self.old_pos.x(),self.old_pos.y()             #鼠标点击的点
                x2,y2=x,y                                           #鼠标移动至的点，求这三点的夹角
                b_len = pow(pow(x1-x0,2)+pow(y1-y0,2),0.5)
                c_len = pow(pow(x2-x0,2)+pow(y2-y0,2),0.5)
                sin_b_x = (y1-y0)/b_len                             #点击点与x轴
                sin_c_x = (y2-y0)/c_len                             #移动点与x轴
                cos_b_x = (x1-x0)/b_len                             #点击点与x轴
                cos_c_x = (x2-x0)/c_len                             #移动点与x轴
                sin_c_b =sin_c_x*cos_b_x-cos_c_x*sin_b_x            #点击点与移动点的夹角
                cos_c_b =cos_c_x*cos_b_x+sin_c_x*sin_b_x            #点击点与移动点的夹角
                d = math.asin(sin_c_b) if cos_c_b > 0 else math.pi-math.asin(sin_c_b)   #分为第一+第四象限、第二+第三象限两种情况
                r = math.degrees(d)
                self.item_dict[self.selected_id].p_list = alg.rotate(self.old_p_list,x0,y0, r)
        elif self.status == 'scale':
            if self.selected_id != '':
                x0,y0=self.centerPoint[0],self.centerPoint[1]       #中心点
                x1,y1=self.old_pos.x(),self.old_pos.y()             #鼠标点击的点
                x2,y2=x,y                                           #鼠标移动至的点，求其距离执之比
                old_len = pow(pow(x1-x0,2)+pow(y1-y0,2),0.5)
                new_len = pow(pow(x2-x0,2)+pow(y2-y0,2),0.5)
                s = new_len/old_len
                self.item_dict[self.selected_id].p_list = alg.scale(self.old_p_list,x0,y0, s)
        elif self.status == 'clip':
            if self.selected_id != '':
                x1,y1=self.old_pos.x(),self.old_pos.y()             #鼠标点击的点
                x2,y2=x,y                                           #鼠标移动至的点,画出一个之间连线的临时的框
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status in ['polygon','curve']:
            self.item_dict[self.temp_id] = self.temp_item
            if not self.list_widget.findItems(self.temp_id, Qt.MatchFlag.MatchExactly):
               self.list_widget.addItem(self.temp_id)
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'clip':
            if self.selected_id != '':
                x_min,x_max = round(min(self.old_pos.x(),self.now_pos.x())),round(max(self.old_pos.x(),self.now_pos.x()))
                y_min,y_max = round(min(self.old_pos.y(),self.now_pos.y())),round(max(self.old_pos.y(),self.now_pos.y()))
                self.item_dict[self.selected_id].p_list = alg.clip(self.old_p_list,x_min,y_min,x_max,y_max, self.temp_algorithm)
                if self.item_dict[self.selected_id].p_list == []:
                    self.delete_item(self.selected_id)
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)



class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color = QColor(0,0,0),parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.p_list == []:
            return QRectF(0,0,0,0)
        if self.item_type in ['line','ellipse']:
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type in ['polygon','curve']:
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for p in self.p_list:
                    x_min = min(p[0],x_min)
                    y_min = min(p[1],y_min)
                    x_max = max(p[0],x_max)
                    y_max = max(p[1],y_max)
            w = x_max - x_min
            h = y_max - y_min
            return QRectF(x_min - 1, y_min - 1, w + 2, h + 2)

    def getCenterPoint(self):
        if self.item_type in ['line','ellipse']:
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return int((x+w/2)),int((y+h/2))
        elif self.item_type in ['polygon','curve']:
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for p in self.p_list:
                    x_min = min(p[0],x_min)
                    y_min = min(p[1],y_min)
                    x_max = max(p[0],x_max)
                    y_max = max(p[1],y_max)
            w = x_max - x_min
            h = y_max - y_min
            return int((x_min+w/2)),int((y_min+h/2))


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        delete_act = edit_menu.addAction('删除')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        exit_act.triggered.connect(qApp.quit)#退出程序
        line_naive_act.triggered.connect(self.line_naive_action)#naive直线
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)#选定目标
        line_dda_act.triggered.connect(self.line_dda_action)#dda直线
        line_bresenham_act.triggered.connect(self.line_bresenham_action)#bresenham直线
        polygon_dda_act.triggered.connect(self.polygon_dda_action)#dda 多边形
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        delete_act.triggered.connect(self.delete_action)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        return str(self.item_cnt)

    def inc_id(self):
        self.item_cnt += 1

    def sub_id(self):
        self.item_cnt -= 1

    def set_pen_action(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas_widget.temp_color = color

    def reset_canvas_action(self):
        height , r1 = QInputDialog.getInt(self, '重置画布', '高(100 <= height <= 1000)', 600, 100, 1000)
        width, r2 = QInputDialog.getInt(self, '重置画布', '宽(100 <= width <= 1000)', 600, 100, 1000)
        if r1 and r2:
            self.list_widget.clearSelection()
            self.list_widget.clear()
            self.item_cnt = 0
            self.scene.setSceneRect(0, 0, height, width)
            self.canvas_widget.reset(height, width)
        else:
            QMessageBox(QMessageBox.Information, '提示', '修改失败').exec_()


    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.inc_id()
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.inc_id()
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.inc_id()
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.inc_id()
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('中点圆算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_draw_translate()
        self.statusBar().showMessage('平移变换')

    def rotate_action(self):
        self.canvas_widget.start_draw_rotate()
        self.statusBar().showMessage('旋转变换')

    def scale_action(self):
        self.canvas_widget.start_draw_scale()
        self.statusBar().showMessage('缩放变换')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_draw_clip('Cohen-Sutherland')
        self.statusBar().showMessage('编码裁剪算法')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_draw_clip('Liang-Barsky')
        self.statusBar().showMessage('梁友栋-Barsky裁剪算法')

    def delete_action(self):
        self.canvas_widget.start_delete()
        self.statusBar().showMessage('删除图元')




if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
