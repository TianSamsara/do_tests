#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取GitHub仓库题库信息"""

import urllib.request
import json

from urllib.parse import quote

# 设置代理
proxy = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)

# 获取仓库文件列表
resp = urllib.request.urlopen(
    'https://api.github.com/repos/TianSamsara/do_test_packet/contents',
    timeout=10
)
files = json.loads(resp.read().decode())

print("=" * 60)
print("GitHub仓库: TianSamsara/do_test_packet")
print("=" * 60)

for file in files:
    if file['type'] == 'file' and file['name'].endswith('.json'):
        name = file['name']
        size = file['size']
        
        # URL编码中文文件名
        encoded_name = quote(name, safe='')
        url = f"https://raw.githubusercontent.com/TianSamsara/do_test_packet/main/{encoded_name}"
        try:
            resp = urllib.request.urlopen(url, timeout=10)
            data = json.loads(resp.read().decode())
            
            questions = data.get('questions', [])
            question_count = len(questions)
            types = set(q.get('type', '') for q in questions)
            
            print(f"\n文件名: {name}")
            print(f"大小: {size:,} 字节")
            print(f"题目数: {question_count} 题")
            print(f"题型: {', '.join(sorted(types))}")
            
            # 提取题库名称（如果有）
            bank_name = data.get('name', name.replace('.json', ''))
            print(f"题库名: {bank_name}")
            
        except Exception as e:
            print(f"\n{name}: 读取失败 - {e}")

print("\n" + "=" * 60)
