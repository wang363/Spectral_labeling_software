# translations.py

DESCRIPTION_HTML_ZH = """
<h3>📋 <b>基本功能</b></h3>
<p>根据设定的 <b>Voigt 峰拟合参数</b>，生成对应的 <b>四种光谱数据</b> 及其标签，适用于深度学习模型训练与数据增强。</p>
<ul>
    <li>📁 <b>文件设置：</b>保存路径</li>
    <li>📊 <b>光谱数量：</b>生成多少条光谱数据，默认>10</li>
    <li>📏 <b>光谱长度：</b>每条光谱的点数，范围100-3200</li>
    <li>📈 <b>峰数量范围：</b>每条光谱中随机生成峰的数量</li>
    <li>📏 <b>谱峰间距：</b>相邻峰之间的最小距离</li>
    <li>🔹 <b>半峰宽范围 (FWHM)：</b>Voigt 峰的宽度范围</li>
</ul>
<p>画图时，半峰宽标签默认除以30以便显示。</p>
"""

DESCRIPTION_HTML_EN = """
<h3>📋 <b>Basic Features</b></h3>
<p>Generate <b>four types of spectra</b> and their corresponding <b>labels</b> based on Voigt peak parameters, used for data augmentation in deep learning model training.</p>
<ul>
    <li>📁 <b>File Settings:</b> Save path</li>
    <li>📊 <b>Number of Spectra:</b> How many spectra to generate. The default number is greater than 10</li>
    <li>📏 <b>Spectrum Length:</b> Number of points in each spectrum, range:100-3200</li>
    <li>📈 <b>Peak Count Range:</b> Random number of peaks in each spectrum</li>
    <li>📏 <b>Peak Spacing:</b> Minimum distance between neighboring peaks</li>
    <li>🔹 <b>FWHM Range:</b> Full width at half maximum of Voigt peaks</li>
</ul>
<p>When plotting, the FWHM labels are divided by 30 for better visualization.</p>
"""


# 包含所有UI组件文本的翻译字典
# 键是原始中文文本（来自.ui文件），值是对应的英文翻译
TRANSLATIONS_MAP = {
    # 主窗口和菜单栏
    "光谱标记软件": "Spectral Labeling Software",
    "文件": "File",
    "语言": "Language",
    "Open File": "Open File",
    "Open File for Voigt Plot": "Open File for Voigt Plot",
    "English": "English",
    "简体中文": "Chinese",

    # Spectra Plot 选项卡
    "Spectra Plot": "Spectra Plot",
    "手动去除基线": "Manual Baseline Removal",
    "添加基线点": "Add Baseline Point",
    "移除基线点": "Remove Baseline Point",
    "重置所有基线点": "Reset All Baseline Points",
    "应用基线扣除": "Apply Baseline Subtraction",
    "基线信息于此显示": "Baseline information is displayed here",
    "自动去除基线": "Automatic Baseline Removal",
    "选择去基线算法": "Select Baseline Algorithm",
    "应用算法去除": "Apply Algorithm",
    "导出去基线数据 - 1*": "Export Baseline-subtracted Data - 1*",
    "Export normalized data 1*": "Export Normalized Data - 1*",
    "自动基线": "Auto Baseline",     
    "自动去基线": "Auto Subtracted",    
    "导出和视图": "Export and View",
    "导出原始数据 - 2*": "Export Raw Data - 2*",
    "Export normalized data 2*": "Export Normalized Data - 2*",
    "导出去基线数据 - 3*": "Export Baseline-subtracted Data - 3*",
    "Export normalized data 3*": "Export Normalized Data - 3*",
    "缩放:": "Zoom:",
    "放大": "Zoom In",
    "缩小": "Zoom Out",
    "重置视图": "Reset View",
    "显示:": "Show:",
    "原始数据": "Raw Data",
    "基线": "Baseline",
    "手动基线": "Manual Baseline",   
    "手动去基线": "Manual Subtracted",

    # Voigt Plot 选项卡
    "Voigt Plot": "Voigt Plot",
    "导入数据显示": "Show Imported Data",
    "去基线数据显示": "Show Baseline-subtracted Data",
    "单峰拟合数据": "Single Peak Fit",
    "模型拟合数据": "Model Fit Data",
    "Voigt整体拟合数据": "Overall Voigt Fit Data",
    "Voigt Fit": "Voigt Fit",
    "水平基线值(y0):": "Baseline (y0):",
    "振幅(amp):": "Amplitude (amp):",
    "位置(pos):": "Position (pos):",
    "半高全宽(fwhm):": "FWHM (fwhm):",
    "形状参数(shape):": "Shape (shape):",
    "单峰参数拟合": "Single Peak Fit",
    "*模型拟合*": "*Model Fit*",
    "添加Voigt峰→": "Add Voigt Peak →",
    "Voigt 峰列表": "Voigt Peak List",
    "Voigt峰整体拟合": "Overall Voigt Fit",
    "删除选中数据": "Delete Selected",
    "导出Voigt拟合数据": "Export Voigt Fit Data",

    # Voigt Plot 表头
    '位置(pos)': 'Position (pos)',
    '振幅(amp)': 'Amplitude (amp)',
    '半高全宽(fwhm)': 'FWHM (fwhm)',
    '水平基线值(y0)': 'Baseline (y0)',
    '形状参数(shape)': 'Shape (shape)',

    # Data Generator 选项卡
    '文件设置': 'File Settings',
    'Save path:': 'Save path:',
    'Browse': 'Browse',
    '开始生成': 'Start Generating',

    '生成器参数': 'Generator Parameters',
    '光谱数量:': 'Number of Spectrums:',
    '光谱长度:': "Spectrum Length:",
    '最小谱峰数量:': 'Minimum Peaks:',
    '最大谱峰数量:': 'Maximum Peaks:',
    '最小谱峰间距:': 'Minimum Peak Spacing:',
    '最小半峰宽:': 'Minimum FWHM:',
    '最大半峰宽:': 'Maximum FWHM:',
    
    '数据展示': 'Data Visualization',
    '数据索引:': 'Data Index:',
    '数据展示': 'Display Data',
    '谱峰位移标签': 'Peak Shift Labels',
    '峰强标签': 'Peak Intensity Labels',
    '半高全宽标签': 'FWHM Labels',    

    # ========================
    #  新增的动态文本
    # ========================
    # 文件对话框标题
    "为 Spectra Plot 打开文件": "Open File for Spectra Plot",
    "为 Voigt Plot 打开文件": "Open File for Voigt Plot",
    "导出原始数据": "Export Raw Data",
    "导出校正后数据": "Export Corrected Data",
    "导出自动校正后数据": "Export Auto Corrected Data",
    "导出自动校正后归一化数据": "Export Auto Corrected Normalized Data",
    "导出归一化后原始数据": "Export Normalized Raw Data",
    "导出校正后归一化数据": "Export Corrected Normalized Data",
    "导出Voigt拟合数据": "Export Voigt Fit Data",

    # 消息框 (QMessageBox)
    "错误": "Error",
    "警告": "Warning",
    "提示": "Information",
    "成功": "Success",
    "数据错误": "Data Error",
    "准备数据错误": "Data Preparation Error",
    "模型拟合错误": "Model Fit Error",
    "无法打开或解析文件: {error}": "Could not open or parse file: {error}",
    "文件需要至少包含两列数据": "The file must contain at least two columns of data.",
    "无法打开或解析Voigt文件: {error}": "Could not open or parse Voigt file: {error}",
    "选点模式已开启。\n请在图上点击以选择基线点。\n鼠标移动时将显示坐标。": "Pick points mode is enabled.\nPlease click on the plot to select baseline points.\nCoordinates will be shown on mouse move.",
    "已选基线点:\n{points}": "Selected baseline points:\n{points}",
    "尚未选择基线点。": "No baseline points have been selected yet.",
    "请至少选择两个基线点。": "Please select at least two baseline points.",
    "请先加载原始数据！": "Please load the raw data first!",
    "请选择有效的去基线算法！": "Please select a valid baseline removal algorithm!",
    "{algo} 去基线处理完成。": "{algo} baseline removal process completed.",
    "算法执行失败: {e}": "Algorithm execution failed: {e}",
    "原始数据已成功导出。": "Raw data has been successfully exported.",
    "导出原始数据失败: {str_e}": "Failed to export raw data: {str_e}",
    "基线校正后的数据已成功导出。": "Baseline-corrected data has been successfully exported.",
    "导出校正后数据失败: {str_e}": "Failed to export corrected data: {str_e}",
    "自动基线校正后的数据已成功导出。": "Auto baseline-corrected data has been successfully exported.",
    "导出自动校正后数据失败: {str_e}": "Failed to export auto corrected data: {str_e}",
    "自动基线校正后的归一化数据已成功导出。": "Auto corrected and normalized data has been successfully exported.",
    "导出自动校正后归一化数据失败: {str_e}": "Failed to export auto corrected and normalized data: {str_e}",
    "归一化后的原始数据已成功导出。": "Normalized raw data has been successfully exported.",
    "导出数据失败: {str_e}": "Failed to export data: {str_e}",
    "基线校正后的归一化数据已成功导出。": "Baseline-corrected and normalized data has been successfully exported.",
    "请先向Voigt Plot中加载数据再进行拟合。": "Please load data into the Voigt Plot before fitting.",
    "请先添加至少一个峰参数再进行整体拟合。": "Please add at least one peak parameter before performing an overall fit.",
    "第{row}行数据格式错误: {str_e}": "Data format error in row {row}: {str_e}",
    "请先向Voigt Plot中加载数据再进行模型拟合。": "Please load data into the Voigt Plot before model fitting.",
    "数据准备过程中发生错误: {str_e}": "An error occurred during data preparation: {str_e}",
    "模型拟合完成，共检测到{peak_count}个峰": "Model fit completed. {peak_count} peaks were detected.",
    "模型拟合过程中发生错误: {error_msg}": "An error occurred during the model fitting process: {error_msg}",
    "请先选中要删除的行": "Please select the row(s) to delete first.",
    "Voigt拟合数据已成功导出。": "Voigt fit data has been successfully exported.",
    "导出Voigt拟合数据失败: {str_e}": "Failed to export Voigt fit data: {str_e}",

    "请先选择一个保存路径！": "Please select a save path first!",
    "参数错误": "Parameter Error",
    "最小谱峰数量不能大于最大谱峰数量！": "Minimum peak count cannot be greater than maximum peak count!",
    "最小半峰宽不能大于最大半峰宽！": "Minimum FWHM cannot be greater than maximum FWHM!",
    "完成": "Completed",
    "数据生成成功！": "Data generation successful!",
    "生成数据时出错: {e}": "Error generating data: {e}",
    "数据索引超出范围！": "Data index out of range!",



    # 进度对话框
    "正在进行模型拟合...": "Model fitting in progress...",
    "拟合中": "Fitting...",


    # ========================
    #  图例和坐标轴文本
    # ========================
    "原始数据": "Raw Data",
    "导入数据": "Imported Data",
    "去基线数据": "Baseline-subtracted Data",
    "基线": "Baseline",
    "手动去基线数据": "Manual Subtracted Data",
    # 注意下面这个是模板，用于动态生成图例
    "{algo}去除基线": "{algo} Baseline",
    "基线点": "Baseline Points",
    "单峰拟合曲线": "Single Peak Fit Curve",
    "整体拟合曲线总和": "Overall Fit Curve Sum",
    "模型拟合数据": "Model Fit Data",
    "Raman Shift (${cm}$$^{-1}$)": "Raman Shift (${cm}$$^{-1}$)",
    "Raman Intensity (a.u.)": "Raman Intensity (a.u.)",

    '理想数据': 'Ideal Data',
    '微噪数据': 'Slight Noise Data',
    '仿真实数据': 'Simulated Real Data',
    '仿生物样本': 'Simulated Biological Data',
    "峰位": "Pos",
    '峰振幅': 'Amp',
    "半峰宽": "FWHM"

}

# 添加到 TRANSLATIONS_MAP，可直接调用 get_translation()
TRANSLATIONS_MAP[DESCRIPTION_HTML_ZH] = DESCRIPTION_HTML_EN

# 全局变量来存储当前语言
current_language = 'zh'

def set_language(lang):
    """设置全局语言"""
    global current_language
    current_language = lang

def get_translation( key, **kwargs):
    """
    获取翻译文本。支持格式化字符串。
    :param key: 翻译字典中的键 (通常是中文原文)
    :param kwargs: 用于字符串格式化的参数
    :return: 翻译后的字符串
    """
    if current_language == 'en':
        translated_text = TRANSLATIONS_MAP.get(key, key)
     
    else:
        translated_text = key
   
    # 如果有格式化参数，则应用它们
    if kwargs:
        return translated_text.format(**kwargs)
    return translated_text

def translate_ui(window, language):
    """
    根据选择的语言翻译整个UI。
    :param window: 主窗口实例 (self)
    :param language: 目标语言 ('en' 或 'zh')
    """
    set_language(language)
    def tr(text):
        return get_translation( text)
    # 更新主窗口和菜单
    window.setWindowTitle(tr("光谱标记软件"))
    window.menu.setTitle(tr("文件"))
    window.menu_2.setTitle(tr("语言"))
    window.actionOpen_File.setText(tr("Open File"))
    window.actionOpen_File_for_Voigt_Plot.setText(tr("Open File for Voigt Plot"))
    window.actionEnglish.setText(tr("English"))
    window.action_6.setText(tr("简体中文")) # action_6 is the new name for the Chinese action

    # 更新 Spectra Plot 选项卡
    window.tabWidget.setTabText(window.tabWidget.indexOf(window.tab), tr("Spectra Plot"))
    window.groupBox.setTitle(tr("手动去除基线"))
    window.pushButton.setText(tr("添加基线点"))
    window.pushButton_2.setText(tr("移除基线点"))
    window.pushButton_3.setText(tr("重置所有基线点"))
    window.pushButton_4.setText(tr("应用基线扣除"))
    window.textEdit.setPlaceholderText(tr("基线信息于此显示"))
    
    window.groupBox_5.setTitle(tr("自动去除基线"))
    # ComboBox 需要特殊处理
    current_index = window.comboBox.currentIndex()
    window.comboBox.setItemText(0, tr("选择去基线算法"))
    window.comboBox.setCurrentIndex(current_index)
    
    window.pushButton_16.setText(tr("应用算法去除"))
    window.pushButton_14.setText(tr("导出去基线数据 - 1*"))
    window.pushButton_15.setText(tr("Export normalized data 1*"))
    
    window.groupBox_3.setTitle(tr("导出和视图"))
    window.pushButton_9.setText(tr("导出原始数据 - 2*"))
    window.pushButton_8.setText(tr("Export normalized data 2*"))
    window.pushButton_10.setText(tr("导出去基线数据 - 3*"))
    window.pushButton_11.setText(tr("Export normalized data 3*"))
    window.label_2.setText(tr("缩放:"))
    window.pushButton_5.setText(tr("放大"))
    window.pushButton_6.setText(tr("缩小"))
    window.pushButton_7.setText(tr("重置视图"))
    window.label.setText(tr("显示:"))
    window.checkBox.setText(tr("原始数据"))
    window.checkBox_2.setText(tr("手动基线"))
    window.checkBox_3.setText(tr("手动去基线"))
    window.checkBox_5.setText(tr("自动去基线"))
    window.checkBox_6.setText(tr("自动基线"))

    # 更新 Voigt Plot 选项卡
    window.tabWidget.setTabText(window.tabWidget.indexOf(window.tab_2), tr("Voigt Plot"))
    window.checkBox_11.setText(tr("导入数据显示"))
    window.checkBox_14.setText(tr("去基线数据显示"))
    window.checkBox_12.setText(tr("单峰拟合数据"))
    window.checkBox_4.setText(tr("模型拟合数据"))
    window.checkBox_13.setText(tr("Voigt整体拟合数据"))
    
    window.groupBox_2.setTitle(tr("Voigt Fit"))
    window.label_3.setText(tr("水平基线值(y0):"))
    window.label_4.setText(tr("振幅(amp):"))
    window.label_5.setText(tr("位置(pos):"))
    window.label_6.setText(tr("半高全宽(fwhm):"))
    window.label_19.setText(tr("形状参数(shape):"))
    window.pushButton_36.setText(tr("单峰参数拟合"))
    window.pushButton_13.setText(tr("*模型拟合*"))
    window.pushButton_34.setText(tr("添加Voigt峰→"))
    
    window.groupBox_4.setTitle(tr("Voigt 峰列表"))
    window.pushButton_35.setText(tr("Voigt峰整体拟合"))
    window.pushButton_37.setText(tr("删除选中数据"))
    window.pushButton_12.setText(tr("导出Voigt拟合数据"))

    window.groupBox_6.setTitle(tr("文件设置"))
    window.label_7.setText(tr("Save path:"))
    window.pushButton_17.setText(tr("Browse"))
    window.pushButton_18.setText(tr("开始生成"))
    window.groupBox_7.setTitle(tr("生成器参数"))
    window.label_8.setText(tr("光谱数量:"))
    window.label_15.setText(tr("光谱长度:"))
    window.label_9.setText(tr("最小谱峰数量:"))
    window.label_10.setText(tr("最大谱峰数量:"))
    window.label_11.setText(tr("最小谱峰间距:"))
    window.label_12.setText(tr("最小半峰宽:"))
    window.label_13.setText(tr("最大半峰宽:"))
    window.groupBox_8.setTitle(tr("数据展示"))
    window.label_14.setText(tr("数据索引:"))
    window.pushButton_19.setText(tr("数据展示"))
    window.checkBox_7.setText(tr("谱峰位移标签"))
    window.checkBox_8.setText(tr("峰强标签"))
    window.checkBox_9.setText(tr("半高全宽标签"))

    
    


    # 更新 TableView 的表头
    header_labels = [
        tr('位置(pos)'), 
        tr('振幅(amp)'), 
        tr('半高全宽(fwhm)'), 
        tr('水平基线值(y0)'), 
        tr('形状参数(shape)')
    ]
    window.table_model.setHorizontalHeaderLabels(header_labels)