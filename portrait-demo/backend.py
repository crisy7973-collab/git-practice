"""真正的 AI 入口。必须从 LivePortrait 的 Python 环境启动，见 README。"""
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

app = FastAPI(title='人像动画教学 API')
ROOT = Path(__file__).parent
MODEL = Path(os.environ.get('LIVEPORTRAIT_DIR', str(ROOT / 'LivePortrait'))).resolve()
LOCK = threading.Lock()  # 教学版只允许一项推理，避免同时耗尽内存


def region_from_prompt(prompt: str) -> str:
    """只做明确的关键词映射，动作本身由驱动视频决定。"""
    for words, region in [('眼睛', 'eyes'), ('嘴', 'lip'), ('表情', 'exp'), ('头部', 'pose')]:
        if words in prompt:
            return region
    return 'all'


def save_upload(upload: UploadFile, target: Path, limit: int):
    total = 0
    with target.open('wb') as f:
        while chunk := upload.file.read(1024 * 1024):
            total += len(chunk)
            if total > limit:
                raise HTTPException(413, '文件过大：照片最多 20MB，视频最多 50MB。')
            f.write(chunk)
    if not total:
        raise HTTPException(400, '上传文件为空。')


@app.post('/api/generate')
def generate(photo: UploadFile = File(...), driving: UploadFile = File(...), prompt: str = Form('头部')):
    """收到文件 → 保存 → 调用模型 → 返回 MP4。同步函数由 FastAPI 放在线程执行。"""
    if not (MODEL / 'inference.py').is_file():
        raise HTTPException(503, '找不到 LivePortrait。请设置 LIVEPORTRAIT_DIR 并安装模型。')
    suffix = Path(photo.filename or '').suffix.lower()
    if suffix not in {'.jpg', '.jpeg', '.png', '.webp'} or Path(driving.filename or '').suffix.lower() != '.mp4':
        raise HTTPException(400, '照片请用 JPG/PNG/WebP，驱动视频请用 MP4。')
    if not LOCK.acquire(blocking=False):
        raise HTTPException(429, '已有视频正在生成，请稍后再试。')
    folder = tempfile.TemporaryDirectory(prefix='portrait-')
    try:
        job = Path(folder.name)
        source, driver, output = job / ('source' + suffix), job / 'driving.mp4', job / 'output'
        save_upload(photo, source, 20 * 1024 * 1024)
        save_upload(driving, driver, 50 * 1024 * 1024)
        command = [sys.executable, 'inference.py', '-s', str(source), '-d', str(driver),
                   '-o', str(output), '--flag-force-cpu', '--no-flag-use-half-precision',
                   '--flag-crop-driving-video', '--animation-region', region_from_prompt(prompt)]
        # 用参数列表，提示词不进入 shell。模型日志直接显示在启动终端。
        result = subprocess.run(command, cwd=MODEL, timeout=1800, check=False)
        if result.returncode:
            raise HTTPException(500, '模型推理失败。请查看终端日志，并先跑通官方示例。')
        videos = sorted(p for p in output.glob('*.mp4') if not p.stem.endswith('_concat'))
        if not videos:
            raise HTTPException(500, '模型没有产生 MP4，请查看终端日志。')
        return FileResponse(videos[0], media_type='video/mp4', filename='liveportrait.mp4',
                            background=BackgroundTask(folder.cleanup))
    except subprocess.TimeoutExpired:
        folder.cleanup()
        raise HTTPException(504, '推理超过 30 分钟，请缩短驱动视频或换 GPU。')
    except Exception:
        folder.cleanup()
        raise
    finally:
        LOCK.release()


# 最后挂载首页，避免 /api/generate 被静态文件路由覆盖。
app.mount('/', StaticFiles(directory=ROOT / 'web', html=True), name='web')
