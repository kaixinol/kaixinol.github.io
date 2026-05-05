import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import BoundedSemaphore, Lock

IS_CI = os.environ.get('CI') == 'true'

if not IS_CI:
    from imagekitio import ImageKit

IMAGE_DIR = Path('static/images')
CONTENT_DIR = Path('content')
CACHE_FILE = Path('upload_cache.json')
MAX_CONCURRENT = 10  # 并发数控制
IS_CI = os.environ.get('CI') == 'true'

# ImageKit 配置
IK_URL_ENDPOINT = 'https://ik.imagekit.io/kaesinol/'
IK_PRIVATE_KEY = os.environ.get('IK_PRIVATE_KEY')
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


cache = load_cache()
to_upload = [f for f in IMAGE_DIR.glob('*') if f.is_file() and f.name not in cache]

if IS_CI:
    # CI 模式：只替换，不上传
    if to_upload:
        print(f'❌ CI 错误: 检测到 {len(to_upload)} 个新图片未上传:')
        for f in to_upload:
            print(f'   - {f.name}')
        print('请先在本地运行 upload_img.py 上传图片后重新提交')
        sys.exit(1)
    print('🔍 CI 模式：正在扫描 Markdown 并替换链接...')
    count = process_markdowns(cache)
    print(f'✨ 大功告成！本次共修正 {count} 处链接。')
else:
    # 本地模式：只上传 + 改 cache，不替换
    if to_upload:
        if not IK_PRIVATE_KEY:
            print('❌ 错误: 本地模式需要 IK_PRIVATE_KEY 才能上传图片')
            sys.exit(1)
        print(f'🚀 正在上传 {len(to_upload)} 个新文件...')
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
            results = list(executor.map(upload_task, to_upload))
            for res in results:
                if res:
                    fname, furi = res
                    cache[fname] = furi
        save_cache(cache)
        print(f'✅ 上传完成，已更新 cache（{len(to_upload)} 个文件）')
    else:
        print('✅ 没有新图片需要上传')


