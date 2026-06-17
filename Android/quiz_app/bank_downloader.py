#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库下载模块
支持代理联网下载，从GitHub仓库获取题库
GitHub仓库：https://github.com/TianSamsara/do_test_packet
"""

import os
import json
import urllib.request
import urllib.error
import threading
import hashlib
from urllib.parse import quote, urlparse, urlunparse


class BankInfo:
    """题库信息类"""

    def __init__(self, bank_id, name, description, version, download_url,
                 size=0, question_count=0, types=None, checksum=""):
        self.bank_id = bank_id
        self.name = name
        self.description = description
        self.version = version
        self.download_url = download_url
        self.size = size
        self.question_count = question_count
        self.types = types or []
        self.checksum = checksum
        self.installed = False
        self.local_version = ""


class BankDownloader:
    """题库下载管理器"""

    def __init__(self):
        # 代理配置
        self.use_proxy = False
        self.proxy_address = "127.0.0.1:7890"
        # 可用题库列表
        self.available_banks = []
        # 已安装题库信息（从配置文件加载）
        from app_config import AppConfig
        self.app_config = AppConfig()
        self.installed_banks = self.app_config.get_installed_banks()
        # 下载状态
        self.downloading = False
        # 进度回调
        self.progress_callback = None
        self.status_callback = None

    def get_proxy_handler(self):
        """获取代理处理器"""
        if self.use_proxy and self.proxy_address:
            proxies = {
                'http': f'http://{self.proxy_address}',
                'https': f'http://{self.proxy_address}'
            }
            return urllib.request.ProxyHandler(proxies)
        return None

    def create_opener(self):
        """创建支持代理的urllib opener"""
        handlers = []
        proxy_handler = self.get_proxy_handler()
        if proxy_handler:
            handlers.append(proxy_handler)
        handlers.append(urllib.request.HTTPSHandler())
        return urllib.request.build_opener(*handlers)

    def _encode_url(self, url):
        """对URL路径进行编码，支持中文文件名
        如果URL已经包含编码字符（%XX），则不再重复编码
        """
        parsed = urlparse(url)
        path = parsed.path
        
        # 检查路径是否已经URL编码（包含%XX格式）
        if '%' in path:
            # 已经编码过，直接返回原URL
            return url
        
        # 未编码，对路径中的非ASCII字符进行编码
        encoded_path = quote(path, safe='/')
        return urlunparse((
            parsed.scheme, parsed.netloc, encoded_path,
            parsed.params, parsed.query, parsed.fragment
        ))

    def fetch_catalog(self, catalog_url, callback=None):
        """异步获取题库清单
        Args:
            catalog_url: bank_catalog.json 的 raw 直链地址
            callback: 回调函数 callback(success, data)
        """
        def _fetch():
            try:
                opener = self.create_opener()
                urllib.request.install_opener(opener)

                req = urllib.request.Request(
                    catalog_url,
                    headers={'User-Agent': 'QuizApp/1.0'}
                )
                response = urllib.request.urlopen(req, timeout=15)
                data = response.read().decode('utf-8')
                catalog = json.loads(data)

                self.available_banks = []
                for bank_data in catalog.get("banks", []):
                    info = BankInfo(
                        bank_id=bank_data.get("id", ""),
                        name=bank_data.get("name", "未知题库"),
                        description=bank_data.get("description", ""),
                        version=bank_data.get("version", "1.0.0"),
                        download_url=bank_data.get("download_url", ""),
                        size=bank_data.get("size", 0),
                        question_count=bank_data.get("question_count", 0),
                        types=bank_data.get("types", []),
                        checksum=bank_data.get("checksum", "")
                    )
                    # 检查是否已安装
                    info.installed = bank_data.get("id", "") in self.installed_banks
                    info.local_version = self.installed_banks.get(
                        bank_data.get("id", ""), {}
                    ).get("version", "")
                    self.available_banks.append(info)

                # 恢复默认opener
                urllib.request.install_opener(urllib.request.build_opener())

                if callback:
                    callback(True, self.available_banks)

            except urllib.error.URLError as e:
                error_msg = (
                    f"无法连接题库服务器：{str(e)}\n\n"
                    "如果在中国大陆，请在'代理设置'中配置代理。"
                )
                if callback:
                    callback(False, error_msg)
                urllib.request.install_opener(urllib.request.build_opener())
            except json.JSONDecodeError:
                if callback:
                    callback(False, "题库清单格式错误！")
                urllib.request.install_opener(urllib.request.build_opener())
            except Exception as e:
                if callback:
                    callback(False, f"获取题库列表失败：{str(e)}")
                urllib.request.install_opener(urllib.request.build_opener())

        thread = threading.Thread(target=_fetch)
        thread.daemon = True
        thread.start()

    def download_bank(self, bank_info, save_dir, progress_callback=None,
                      complete_callback=None):
        """异步下载单个题库文件"""
        if self.downloading:
            if complete_callback:
                complete_callback(False, "已有下载任务正在进行中！")
            return

        self.downloading = True

        def _download():
            try:
                # 确保目录存在
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                # 生成安全文件名
                safe_name = bank_info.name.replace('/', '_').replace('\\', '_')
                file_path = os.path.join(save_dir, f'{safe_name}.json')

                # 编码URL
                encoded_url = self._encode_url(bank_info.download_url)

                # 创建支持代理的opener
                opener = self.create_opener()
                urllib.request.install_opener(opener)

                def report_progress(block_num, block_size, total_size):
                    """下载进度回调"""
                    downloaded = block_num * block_size
                    if total_size > 0:
                        percent = min(100, (downloaded / total_size) * 100)
                        if progress_callback:
                            progress_callback(percent, downloaded, total_size)

                if progress_callback:
                    progress_callback(0, 0, bank_info.size)

                # 下载文件
                urllib.request.urlretrieve(
                    encoded_url, file_path, reporthook=report_progress
                )

                # 恢复默认opener
                urllib.request.install_opener(urllib.request.build_opener())

                # 校验文件（如果有checksum）
                if bank_info.checksum:
                    if not self._verify_checksum(file_path, bank_info.checksum):
                        os.remove(file_path)
                        raise Exception("文件校验失败，下载的文件可能已损坏！")

                # 记录已安装信息（保存到配置文件）
                bank_info_dict = {
                    "name": bank_info.name,
                    "version": bank_info.version,
                    "install_time": self._get_current_time(),
                    "file": f'{safe_name}.json'
                }
                self.installed_banks[bank_info.bank_id] = bank_info_dict
                self.app_config.add_installed_bank(bank_info.bank_id, bank_info_dict)

                if complete_callback:
                    complete_callback(True, file_path)

            except Exception as e:
                # 清理可能不完整的文件
                if 'file_path' in locals() and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass

                if complete_callback:
                    complete_callback(False, str(e))
                urllib.request.install_opener(urllib.request.build_opener())
            finally:
                self.downloading = False

        thread = threading.Thread(target=_download)
        thread.daemon = True
        thread.start()

    def _verify_checksum(self, file_path, expected_checksum):
        """验证文件SHA256校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        actual = sha256_hash.hexdigest()
        return actual.lower() == expected_checksum.lower()

    def _get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "未知"
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        size = float(size_bytes)
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        return f"{size:.2f} {units[unit_index]}"

    def remove_installed_bank(self, bank_id):
        """移除已安装题库记录（当用户手动删除题库文件时调用）
        
        Args:
            bank_id: 题库ID
            
        Returns:
            bool: 是否成功移除
        """
        if self.app_config.remove_installed_bank(bank_id):
            # 同步更新内存中的字典
            if bank_id in self.installed_banks:
                del self.installed_banks[bank_id]
            return True
        return False

    def test_proxy(self, callback=None):
        """测试代理连接"""
        if not self.use_proxy or not self.proxy_address:
            if callback:
                callback(False, "请先启用代理并填写代理地址！")
            return

        def _test():
            try:
                opener = self.create_opener()
                urllib.request.install_opener(opener)

                req = urllib.request.Request(
                    'https://raw.githubusercontent.com',
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                urllib.request.urlopen(req, timeout=8)

                urllib.request.install_opener(urllib.request.build_opener())
                if callback:
                    callback(True, f"代理连接成功！\n{self.proxy_address}")
            except Exception as e:
                urllib.request.install_opener(urllib.request.build_opener())
                if callback:
                    callback(False, f"代理测试失败：{str(e)}")

        thread = threading.Thread(target=_test)
        thread.daemon = True
        thread.start()
