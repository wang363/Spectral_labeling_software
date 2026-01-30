# RamanNet Labeler: A PyQt5-Based Raman Spectra Unmixing Tool via Physical Modeling for Generating Deep Learning Labels

## 1. Software Overview  
This is a spectral data processing tool developed based on PyQt5 and Matplotlib, mainly used for visualization, **manual** baseline subtraction, peak fitting (Voigt fitting), and data export of Raman spectral data. The software implements the data processing workflow through two core plotting areas (Spectra Plot and Voigt Plot) and generates synthetic spectral data through (Data Generator), which is suitable for researchers to conduct in-depth analysis of Raman spectral data.

---

### 1.1 Run from Source Code (Python Environment Required)
The software is developed and tested under Python ≥ 3.8.The required dependencies can be installed using:
```
pip install -r requirements.txt
```
After installing dependencies, the GUI can be launched directly:
```
python Ui_main.py
```
This will start the full PyQt5 graphical interface with all functionalities enabled, including spectral visualization, baseline correction, Voigt fitting, and data generation.

### 1.2 Build Executable from Source (Optional)
Users can build a standalone executable using PyInstaller, which packages the Python interpreter and all dependencies.
The provided RamanLabeler.spec file defines the packaging configuration, including:
- Included Python modules
- Required dynamic libraries
- GUI entry point
Advanced users may edit this file to customize the build process.
To build the executable, simply run:
```
pyinstaller --clean RamanLabeler.spec
```
After successful compilation, the executable will be generated in the ```dist/``` directory.
**⚠️ Note:** The first launch of the executable may take longer due to dependency initialization.

### 1.3 Use Precompiled Executable (No Python Required)
For users who do not wish to install Python or dependencies, a precompiled executable package is provided.
**Download Link 1**  
Link: https://pan.baidu.com/s/1kHRw2KKZKXuoJJ74fnP1yg?pwd=ntei    
Extraction code: ntei   
![Software storage and dependencies](https://gitee.com/cjlu-wzl/project_/raw/master/软件.png) 

**Download Link 2**  
Link: https://pan.quark.cn/s/9ae83680a1c4?pwd=B4S2
Extraction code：B4S2

### Note  
The exe file loads slowly for the first time. Please wait patiently. Do not move the exe file, otherwise it will not be able to obtain the dependencies in the '_internal' folder. It is recommended to open it by creating a shortcut.

---

## 2. Core Function Modules

### 2.1. Spectral Data Visualization and Baseline Processing (Spectra Plot Tab)
Mainly used for display, baseline correction, and preprocessing of raw spectral data, supporting the following functions:

#### （1）File Operations
- **Data Import**：Supports importing CSV format spectral data files (containing at least two columns: wavenumber and intensity). After import, interpolation processing is automatically performed to convert wavenumbers into an integer sequence with an interval of 1, facilitating subsequent analysis.
- **Data Reset**：One-click to clear current spectral data and all processing results (such as baseline, baseline-removed data, etc.).

#### （2）Baseline Correction
- **Baseline Point Selection**：Supports manual point selection mode. Click on the spectral graph with the mouse to select baseline reference points (at least 2 points). After selection, the points are automatically sorted by the x-axis for convenient baseline fitting.
- **Baseline Point Management**：Can delete the last selected baseline point or reset all baseline points.
- **Baseline Processing**：
  - Manually mark baseline points (supporting add, delete, and reset operations)
  - Perform baseline fitting and subtraction based on marked points
- **Baseline Calculation and Subtraction**：Calculate the baseline curve through interpolation based on the selected baseline points, and automatically generate baseline-removed data (raw data minus baseline), supporting real-time visual comparison.

#### （3）View Control
- **Visual Interaction**：
  - Switch display of raw data, baseline, and baseline-removed data
  - Automatically display vertical lines and intersection points with the spectrum when the mouse moves
  - Real-time display of intersection coordinates
  - Support view zoom (zoom in/zoom out/reset)

#### （4）Data Export
Supports exporting various preprocessed data, including：
- Raw spectral data (untreated)
- Baseline-corrected data (including original intensity, baseline-removed intensity, baseline value)
- Normalized raw data (normalized to [0,1] range by original intensity)
- Normalized data after baseline correction (normalized to [0,1] range by baseline-removed intensity)

---

### 2.2. Voigt Peak Fitting Analysis (Voigt Plot Tab)
Focus on spectral peak fitting analysis, supporting single-peak/multi-peak fitting based on the Voigt function, with functions including:

#### （1）Data Source
- **Data Source**：Directly import CSV format data, which is automatically normalized for fitting.
- **Data Transfer**：Can receive **baseline-corrected** data from Spectra Plot (automatically normalized), realizing the coherence of the data processing workflow.

#### （2）Voigt Fitting Functions
- **Single-Peak Fitting**：Generate a single-peak Voigt fitting curve and visualize it by manually inputting fitting parameters (amplitude amp, peak position pos, full width at half maximum fwhm, baseline value y0, shape parameter shape). y0 and shape default to 0 and 1 respectively, and it is recommended not to modify these two parameters.
- **Multi-Peak Overall Fitting**：Support adding multiple peak parameters (managed through a table), calculate Voigt curves and sum curves of all sub-peaks, realize multi-peak superposition fitting, and sub-peak curves are distinguished by different colors.
- **Spectral Unmixing Model Fitting**： Support automatic fitting based on pre-trained deep learning models, automatically identify spectral peak positions and generate fitting curves, improving fitting efficiency.

#### （3）Parameter Management
Fitting parameters are visually managed through a table (TableView), supporting adding new peak parameter rows and deleting selected peak parameter rows, facilitating adjustment of multi-peak fitting models.

#### （4）Data Export
Supports exporting Voigt fitting result data for subsequent analysis or report generation. The export includes fitting data of Raman shift, normalized intensity, peak position, amplitude, and full width at half maximum.


## Brief Usage Process
1. Import spectral data through the top "File" menu
2. Complete baseline marking and subtraction in the Spectra Plot tab
3. Switch to the Voigt Plot tab, set peak parameters and perform manual or model automatic fitting
4. Export the required data results using the corresponding buttons

---

### 2.3. Synthetic Data Generation Module (Data Generator Tab)
Used for batch generation of spectral data for training, supporting custom parameter configuration to meet deep learning data needs: 
**（1）Parameter Configuration**
- **Basic Settings**:  
  - Save Path: Set the storage location of generated data.
  - Number of Spectra: Number of spectral lines generated at one time (default 10).
  - Spectral Length: Number of data points per spectrum (default 100, recommended ≥1000).
- **Peak Parameter Settings**:  
  - Minimum/Maximum Number of Peaks: ≥1 and ≥2 respectively.
  - Minimum Peak Spacing: Default 1 data point, recommended ≥30 to avoid peak overlap.
  - FWHM Range: 1-100.

**（2）Data Generation and Viewing**
- Click "Start Generating" after configuration to start, and the progress bar displays the generation status in real-time.
- Browse different spectra through the data index slider, check the corresponding data type checkboxes to visualize peak position labels, amplitude labels, and FWHM labels.

**（3）Output Format**
Generate .spt format files (PyTorch tensor serialization), including:
- X_ideal: Ideal spectral tensor [num_samples, data_length]
- X_add_noise: Spectra with added noise
- X_add_baseline: Spectra with added baseline
- X_final_noise: Biological-like sample spectra
- y_ideal: Three-channel parameter labels [num_samples, 3, data_length]


---


##  3.Partial Interface Display
1. ![File import](https://gitee.com/cjlu-wzl/project_/raw/master/Project_Manual_label/文件导入.png)  
- 'Open File' is used to import data into the "Spectra Plot" tab
- 'Open File for Voigt Plot' is used to import data into the "Voigt Plot" tab
2. ![Spectra Plot](https://gitee.com/cjlu-wzl/project_/raw/master/Project_Manual_label/Spectra_plot.png)
- After manual baseline removal in the "Spectra Plot" interface, regardless of whether data is imported using 'Open File for Voigt Plot', "Voigt Plot" will automatically display the curve after baseline removal
3. ![Voigt Plot](https://gitee.com/cjlu-wzl/project_/raw/master/Voigt_Plot_1.png) 
4. ![Voigt Plot](https://gitee.com/cjlu-wzl/project_/raw/master/Voigt_Plot_2.png)
- Click the "Model Fitting" button to perform automatic Voigt fitting, and you can export various parameter information after fitting
```
# Parameter information is as follows
data_to_export = pd.DataFrame({
                        'Raman Shift': raman_shift,
                        'Norm Intensity': Norm_raw_intensity,
                        'Voigt Intensity':Voigt Fitting Data ,
                        'Pos': pos_col,
                        'Amp': amp_col,
                        'Fwhm': fwhm_col
                    })
```
5. ![Data Generator](https://gitee.com/cjlu-wzl/project_/raw/master/Figure_5.png)
- After setting basic parameters, click "Start Generating" to generate four types of training spectral data.