import json
import os
import re
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import TypedDict

import niquests as requests

# X (Twitter) 通用 Header
X_HEADERS = {
    'User-Agent': 'KaesinolBlogSpider/1.0 (+https://github.com/kaixinol)',
    'Referer': 'https://www.google.com/',
}

BILI_HEADERS = X_HEADERS | {
    'Referer': 'https://www.bilibili.com/',
}
print(BILI_HEADERS)
def format_date(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


def wrap_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ident = args[0] if args else ''
            print(f'[{func.__name__}] 错误: {ident} -> {e}')
            return None
    return wrapper


@wrap_errors
def get_bilibili_data(b_id):
    api = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={b_id}'
    # 使用 BILI_HEADERS
    resp = requests.get(api, headers=BILI_HEADERS, timeout=10).json()
    if resp.get('code') != 0:
        return None

    data_card = resp['data']['card']
    inner_card = json.loads(data_card['card'])
    ts = data_card['desc']['timestamp']

    user = inner_card['author']['name'] if 'author' in inner_card else inner_card['user']['name']
    uid = inner_card['author']['mid'] if 'author' in inner_card else inner_card['user']['uid']
    content = (
        inner_card['summary'] if 'summary' in inner_card
        else inner_card['item']['description']
    )

    # --- 图片提取逻辑 ---
    images: list[str] = []
    if 'item' in inner_card and 'pictures' in inner_card['item']:
        images = [p['img_src']+"@1024w1024h_70q.avif" for p in inner_card['item']['pictures']]
    if 'origin' in inner_card:
            origin_json = json.loads(inner_card['origin'])
            orig_user = (
                inner_card
                .get('origin_user', {})
                .get('info', {})
                .get('uname', '未知')
            )
            orig_content = (
                origin_json.get('dynamic')
                or origin_json.get('item', {}).get('content')
                or origin_json.get('title')
                or ''
            )
            content += f' // @{orig_user}: {orig_content}'

            if not images:
                if 'item' in origin_json and 'pictures' in origin_json['item']:
                    images = [p['img_src'] for p in origin_json['item']['pictures']]
                elif 'pic' in origin_json:
                    images = [origin_json['pic']]

    return {
        'user': user,
        'face': inner_card['author']['face']
        if 'author' in inner_card
        else inner_card['user']['head_url'],
        'text': content,
        'images': [image.replace('http:', 'https:') for image in images],
        'date': format_date(ts),
        'link': f'https://bilibili.com/opus/{b_id}',
        'user_link': f'https://space.bilibili.com/{uid}',
    }


@wrap_errors
def get_x_data(x_id):
    api = f'https://api.fxtwitter.com/i/status/{x_id}'
    # 使用 X_HEADERS
    resp = requests.get(api, headers=X_HEADERS, timeout=10).json()
    t = resp['tweet']
    dt = datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S %z %Y')

    images = []
    if 'media' in t and 'photos' in t['media']:
        images = [p['url'].replace('orig','medium') for p in t['media']['photos']]

    return {
        'user': t['author']['name'],
        'screen_name': t['author']['screen_name'],
        'face': t['author']['avatar_url'],
        'text': t['text'],
        'images': images,
        'date': dt.strftime('%Y-%m-%d %H:%M'),
        'link': f'https://x.com/i/status/{x_id}',
        'user_link': f'https://x.com/{t["author"]["screen_name"]}',
    }

class PlatformConfig(TypedDict):
    pattern: str
    fetcher: Callable[..., object]
    file: str


def main():
    print('>>> 开始扫描 Markdown 文件...')
    os.makedirs('data', exist_ok=True)

    platforms: dict[str, PlatformConfig] = {
        'bili': {
            'pattern': r'bili_dynamic\(id="(\d+)"',
            'fetcher': get_bilibili_data,
            'file': 'data/bili.json',
        },
        'x': {
            'pattern': r'x\(id="(\d+)"',
            'fetcher': get_x_data,
            'file': 'data/x.json',
        },
    }

    for name, p_info in platforms.items():
        # 1. 初始化 ID 集合
        all_found_ids = set()

        # 2. 从 Markdown 中提取所有 ID
        for root, _, files in os.walk('content'):
            for file in files:
                if file.endswith('.md'):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        all_found_ids.update(re.findall(p_info['pattern'], f.read()))

        # 3. 读取现有 JSON 数据（如果存在）
        existing_data = {}
        if os.path.exists(p_info['file']):
            try:
                with open(p_info['file'], 'r', encoding='utf-8') as f:
                    existing_data = json.load(f) or {}
            except json.JSONDecodeError:
                existing_data = {}

        # 4. 过滤：只抓取不存在于现有 JSON 中的 ID
        new_ids = [i for i in all_found_ids if i not in existing_data]

        if not new_ids:
            print(f'[{name.upper()}] 没有新 ID 需要抓取。')
        else:
            print(f'[{name.upper()}] 发现 {len(new_ids)} 个新 ID，开始抓取...')
            for item_id in new_ids:
                data = p_info['fetcher'](item_id)
                if data:
                    existing_data[item_id] = data
                else:
                    print(f'[{name.upper()}] 获取失败: {item_id}')

            # 5. 写回文件（包含旧数据和新抓取的数据）
            with open(p_info['file'], 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, separators=(',', ':'))

    print('\n>>> 同步任务结束!')
main()