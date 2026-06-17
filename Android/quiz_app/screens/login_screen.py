from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.metrics import dp


class ChineseSpinnerOption(SpinnerOption):
    """自定义Spinner选项，强制使用中文字体，避免下拉菜单乱码"""
    font_name = 'chinese'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10)
        )

        # 标题
        from kivy.uix.label import Label
        title = Label(
            text='刷题系统',
            font_name='chinese',
            font_size=dp(32),
            bold=True,
            size_hint_y=0.2
        )
        main_layout.add_widget(title)

        # 输入框容器
        input_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=0.4
        )

        # 用户名输入框
        from kivy.uix.textinput import TextInput
        self.username_input = TextInput(
            hint_text='请输入用户名',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_name='chinese',
            font_size=dp(18),
            padding=[dp(10), dp(10)]
        )
        input_container.add_widget(self.username_input)

        # 用户列表
        self.user_spinner = Spinner(
            text='选择用户',
            values=['请选择'],
            option_cls=ChineseSpinnerOption,
            size_hint_y=None,
            height=dp(50),
            font_name='chinese',
            font_size=dp(18)
        )
        self.refresh_users()
        input_container.add_widget(self.user_spinner)

        main_layout.add_widget(input_container)

        # 按钮容器
        button_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=0.4
        )

        # 登录按钮
        login_btn = Button(
            text='登录',
            size_hint_y=None,
            height=dp(50),
            font_name='chinese',
            font_size=dp(20),
            background_color=(0.2, 0.6, 1, 1)
        )
        login_btn.bind(on_press=self.login)
        button_container.add_widget(login_btn)

        # 注册按钮
        register_btn = Button(
            text='注册',
            size_hint_y=None,
            height=dp(50),
            font_name='chinese',
            font_size=dp(20),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        register_btn.bind(on_press=self.register)
        button_container.add_widget(register_btn)

        # 刷新按钮
        refresh_btn = Button(
            text='刷新用户列表',
            size_hint_y=None,
            height=dp(50),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.8, 0.6, 0.2, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.refresh_users())
        button_container.add_widget(refresh_btn)

        # 删除用户按钮
        delete_btn = Button(
            text='删除选中用户',
            size_hint_y=None,
            height=dp(50),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.9, 0.3, 0.3, 1)
        )
        delete_btn.bind(on_press=self.delete_selected_user)
        button_container.add_widget(delete_btn)

        main_layout.add_widget(button_container)
        
        # 将主布局添加到Screen
        self.add_widget(main_layout)

    def refresh_users(self, *args):
        """刷新用户列表"""
        app = self.get_app()
        users = app.db.get_all_users()
        user_names = [u[1] for u in users]
        if not user_names:
            user_names = ['请先注册']
        self.user_spinner.values = ['请选择'] + user_names

    def login(self, instance):
        """登录"""
        # 优先使用Spinner选择的值，如果没有选择则使用输入框的值
        selected_user = self.user_spinner.text
        username = self.username_input.text.strip()
        
        # 如果选择了用户（不是"请选择"），使用选择的值
        if selected_user and selected_user != '请选择' and selected_user != '请先注册':
            username = selected_user
        
        if not username:
            self.show_error('请输入用户名或选择一个用户')
            return

        app = self.get_app()
        user = app.db.get_user(username)

        if user:
            app.current_user = user
            self.manager.current = 'main'
            self.username_input.text = ''
        else:
            self.show_error('用户不存在，请先注册')

    def register(self, instance):
        """注册"""
        username = self.username_input.text.strip()

        if not username:
            self.show_error('请输入用户名')
            return

        app = self.get_app()
        success = app.db.add_user(username)

        if success:
            self.show_success(f'用户 {username} 注册成功')
            self.refresh_users()
            self.username_input.text = ''
        else:
            self.show_error('用户名已存在')

    def show_error(self, message):
        """显示错误提示"""
        popup = Popup(
            title='错误',
            content=Label(text=message, font_name='chinese', font_size=dp(18)),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def show_success(self, message):
        """显示成功提示"""
        popup = Popup(
            title='成功',
            content=Label(text=message, font_name='chinese', font_size=dp(18)),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def delete_selected_user(self, instance):
        """删除选中的用户"""
        selected_user = self.user_spinner.text
        
        # 检查是否选择了有效的用户
        if not selected_user or selected_user in ['请选择', '请先注册']:
            self.show_error('请先选择一个要删除的用户')
            return
        
        app = self.get_app()
        user = app.db.get_user(selected_user)
        
        if not user:
            self.show_error('用户不存在')
            return
        
        # 确认删除对话框
        confirm_content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        confirm_label = Label(
            text=f'确定要删除用户 "{selected_user}" 吗？\n所有相关数据将被永久删除！',
            font_name='chinese',
            font_size=dp(16),
            color=(0.9, 0.3, 0.3, 1)
        )
        confirm_content.add_widget(confirm_label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        cancel_btn = Button(text='取消', font_name='chinese', background_color=(0.6, 0.6, 0.6, 1))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        confirm_delete_btn = Button(text='确定删除', font_name='chinese', background_color=(0.9, 0.3, 0.3, 1))
        
        def do_delete(instance):
            app.db.delete_user(user[0])
            popup.dismiss()
            self.show_success(f'用户 "{selected_user}" 已删除')
            self.refresh_users()
            self.username_input.text = ''
        
        confirm_delete_btn.bind(on_press=do_delete)
        btn_layout.add_widget(confirm_delete_btn)
        
        confirm_content.add_widget(btn_layout)
        
        popup = Popup(title='确认删除', content=confirm_content, size_hint=(0.8, 0.4))
        popup.open()

    def get_app(self):
        """获取App实例"""
        from kivy.app import App
        return App.get_running_app()
