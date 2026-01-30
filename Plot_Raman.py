from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor 
import translations
class Raman_Figure(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super(Raman_Figure, self).__init__(self.fig)
        self.main_window = parent

        self.cursor = Cursor(self.axes, color='red', linewidth=1, linestyle='--') 
        self.annotation = self.axes.annotate(
            "", xy=(0, 0), xytext=(10, 10),
            textcoords="offset points", bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8),
            arrowprops=dict(arrowstyle="->")
        )
        self.annotation.set_visible(False) 
        
        self.point_annotation = self.axes.annotate(
            "", xy=(0, 0), xytext=(5, 5), 
            textcoords="offset points", bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="blue", alpha=0.9),
            fontsize=8, color="blue"
        )
        self.point_annotation.set_visible(False) 
        
        self.vertical_line = self.axes.axvline(x=0, color='blue', linestyle=':', alpha=0.7)
        self.data_point_marker, = self.axes.plot([], [], 'bo', markersize=5)
        self.vertical_line.set_visible(False)
        self.data_point_marker.set_visible(False)

    def update_plot(self):
        self.axes.clear()
        self.cursor = Cursor(self.axes, color='red', linewidth=1, linestyle='--')
        self.annotation = self.axes.annotate(
            "", xy=(0, 0), xytext=(-55, -35),
            textcoords="offset points", bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8),
            arrowprops=dict(arrowstyle="->")
        )
        self.annotation.set_visible(False)
        self.point_annotation = self.axes.annotate(
            "", xy=(0, 0), xytext=(5, 5),
            textcoords="offset points", bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="blue", alpha=0.9),
            fontsize=10, color="blue"
        )
        self.point_annotation.set_visible(False)
        
        self.vertical_line = self.axes.axvline(x=0, color='blue', linestyle=':', alpha=0.7)
        self.data_point_marker, = self.axes.plot([], [], 'bo', markersize=5)
        self.vertical_line.set_visible(False)
        self.data_point_marker.set_visible(False)

        if self.main_window.raw_data is not None and self.main_window.checkBox.isChecked():
            
            self.axes.plot(self.main_window.raw_data.iloc[:, 0], self.main_window.raw_data.iloc[:, 1], label = translations.get_translation('原始数据'))

        if self.main_window.baseline is not None and self.main_window.checkBox_2.isChecked():
            label = translations.get_translation('基线')
            self.axes.plot(self.main_window.raw_data.iloc[:, 0], self.main_window.baseline, 'g--', label=label)

        if self.main_window.baseline_subtracted_data is not None and self.main_window.checkBox_3.isChecked():
            label = translations.get_translation('手动去基线数据')
            self.axes.plot(self.main_window.raw_data.iloc[:, 0], self.main_window.baseline_subtracted_data, 'm', label=label)

        if self.main_window.baseline_subtracted_auto_data is not None and self.main_window.checkBox_5.isChecked():
            self.axes.plot(self.main_window.raw_data.iloc[:, 0], self.main_window.baseline_subtracted_auto_data[1], 'navy', label=self.main_window.comboBox.currentText())
        if self.main_window.baseline_auto is not None and self.main_window.checkBox_6.isChecked():
            algo_name = self.main_window.comboBox.currentText()
            label = translations.get_translation('{algo}去除基线', algo=algo_name)
            self.axes.plot(self.main_window.raw_data.iloc[:, 0], self.main_window.baseline_auto, 'royalblue', label=label)


        if self.main_window.baseline_points:
            points_x, points_y = zip(*self.main_window.baseline_points)
            label = translations.get_translation('基线点')
            self.axes.plot(points_x, points_y, 'ro', label=label, markersize=3)

        self.axes.set_xlabel('Raman Shift (${cm}$$^{-1}$)')
        self.axes.set_ylabel('Raman Intensity (a.u.)')
        self.axes.grid(True)

        if self.axes.get_legend_handles_labels()[0]:
            self.axes.legend()
        self.draw()

    def update_annotation(self, x, y):
        text = f'x: {x:.2f}\ny: {y:.2f}'
        self.annotation.xy = (x, y)
        self.annotation.set_text(text)
        self.annotation.set_visible(True)
        self.fig.canvas.draw_idle()  
    
    def show_vertical_line_and_data_point(self, x, y):
        self.vertical_line.set_xdata([x])
        self.vertical_line.set_visible(True)
        self.data_point_marker.set_data([x], [y])
        self.data_point_marker.set_visible(True)
        
        text = f'({x:.2f}, {y:.2f})'
        self.point_annotation.xy = (x+50, y+60)
        self.point_annotation.set_text(text)
        self.point_annotation.set_visible(True)
        
        self.fig.canvas.draw_idle()
    
    def hide_vertical_line_and_data_point(self):
        self.vertical_line.set_visible(False)
        self.data_point_marker.set_visible(False)
        self.point_annotation.set_visible(False)  
        self.fig.canvas.draw_idle()
