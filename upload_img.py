import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import BoundedSemaphore, Lock

from imagekitio import ImageKit

# --- 1. 配置区 ---
IMAGE_DIR = Path('static/images')
CONTENT_DIR = Path('content')
CACHE_FILE = Path('upload_cache.json')
MAX_CONCURRENT = 10  # 并发数控制

# 从环境变量获取配置
IK_PRIVATE_KEY = os.environ.get('IMAGEKIT_PRIVATE_KEY')
IK_URL_ENDPOINT = os.environ.get('IMAGEKIT_URL_ENDPOINT')
if IK_URL_ENDPOINT and not IK_URL_ENDPOINT.endswith('/'):
    IK_URL_ENDPOINT += '/'
# --- 2. 初始化 ---
ik = None
if IK_PRIVATE_KEY:
    ik = ImageKit(private_key=IK_PRIVATE_KEY)
rate_limiter = BoundedSemaphore(MAX_CONCURRENT)
cache_lock = Lock()


def load_cache()->dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with cache_lock:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)


# --- 3. 上传逻辑 ---
def upload_task(file_path: Path):
    with rate_limiter:
        while True:
            try:
                with open(file_path, 'rb') as f:
                    res = ik.files.upload(file=f, file_name=file_path.name)
                if res.file_id:
                    return file_path.name, res.name.removeprefix(
                        file_path.stem
                    ).removesuffix(file_path.suffix)
            except Exception as e:
                if '429' in str(e):
                    time.sleep(2)
                    continue
                raise e


# --- 4. Markdown 替换逻辑 ---
def process_markdowns(cache):
    # 正则匹配 ![alt](path)，捕获 path 部分
    # 兼容各种路径写法：../../static/images/xxx.png 或 /images/xxx.png
    img_regex = re.compile(r'!\[(.*?)\]\((?!https?://)(.*?)\)')
    md_files = list(CONTENT_DIR.rglob('*.md'))
    count = 0

    def replace_func(match):
        alt_text, img_path = match.groups()
        img_name = Path(img_path).name
        new_url = (
            IK_URL_ENDPOINT
            + str(Path(img_path).stem)
            + cache[img_name]
            + str(Path(img_path).suffix)
        )
        return f'![{alt_text}]({new_url})'

    for md_path in md_files:
        content = md_path.read_text(encoding='utf-8')
        result, _count = re.subn(img_regex, replace_func, content)
        if _count > 0:
            md_path.write_text(result, encoding='utf-8')
            print(f'📝 处理 {md_path.name}: 替换了 {_count} 处链接')
            count += _count
    return count


# --- 5. 主程序 ---
if not IK_URL_ENDPOINT:
    print('❌ 错误: 请先设置 IK_URL_ENDPOINT 环境变量')
    raise SystemExit(1)
# A. 上传阶段
cache = load_cache()
to_upload = [f for f in IMAGE_DIR.glob('*') if f.is_file() and f.name not in cache]

if to_upload and ik:
    print(f'🚀 正在上传 {len(to_upload)} 个新文件...')
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        results = list(executor.map(upload_task, to_upload))
        for res in results:
            if res:
                fname, furi = res
                cache[fname] = furi
    save_cache(cache)
else:
    print('✅ 没有新图片需要上传' if ik else '⚠️  未配置 ImageKit，跳过图片上传阶段，改为直接对已有进行替换。')
# B. 替换阶段
print('🔍 正在扫描 Markdown 并修正路径...')
count = process_markdowns(cache)
print(f'✨ 大功告成！本次共修正 {count} 处链接。')


