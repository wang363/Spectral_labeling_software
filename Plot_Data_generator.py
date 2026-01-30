from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor  # 导入Cursor工具
import torch
from scipy.special import wofz
import numpy as np
from scipy.signal import savgol_filter
import random
from translations import get_translation, DESCRIPTION_HTML_ZH
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QMessageBox, QFileDialog, QProgressBar, QPushButton, QSpinBox, QCheckBox
from PyQt5.QtCore import QThread, QObject, pyqtSignal


class GenerationWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            # 调用 generate_raman_data 并传递 progress 信号
            generated_data = generate_raman_data(
                num_samples=self.params['num_samples'],
                data_length=self.params['spec_length'],
                min_peak=self.params['min_peak'],
                max_peak=self.params['max_peak'],
                min_peak_distance=self.params['min_peak_distance'],
                min_fwhm=self.params['min_fwhm'],
                max_fwhm=self.params['max_fwhm'],
                save_dir=self.params['save_dir'],
                progress_callback=self.progress
            )
            self.finished.emit(generated_data)
        except Exception as e:
            self.error.emit(get_translation("生成数据时出错: {e}", e=str(e))) 

class Generator_Figure(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.text_container = QWidget()
        self.text_layout = QVBoxLayout(self.text_container)
        self.label_desc = QtWidgets.QLabel()
        self.label_desc.setWordWrap(True)
        self.label_desc.setTextFormat(QtCore.Qt.RichText)
        self.text_layout.addWidget(self.label_desc)
        self.scroll_area.setWidget(self.text_container)
        # ✅  Generator_Figure 
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)

        self.set_gen_language("zh") 
    def set_gen_language(self, lang="zh"):
        if lang == "zh":
            self.label_desc.setText(get_translation(DESCRIPTION_HTML_ZH))
        else:
            self.label_desc.setText(get_translation(DESCRIPTION_HTML_ZH, target="en"))


class GeneratedData_Plot(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(tight_layout=True)
        self.axes = self.fig.add_subplot(111)        
        super(GeneratedData_Plot, self).__init__(self.fig)
        self.main_window = parent
        self.lang = "zh"

        self.cursor = Cursor(self.axes, color='red', linewidth=1, linestyle='--') 
        self.annotation = self.axes.annotate(
            "", xy=(0, 0), xytext=(10, 10),
            textcoords="offset points", bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8),
            arrowprops=dict(arrowstyle="->")
        )
        self.annotation.set_visible(False) 

        self.main_window.pushButton_17.clicked.connect(self.browse_save_directory) 
        self.main_window.pushButton_18.clicked.connect(self.start_data_generation)
        self.main_window.pushButton_19.clicked.connect(self.display_generated_data) 
        self.main_window.checkBox_7.stateChanged.connect(self.display_generated_data)
        self.main_window.checkBox_8.stateChanged.connect(self.display_generated_data)
        self.main_window.checkBox_9.stateChanged.connect(self.display_generated_data)
        self.main_window.spinBox_8.valueChanged.connect(self.display_generated_data)


    def browse_save_directory(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ShowDirsOnly
        directory = QtWidgets.QFileDialog.getExistingDirectory(self.main_window, 
                                                               get_translation("选择保存目录"), 
                                                               options=options)
        if directory:
            self.main_window.lineEdit.setText(directory)
    

    def start_data_generation(self):
            save_path = self.main_window.lineEdit.text()
            if not save_path:
                QMessageBox.warning(self, get_translation('警告'), get_translation("请先选择一个保存路径！"))
                return

            params = {
                'num_samples': self.main_window.spinBox_2.value(),
                'spec_length': self.main_window.spinBox_10.value(),
                'min_peak': self.main_window.spinBox_3.value(),
                'max_peak': self.main_window.spinBox_5.value(),
                'min_peak_distance': self.main_window.spinBox_6.value(),
                'min_fwhm': self.main_window.spinBox_7.value(),
                'max_fwhm': self.main_window.spinBox_9.value(),
                'save_dir': save_path
            }
            
            if params['min_peak'] > params['max_peak']:
                QMessageBox.warning(self, get_translation("参数错误"), get_translation("最小谱峰数量不能大于最大谱峰数量！"))
                return
            if params['min_fwhm'] > params['max_fwhm']:
                QMessageBox.warning(self, get_translation("参数错误"), get_translation("最小半峰宽不能大于最大半峰宽！"))
                return

            self.main_window.pushButton_18.setEnabled(False)
            self.main_window.progressBar.setValue(0)

            self.thread = QThread()
            self.worker = GenerationWorker(params)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.generation_finished)
            self.worker.error.connect(self.generation_error)
            self.worker.progress.connect(self.update_generation_progress)
            
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            self.thread.start()

    def update_generation_progress(self, value):
        self.main_window.progressBar.setValue(value)

    def generation_finished(self, data):
        self.generated_data = data
        self.main_window.pushButton_18.setEnabled(True)
        QMessageBox.information(self, get_translation("完成"), get_translation("数据生成成功！"))
        self.main_window.progressBar.setValue(100)
        self.display_generated_data()


    def generation_error(self, error_msg):
        self.main_window.pushButton_18.setEnabled(True)
        QMessageBox.critical(self, "错误", error_msg)
        self.main_window.progressBar.setValue(0)
    
    def display_generated_data(self):
        if not hasattr(self, 'generated_data'):
            QMessageBox.warning(self, get_translation("警告"), get_translation("请先生成数据！"))
            return
        index = self.main_window.spinBox_8.value()-1
        num_samples = len(self.generated_data[0])
        if not (0 <= index < num_samples):
            QMessageBox.warning(self.main_window, get_translation("警告"), get_translation("数据索引超出范围！"))
            return
        
        self.axes.clear()

        X_ideal, X_add_noise, X_add_baseline, X_final_noise, y_ideal = self.generated_data

        x_axis = np.arange(len(X_ideal[index]))

        self.axes.plot(x_axis, X_ideal[index].numpy(), label=get_translation('理想数据'), alpha=0.8)
        self.axes.plot(x_axis, X_add_noise[index].numpy()+1, label=get_translation('微噪数据'), alpha=0.8)
        self.axes.plot(x_axis, X_add_baseline[index].numpy()+2, label=get_translation('仿真实数据'), alpha=0.8)
        self.axes.plot(x_axis, X_final_noise[index].numpy()+3, label=get_translation('仿生物样本'), alpha=0.8)
        
        self._do_display_data()

        self.axes.legend(loc='upper right', ncol=7, fontsize='small',
                          handlelength=0.5, columnspacing=0.5, handletextpad=0.1)
        
        self.axes.grid(True, alpha=0.3)
        self.draw()

    def _do_display_data(self):
        if not hasattr(self, 'generated_data'):
            return

        index = self.main_window.spinBox_8.value() - 1
        X_ideal, _, _, X_final_noise, y_ideal = self.generated_data
        labels = y_ideal[index].numpy()
        pos_labels, amp_labels, fwhm_labels = labels

        show_pos = self.main_window.checkBox_7.isChecked()
        show_amp = self.main_window.checkBox_8.isChecked()
        show_fwhm = self.main_window.checkBox_9.isChecked()

        peak_indices = np.where(pos_labels > 0)[0]
        if len(peak_indices) == 0:
            return

        max_final_noise = np.max(X_final_noise[index].numpy())

        if show_amp:
            self.axes.plot([], [], 'x', color='red', markersize=7, label=get_translation('峰振幅'))
        if show_pos:
            self.axes.plot([], [], '--', color='green', linewidth=1, label=get_translation('峰位'))
        if show_fwhm:
            self.axes.plot([], [], '-', color='magenta', linewidth=2, label=get_translation('半峰宽'))

        for peak_x in peak_indices:
            peak_y = X_ideal[index].numpy()[peak_x]
            if show_amp:
                self.axes.plot(peak_x, peak_y, 'x', color='red', markersize=7)

            if show_pos:
                self.axes.plot([peak_x, peak_x], [0, max_final_noise + 3.1],
                               color='green', linestyle='--', linewidth=1)

            if show_fwhm:
                fwhm_height = fwhm_labels[peak_x] / 30
                self.axes.plot([peak_x, peak_x], [0, fwhm_height],
                               color='magenta', linestyle='-', linewidth=2, zorder=5)
        
def wofz_torch(x):
    wofzdata = torch.from_numpy(wofz(x.numpy()))
    return wofzdata 

# Voigt函数生成拉曼峰
def Voigt_Data(x, y0, amp, pos, fwhm, shape=1):
    tmp = 1/wofz_torch(torch.zeros((len(x))) + 1j*torch.sqrt(torch.log(torch.tensor(2.0)))*shape).real
    return y0 + tmp * amp * wofz_torch(2*torch.sqrt(torch.log(torch.tensor(2.0)))*(x-pos)/fwhm + 1j*torch.sqrt(torch.log(torch.tensor(2.0)))*shape).real

def add_trace_noise(raman_shift=1500, raman_data=None, scale=500):

    raman_data = raman_data.squeeze().numpy()

    noise = np.random.normal(0, scale, size=raman_shift) 
    y_noise = noise
    y_noise = y_noise + abs(np.min(y_noise)) 
    window_length = raman_shift 
    # flag = random.uniform(0.4, 0.6)
    # if flag>0.5:
    #     polyorder = 5 
    # else:
    #     polyorder = 4
    polyorder = 5
    y_smooth = savgol_filter(y_noise, window_length, polyorder) 
    min_y_smooth = np.min(y_smooth)
    abs_y_smooth = abs(min_y_smooth) + y_smooth

    abs_y_smooth = (abs_y_smooth - np.min(abs_y_smooth) )/( np.max(abs_y_smooth) - np.min(abs_y_smooth) )
    alpha = random.uniform(0.5, 0.85)
    alpha = np.round(alpha, 5) 
    noisy_data = raman_data + (1-alpha)*abs_y_smooth 
    noisy_data = np.round(noisy_data, 5) 

    return torch.tensor(noisy_data)

def random_add_noise(raman_shift=1500, scale=0.5, data_x=None, bias=0.05):
    data_x = data_x.numpy()
    noise = bias * np.random.normal(0, scale, size=raman_shift)

    save_x_data = noise + data_x

    return torch.tensor(save_x_data)

def add_noise(number, data_x, data_length=1500):
    bias = round(random.uniform(0.9, 0.95), 3) 
    noise = torch.randn([number, 1, data_length])
    noise = noise - torch.min(noise, dim=2, keepdim=True)[0]
    noise = noise / torch.max(noise, dim=2, keepdim=True)[0]
    noise = noise * torch.rand([number, 1, 1]) * (1 - bias)
    save_x_data = noise.squeeze(0) + data_x

    return save_x_data

def generate_raman_data(num_samples=1500, data_length=1500, min_peak=3, max_peak=7, min_peak_distance=75,
                       min_fwhm=20, max_fwhm=100, envelope_flag=True, save_dir='zl_save_data/data', progress_callback=None):
    import os
    os.makedirs(f'{save_dir}/data', exist_ok=True)
    os.makedirs(f'{save_dir}/label', exist_ok=True)

    shape_x = [num_samples, data_length]
    shape_y = [num_samples, 3, data_length]

    save_X = torch.zeros(shape_x)
    save_y = torch.zeros(shape_y)
    save_add_noise_X = torch.zeros(shape_x)
    save_add_baseline_X = torch.zeros(shape_x)
    save_final_noise_X = torch.zeros(shape_x)

    for i in range(num_samples):
        init_x = torch.linspace(0, data_length-1, data_length)
        
        peak_size = random.randint(min_peak, max_peak)

        peak_start = int(data_length * 0.05)
        peak_end = int(data_length - data_length * 0.05)

        if peak_start >= peak_end:
            peak_start, peak_end = 0, data_length -1
        peak_position = torch.randint(peak_start, peak_end, (peak_size,))
        peak_position = torch.sort(peak_position)
        diff_peak = torch.diff(peak_position[0])
        
        diff_peak = diff_peak < min_peak_distance
        new_peak = peak_position[0][~torch.cat([diff_peak, torch.tensor([False])], dim=0)]
        peak_position = torch.unique_consecutive(new_peak)
        
        train_y = torch.zeros([3, data_length])
        train_X = torch.zeros([data_length,])
        
        for j in range(peak_position.shape[0]):
            amp = random.random() * 0.95 + 0.05
            pos = peak_position[j]
            set_right = peak_position.shape[0]-1 
            if set_right < 0:
                set_right = 0
            ramdom_peak_size = random.randint(0, set_right)
            
            if j == ramdom_peak_size:
                amp = 1.00
                
            fwhm = random.randint(min_fwhm, max_fwhm)
            tmp_data = Voigt_Data(init_x, 0, amp, pos, fwhm)
            
            train_y[0][pos] = 1
            train_y[1][pos] = amp
            train_y[2][pos] = fwhm
            
            if envelope_flag:
                train_X = torch.maximum(train_X, tmp_data)
            else:
                train_X = train_X + tmp_data
        
        train_X, train_y = train_X.unsqueeze(0), train_y.unsqueeze(0)
        save_X[i], save_y[i] = train_X, train_y
        add_noise_data_x = add_noise(1, train_X, data_length)
        save_add_noise_X[i] = add_noise_data_x
        add_baseline_data_x = add_trace_noise(data_length, add_noise_data_x)
        save_add_baseline_X[i] = add_baseline_data_x
        scale = round(random.uniform(0.8, 1.2), 3)
        random_bias = round(random.uniform(0.05, 0.08), 5)
        final_noise_data_x = random_add_noise(data_length, scale=scale, data_x=add_baseline_data_x, bias=random_bias)
        save_final_noise_X[i] = final_noise_data_x

        if progress_callback:
            progress_callback.emit(int(100 * (i + 1) / num_samples))
    
    torch.save(save_X, f'{save_dir}/data/X_ideal.spt')
    torch.save(save_add_noise_X, f'{save_dir}/data/X_add_noise.spt')
    torch.save(save_add_baseline_X, f'{save_dir}/data/X_add_baseline.spt')
    torch.save(save_final_noise_X, f'{save_dir}/data/X_final_noise.spt')
    torch.save(save_y, f'{save_dir}/label/y_ideal.spt')
    
    return save_X, save_add_noise_X, save_add_baseline_X, save_final_noise_X, save_y

if __name__ == "__main__":
    save_X, save_add_noise_X, save_add_baseline_X, save_final_noise_X, save_y = generate_raman_data(
        num_samples=10,           
        data_length=1500,        
        min_peak=3,              
        max_peak=7,              
        min_peak_distance=75,    
        min_fwhm=20,              
        max_fwhm=100,            
        envelope_flag=True,       
        save_dir='my_raman_data',  
        progress_callback=None     

    )
    