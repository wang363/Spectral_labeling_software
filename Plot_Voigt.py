from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import torch
from scipy.special import wofz
import translations
LOG2 = torch.log(torch.tensor(2.0))
SQRT_LOG2 = torch.sqrt(LOG2)

def Voigt(x, y0, amp, pos, fwhm, shape=1):
    tmp = 1 / wofz(torch.zeros((len(x),)) + 1j * SQRT_LOG2 * shape).real
    return y0 + tmp * amp * wofz(2 * SQRT_LOG2 * (x - pos) / fwhm + 1j * SQRT_LOG2 * shape).real


class Voigt_Figure(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super(Voigt_Figure, self).__init__(self.fig)
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
            fontsize=10, color="blue"
        )
        self.point_annotation.set_visible(False)
        
        self.vertical_line = self.axes.axvline(x=0, color='blue', linestyle=':', alpha=0.7)
        self.data_point_marker, = self.axes.plot([], [], 'bo', markersize=4)
        self.vertical_line.set_visible(False)
        self.data_point_marker.set_visible(False)

    def update_plot(self):
        self.axes.clear()
        self.current_voigt_fit_curve = None
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
            fontsize=12, color="blue"
        )
        self.point_annotation.set_visible(False)
        self.vertical_line = self.axes.axvline(x=0, color='blue', linestyle=':', alpha=0.7)
        self.data_point_marker, = self.axes.plot([], [], 'bo', markersize=5)
        self.vertical_line.set_visible(False)
        self.data_point_marker.set_visible(False)

        x_data_for_fit = None
        if self.main_window.voigt_data_from_file is not None and self.main_window.checkBox_11.isChecked():
            self.axes.plot(self.main_window.voigt_data_from_file.iloc[:, 0], self.main_window.voigt_data_from_file.iloc[:, 1],
                           label=translations.get_translation('导入数据'))
            x_data_for_fit = self.main_window.voigt_data_from_file.iloc[:, 0]
        if self.main_window.voigt_data_from_baseline is not None and self.main_window.checkBox_14.isChecked():
            self.axes.plot(self.main_window.voigt_data_from_baseline.iloc[:, 0], self.main_window.voigt_data_from_baseline.iloc[:, 1],
                           'm', label=translations.get_translation('去基线数据'))
            x_data_for_fit = self.main_window.voigt_data_from_baseline.iloc[:, 0]
        if self.main_window.voigt_fit_curves and x_data_for_fit is not None:
            x = torch.tensor(x_data_for_fit.values)
            total_fit = torch.zeros_like(x, dtype=torch.float64)
            curves = []
            for params in self.main_window.voigt_fit_curves:
                curve = Voigt(x, **params)
                curves.append(curve)
                total_fit += curve
            
            self.current_voigt_fit_curve = total_fit.numpy() 
            if len(self.main_window.voigt_fit_curves) == 1:
                if self.main_window.checkBox_12.isChecked():
                    self.axes.plot(x_data_for_fit, total_fit.numpy(), 'r--', label=translations.get_translation('单峰拟合曲线'))
            else:
                if self.main_window.checkBox_13.isChecked():
                    for i, curve in enumerate(curves):
                        self.axes.plot(x_data_for_fit, curve.numpy(),
                                      f'C{i}--', linewidth=0.75, 
                                      )
                    self.axes.plot(x_data_for_fit, total_fit.numpy(), 'g-', label=translations.get_translation('整体拟合曲线总和'))
        if hasattr(self.main_window, 'model_fit_result') and self.main_window.checkBox_4.isChecked():
            model_result = self.main_window.model_fit_result
            self.axes.plot(model_result['raman_shift'], model_result['voigt_curve'], 
                        'k-', linewidth=2, label=translations.get_translation('模型拟合数据'))

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
        self.point_annotation.xy = (x+50, y+0.05) 
        self.point_annotation.set_text(text)
        self.point_annotation.set_visible(True)
        
        self.fig.canvas.draw_idle()
    
    def hide_vertical_line_and_data_point(self):
        self.vertical_line.set_visible(False)
        self.data_point_marker.set_visible(False)
        self.point_annotation.set_visible(False) 
        self.fig.canvas.draw_idle()
