"""
UI工具模块 - 提供统一的UI组件创建方法
"""
from kivy.uix.label import Label
from kivy.metrics import dp


def create_label(text='', font_size=16, **kwargs):
    """
    创建支持中文的Label
    
    Args:
        text: 文本内容
        font_size: 字体大小（dp单位）
        **kwargs: 其他Label参数
    
    Returns:
        Label实例
    """
    label = Label(
        text=text,
        font_size=dp(font_size),
        font_name='chinese',  # 使用中文字体
        **kwargs
    )
    return label


def create_button(text='', font_size=18, **kwargs):
    """
    创建按钮（自动设置中文字体）
    
    Args:
        text: 按钮文本
        font_size: 字体大小
        **kwargs: 其他Button参数
    
    Returns:
        Button实例
    """
    from kivy.uix.button import Button
    
    button = Button(
        text=text,
        font_size=dp(font_size),
        **kwargs
    )
    # Kivy的Button内部使用Label，会自动继承font_name
    return button
