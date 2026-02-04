import string
import zipfile
from io import BytesIO
from pathlib import Path
from typing import cast

import niquests as requests
from fontTools import subset

# ---------------- 配置 ----------------
MONO_FONT_NAME = 'cute-mono/retro-pixel-cute-mono.ttf.woff2'
PROP_FONT_NAME = 'ark-pixel-12px-proportional-zh_cn.ttf.woff2'
MONOSPACED_FONT_NAME = 'retro-pixel-font-ttf.woff2'
PROPORTIONAL_FONT_NAME = 'ark-pixel-font-12px-proportional-ttf.woff2'

TARGET_DIR = Path('static/fonts')

CONTENT_DIR = Path('content')
DATA_FILES = [Path('data/bili.json'), Path('data/x.json')]

GITHUB_API_RELEASES = 'https://api.github.com/repos/{name}/{repository}/releases/latest'


# ---------------- 下载函数 ----------------
def download_font(
    zip_name: str, font_name: str, repository: str, name: str = 'TakWolf'
):
    """下载最新 release 的字体并解压"""
    r = requests.get(GITHUB_API_RELEASES.format(repository=repository, name=name))
    r.raise_for_status()
    latest_tag = r.json()['tag_name']  # e.g., "2026.01.04"
    zip_name = f'{zip_name}-v{latest_tag}.zip'
    url = f'https://github.com/{name}/{repository}/releases/download/{latest_tag}/{zip_name}'
    resp = requests.get(url)
    resp.raise_for_status()
    with zipfile.ZipFile(BytesIO(cast(bytes, resp.content))) as z:
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
    chars.update('查看存档内容(包含 张图片)')
    return ''.join(chars)


# ---------------- 字体精简 ----------------
def subset_font(input_path: Path, text: str) -> int:
    options = subset.Options()
    options.flavor = 'woff2'
    options.with_zopfli = False
    options.desubroutinize = True
    options.notdef_glyph = True
    options.recalc_bounds = True
    options.recalc_timestamp = False

    # 1. 加载字体
    font = subset.load_font(str(input_path), options)

    # 2. 缺字检查逻辑
    # 获取字体支持的所有 Unicode 字符集合
    chars_in_font = set()
    for table in font['cmap'].tables:
        chars_in_font.update(table.cmap.keys())

    # 检查输入的 text 中哪些字不在字体里
    input_chars = set(ord(c) for c in text)
    missing_codes = input_chars - chars_in_font
    missing_chars = ''.join([chr(c) for c in missing_codes])

    if missing_chars:
        print(f'⚠️ 警告: 原字体中缺少以下字符: {missing_chars}')

    # 3. 执行子集化
    sub = subset.Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)

    # 4. 保存文件
    output_path = input_path.with_suffix(f'.{options.flavor}')
    font.save(str(output_path))

    # 5. 返回结果字典，包含文件大小和缺失字符
    return output_path.stat().st_size



mono_path, m_size = download_font(
    MONOSPACED_FONT_NAME, MONO_FONT_NAME, 'retro-pixel-font'
)
# prop_path, p_size = download_font(
#     PROPORTIONAL_FONT_NAME, PROP_FONT_NAME, 'ark-pixel-font'
# )
ZPIX = Path('./static/fonts/zpix-12px.ttf')
p_size = ZPIX.write_bytes(
    requests.get(
        'https://github.com/SolidZORO/zpix-pixel-font/releases/latest/download/zpix.ttf'
    ).content  # type: ignore
)
mono_path.move(mono_path.parent.parent / mono_path.name)
mono_path.parent.rmdir()
all_text = get_all_text()
# prop_size = subset_font(prop_path, all_text)
prop_size = subset_font(ZPIX, all_text)
print(f'字体压缩比例： {prop_size / p_size * 100:.2f}%')
ZPIX.unlink()