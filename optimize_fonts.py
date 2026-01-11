import string
import zipfile
from io import BytesIO
from pathlib import Path

import requests
from fontTools import subset

# ---------------- 配置 ----------------
MONO_FONT_NAME = 'cute-mono/retro-pixel-cute-mono.ttf.woff2'
PROP_FONT_NAME = 'ark-pixel-12px-proportional-zh_cn.ttf.woff2'
MONOSPACED_FONT_NAME = 'retro-pixel-font-ttf.woff2'
PROPORTIONAL_FONT_NAME = 'ark-pixel-font-12px-proportional-ttf.woff2'

TARGET_DIR = Path('static/fonts')

CONTENT_DIR = Path('content')
DATA_FILES = [Path('data/bili.json'), Path('data/x.json')]

GITHUB_API_RELEASES = (
    'https://api.github.com/repos/TakWolf/{repository}/releases/latest'
)


# ---------------- 下载函数 ----------------
def download_font(zip_name: str, font_name: str,repository: str):
    """下载最新 release 的字体并解压"""
    r = requests.get(GITHUB_API_RELEASES.format(repository=repository))
    r.raise_for_status()
    latest_tag = r.json()['tag_name']  # e.g., "2026.01.04"
    zip_name = f'{zip_name}-v{latest_tag}.zip'
    url = f'https://github.com/TakWolf/{repository}/releases/download/{latest_tag}/{zip_name}'
    print(f'Downloading {url} ...')

    resp = requests.get(url)
    resp.raise_for_status()
    resp=resp.content
    with zipfile.ZipFile(BytesIO(resp)) as z:
        with z.open(font_name) as font_file:
            target_path = TARGET_DIR / font_name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, 'wb') as f_out:
                f_out.write(font_file.read())
            return target_path, target_path.stat().st_size


# ---------------- 文本收集 ----------------
def get_all_text():
    """收集博客中出现的所有文本"""
    chars = set()
    if CONTENT_DIR.exists():
        for md_file in CONTENT_DIR.rglob('*.md'):
            chars.update(md_file.read_text(encoding='utf-8'))
    for data_path in DATA_FILES:
        if data_path.exists():
            chars.update(data_path.read_text(encoding='utf-8'))
    # 基础可打印字符
    chars.update(c for c in string.printable if c.isprintable())
    return ''.join(chars)


# ---------------- 字体精简 ----------------
def subset_font(input_path: Path, text: str):
    options = subset.Options()
    options.flavor = 'woff2'
    options.with_zopfli = False
    options.desubroutinize = True
    options.notdef_glyph = True
    options.recalc_bounds = True
    options.recalc_timestamp = False

    font = subset.load_font(str(input_path), options)

    sub = subset.Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)
    font.save(str(input_path))
    print(f'Subset font saved to {input_path}')
    return input_path.stat().st_size

mono_path,m_size = download_font(MONOSPACED_FONT_NAME, MONO_FONT_NAME,'retro-pixel-font')
prop_path,p_size = download_font(PROPORTIONAL_FONT_NAME, PROP_FONT_NAME,'ark-pixel-font')
mono_path.move(mono_path.parent.parent / mono_path.name)
mono_path.parent.rmdir()
all_text = get_all_text()
prop_size = subset_font(
    prop_path, all_text
)
print(f"字体压缩比例： {prop_size / p_size * 100:.2f}%")
