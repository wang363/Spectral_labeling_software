# encoding: utf-8
from models import *
import numpy as np
import torch
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import wofz
import math
import sys
import os

def wofz_torch(x, device):
    wofzdata = torch.from_numpy(wofz(x.cpu().detach().numpy()))
    return wofzdata.to(device)

def total_voigt(x, y0, amps, poss, fwhms, shape=1, device='cpu'):

    # x = x.to(device)
    # amps = amps.to(device)
    # poss = poss.to(device)
    # fwhms = fwhms.to(device)

    normalization = 1 / wofz_torch(
        torch.zeros_like(x, dtype=torch.float32) + 1j * torch.sqrt(torch.log(torch.tensor(2.0, device=device, dtype=torch.float32))) * shape,
        device=device
    ).real
    
    signal = torch.zeros_like(x, device=device, dtype=torch.float32)
    
    sqrt_log_2 = torch.sqrt(torch.log(torch.tensor(2.0, device=device, dtype=torch.float32)))
    
    for amp, pos, fwhm in zip(amps, poss, fwhms):
        z = 2 * sqrt_log_2 * (x - pos) / fwhm + 1j * sqrt_log_2 * shape
        voigt_profile = wofz_torch(z, device=device).real
        signal += amp * voigt_profile
    signal = y0 + signal * normalization
    
    return signal

def make_voigt(data, device = 'cpu'):
    length = data.size(-1)
    x_values = torch.linspace(0, length - 1, length, device = device)  # 生成 x 值
    voigt_data = []

    for i in range(data.size(0)):  # 遍历批次中的每一条数据
        pos=data[i][0].squeeze(),  # 峰位
        amp=data[i][1].squeeze(),  # 振幅
        fwhm=data[i][2].squeeze(),  # 半峰宽      

        positions = torch.where(pos[0] >= 0.05)
        pos = positions[0]
        amps = amp[0][positions]
        fwhms = fwhm[0][positions]  # 
        # demo = out_amp[i].squeeze()
        tmp_voigt = total_voigt(
            x_values,  
            y0=0,  
            poss=pos,  
            amps=amps,  
            fwhms=fwhms* 50, 
            device=device
        )
        tmp_voigt = torch.where(tmp_voigt<=0.00002, torch.tensor(0), tmp_voigt)
        voigt_data.append(tmp_voigt)

    voigt_data = torch.stack(voigt_data, dim=0)

    return voigt_data

def update_output_labels(output_labels, num_slices=29, stride=50, Raman_shift=None, length=1500, flag = 0):

    input_length = 100
    bs, _, total_length = output_labels.shape

    device = output_labels.device
    updated_labels = torch.zeros(bs, 3, length, device=device)
    mask = torch.zeros(bs, 3, length, num_slices, device=device)

    for i in range(num_slices):

        if flag == 1 and i == num_slices -1 :
            current_slice = output_labels[:, :, -100 :]
            mask[:, :, -100 :, -1] = current_slice[:, :, :end-start]
            break 

        start = i * stride
        end = start + input_length
        if start >= length:
            break
        end = min(end, length)
        current_slice = output_labels[:, :, i*input_length : i*input_length + input_length]
        mask[:, :, start:end, i] = current_slice[:, :, :end-start]

    updated_labels, _ = torch.max(mask, dim=3)
    return updated_labels

def all_sparse_filter(output_labels, window_size=5, threshold=0.1):

    displacement = output_labels[:, 0, :].squeeze().clone()  # (bs, 1500)
    displacement_amp = output_labels[:, 1, :].squeeze().clone()  # (bs, 1500)
    displacement_fwhm = output_labels[:, 2, :].squeeze().clone()  # (bs, 1500)

    mask_displacement = torch.rand_like(displacement)
    displacement = torch.where(displacement >= threshold, displacement, mask_displacement * 1e-5)

    nonzero_mask = displacement >= threshold
    indices = torch.nonzero(nonzero_mask, as_tuple=True)[0]
    if len(indices) == 0:
        return displacement

    values = displacement[indices]
    sorted_values, sorted_order = torch.sort(values, descending=True)
    sorted_indices = indices[sorted_order]

    keep_mask = torch.zeros_like(displacement, dtype=torch.bool)
    suppressed = torch.zeros_like(displacement, dtype=torch.bool)
    for idx in sorted_indices:
        idx = idx.item()
        if not suppressed[idx]:
            keep_mask[idx] = True
            start = max(0, idx - window_size)
            end = min(len(displacement), idx + window_size + 1)
            suppressed[start:end] = True
    
    displacement_updated = torch.where(keep_mask, displacement, mask_displacement * 1e-5)
    mask_displacement = torch.rand_like(displacement)
    displacement_updated_amp = torch.where(keep_mask,  displacement_amp, mask_displacement * 1e-5)
    # mask_displacement = torch.rand_like(displacement)
    # displacement_updated_fwhm = torch.where(keep_mask, displacement_fwhm, mask_displacement * 1e-5)

    output_labels[:, 0, :] = displacement_updated
    output_labels[:, 1, :] = displacement_updated_amp
    # output_labels[:, 2, :] = displacement_updated_fwhm

    return output_labels

def process_test_model(model, input_data, flag=True, threshold=0.2, stride=20, Raman_shift=None):
    """
    使用模型对输入数据按 100 切片处理，并整合输出。
    Args:
        model: 处理的模型，接受形状 (bs, 1, 100)，输出 (bs, 3, 100)
        input_data: 输入数据，形状为 (bs, 1, length)，length > 100
    Returns:
        output_labels: 标签整合后的结果，形状为 (bs, 3, length)
        output_peaks: 峰值输出
        output_voigt: Voigt 重构光谱
    """
    input_data = input_data.view(1, 1, -1)
    bs, _, length = input_data.shape
    assert length > 100, "输入长度必须大于100"

    input_length = 100

    diff = length - input_length
    raw = diff / stride

    if diff % stride == 0:
        num_slices = int(raw) + 1
        set_flag = 0
    else:
        num_slices = math.ceil(raw) 
        set_flag = 1

    output_labels = []
    output_peaks = []

    for i in range(num_slices):
        if set_flag == 1 and i == num_slices - 1:
            input_slice = input_data[:, :, -100:]
            output_slice, peaks = model(input_slice, flag, threshold, 'cpu')
            output_labels.append(output_slice)
            output_peaks.append(peaks)    
            break              
        start = i * stride
        end = start + input_length
        input_slice = input_data[:, :, start:end]
        output_slice, peaks = model(input_slice, flag, threshold, 'cpu')
        output_labels.append(output_slice)
        output_peaks.append(peaks)

    output_labels = torch.cat(output_labels, dim=-1)
    output_labels = update_output_labels(output_labels, num_slices=num_slices, stride=stride,
                                         Raman_shift=Raman_shift, length=length, flag = set_flag)
    output_labels = all_sparse_filter(output_labels)
    output_voigt = make_voigt(output_labels)

    return output_labels, torch.cat(output_peaks, dim=-1), output_voigt

def nor_max(arrlist, thread):
    max_val = np.max(arrlist)
    arr_norm = arrlist / (max_val + 1e-4)
    arr_norm[arr_norm<thread] = 0
    return arr_norm

# 读取csv数据
def read_model_data(start, end, path):
    # data = pd.read_csv(path, header=None)
    # 如果csv有表头，使用 header=0；如果没有表头，使用 header=None
    # 校验文件是否存在
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在：{path}")
    
    # 读取第一行内容并处理空值
    with open(path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        # 处理空行/全空格的情况
        if not first_line:
            raise ValueError("CSV文件第一行为空，无法判断表头")
        first_line = first_line.split(',')
    
    # 更严谨的表头判断逻辑：第一行所有单元格是否都是非数字（更符合实际业务场景）
    # 若第一行任意一个单元格无法转为数字，则判定为有表头
    has_header = False
    for cell in first_line:
        cell = cell.strip()  # 去除单元格前后空格
        if not cell:  # 跳过空单元格
            continue
        try:
            float(cell)
        except ValueError:
            has_header = True
            break  # 只要有一个非数字，就判定为有表头
    
    # 设置header参数
    header_option = 0 if has_header else None
    # 读取数据
    data = pd.read_csv(path, header=header_option)

    Raman_Shift = data.iloc[:,0].values
    Intensity = data.iloc[:,1].values
    idx_start = np.argmin(np.abs(Raman_Shift - start))

    length = end - start + 1
    Out_Raman_Shift = Raman_Shift[idx_start : length + idx_start]
    Out_Intensity = Intensity[idx_start : length + idx_start]

    # Intensity = pull_baseline(Raman_Shift, Intensity )
    Out_Intensity = nor_max(Out_Intensity, 0.0)
    origin_intensity = Out_Intensity
    Out_Intensity = torch.tensor(Out_Intensity).to(torch.float32)
    Out_Intensity = Out_Intensity.view(1,1, length)
    return Out_Raman_Shift, Out_Intensity, origin_intensity # 拉曼位移，归一化tensor，归一化原始数据

# =============================================
def calculate_hqi(spec1, spec2):
    spec1_normalized = spec1 / np.linalg.norm(spec1)
    spec2_normalized = spec2 / np.linalg.norm(spec2)
    dot_product = np.dot(spec1_normalized, spec2_normalized)
    
    # 计算HQI
    hqi = (dot_product ** 2) 
    return hqi

#################################################################
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'save_model', relative_path)

def test_model_data(raman_shift, raman_data, stride=5):
    try:
        raman_data = nor_max(raman_data, 0.0)

        peak_model_path = resource_path('peaks_model_train.pt')
        model_path = resource_path('A2B_model.pt')

        peak_model = Peak_Determination()
        peak_model.load_state_dict(torch.load(peak_model_path, map_location='cpu', weights_only=False))
        peak_model.eval()

        model = Generator(pretrained_model=peak_model, inputlength=100)
        model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=False))
        model.eval()

        # 将数据转换为张量
        raman_data = torch.tensor(raman_data).to(torch.float32)
        raman_data = raman_data.view(1, 1, raman_data.shape[-1])

        output_1, labels_z_1, output_voigt_1 = process_test_model(model, raman_data, flag=True, threshold=0.6, stride=stride, Raman_shift=raman_shift)

        output_1 = output_1.squeeze(0).detach()
        output_numpy_1 = output_1.numpy()

        return output_numpy_1, labels_z_1, output_voigt_1
        
    except Exception as e:
        raise e

if __name__ == "__main__":

    # path_1 = r'demo_data\(3-巯基丙基)三甲氧基硅烷_1.csv' # 科学拉曼
    path_1 = r'D:\study_data\problem\光谱解混\peaks_function\label_data\Compare_Ramn_2\对苯二酚_mean_voigt_fit.csv'
    start = 300
    end = 2000
    raman_length = end - start + 1 # 数据点长度
    Raman_shift, intensity_1, origin_intensity_1 = read_model_data(start, end, path_1)
    stride = 7

    output_numpy_1, labels_z_1, output_voigt_1 = test_model_data(Raman_shift, origin_intensity_1, stride=stride)
    plt.plot(Raman_shift, origin_intensity_1, c = 'green', label='Scientific_Raman data') # 初始科学数据
    plt.plot(Raman_shift, output_numpy_1[1,:] , c = 'blue', label='model_Scientific_amp', lw=0.5) # 画科学拉曼振幅
    plt.legend(labelspacing=0.1,ncol=2,frameon=False,loc='upper center')
    plt.yticks([])
    plt.show()
