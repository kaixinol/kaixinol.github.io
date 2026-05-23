import re
from pathlib import Path

import tomlkit

# 建立 Shortcode 标记与需要引入的 CSS 文件名的映射关系
SHORTCODE_MAP = {
    r'\{\{\s*bilibili\(': 'bilibili',
    r'\{\{\s*gist\(': 'gist-dark',
    r'\{\{\s*(?:bili_dynamic|x)\(': 'dynamic',
}

CONTENT_DIR = Path('content')


def analyze_md_file(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Zola 的 Front-matter 是被 +++ 包裹的
    parts = content.split('+++', 2)
    if len(parts) < 3:
        return  # 格式不符合，跳过

    front_matter_str = parts[1]
    body_str = parts[2]

    # 1. 扫描正文，看触发了哪些 Shortcode
    needed_css = set()
    for pattern, css_name in SHORTCODE_MAP.items():
        if re.search(pattern, body_str):
            needed_css.add(css_name)

    if not needed_css:
        return  # 没有用到任何相关的 Shortcode，无需处理

    # 2. 解析 Front-matter
    try:
        doc = tomlkit.parse(front_matter_str)
    except Exception as e:
        print(f'[Error] 解析 TOML 失败 {file_path}: {e}')
        return

    # 确保 [extra] 块存在
    if 'extra' not in doc:
        doc['extra'] = tomlkit.table()

    extra_table = doc['extra']

    # 确保 use_css 数组存在
    if 'use_css' not in extra_table:
        extra_table['use_css'] = tomlkit.array()

    current_css_list = extra_table['use_css']

    # 3. 对比并追加漏掉的 CSS
    has_changed = False
    for css in sorted(needed_css):
        if css not in current_css_list:
            current_css_list.append(css)
            has_changed = True

    # 4. 如果有变动，写回文件（完美保留原有格式）
    if has_changed:
        new_front_matter = tomlkit.dumps(doc)
        # 重新拼接并写入，剥离 dumps 自动生成的尾部换行带来的影响
        new_content = f'+++\n{new_front_matter.strip()}\n+++{parts[2]}'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'[Updated] {file_path} -> Added CSS: {list(needed_css)}')


if not CONTENT_DIR.exists():
    print(f'[Error] 未找到 {CONTENT_DIR} 目录，请在 Zola 项目根目录下运行此脚本。')

print('开始扫描 content 目录下的 Markdown 文件...')
for md_file in CONTENT_DIR.rglob('*.md'):
    analyze_md_file(md_file)
print('扫描完成！')

