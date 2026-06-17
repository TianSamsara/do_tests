import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.config import Config
from kivy.core.text import LabelBase

# 配置中文字体
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '700')
Config.set('kivy', 'keyboard_mode', 'system')

# 注册中文字体（支持多平台）
try:
    import platform
    system = platform.system()
    
    if system == 'Windows':
        # Windows系统常见中文字体路径
        font_paths = [
            'C:/Windows/Fonts/simhei.ttf',  # 黑体
            'C:/Windows/Fonts/msyh.ttc',     # 微软雅黑
            'C:/Windows/Fonts/simsun.ttc',   # 宋体
        ]
    elif system == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',  # 苹方
            '/Library/Fonts/Arial Unicode.ttf',
        ]
    elif system == 'Linux':
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # 文泉驿正黑
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
        ]
    else:  # Android / iOS
        # Android/iOS 使用系统默认字体，Kivy 会自动处理
        # 如果需要自定义字体，将字体文件放在项目目录并引用相对路径
        font_paths = []
    
    font_loaded = False
    loaded_font_path = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            LabelBase.register(name='chinese', fn_regular=font_path)
            print(f"使用中文字体: {font_path}")
            font_loaded = True
            loaded_font_path = font_path
            break
    
    if not font_loaded:
        # 如果找不到字体，尝试使用 Kivy 内置的 Droid Sans Fallback
        try:
            from kivy.resources import resource_find
            fallback_font = resource_find('data/fonts/DroidSansFallback.ttf')
            if fallback_font and os.path.exists(fallback_font):
                LabelBase.register(name='chinese', fn_regular=fallback_font)
                print(f"使用 Kivy 内置字体: {fallback_font}")
                font_loaded = True
                loaded_font_path = fallback_font
            else:
                print("警告: 未找到中文字体，中文可能显示为方块")
        except Exception as e:
            print(f"字体加载失败: {e}")
    
    # 同时将中文字体注册为Kivy默认字体名（Roboto），
    # 确保Popup标题等未显式设置font_name的组件也能正常显示中文
    if loaded_font_path:
        LabelBase.register(name='Roboto', fn_regular=loaded_font_path)
        print(f"已设置默认中文字体（Roboto回退）")
    
    # Android 特殊处理：如果没有加载到字体，使用系统默认
    if not font_loaded and system not in ['Windows', 'Darwin', 'Linux']:
        print("Android/iOS 环境：使用系统默认字体")
        # Kivy 在 Android 上会自动使用系统字体，无需额外配置
        # 只需确保所有 Label 都使用 font_name='chinese'，Kivy 会回退到系统字体
            
except Exception as e:
    print(f"字体配置失败: {e}")

from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.quiz_screen import QuizScreen
from screens.review_screen import ReviewScreen
from screens.profile_screen import ProfileScreen
from database import Database


class QuizApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.current_bank = None
        self.db = Database()

    def build(self):
        Window.clearcolor = (0.96, 0.96, 0.96, 1)

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(QuizScreen(name='quiz'))
        sm.add_widget(ReviewScreen(name='review'))
        sm.add_widget(ProfileScreen(name='profile'))

        return sm

    def on_stop(self):
        if hasattr(self, 'db'):
            self.db.close()


if __name__ == '__main__':
    QuizApp().run()

