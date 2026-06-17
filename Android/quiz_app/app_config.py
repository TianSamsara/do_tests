#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理模块
用于保存和加载用户设置、已安装题库信息等
"""

import os
import json


class AppConfig:
    """应用配置管理器"""
    
    def __init__(self):
        # 配置文件路径（在 quiz_app 目录下）
        self.config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.config_dir, 'app_config.json')
        
        # 默认配置
        self.default_config = {
            # GitHub 仓库地址
            'github_repo': '',
            
            # 已安装题库信息 {bank_id: {name, version, install_time, file}}
            'installed_banks': {},
            
            # 刷题界面颜色设置
            'quiz_colors': {
                'selected': [0.2, 0.6, 1.0, 1.0],    # 选项选中颜色（默认蓝色）
                'correct': [0.2, 0.8, 0.2, 1.0],     # 正确答案颜色（绿色）
                'wrong': [0.9, 0.3, 0.3, 1.0],       # 错误答案颜色（红色）
                'default': [0.7, 0.7, 0.7, 1.0]      # 默认选项颜色（灰色）
            }
        }
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有字段存在
                    merged = self.default_config.copy()
                    merged.update(config)
                    return merged
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_github_repo(self):
        """获取 GitHub 仓库地址"""
        return self.config.get('github_repo', '')
    
    def set_github_repo(self, repo_url):
        """设置 GitHub 仓库地址"""
        self.config['github_repo'] = repo_url
        return self._save_config()
    
    def get_installed_banks(self):
        """获取已安装题库字典"""
        return self.config.get('installed_banks', {})
    
    def add_installed_bank(self, bank_id, bank_info):
        """添加已安装题库记录
        
        Args:
            bank_id: 题库ID
            bank_info: 字典，包含 name, version, install_time, file
        """
        self.config['installed_banks'][bank_id] = bank_info
        return self._save_config()
    
    def remove_installed_bank(self, bank_id):
        """移除已安装题库记录
        
        Args:
            bank_id: 题库ID
            
        Returns:
            bool: 是否成功移除
        """
        if bank_id in self.config['installed_banks']:
            del self.config['installed_banks'][bank_id]
            return self._save_config()
        return False
    
    def is_bank_installed(self, bank_id):
        """检查题库是否已安装
        
        Args:
            bank_id: 题库ID
            
        Returns:
            bool: 是否已安装
        """
        return bank_id in self.config['installed_banks']
    
    def get_bank_version(self, bank_id):
        """获取已安装题库的版本号
        
        Args:
            bank_id: 题库ID
            
        Returns:
            str: 版本号，如果未安装返回空字符串
        """
        bank_info = self.config['installed_banks'].get(bank_id, {})
        return bank_info.get('version', '')
    
    def get_quiz_colors(self):
        """获取刷题界面颜色设置
        
        Returns:
            dict: 颜色配置字典
        """
        return self.config.get('quiz_colors', self.default_config['quiz_colors'])
    
    def set_quiz_color(self, color_key, rgba):
        """设置某个颜色
        
        Args:
            color_key: 颜色键名 ('selected', 'correct', 'wrong', 'default')
            rgba: [r, g, b, a] 颜色值列表
        """
        if 'quiz_colors' not in self.config:
            self.config['quiz_colors'] = self.default_config['quiz_colors'].copy()
        self.config['quiz_colors'][color_key] = rgba
        return self._save_config()
    
    def reset_quiz_colors(self):
        """重置刷题颜色为默认值"""
        self.config['quiz_colors'] = self.default_config['quiz_colors'].copy()
        return self._save_config()
