# 映动：照片动画与 LivePortrait 入门 demo

## 先看结论

你的截图显示 Core Ultra 7 255H、Intel Arc 140T 核显、32GB 内存。可以开发软件，也可以尝试 LivePortrait 人物模型的 CPU 推理。截图显示的 128MB/16GB 不等同于 NVIDIA 独立显存：不要安装 CUDA 来试图让 Intel 核显变成 CUDA 显卡。官方设备选择代码只有 CPU、CUDA、Apple MPS，没有 Intel XPU 分支。CPU 参数在官方代码中仍标为 WIP，不保证你的机器能快速或无问题完成推理。

本目录包含两条完整的代码路径：
- **马上体验**：浏览器上传照片，提示词选择摇摆/拉近/呼吸，导出 4 秒 WebM。普通图片变换，没有 AI、没有脸部表情生成。
- **接入真正 AI**：同一界面切换 LivePortrait，上传照片和驱动视频，FastAPI 调用官方推理脚本，返回 MP4。此路径必须先安装权重与环境；本次没有下载大模型，未在你的电脑上完成真实推理验证。

LivePortrait 主要把驱动视频中的动作迁移到照片，不直接理解任意提示词。如果比赛要求“照片 + 文本 → 任意动作视频”，后续需要文本驱动的视频模型/API，或先将有限动作提示词映射到你们准备的驱动视频。例：“微笑”选 smile.mp4，“点头”选 nod.mp4；这种方案应称为动作模板选择，不是开放式文本生成。当前 AI demo 只映射动画区域：眼睛→eyes，嘴→lip，表情→exp，头部→pose，其他→all。写“微笑”不会凭空产生微笑。

## 1. 三分钟跑通普通动画

在 PowerShell 中逐行执行：

```powershell
cd C:\Users\29346\git-practice\portrait-demo
python serve.py
```

浏览器打开 http://127.0.0.1:8765 。可直接体验示例插画，或上传自己的 JPG/PNG/WebP。
输入“轻轻摇摆，缓慢拉近”或“呼吸”，点击预览，再点击导出。使用新版 Edge/Chrome，录制期间保持页面在前台。导出 WebM 可以直接在浏览器播放；不需要 FFmpeg。

这个服务只提供静态网页，照片在浏览器内处理。上传和导出没有调用后端或 AI。结束时在终端 Ctrl+C。也可以直接双击 web/index.html，HTTP 启动方式更适合后续学习。

## 2. 安装 LivePortrait 人物模型：Windows CPU 路线

已检查到本机有 Python 3.13、Git 和 Anaconda，当前命令行找不到 FFmpeg。以下是依据官方仓库整理的 CPU 安装方案，不是官方对这台 Intel 电脑的兼容保证。只装人物模型，不需要动物模型的 X-Pose/CUDA 编译。

### A. 建独立环境

打开开始菜单的 **Anaconda Prompt**，逐行运行。以下命令中的 cd 用的是 CMD 语法：

```bat
cd /d C:\Users\29346\git-practice\portrait-demo
conda create -n liveportrait-cpu python=3.10 -y
conda activate liveportrait-cpu
conda install -c conda-forge ffmpeg -y
git clone https://github.com/KlingTeam/LivePortrait.git
cd LivePortrait
python -m pip install torch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements_base.txt
python -m pip install onnxruntime==1.18.0 transformers==4.38.0 huggingface_hub
```

这里有意使用 CPU 版 PyTorch、CPU 版 onnxruntime。不要再执行官方 requirements.txt，它包含 onnxruntime-gpu。不要同时安装 onnxruntime 和 onnxruntime-gpu。环境里采用官方基础依赖的版本组合；不要随意更新其中某一个包。若 LivePortrait 文件夹已存在，不要重复 clone，直接 cd 进去。

### B. 下载人物权重

继续在 LivePortrait 目录执行（需联网，下载可能较慢）：

```bat
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='KlingTeam/LivePortrait', local_dir='pretrained_weights', allow_patterns=['liveportrait/*','insightface/*'])"
```

应当包含这些文件，不要形成 pretrained_weights/pretrained_weights 双层目录：

```text
pretrained_weights/
  liveportrait/base_models/appearance_feature_extractor.pth
  liveportrait/base_models/motion_extractor.pth
  liveportrait/base_models/warping_module.pth
  liveportrait/base_models/spade_generator.pth
  liveportrait/retargeting_models/stitching_retargeting_module.pth
  liveportrait/landmark.onnx
  insightface/models/buffalo_l/2d106det.onnx
  insightface/models/buffalo_l/det_10g.onnx
```

若 Hugging Face 无法连接，可用官方 README 提供的百度网盘/Google Drive 下载途径，按目录放好权重；不要反复重装 Python。保留一些额外磁盘空间给环境、权重和视频，截图中的存储容量足够，但实际空闲量以磁盘为准。

### C. 验收环境

```bat
python --version
ffmpeg -version
python -c "import torch, onnxruntime as ort; print(torch.__version__); print('CUDA:', torch.cuda.is_available()); print(ort.get_available_providers())"
python inference.py --help
```

应是 Python 3.10，FFmpeg 能输出版本，CUDA: False 是这个 CPU 环境的正常结果，ONNX providers 应包含 CPUExecutionProvider。

### D. 先跑官方示例

```bat
python inference.py -s assets/examples/source/s9.jpg -d assets/examples/driving/d0.mp4 --flag-force-cpu --no-flag-use-half-precision
```

核心是强制 CPU 并关闭 FP16；不要用 --flag-do-torch-compile。结果查看 animations 目录下 MP4。CPU 耗时与驱动视频长度、处理选项有关，本次没有实测，不承诺几秒或几分钟。

官方示例成功后，换成自己的素材，先用 1–3 秒、正脸、单人的驱动视频：

```bat
python inference.py -s "C:\你的目录\photo.jpg" -d "C:\你的目录\drive.mp4" --flag-force-cpu --no-flag-use-half-precision --flag-crop-driving-video
```

可选：官方 Gradio 界面比 FastAPI 更容易入门：

```bat
python app.py --flag-force-cpu --no-flag-use-half-precision
```

打开终端实际打印的 URL。先用命令行确认模型正常，再排查网页，能减少同时遇到的问题。

## 3. 接通本 demo 的 AI 模式

在同一个 **Anaconda Prompt** 中确保 liveportrait-cpu 环境已经激活，然后：

```bat
cd /d C:\Users\29346\git-practice\portrait-demo
python -m pip install -r requirements-backend.txt
set LIVEPORTRAIT_DIR=C:\Users\29346\git-practice\portrait-demo\LivePortrait
python -m uvicorn backend:app --host 127.0.0.1 --port 8766
```

浏览器打开 http://127.0.0.1:8766 ，切换 LivePortrait，上传真实照片和短 MP4，点击生成。不要在 8765 的静态服务器上调用 AI；静态服务器没有 /api/generate 接口。

PowerShell 设置环境变量的写法是 `$env:LIVEPORTRAIT_DIR = 'C:\Users\29346\git-practice\portrait-demo\LivePortrait'`，与上面的 CMD set 不同。

FastAPI 自动接口文档：http://127.0.0.1:8766/docs 。返回视频是 MP4。界面会等待完整推理；本地教学版只允许一个任务，有 30 分钟超时，照片最大 20MB、驱动视频最大 50MB。扩展名检查是基本提示，不是完整内容验证。长视频可能耗尽内存；先使用短视频。本服务面向本机教学，比赛部署前还需任务队列、进度查询、身份验证、视频时长和文件内容校验。

## 4. FastAPI 到底是什么：把你认识的函数接到网页上

你会写这样的 Python 函数：

```python
def generate(photo, driving, prompt):
    # 处理输入，运行模型，再返回结果
    ...
```

FastAPI 让浏览器能够通过一个地址调用它。backend.py 中的 `@app.post('/api/generate')` 相当于给这个函数挂牌：“发往这个地址的 POST 请求，由我处理”。

- `photo: UploadFile = File(...)`：收到网页上传的照片；UploadFile 是有类型说明的文件对象。
- `prompt: str = Form('头部')`：收到表单里的字符串；没有值时默认“头部”。
- `FormData`：浏览器把文件与文字打包。
- `fetch('/api/generate', ...)`：网页发送 HTTP 请求。
- `subprocess.run([...])`：Python 启动官方推理脚本；跟你手动在终端输入命令一样。
- `FileResponse`：把生成的视频传回浏览器。
- `uvicorn backend:app`：启动服务器；backend 是文件名，app 是其中的 FastAPI 对象。

一次调用的路线：按钮 → FormData → HTTP POST → generate 函数 → LivePortrait → MP4 → 网页播放器。
先理解这一条路线，不必一开始就学习所有异步、数据库、登录、Docker 和微服务。

## 5. 四周学习路线（按验收结果推进）

1. **第 1 周：Python 与命令行。** 学函数、模块、Path、异常、pip、虚拟环境、subprocess。目标：自己运行 serve.py，并解释照片动画为什么不是真正 AI。做一个能检查文件是否存在的小程序。
2. **第 2 周：网页与 HTTP。** 学 HTML 的 input/button/video，JavaScript 事件、FormData、fetch，GET/POST 和状态码。目标：把网页按钮接到返回 `{ "message": "收到照片" }` 的接口，先不接模型。参考 FastAPI 官方 First Steps 和 Request Files。
3. **第 3 周：模型推理与联调。** 学权重、输入尺寸、CPU/GPU、推理与训练的区别。目标：先官方示例出 MP4，再自己的素材出 MP4，再通过本 demo 出 MP4。记录每次耗时、失败原因和素材质量；不需要训练模型。
4. **第 4 周：比赛作品。** 准备 3–5 个授权驱动视频，完成“点头/微笑/眨眼”动作模板选择；再做任务进度、失败提示、下载和演示素材。如果比赛必须支持自由提示词，这周先验证文本视频模型/API 是否满足效果与费用，再写适配器。

团队分工可按前端、Python/API、模型与素材、演示与测试安排；成员少则合并。不要四个人同时从训练模型开始。每周让所有人跑通一次完整流程。

## 6. 常见故障

- **Torch not compiled with CUDA / no NVIDIA driver**：Intel 机器必须加 --flag-force-cpu。装 CUDA 不能解决。
- **NumPy/onnxruntime 无法 import**：确认激活的是 Python 3.10 环境，并检查 `python -m pip show numpy onnxruntime`；基础依赖使用 numpy 1.26.4，不要擅自换 NumPy 2。
- **找不到 ffmpeg**：在当前激活环境运行 conda install -c conda-forge ffmpeg，然后用 ffmpeg -version 验证。ffmpeg-python 只是 Python 包，不代替 FFmpeg 程序。
- **找不到权重**：核对上面的完整目录，先在 LivePortrait 目录跑 inference.py。
- **没有检测到人脸**：换单人正脸、较清晰、无遮挡的照片；驱动视频第一帧保持正脸自然表情，避免多人、快速移动。
- **CPU 太慢**：缩短视频，关闭其他占内存程序；若仍无法满足演示，笔记本运行界面与 API，在有 NVIDIA GPU 的学校服务器或云环境运行模型。先用官方示例实测耗时和内存，再决定是否付费。
- **API 404/501/找不到模型**：打开 8766，不是 8765；检查 LIVEPORTRAIT_DIR；必须用模型环境的 python 启动 uvicorn。
- **API 500**：查看启动 uvicorn 的终端；本 demo 故意不把底层本机路径和错误日志返回网页。

## 7. 本次验证范围与来源

普通模式无需第三方 Python 包。模型调用入口按官方当前参数实现，但尚未安装权重，不能声称 AI 模式已实测成功。首次 CPU 运行可能还有官方 WIP 路径或依赖兼容问题。

核对日期：2026-10-14。安装方案在官方默认 GPU 步骤上做了 CPU 适配；官方后续版本改变依赖时，应重新核对。

- 官方仓库与安装说明：https://github.com/KlingTeam/LivePortrait
- CPU 与区域参数：https://github.com/KlingTeam/LivePortrait/blob/main/src/config/argument_config.py
- 设备选择：https://github.com/KlingTeam/LivePortrait/blob/main/src/live_portrait_wrapper.py
- CPU 人脸检测：https://github.com/KlingTeam/LivePortrait/blob/main/src/utils/cropper.py
- 基础依赖：https://github.com/KlingTeam/LivePortrait/blob/main/requirements_base.txt
- 权重：https://huggingface.co/KlingTeam/LivePortrait
- FastAPI 入门：https://fastapi.tiangolo.com/tutorial/first-steps/
- FastAPI 文件上传：https://fastapi.tiangolo.com/tutorial/request-files/

比赛展示时明确模型来自 LivePortrait，区分你们开发的交互、模板管理和服务功能与底层模型贡献。
