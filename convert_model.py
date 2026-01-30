import torch
from models import Peak_Determination, Generator

# 1. 加载Peak_Determination模型
peak_model = Peak_Determination()  # 实例化模型
peak_state_dict = torch.load('save_model/peaks_model_train.pt', map_location='cpu')  # 加载原参数文件
peak_model.load_state_dict(peak_state_dict)  # 加载参数
peak_model.eval()  # 设置为评估模式

# 2. 保存完整的Peak_Determination模型
torch.save(peak_model, 'save_model/peaks_model_full.pt')
print("Peak_Determination完整模型已保存")

# 3. 加载Generator模型（假设需要依赖Peak_Determination）
generator = Generator(pretrained_model=peak_model, inputlength=100)  # 实例化生成器
generator_state_dict = torch.load('save_model/A2B_model.pt', map_location='cpu')  # 加载原生成器参数
generator.load_state_dict(generator_state_dict)  # 加载参数
generator.eval()  # 设置为评估模式

# 4. 保存完整的Generator模型
torch.save(generator, 'save_model/A2B_model_full.pt')
print("Generator完整模型已保存")