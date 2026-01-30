# -*- coding: utf-8 -*-
import sys
import pandas as pd
import PyQt5.QtCore as QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QFileDialog, QMessageBox, QProgressDialog
from Ui_Manual_label import Ui_MainWindow 
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.special import wofz
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal
import multiprocessing 
from Plot_Raman import Raman_Figure
from Plot_Voigt import Voigt_Figure
from Plot_Data_generator import Generator_Figure, GeneratedData_Plot
from function import airPLS, voigtanalysis, pull_baseline
import translations
from utils import *

plt.rcParams["font.family"] = ["Times New Roman", "SimSun"]
plt.rcParams['mathtext.fontset'] = 'stix' # 公式字体

# import logging
# logging.basicConfig(filename='app_debug.log', level=logging.INFO, 
#                     format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

class FitWorker(QtCore.QObject):
    finished = pyqtSignal(dict, list) 
    error = pyqtSignal(str)

    def __init__(self, raman_shift, intensity):
        super().__init__()
        self.raman_shift = raman_shift
        self.intensity = intensity
    def run(self):            
        try:
            # logging.info("FitWorker thread started.")
            # logging.info("Calling test_model_data...")
            output_numpy, _, output_voigt = test_model_data(self.raman_shift, self.intensity)
            # logging.info("test_model_data finished successfully.")
            
            displacement = output_numpy[0, :]
            threshold = 0.6
            peak_indices = np.where(displacement > threshold)[0].tolist()
            
            result = {
                'output_numpy': output_numpy,
                'output_voigt': output_voigt
            }
            # logging.info(f"Emitting finished signal with {len(peak_indices)} peaks.")
            self.finished.emit(result, peak_indices)
        except Exception as e:
            # logging.error("An error occurred in FitWorker.run", exc_info=True)
            self.error.emit(str(e))

class Raman_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Raman_MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.raw_data = None
        self.baseline = None
        self.baseline_subtracted_data = None
        self.baseline_auto = None
        self.baseline_subtracted_auto_data = None
        self.baseline_points = []
        self.pick_points_mode = False
        self.input_file_name = ""
        self.input_voigt_file_name = ""
        self.voigt_data_from_file = None  
        self.voigt_data_from_baseline = None 
        self.voigt_fit_curves = [] 
        self.generator_figure = Generator_Figure()
        layout_gen = QVBoxLayout(self.widget_3)
        layout_gen.setContentsMargins(0, 0, 0, 0)
        layout_gen.addWidget(self.generator_figure)

        self.raman_figure = Raman_Figure(self)
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.raman_figure)
        self.voigt_figure = Voigt_Figure(self)
        layout_voigt = QVBoxLayout(self.widget_2)
        layout_voigt.setContentsMargins(0, 0, 0, 0)
        layout_voigt.addWidget(self.voigt_figure)
        self.generator_plot_figure = GeneratedData_Plot(self)
        layout_gen_plot = QVBoxLayout(self.widget_4)
        layout_gen_plot.setContentsMargins(0, 0, 0, 0)
        layout_gen_plot.addWidget(self.generator_plot_figure)

        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(['位置(pos)', '振幅(amp)', '半高全宽(fwhm)', '水平基线值(y0)', '形状参数(shape)'])
        self.tableView.setModel(self.table_model)

        self.doubleSpinBox_10.setValue(1.0)
        self.actionOpen_File.triggered.connect(self.open_file_for_spectra)
        self.actionOpen_File_for_Voigt_Plot.triggered.connect(self.open_file_for_voigt)

        self.pushButton.clicked.connect(self.toggle_pick_points_mode)
        self.pushButton_2.clicked.connect(self.remove_last_baseline_point)
        self.pushButton_3.clicked.connect(self.reset_baseline_points)
        self.pushButton_4.clicked.connect(self.apply_baseline_subtraction)
        self.pushButton_5.clicked.connect(self.zoom_in)
        self.pushButton_6.clicked.connect(self.zoom_out)
        self.pushButton_7.clicked.connect(self.reset_view)
        self.pushButton_9.clicked.connect(self.export_raw_data)
        self.pushButton_10.clicked.connect(self.export_baseline_subtracted_data)
        self.pushButton_8.clicked.connect(self.export_normalized_data_1)
        self.pushButton_11.clicked.connect(self.export_normalized_data_2)
        self.pushButton_14.clicked.connect(self.export_baseline_subtracted_auto_data)
        self.pushButton_15.clicked.connect(self.export_baseline_subtracted_norm_auto_data)
        self.checkBox.stateChanged.connect(self.raman_figure.update_plot)
        self.checkBox_2.stateChanged.connect(self.raman_figure.update_plot)
        self.checkBox_3.stateChanged.connect(self.raman_figure.update_plot)
        self.checkBox_5.stateChanged.connect(self.raman_figure.update_plot)
        self.checkBox_6.stateChanged.connect(self.raman_figure.update_plot)
        self.pushButton_34.clicked.connect(self.add_voigt_peak)
        self.pushButton_36.clicked.connect(self.single_peak_fit)
        self.pushButton_35.clicked.connect(self.overall_voigt_fit) 
        self.pushButton_12.clicked.connect(self.export_voigt_fit_data)
        self.pushButton_13.clicked.connect(self.model_based_fit) 
        self.pushButton_37.clicked.connect(self.delete_selected_rows)

        self.checkBox_11.stateChanged.connect(self.voigt_figure.update_plot)
        self.checkBox_14.stateChanged.connect(self.voigt_figure.update_plot)
        self.checkBox_12.stateChanged.connect(self.voigt_figure.update_plot)  
        self.checkBox_13.stateChanged.connect(self.voigt_figure.update_plot)  
        self.checkBox_4.stateChanged.connect(self.voigt_figure.update_plot)

        self.cid_motion = self.raman_figure.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.cid_click = self.raman_figure.mpl_connect('button_press_event', self.on_canvas_click)
        self.cid_motion_voigt = self.voigt_figure.mpl_connect('motion_notify_event', self.on_voigt_mouse_move)
        self.cid_click_voigt = self.voigt_figure.mpl_connect('button_press_event', self.on_voigt_canvas_click)

        self.translator = QtCore.QTranslator()
        self.actionEnglish.triggered.connect(lambda: self.switch_language('en'))
        self.action_6.triggered.connect(lambda: self.switch_language('zh'))
        self.comboBox.clear()
        self.comboBox.addItems(["选择去基线算法", "Airpls", "Wavelet_transform", "Iterative_fitting"])
        self.pushButton_16.clicked.connect(self.apply_selected_baseline_algorithm) 
        self.switch_language('zh')

    def switch_language(self, lang):
        translations.translate_ui(self, lang)

        self.update_baseline_points_text()
        if hasattr(self, "generator_figure"):
            self.generator_figure.set_gen_language(lang)

    def interpolate_raman_data(self, data):
        original_wavenumbers = data.iloc[:, 0].values
        original_intensity = data.iloc[:, 1].values
        min_wavenumber = int(np.floor(original_wavenumbers.min()))
        max_wavenumber = int(np.ceil(original_wavenumbers.max()))
        new_wavenumbers = np.arange(min_wavenumber, max_wavenumber + 1)
        
        new_intensity = np.interp(
            new_wavenumbers, 
            original_wavenumbers, 
            original_intensity
        )
        interpolated_data = pd.DataFrame({
            0: new_wavenumbers,
            1: new_intensity
        })

        return interpolated_data

    def open_file_for_spectra(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "为 Spectra Plot 打开文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            try:
                raw_data = pd.read_csv(file_path, header=None)

                first_element = raw_data.iloc[0, 0]
                if not str(first_element).replace('.', '', 1).isdigit():
                    raw_data = pd.read_csv(file_path)

                if raw_data.shape[1] < 2:
                    raise ValueError(translations.get_translation("文件需要至少包含两列数据"))
                self.raw_data = self.interpolate_raman_data(raw_data)

                self.reset_all_spectra()
                self.reset_view()
                self.input_file_name = os.path.splitext(os.path.basename(file_path))[0]
                self.checkBox.setChecked(True)
                self.raman_figure.update_plot()
            except Exception as e:
                title = translations.get_translation("错误")
                message = translations.get_translation("无法打开或解析文件: {error}", error=str(e))
                QMessageBox.critical(self, title, message)

    def open_file_for_voigt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "为 Voigt Plot 打开文件", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_path:
            try:
                voigt_data = pd.read_csv(file_path, header=None)
                first_element = voigt_data.iloc[0, 0]
                if not str(first_element).replace('.', '', 1).isdigit():
                    voigt_data = pd.read_csv(file_path, header=0)                

                if voigt_data.shape[1] < 2:
                    raise ValueError(translations.get_translation("文件需要至少包含两列数据"))
                voigt_data = self.interpolate_raman_data(voigt_data)

                self.reset_voigt_plot()

                y_data = voigt_data.iloc[:, 1]
                voigt_data.iloc[:, 1] = (y_data - y_data.min()) / (y_data.max() - y_data.min())
                self.voigt_data_from_file = voigt_data

                self.input_voigt_file_name = os.path.splitext(os.path.basename(file_path))[0]
                self.checkBox_11.setChecked(True)
                self.checkBox_14.setChecked(False)
                self.voigt_figure.update_plot()

            except Exception as e:
                title = translations.get_translation("错误")
                message = translations.get_translation("无法打开或解析文件: {error}", error=str(e))
                QMessageBox.critical(self, title, message)

    def reset_all_spectra(self):
        """重置Spectra Plot的计算数据和基线点"""
        self.baseline = None
        self.baseline_subtracted_data = None
        self.baseline_points = []
        self.update_baseline_points_text()
        self.raman_figure.update_plot()

    def reset_voigt_plot(self):
        """清除Voigt Plot的所有数据和拟合结果"""
        self.voigt_data_from_file = None
        self.voigt_data_from_baseline = None
        self.voigt_fit_curves = []
        self.table_model.setRowCount(0) # 清空tableview
        self.voigt_figure.update_plot()

    def toggle_pick_points_mode(self):
        self.pick_points_mode = not self.pick_points_mode
        if self.pick_points_mode:
            self.pushButton.setStyleSheet("background-color: lightgreen;")
            message = translations.get_translation("选点模式已开启。\n请在图上点击以选择基线点。\n鼠标移动时将显示坐标。")
            self.textEdit.setText(message)
        else:
            self.pushButton.setStyleSheet("")
            self.update_baseline_points_text()

    # 根据事件更新画布坐标
    def on_mouse_move(self, event):
        if event.inaxes == self.raman_figure.axes:
            self.raman_figure.update_annotation(event.xdata, event.ydata)
            
            # 显示竖直线和数据点
            if self.raw_data is not None:
                x_data = self.raw_data.iloc[:, 0].values
                y_data = self.raw_data.iloc[:, 1].values
                
                # 找到最接近鼠标x坐标的数据点
                idx = np.argmin(np.abs(x_data - event.xdata))
                closest_x = x_data[idx]
                closest_y = y_data[idx]
                
                self.raman_figure.show_vertical_line_and_data_point(closest_x, closest_y)
        else:
            self.raman_figure.annotation.set_visible(False)
            self.raman_figure.hide_vertical_line_and_data_point()
            self.raman_figure.fig.canvas.draw_idle()

    def on_canvas_click(self, event):
        if self.pick_points_mode and event.inaxes is self.raman_figure.axes and event.button in [1, 3]:
            x, y = event.xdata, event.ydata
            self.baseline_points.append((x, y))
            self.baseline_points.sort(key=lambda p: p[0])
            self.update_baseline_points_text()
            self.raman_figure.update_plot()

    def update_baseline_points_text(self):
        if self.baseline_points:
            points_str = "\n".join([f"({x:.2f}, {y:.2f})" for x, y in self.baseline_points])
            message = translations.get_translation("已选基线点:\n{points}", points=points_str)
            self.textEdit.setText(message)
        else:
            message = translations.get_translation("尚未选择基线点。")
            self.textEdit.setText(message)

    def remove_last_baseline_point(self):
        if self.baseline_points:
            self.baseline_points.pop()
            self.update_baseline_points_text()
            self.raman_figure.update_plot()

    def reset_baseline_points(self):
        self.baseline_points = []
        self.update_baseline_points_text()
        self.raman_figure.update_plot()


    # 手动去基线
    def apply_baseline_subtraction(self):
        if self.raw_data is not None and len(self.baseline_points) >= 2:
            self.baseline_points.sort(key=lambda p: p[0])
            baseline_x, baseline_y = zip(*self.baseline_points)

            self.baseline = np.interp(self.raw_data.iloc[:, 0], baseline_x, baseline_y)
            self.baseline_subtracted_data = self.raw_data.iloc[:, 1] - self.baseline
            self.checkBox_3.setChecked(True)
            self.raman_figure.update_plot()

            # 更新Voigt Plot
            self.reset_voigt_plot()
            y_subtracted = self.baseline_subtracted_data
            y_normalized = (y_subtracted - y_subtracted.min()) / (y_subtracted.max() - y_subtracted.min())
            
            # self.voigt_data_from_baseline 用于传参
            self.voigt_data_from_baseline = pd.DataFrame({
                0: self.raw_data.iloc[:, 0],
                1: y_normalized
            })
            self.checkBox_14.setChecked(True)
            self.checkBox_11.setChecked(False)
            self.voigt_figure.update_plot()
        else:
            title = translations.get_translation("警告")
            message = translations.get_translation("请至少选择两个基线点。")
            QMessageBox.warning(self, title, message)

    # 三种算法自动去基线
    def apply_selected_baseline_algorithm(self):
        if self.raw_data is None:
            title = translations.get_translation("警告")
            message = translations.get_translation("请先加载原始数据！")
            QMessageBox.warning(self, title, message)
            return
        
        algo = self.comboBox.currentText()
        if algo not in ["Iterative_fitting", "Airpls", "Wavelet_transform"]:
            title = translations.get_translation("提示")
            message = translations.get_translation("请选择有效的去基线算法！")
            QMessageBox.warning(self, title, message)
            return

        x = self.raw_data.iloc[:, 0].values
        y = self.raw_data.iloc[:, 1].values

        try:
            if algo == "Iterative_fitting":
                y_corrected = voigtanalysis(y)
                self.baseline_auto = y - y_corrected
            elif algo == "Airpls":
                y_corrected  = airPLS(y)
                self.baseline_auto = y - y_corrected
            elif algo == "Wavelet_transform":
                y_corrected = pull_baseline(x, y, Denosing=None)
                self.baseline_auto = y - y_corrected
            # 存储结果
            self.baseline_subtracted_auto_data = pd.DataFrame({
            0: x,
            1: y_corrected
            })

            # 自动更新图像显示
            self.checkBox_5.setChecked(True)
            self.checkBox_6.setChecked(True)
            self.raman_figure.update_plot()

            QMessageBox.information(self, translations.get_translation("成功"), 
                                    translations.get_translation("{fun} 去基线处理完成。", fun=algo))

        except Exception as e:
            QMessageBox.critical(self, translations.get_translation("错误"), 
                                 translations.get_translation("算法执行失败: {e}", e=e))

    # 放大放小操作
    def zoom_in(self):
        xlim = self.raman_figure.axes.get_xlim()
        ylim = self.raman_figure.axes.get_ylim()
        self.raman_figure.axes.set_xlim(xlim[0] * 1.1, xlim[1] * 0.9)
        self.raman_figure.axes.set_ylim(ylim[0] * 1.1, ylim[1] * 0.9)
        self.raman_figure.draw()

    def zoom_out(self):
        xlim = self.raman_figure.axes.get_xlim()
        ylim = self.raman_figure.axes.get_ylim()
        self.raman_figure.axes.set_xlim(xlim[0] * 0.9, xlim[1] * 1.1)
        self.raman_figure.axes.set_ylim(ylim[0] * 0.9, ylim[1] * 1.1)
        self.raman_figure.draw()

    # 重置视图
    def reset_view(self):
        if self.raw_data is not None:
            x_min = self.raw_data.iloc[:, 0].min()
            x_max = self.raw_data.iloc[:, 0].max()
            self.raman_figure.axes.set_xlim(x_min, x_max)

            visible_ys = []
            if self.checkBox.isChecked():
                visible_ys.extend(self.raw_data.iloc[:, 1].values)
            if self.checkBox_2.isChecked() and self.baseline is not None:
                visible_ys.extend(self.baseline)
            if self.checkBox_3.isChecked() and self.baseline_subtracted_data is not None:
                visible_ys.extend(self.baseline_subtracted_data)

            if visible_ys:
                y_min, y_max = min(visible_ys), max(visible_ys)
            else:
                y_min, y_max = self.raw_data.iloc[:, 1].min(), self.raw_data.iloc[:, 1].max()

            y_range = y_max - y_min if y_max - y_min > 0 else 1.0
            self.raman_figure.axes.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
            self.raman_figure.draw()

    def export_raw_data(self):
        if self.raw_data is not None:
            default_file_path = f"{self.input_file_name}_raw.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出原始数据", default_file_path, "CSV Files (*.csv)")
            if file_path:
                try:
                    self.raw_data.to_csv(file_path, sep=',', header=False, index=False)
                    title = translations.get_translation("成功")
                    message = translations.get_translation("原始数据已成功导出。")
                    QMessageBox.information(self, title, message)
                except Exception as e:
                    title = translations.get_translation("错误")
                    message = translations.get_translation("导出原始数据失败: {error}", error=str(e))
                    QMessageBox.critical(self, title, message)

    def export_baseline_subtracted_data(self):
        if self.baseline_subtracted_data is not None:
            default_file_path = f"{self.input_file_name}_baseline_subtracted.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出校正后数据", default_file_path, "CSV Files (*.csv)")
            if file_path:
                try:
                    data_to_export = pd.DataFrame({
                        'Raman Shift': self.raw_data.iloc[:, 0],
                        'Intensity': self.baseline_subtracted_data,
                        'baseline': self.raw_data.iloc[:, 1] - self.baseline_subtracted_data
                    })
                    data_to_export.to_csv(file_path, sep=',', header=False, index=False)
                    QMessageBox.information(self, translations.get_translation("成功"),
                                             translations.get_translation("基线校正后的数据已成功导出。"))
                except Exception as e:
                    QMessageBox.critical(self, translations.get_translation("错误"),
                                          translations.get_translation("导出校正后数据失败: {error}", error=str(e)))

    def export_baseline_subtracted_auto_data(self):
        if self.baseline_subtracted_auto_data is not None:
            default_file_path = f"{self.input_file_name}_auto_baseline_subtracted.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出自动校正后数据", default_file_path, "CSV Files (*.csv)")
            if file_path:
                try:
                    header = ['Raman Shift', 'Intensity']
                    self.baseline_subtracted_auto_data.to_csv(file_path, sep=',', header=header, index=False)
                    QMessageBox.information(self, translations.get_translation("成功"), translations.get_translation("自动基线校正后的数据已成功导出。"))
                except Exception as e:
                    QMessageBox.critical(self, translations.get_translation("错误"), translations.get_translation("导出自动校正后数据失败: {error}", error=str(e)))

    def export_baseline_subtracted_norm_auto_data(self): # 导出归一化后的自动去基线数据
        if self.baseline_subtracted_auto_data is not None:
            default_file_path = f"{self.input_file_name}_auto_baseline_normalized.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出自动校正后归一化数据", default_file_path, "CSV Files (*.csv)")
            if file_path:
                try:
                    y_data = self.baseline_subtracted_auto_data.iloc[:, 1]
                    y_normalized = (y_data - y_data.min()) / (y_data.max() - y_data.min())
                    data_to_export = pd.DataFrame({
                        'Raman Shift': self.baseline_subtracted_auto_data.iloc[:, 0],
                        'Intensity': y_normalized
                    })
                    data_to_export.to_csv(file_path, sep=',', header=False, index=False)
                    QMessageBox.information(self, translations.get_translation("成功"),
                                             translations.get_translation("自动基线校正后的归一化数据已成功导出。"))
                except Exception as e:
                    QMessageBox.critical(self, translations.get_translation("错误"), translations.get_translation("导出自动校正后归一化数据失败: {error}", error=str(e)))

    # 导出归一化数据
    def export_normalized_data_1(self):
        if self.raw_data is not None:
            default_file_path = f"{self.input_file_name}_normalized_raw.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出归一化后原始数据", default_file_path,
                                                       "CSV Files (*.csv)")
            if file_path:
                try:
                    raw = self.raw_data.iloc[:, 1]
                    intensity = (raw - min(raw)) / (max(raw) - min(raw))
                    data_to_export = pd.DataFrame({
                        'Raman Shift': self.raw_data.iloc[:, 0],
                        'Intensity': intensity
                    })
                    data_to_export.to_csv(file_path, sep=',', header=False, index=False)
                    QMessageBox.information(self, translations.get_translation("成功"),
                                             translations.get_translation("归一化后的原始数据已成功导出。"))
                except Exception as e:
                    QMessageBox.information(self, translations.get_translation("错误"),
                                             translations.get_translation("导出数据失败: {error}", error=str(e)))

    def export_normalized_data_2(self):
        if self.baseline_subtracted_data is not None:
            default_file_path = f"{self.input_file_name}_baseline_normalized.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出校正后归一化数据", default_file_path,
                                                       "CSV Files (*.csv)")
            if file_path:
                try:
                    intensity = (self.baseline_subtracted_data - min(self.baseline_subtracted_data)) / (
                            max(self.baseline_subtracted_data) - min(self.baseline_subtracted_data))
                    data_to_export = pd.DataFrame({
                        'Raman Shift': self.raw_data.iloc[:, 0],
                        'Intensity': intensity
                    })
                    data_to_export.to_csv(file_path, sep=',', header=False, index=False)
                    QMessageBox.information(self, translations.get_translation("成功"),
                                             translations.get_translation("基线校正后的归一化数据已成功导出。"))
                except Exception as e:
                    QMessageBox.information(self, translations.get_translation("错误"), translations.get_translation("导出数据失败: {error}", error=str(e)))

    # 向listview中添加参数
    def add_voigt_peak(self):
        y0 = self.spinBox.value()
        amp = self.doubleSpinBox.value()
        pos = self.spinBox_4.value()
        fwhm = self.doubleSpinBox_3.value()
        shape = self.doubleSpinBox_10.value()

        items = [QStandardItem(str(pos)), QStandardItem(str(amp)), QStandardItem(str(fwhm)),QStandardItem(str(y0)), 
                 QStandardItem(str(shape))]
        self.table_model.appendRow(items)

    # 单峰参数拟合
    def single_peak_fit(self):
        current_voigt_data = None
        if self.voigt_data_from_baseline is not None:
            current_voigt_data = self.voigt_data_from_baseline
        elif self.voigt_data_from_file is not None:
            current_voigt_data = self.voigt_data_from_file

        if current_voigt_data is not None:
            self.voigt_fit_curves = []
            y0 = self.spinBox.value()
            amp = self.doubleSpinBox.value()
            pos = self.spinBox_4.value()
            fwhm = self.doubleSpinBox_3.value()
            shape = self.doubleSpinBox_10.value()
            params = {
                    'y0': y0,
                    'amp': float(amp),
                    'pos': float(pos),
                    'fwhm': float(fwhm),
                    'shape': float(shape)
                }
            self.voigt_fit_curves.append(params)
            
            self.checkBox_12.setChecked(True)  # 自动勾选单峰显示复选框
            self.voigt_figure.update_plot()
        else:
            QMessageBox.warning(self, translations.get_translation('警告'),
                                 translations.get_translation("请先向Voigt Plot中加载数据再进行拟合。"))

    # 多峰参数拟合
    def overall_voigt_fit(self):
        current_voigt_data = None
        if self.voigt_data_from_baseline is not None:
            current_voigt_data = self.voigt_data_from_baseline
        elif self.voigt_data_from_file is not None:
            current_voigt_data = self.voigt_data_from_file

        if current_voigt_data is not None:
            self.voigt_fit_curves = []
            row_count = self.table_model.rowCount()
            
            if row_count == 0:
                QMessageBox.warning(self, translations.get_translation('警告'),
                                    translations.get_translation("请先添加至少一个峰参数再进行整体拟合。"))
                return
                
            for row in range(row_count):
                try:
                    params = {
                        'pos': float(self.table_model.item(row, 0).text()),
                        'amp': float(self.table_model.item(row, 1).text()),
                        'fwhm': float(self.table_model.item(row, 2).text()),
                        'y0': float(self.table_model.item(row, 3).text()),
                        'shape': float(self.table_model.item(row, 4).text())
                    }
                    self.voigt_fit_curves.append(params)
                except Exception as e:
                    num = row + 1
                    QMessageBox.warning(self, translations.get_translation("数据错误"),
                                         translations.get_translation("第{row}行数据格式错误: {e}", row=str(num), e=str(e)))
                    return
            
            self.checkBox_13.setChecked(True)  # 自动勾选整体显示复选框
            self.voigt_figure.update_plot()
        else:
            QMessageBox.warning(self, translations.get_translation("警告"),
                                 translations.get_translation("请先向Voigt Plot中加载数据再进行拟合。"))

    def model_based_fit(self):
        """使用模型进行拟合并显示结果"""
        # 获取当前需要拟合的数据
        current_voigt_data = None
        if self.voigt_data_from_baseline is not None:
            current_voigt_data = self.voigt_data_from_baseline
        elif self.voigt_data_from_file is not None:
            current_voigt_data = self.voigt_data_from_file

        if current_voigt_data is not None:
            try:
                # 准备输入数据
                raman_shift = current_voigt_data.iloc[:, 0].values
                intensity = current_voigt_data.iloc[:, 1].values
                
                # 创建进度对话框（关不掉的模态窗口）
                progress_text = translations.get_translation("正在进行模型拟合...")
                self.progress = QProgressDialog(progress_text, None, 0, 0, self)
                self.progress.setWindowTitle(translations.get_translation("拟合中"))
                # 设置为应用程序级模态，完全阻止其他界面操作
                self.progress.setWindowModality(QtCore.Qt.ApplicationModal)

                # 创建并启动线程
                # 创建线程和 Worker
                self.thread = QThread()
                self.worker = FitWorker(raman_shift, intensity)
                self.worker.moveToThread(self.thread)
                # 3. 连接信号和槽
                self.thread.started.connect(self.worker.run)
                self.worker.finished.connect(self.on_fit_finished)
                self.worker.error.connect(self.on_fit_error)
                
                # 清理操作
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)

                # 如果用户点击了取消按钮，终止线程
                self.progress.canceled.connect(self.thread.quit)
                self.progress.canceled.connect(self.worker.deleteLater)
                self.progress.canceled.connect(self.thread.deleteLater)     

                
                # 移除标题栏的关闭按钮和问号按钮
                self.progress.setWindowFlags(
                    QtCore.Qt.Window | 
                    QtCore.Qt.CustomizeWindowHint | 
                    QtCore.Qt.WindowTitleHint
                )                
                # 隐藏取消按钮
                self.progress.setCancelButton(None)
                # 设置提示文字样式
                self.progress.setLabelText(f"<p style='font-size:12pt; color:#333;'>{progress_text}</p>")
            
                self.thread.start()
                self.progress.show()# 显示进度框

            except Exception as e:
                QMessageBox.critical(self, translations.get_translation("准备数据错误"), 
                                     translations.get_translation("数据准备过程中发生错误: {str_e}", str_e=str(e)))
        else:
            QMessageBox.warning(self, translations.get_translation("警告"), 
                                translations.get_translation("请先向Voigt Plot中加载数据再进行模型拟合。"))

    def on_fit_finished(self, result, peak_indices):
        """模型拟合完成后的处理"""
        if hasattr(self, 'progress') and self.progress.isVisible():
            self.progress.close()
        
        # 解析结果
        output_numpy = result['output_numpy']
        output_voigt = result['output_voigt']
        raman_shift = self.voigt_data_from_baseline.iloc[:, 0].values if self.voigt_data_from_baseline is not None else self.voigt_data_from_file.iloc[:, 0].values
        
        # 存储模型拟合结果
        self.model_fit_result = {
            'raman_shift': raman_shift,
            'voigt_curve': output_voigt.squeeze().detach().numpy()
        }

        # 解析峰参数并更新表格
        # displacement = output_numpy[0, :]
        amplitude = output_numpy[1, :]
        fwhm = output_numpy[2, :]

        # 清空表格
        self.table_model.setRowCount(0)

        # 添加峰参数到表格
        choose_peak = 0
        for idx in peak_indices:
            pos = raman_shift[idx]
            amp = amplitude[idx]
            if amp <= 0.05:
                continue # 忽略振幅小于0.05的峰
            fwhm_val = fwhm[idx] * 50  # 对应make_voigt里的缩放

            items = [
                QStandardItem(f"{pos:.2f}"),
                QStandardItem(f"{amp:.6f}"),
                QStandardItem(f"{fwhm_val:.6f}"),
                QStandardItem("0"),
                QStandardItem("1")
            ]
            self.table_model.appendRow(items)
            choose_peak += 1

        # 更新显示
        self.checkBox_4.setChecked(True)
        self.voigt_figure.update_plot()
        QMessageBox.information(self, translations.get_translation("成功"), 
                                translations.get_translation("模型拟合完成，共检测到{peak_count}个峰", peak_count=choose_peak))

    def on_fit_error(self, error_msg):
        """模型拟合出错时的处理"""
        if hasattr(self, 'progress') and self.progress.isVisible():
            self.progress.close()
        QMessageBox.critical(self, translations.get_translation("模型拟合错误"),
                              translations.get_translation("模型拟合过程中发生错误: {error_msg}", error_msg=error_msg))
        
    def delete_selected_rows(self):
        selected_indexes = self.tableView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.information(self, translations.get_translation("提示"),
                                     translations.get_translation("请先选中要删除的行"))
            return
            
        rows = sorted(list(set(index.row() for index in selected_indexes)), reverse=True)
        for row in rows:
            self.table_model.removeRow(row)
    
    # 导出Voift拟合后数据
    def export_voigt_fit_data(self):
        current_voigt_data = None
        if self.voigt_data_from_baseline is not None:
            current_voigt_data = self.voigt_data_from_baseline
        elif self.voigt_data_from_file is not None:
            current_voigt_data = self.voigt_data_from_file

        # 如果listview中没有数据，则不导出
        row_count = self.table_model.rowCount()  
        if row_count >= 1:          
            if self.input_voigt_file_name != '':
                default_file_path = f"{self.input_voigt_file_name}_voigt_fit.csv"
            else:
                default_file_path = f"{self.input_file_name}_voigt_fit.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "导出Voigt拟合数据", default_file_path,
                                                       "CSV Files (*.csv)")
            if file_path:
                try:
                    raman_shift = current_voigt_data.iloc[:, 0]
                    raw_intensity = current_voigt_data.iloc[:, 1]

                    pos_col = np.zeros_like(raman_shift)
                    amp_col = np.zeros_like(raman_shift, dtype=np.float32)
                    fwhm_col = np.zeros_like(raman_shift, dtype=np.float32)

                    
                    for row in range(row_count):
                        pos = float(self.table_model.item(row, 0).text())
                        amp = float(self.table_model.item(row, 1).text())
                        fwhm = float(self.table_model.item(row, 2).text())

                        # 由于插值误差，选择最近邻的点作为峰值点导出
                        index = np.argmin(np.abs(raman_shift - pos))
                        pos_col[index] = 1
                        amp_col[index] = amp
                        fwhm_col[index] = fwhm

                    data_to_export = pd.DataFrame({
                        'Raman Shift': raman_shift,
                        'Norm Intensity': raw_intensity,
                        # 保存Voigt整体拟合结果，即total_fit.numpy()的数据，不是模型拟合，是根据listview参数拟合的结果
                        'Voigt Intensity': self.voigt_figure.current_voigt_fit_curve if self.voigt_figure.current_voigt_fit_curve is not None else np.zeros_like(raman_shift),
                        'Pos': pos_col,
                        'Amp': amp_col,
                        'Fwhm': fwhm_col
                    })
                    data_to_export.to_csv(file_path, sep=',', index=False)
                    QMessageBox.information(self, translations.get_translation("成功"),
                                             translations.get_translation("Voigt拟合数据已成功导出。"))
                except Exception as e:
                    QMessageBox.critical(self, translations.get_translation("错误"), 
                                         translations.get_translation("导出Voigt拟合数据失败: {e}", e=str(e)))

    def on_voigt_mouse_move(self, event):
        if event.inaxes == self.voigt_figure.axes:
            self.voigt_figure.update_annotation(event.xdata, event.ydata)
            
            # 显示竖直线和数据点
            current_voigt_data = None
            if self.voigt_data_from_baseline is not None:
                current_voigt_data = self.voigt_data_from_baseline
                x_data = current_voigt_data.iloc[:, 0].values
                y_data = current_voigt_data.iloc[:, 1].values  
                # 找到最接近鼠标x坐标的数据点
                idx = np.argmin(np.abs(x_data - event.xdata))
                closest_x = x_data[idx]
                closest_y = y_data[idx]
                self.voigt_figure.show_vertical_line_and_data_point(closest_x, closest_y)

            elif self.voigt_data_from_file is not None:
                current_voigt_data = self.voigt_data_from_file
                x_data = current_voigt_data.iloc[:, 0].values
                y_data = current_voigt_data.iloc[:, 1].values                  
                
                # 找到最接近鼠标x坐标的数据点
                idx = np.argmin(np.abs(x_data - event.xdata))
                closest_x = x_data[idx]
                closest_y = y_data[idx]
                self.voigt_figure.show_vertical_line_and_data_point(closest_x, closest_y)
        else:
            self.voigt_figure.annotation.set_visible(False)
            self.voigt_figure.hide_vertical_line_and_data_point()
            self.voigt_figure.fig.canvas.draw_idle()

    # voigt响应事件，暂时空置
    def on_voigt_canvas_click(self, event):
        pass

# --- 主程序入口 ---
def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWin = Raman_MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()