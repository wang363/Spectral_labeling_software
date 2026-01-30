# test_model.py
import torch
import os
import sys

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.dirname(__file__), relative_path)


model_path = resource_path('save_model/peaks_model_train.pt')
try:
    model = torch.load(model_path, map_location='cpu')
    print("模型加载成功！")
except Exception as e:
    print(f"模型加载失败：{e}")

if __name__ == '__main__':
    # 打包命令：pyinstaller --onefile --add-data "save_model/*;save_model" test_model.py
    pass