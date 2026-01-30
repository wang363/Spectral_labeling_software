from numpy import arange
import scipy.signal as signal
from math import sqrt
import numpy as np
import pywt
from scipy.sparse import csc_matrix, eye, diags
from scipy.sparse.linalg import spsolve

def get_average(records):  # Seeking of average
    return sum(records) / len(records)


def get_rms(records):  # Seeking of rms
    return sqrt(sum([x ** 2 for x in records]) / len(records))


def convo(y, numb):
    wi = np.ones(int(numb)) / float(numb)
    return np.convolve(y, wi, 'same')

def wavelet_transform_db16(Relative_intensity, a):  # Wavelet transform
    w = pywt.Wavelet('db16')  # Select thr Daubechies8

    maxlev = pywt.dwt_max_level(len(Relative_intensity), w.dec_len)

    threshold = a  # Threshold for filtering

    coeffs = pywt.wavedec(Relative_intensity, 'db16', level=maxlev)  # Wavelet decomposition of signal

    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold * max(coeffs[i]))  # Filter noise
    datarec = pywt.waverec(coeffs, 'db16')  # Wavelet reconstruction of signal
    datas = arange(0, Relative_intensity.shape[0], 1)
    for i in range(0, Relative_intensity.shape[0]):
        datas[i] = datarec[i]
    return datas


def wavelet_transform_db8(Relative_intensity, a):  # Wavelet transform

    w = pywt.Wavelet('db8')  # Select thr Daubechies8

    maxlev = pywt.dwt_max_level(len(Relative_intensity), w.dec_len)

    threshold = a  # Threshold for filtering

    coeffs = pywt.wavedec(Relative_intensity, 'db8', level=maxlev)  # Wavelet decomposition of signal

    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold * max(coeffs[i]))  # Filter noise

    datarec = pywt.waverec(coeffs, 'db8')  # Wavelet reconstruction of signal

    datas = arange(0, Relative_intensity.shape[0], 1)

    for i in range(0, Relative_intensity.shape[0]):
        datas[i] = datarec[i]
    return datas


def fft(Relative_intensity):  # FFT denoising
    b, a = signal.butter(8, 0.2, 'lowpass', analog=False)
    filtedData = signal.filtfilt(b, a, Relative_intensity)
    filtedData = signal.filtfilt(b, a, filtedData)
    filtedData = signal.filtfilt(b, a, filtedData)
    filtedData = signal.filtfilt(b, a, filtedData)
    return filtedData


def med(Relative_intensity, n, a):  # median filtering
    med_data = arange(0, Relative_intensity.shape[0], 1)
    for idx in range(0, len(Relative_intensity) - 1):
        med_data[idx] = Relative_intensity[idx]
    med_data[Relative_intensity.shape[0] - 1] = Relative_intensity[Relative_intensity.shape[0] - 2]
    med_data = signal.medfilt(Relative_intensity, 3)  # One dimensional median filter
    for i in range(1, n):
        med_data = signal.medfilt(med_data, a)  # One dimensional median filter
    return med_data


def pull_baseline_db16(Relative_intensity):  # pull_baseline

    wt_1 = wavelet_transform_db16(Relative_intensity, 5)  # wavelet_transform
    data_1 = Relative_intensity - wt_1

    wt_2 = wavelet_transform_db16(data_1, 0.4)  # wavelet_transform
    data_2 = data_1 - wt_2
    data_2 = Relative_intensity - abs(data_2)

    for x in range(0, 10):
        wt_1 = wavelet_transform_db16(data_2, 5)
        data_1 = Relative_intensity - wt_1
        data_2 = Relative_intensity - abs(data_1)

    return (data_1 - min(data_1))


def pull_baseline_db8(Relative_intensity):  # pull_baseline

    wt_1 = wavelet_transform_db8(Relative_intensity, 5)  # wavelet_transform
    data_1 = Relative_intensity - wt_1

    wt_2 = wavelet_transform_db8(data_1, 0.4)  # wavelet_transform
    data_2 = data_1 - wt_2
    data_2 = Relative_intensity - abs(data_2)

    for x in range(0, 10):
        wt_1 = wavelet_transform_db8(data_2, 5)
        data_1 = Relative_intensity - wt_1
        data_2 = Relative_intensity - abs(data_1)

    return (data_1 - min(data_1))


def pull_baseline(Raman_Shift, Relative_intensity, proportion=15, Denosing=1):
    try:
        Raman_Shift = np.array(Raman_Shift)
        Relative_intensity = np.array(Relative_intensity) * 1000

        # 用来去基线
        RI_db8 = pull_baseline_db8(Relative_intensity)
        subscript = np.where(RI_db8 == max(RI_db8))[0][0]

        if Relative_intensity[subscript] / RI_db8[subscript] > proportion:
            pull_data = pull_baseline_db16(Relative_intensity)
        else:
            pull_data = pull_baseline_db8(Relative_intensity)


        if Denosing is not None:
            pull_data = fft(pull_data) 
            pull_data = med(pull_data, 1000, 7)
            for i in range(0, 10):
                pull_data = wavelet_transform_db8(pull_data, 0.005)
            pull_data = pull_baseline_db8(pull_data)
            return pull_data / 1000

        return pull_data / 1000
    
    except: return Relative_intensity

def WhittakerSmooth(x,w,lambda_,differences=1):

    X=np.matrix(x)
    m=X.size
    E=eye(m,format='csc')
    for i in range(differences):
        E=E[1:]-E[:-1] # numpy.diff() does not work with sparse matrix. This is a workaround.
    W=diags(w,0,shape=(m,m))
    A=csc_matrix(W+(lambda_*E.T*E))
    B=csc_matrix(W*X.T)
    background=spsolve(A,B)
    return np.array(background)

def airPLS(x, lambda_=100, porder=1, itermax=15):
    '''
    Adaptive iteratively reweighted penalized least squares for baseline fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background, z
        porder: adaptive iteratively reweighted penalized least squares for baseline fitting
    
    output
        the fitted background vector
    '''
    m=x.shape[0]
    w=np.ones(m)
    for i in range(1,itermax+1):
        z=WhittakerSmooth(x,w,lambda_, porder)
        d=x-z
        dssn=np.abs(d[d<0].sum())
        if(dssn<0.001*(abs(x)).sum() or i==itermax):
            if(i==itermax): print('WARING max iteration reached!')
            break
        w[d>=0]=0 # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
        w[d<0]=np.exp(i*np.abs(d[d<0])/dssn)
        w[0]=np.exp(i*(d[d<0]).max()/dssn) 
        w[-1]=w[0]
    return x-z


from lmfit.models import  PseudoVoigtModel # pip install lmfit
def voigt_func(x, y):
    x_shifted = x - x.min()  # Shifting to 0
    y_shifted = y - y.min()  # Shifting to 0
    mod = PseudoVoigtModel()  # Setting model type
    pars = mod.guess(y_shifted, x=x_shifted)  # Estimating fit
    out = mod.fit(y_shifted, pars, x=x_shifted)  # Fitting fit
    fwhm=out.params['fwhm'].value
    center=out.params['center'].value
    # print(pars)
    # out.plot()  # Plotting fit
    return out.best_fit,fwhm

def iteration(data):
    data = np.asarray(data, dtype=float)
    p = len(data)
    if p < 3:
        return np.zeros_like(data), 0, 0, 0
    peakpoint = np.argmax(data)

    Di = np.diff(data)

    boundr = 0
    for j in range(peakpoint, p-2):
        if (Di[j] < Di[j + 1]) and Di[j + 1] > -2e-10:
            boundr = j - peakpoint + 1
            break

    boundl = 0
    for j in range(peakpoint, 1, -1):
        if (Di[j-1] > Di[j-2]) and Di[j-2] < 2e-10:
            boundl = peakpoint - j + 1
            break

    peak_data = np.zeros_like(data)
    left = max(0, peakpoint - boundl)
    right = min(p, peakpoint + boundr)
    peak_data[left:right] = data[left:right]

    return peak_data, boundr, boundl, peakpoint

def voigtanalysis(signal, voigt_func=voigt_func, max_peaks=6):
    signal = np.asarray(signal, dtype=float)
    threshold = max(signal) * 0.05
    n = len(signal)
    x = np.arange(n)
    peak_accum = np.zeros_like(signal)
    save = np.zeros_like(signal)
    peak_positions = []
    peak_matrix = []

    signal = np.where(signal < threshold, 0, signal)

    for i in range(max_peaks):
        data = signal - peak_accum
        peak_data, boundr, boundl, peakp = iteration(data)

        if np.max(peak_data) < threshold:
            break

        # Voigt拟合
        fit_y, param = voigt_func(x, peak_data)
        if np.max(fit_y) < 1e-6:
            break

        # 计算标准峰
        peak_matrix.append(fit_y)
        peak_positions.append(peakp)

        # 累积结果
        save += fit_y
        peak_accum += peak_data

    # peak_matrix = np.vstack(peak_matrix) if peak_matrix else np.zeros((0, n))
    return save



if __name__ == "__main__":
    import pandas as pd
    data = pd.read_csv(r'demo_data\RM-20230510-005_1.csv', header=None)
    raman_shift = data[0].values
    raman_intensity = data[1].values
    processed_intensity = pull_baseline(raman_shift, raman_intensity, Denosing=None)
    import matplotlib.pyplot as plt
    plt.plot(raman_shift, raman_intensity, label='Original')
    plt.plot(raman_shift, processed_intensity, label='Processed')

    baseline_intensity = airPLS(raman_intensity, lambda_=100, porder=1, itermax=15)
    plt.plot(raman_shift, baseline_intensity, label='Processed')

    total_fit = voigtanalysis(raman_intensity, voigt_func=voigt_func, max_peaks=6)
    plt.plot(raman_shift, total_fit, 'r--', label='Total Fitted Peaks')

    plt.xlabel('Raman Shift (cm⁻¹)')
    plt.ylabel('Intensity (a.u.)')
    plt.legend()
    plt.show()










