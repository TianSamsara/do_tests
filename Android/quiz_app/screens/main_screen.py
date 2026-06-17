from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from bank_downloader import BankDownloader


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 题库下载器
        self.downloader = BankDownloader()
        
        # 创建主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )

        # 顶部信息栏
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        self.user_label = Label(
            text='用户: ',
            font_name='chinese',
            font_size=dp(16),
            halign='left',
            size_hint_x=0.6
        )
        top_bar.add_widget(self.user_label)

        logout_btn = Button(
            text='退出',
            size_hint_x=0.4,
            font_name='chinese',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        logout_btn.bind(on_press=self.logout)
        top_bar.add_widget(logout_btn)

        main_layout.add_widget(top_bar)

        # 题库列表标题
        bank_title = Label(
            text='题库列表',
            font_name='chinese',
            font_size=dp(22),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        main_layout.add_widget(bank_title)

        # 题库滚动列表
        scroll = ScrollView(size_hint_y=0.55)
        self.bank_list = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        self.bank_list.bind(minimum_height=self.bank_list.setter('height'))
        scroll.add_widget(self.bank_list)
        main_layout.add_widget(scroll)

        # 操作按钮区域
        button_area = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint_y=0.3
        )

        # 开始刷题按钮
        start_btn = Button(
            text='开始刷题',
            size_hint_y=None,
            height=dp(42),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.2, 0.6, 1, 1)
        )
        start_btn.bind(on_press=self.start_quiz)
        button_area.add_widget(start_btn)

        # 下载题库按钮
        download_btn = Button(
            text='下载题库',
            size_hint_y=None,
            height=dp(42),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.2, 0.7, 0.7, 1)
        )
        download_btn.bind(on_press=self.show_bank_downloader)
        button_area.add_widget(download_btn)

        # 导入题库按钮
        import_btn = Button(
            text='导入题库',
            size_hint_y=None,
            height=dp(42),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        import_btn.bind(on_press=self.import_bank)
        button_area.add_widget(import_btn)

        # 复习模式按钮
        review_btn = Button(
            text='复习模式',
            size_hint_y=None,
            height=dp(42),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.8, 0.6, 0.2, 1)
        )
        review_btn.bind(on_press=self.open_review)
        button_area.add_widget(review_btn)
        
        # 个人中心按钮
        profile_btn = Button(
            text='个人中心',
            size_hint_y=None,
            height=dp(42),
            font_name='chinese',
            font_size=dp(18),
            background_color=(0.6, 0.3, 0.8, 1)
        )
        profile_btn.bind(on_press=self.open_profile)
        button_area.add_widget(profile_btn)

        main_layout.add_widget(button_area)
        
        # 将主布局添加到Screen
        self.add_widget(main_layout)

    def on_enter(self):
        """进入屏幕时刷新信息"""
        self.refresh_info()

    def refresh_info(self):
        """刷新用户信息和题库列表"""
        app = self.get_app()
        
        if app.current_user:
            self.user_label.text = f"用户: {app.current_user[1]}"

        # 刷新题库列表
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        banks = bank_manager.list_banks()

        self.bank_list.clear_widgets()

        if not banks:
            no_data = Label(
                text='暂无题库，请导入题库文件',
                font_name='chinese',
                font_size=dp(16),
                size_hint_y=None,
                height=dp(40)
            )
            self.bank_list.add_widget(no_data)
        else:
            for bank_name in banks:
                # 创建包含按钮和删除图标的布局
                bank_item = BoxLayout(
                    orientation='horizontal',
                    spacing=dp(5),
                    size_hint_y=None,
                    height=dp(50)
                )
                
                btn = Button(
                    text=bank_name,
                    size_hint_x=0.85,
                    font_name='chinese',
                    font_size=dp(18)
                )
                btn.bind(on_press=lambda instance, name=bank_name: self.select_bank(name))
                bank_item.add_widget(btn)
                
                # 删除按钮
                delete_btn = Button(
                    text='×',
                    size_hint_x=0.15,
                    font_name='chinese',
                    font_size=dp(24),
                    background_color=(0.9, 0.3, 0.3, 1),
                    color=(1, 1, 1, 1)
                )
                delete_btn.bind(on_press=lambda instance, name=bank_name: self.delete_bank(name))
                bank_item.add_widget(delete_btn)
                
                self.bank_list.add_widget(bank_item)

    def select_bank(self, bank_name):
        """选择题库"""
        app = self.get_app()
        app.current_bank = bank_name
        
        popup = Popup(
            title='提示',
            content=Label(text=f'已选择题库: {bank_name}', font_name='chinese', font_size=dp(18)),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        
        # 自动关闭popup
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def delete_bank(self, bank_name):
        """删除题库"""
        # 确认删除对话框
        confirm_content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        confirm_label = Label(
            text=f'确定要删除题库 "{bank_name}" 吗？\n所有题目数据将被永久删除！',
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
            from question_bank import QuestionBankManager
            bank_manager = QuestionBankManager()
            success = bank_manager.delete_bank(bank_name)
            popup.dismiss()
            
            if success:
                self.show_success(f'题库 "{bank_name}" 已删除')
                # 如果当前选择的是被删除的题库，清空选择
                app = self.get_app()
                if app.current_bank == bank_name:
                    app.current_bank = None
                
                # 同步更新下载器的已安装题库记录
                # 需要根据题库名称找到对应的 bank_id
                self._sync_installed_banks_after_delete(bank_name)
                
                self.refresh_info()
            else:
                self.show_error('删除失败')
        
        confirm_delete_btn.bind(on_press=do_delete)
        btn_layout.add_widget(confirm_delete_btn)
        
        confirm_content.add_widget(btn_layout)
        
        popup = Popup(title='确认删除', content=confirm_content, size_hint=(0.8, 0.4))
        popup.open()

    def show_success(self, message):
        """显示成功提示"""
        popup = Popup(
            title='成功',
            content=Label(text=message, font_name='chinese', font_size=dp(18)),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def show_error(self, message):
        """显示错误提示"""
        popup = Popup(
            title='错误',
            content=Label(text=message, font_name='chinese', font_size=dp(18)),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def import_bank(self, instance):
        """导入题库"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # 说明文字
        info_label = Label(
            text='请输入题库文件名（.json格式）\n文件应放在 question_banks 目录下',
            font_name='chinese',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(info_label)
        
        # 文件名输入框
        from kivy.uix.textinput import TextInput
        self.filename_input = TextInput(
            hint_text='例如: 数学题库.json',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_name='chinese',
            font_size=dp(16),
            padding=[dp(10), dp(10)]
        )
        content.add_widget(self.filename_input)
        
        # 确认按钮
        confirm_btn = Button(
            text='导入',
            size_hint_y=None,
            height=dp(45),
            font_name='chinese'
        )
        confirm_btn.bind(on_press=self.confirm_import)
        content.add_widget(confirm_btn)
        
        popup = Popup(title='导入题库', content=content, size_hint=(0.8, 0.5))
        popup.open()

    def confirm_import(self, instance):
        """确认导入题库"""
        filename = self.filename_input.text.strip()
        
        if not filename:
            popup = Popup(
                title='错误',
                content=Label(text='请输入文件名', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        # 确保有.json后缀
        if not filename.endswith('.json'):
            filename += '.json'
        
        from question_bank import QuestionBankManager
        import os
        bank_manager = QuestionBankManager()
        
        # 构建完整文件路径
        file_path = os.path.join(bank_manager.banks_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            popup = Popup(
                title='错误',
                content=Label(text=f'文件不存在：{filename}\n请将文件放在 question_banks 目录', font_name='chinese', font_size=dp(14)),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            return
        
        try:
            # 尝试导入题库
            bank_name = bank_manager.import_from_json(file_path)
            
            popup = Popup(
                title='成功',
                content=Label(text=f'题库 "{bank_name}" 导入成功！', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            # 刷新题库列表
            self.refresh_info()
        except Exception as e:
            popup = Popup(
                title='错误',
                content=Label(text=f'导入失败：{str(e)}', font_name='chinese', font_size=dp(14)),
                size_hint=(0.8, 0.4)
            )
            popup.open()
        
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def start_quiz(self, instance):
        """开始刷题"""
        app = self.get_app()
        
        if not app.current_bank:
            popup = Popup(
                title='提示',
                content=Label(text='请先选择一个题库', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # 显示刷题设置对话框
        self.show_quiz_settings()

    def show_quiz_settings(self):
        """显示刷题设置对话框"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # 答题模式选择 - 使用Button代替Spinner避免乱码
        mode_label = Label(text='答题模式:', font_name='chinese', font_size=dp(16), size_hint_y=None, height=dp(30))
        content.add_widget(mode_label)
        
        # 创建两个按钮用于切换模式
        self.mode_buttons_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        
        # 用变量追踪当前选中的模式，避免 background_color 比较不准确
        self.selected_mode = 'immediate'
        
        self.immediate_btn = Button(
            text='即时反馈',
            font_name='chinese',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        
        self.batch_btn = Button(
            text='批量答题',
            font_name='chinese',
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0, 0, 0, 1)
        )
        
        def set_immediate_mode(instance):
            self.selected_mode = 'immediate'
            self.immediate_btn.background_color = (0.2, 0.6, 1, 1)
            self.immediate_btn.color = (1, 1, 1, 1)
            self.batch_btn.background_color = (0.8, 0.8, 0.8, 1)
            self.batch_btn.color = (0, 0, 0, 1)
        
        def set_batch_mode(instance):
            self.selected_mode = 'batch'
            self.batch_btn.background_color = (0.2, 0.6, 1, 1)
            self.batch_btn.color = (1, 1, 1, 1)
            self.immediate_btn.background_color = (0.8, 0.8, 0.8, 1)
            self.immediate_btn.color = (0, 0, 0, 1)
        
        self.immediate_btn.bind(on_press=set_immediate_mode)
        self.batch_btn.bind(on_press=set_batch_mode)
        
        self.mode_buttons_layout.add_widget(self.immediate_btn)
        self.mode_buttons_layout.add_widget(self.batch_btn)
        content.add_widget(self.mode_buttons_layout)
        
        # 选项打乱
        from kivy.uix.checkbox import CheckBox
        shuffle_options_layout = BoxLayout(size_hint_y=None, height=dp(40))
        shuffle_options_label = Label(text='打乱选项顺序:', font_name='chinese', font_size=dp(16))
        self.shuffle_options_check = CheckBox(active=False)
        shuffle_options_layout.add_widget(shuffle_options_label)
        shuffle_options_layout.add_widget(self.shuffle_options_check)
        content.add_widget(shuffle_options_layout)
        
        # 题目打乱
        shuffle_questions_layout = BoxLayout(size_hint_y=None, height=dp(40))
        shuffle_questions_label = Label(text='打乱题目顺序:', font_name='chinese', font_size=dp(16))
        self.shuffle_questions_check = CheckBox(active=True)
        shuffle_questions_layout.add_widget(shuffle_questions_label)
        shuffle_questions_layout.add_widget(self.shuffle_questions_check)
        content.add_widget(shuffle_questions_layout)
        
        # 确认按钮
        confirm_btn = Button(text='开始', size_hint_y=None, height=dp(45), font_name='chinese')
        confirm_btn.bind(on_press=self.confirm_quiz)
        content.add_widget(confirm_btn)
        
        popup = Popup(title='刷题设置', content=content, size_hint=(0.8, 0.7))
        self.quiz_settings_popup = popup  # 保存引用以便后续关闭
        popup.open()

    def confirm_quiz(self, instance):
        """确认开始刷题"""
        app = self.get_app()
        
        # 保存设置 - 使用变量追踪模式，更可靠
        mode = self.selected_mode
        shuffle_options = self.shuffle_options_check.active
        shuffle_questions = self.shuffle_questions_check.active
        
        # 加载题库
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        bank_data = bank_manager.load_bank(app.current_bank)
        
        if not bank_data or not bank_data['questions']:
            popup = Popup(
                title='错误',
                content=Label(text='题库为空', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        # 过滤掉大题（essay类型），刷题只包含选择题和判断题
        questions = [q for q in bank_data['questions'] if q.get('type', 'single') != 'essay']
        
        if not questions:
            popup = Popup(
                title='提示',
                content=Label(text='该题库中没有适合刷题的题目（已排除大题）', font_name='chinese', font_size=dp(16)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        # 跳转到刷题界面
        quiz_screen = self.manager.get_screen('quiz')
        quiz_screen.setup_quiz(
            questions,
            app.current_bank,
            mode,
            shuffle_options,
            shuffle_questions
        )
        
        # 关闭设置对话框
        self.quiz_settings_popup.dismiss()
        
        self.manager.current = 'quiz'

    def open_review(self, instance):
        """打开复习模式"""
        app = self.get_app()
        
        if not app.current_bank:
            popup = Popup(
                title='提示',
                content=Label(text='请先选择一个题库', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        # 跳转到复习界面
        review_screen = self.manager.get_screen('review')
        review_screen.setup_review(app.current_bank)
        self.manager.current = 'review'

    def open_profile(self, instance):
        """打开个人中心"""
        self.manager.current = 'profile'
    
    def logout(self, instance):
        """退出登录"""
        app = self.get_app()
        app.current_user = None
        app.current_bank = None
        self.manager.current = 'login'

    # ==================== 题库下载功能 ====================

    def show_bank_downloader(self, instance):
        """显示题库下载对话框"""
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))

        # 标题栏
        title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35)
        )
        title_layout.add_widget(Label(
            text='题库下载中心',
            font_name='chinese',
            font_size=dp(18),
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_x=0.5
        ))

        # 代理设置按钮
        proxy_btn = Button(
            text='代理设置',
            font_name='chinese',
            font_size=dp(14),
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        proxy_btn.bind(on_press=self.show_proxy_settings)
        title_layout.add_widget(proxy_btn)

        # 刷新按钮
        refresh_btn = Button(
            text='刷新列表',
            font_name='chinese',
            font_size=dp(14),
            size_hint_x=0.25,
            background_color=(0.2, 0.6, 1, 1)
        )
        refresh_btn.bind(on_press=lambda x: self._fetch_catalog(download_popup, bank_scroll, bank_list_container, status_label, repo_input))
        title_layout.add_widget(refresh_btn)

        content.add_widget(title_layout)

        # GitHub仓库地址输入
        repo_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            height=dp(70)
        )
        repo_label = Label(
            text='GitHub仓库地址（需包含 bank_catalog.json）：',
            font_name='chinese',
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        repo_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        repo_layout.add_widget(repo_label)

        repo_input = TextInput(
            text='',  # 先设为空，后面会填充
            hint_text='例如: TianSamsara/do_test_packet',
            multiline=False,
            font_name='chinese',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(42),
            padding=[dp(8), dp(8)]
        )
        
        # 自动填充之前保存的 GitHub 仓库地址
        saved_repo = self.downloader.app_config.get_github_repo()
        if saved_repo:
            repo_input.text = saved_repo
        
        repo_layout.add_widget(repo_input)
        content.add_widget(repo_layout)
        self._dl_repo_input = repo_input  # 保存引用供后续刷新使用

        # 状态标签
        status_label = Label(
            text='请填写仓库地址后点击"刷新列表"',
            font_name='chinese',
            font_size=dp(13),
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(status_label)

        # 题库滚动列表
        bank_scroll = ScrollView(size_hint_y=0.6)
        bank_list_container = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            padding=[dp(5), dp(5)]
        )
        bank_list_container.bind(minimum_height=bank_list_container.setter('height'))
        bank_scroll.add_widget(bank_list_container)
        content.add_widget(bank_scroll)

        # 进度条（默认隐藏）
        self.dl_progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(8),
            opacity=0
        )
        content.add_widget(self.dl_progress)

        self.dl_progress_label = Label(
            text='',
            font_name='chinese',
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(18),
            opacity=0
        )
        content.add_widget(self.dl_progress_label)

        # 底部按钮
        close_btn = Button(
            text='关闭',
            font_name='chinese',
            size_hint_y=None,
            height=dp(45),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        close_btn.bind(on_press=lambda x: download_popup.dismiss())
        content.add_widget(close_btn)

        download_popup = Popup(
            title='下载题库',
            content=content,
            size_hint=(0.92, 0.88)
        )
        download_popup.open()

    def _sync_installed_banks_after_delete(self, bank_name):
        """删除题库后同步更新下载器的已安装记录
        
        Args:
            bank_name: 被删除的题库名称（不含.json后缀）
        """
        # 遍历所有已安装的题库，找到匹配的并移除
        for bank_id, bank_info in list(self.downloader.installed_banks.items()):
            if bank_info.get('name') == bank_name or bank_info.get('file', '').replace('.json', '') == bank_name:
                self.downloader.remove_installed_bank(bank_id)
                break

    def _build_catalog_url(self, repo_input_text):
        """根据用户输入的仓库地址构建 bank_catalog.json 的 raw 直链
        支持格式：
        - TianSamsara/do_test_packet
        - https://github.com/TianSamsara/do_test_packet
        - https://raw.githubusercontent.com/TianSamsara/do_test_packet/main/bank_catalog.json
        """
        import re
        text = repo_input_text.strip()
        if not text:
            return None

        # 如果已经是完整的 raw URL，直接返回
        if text.startswith('https://raw.githubusercontent.com/'):
            return text

        # 去掉可能的前缀 https://github.com/
        text = re.sub(r'^https?://github\.com/', '', text)
        # 去掉末尾的斜杠
        text = text.rstrip('/')

        # 格式应为 用户名/仓库名
        if '/' not in text or text.count('/') < 1:
            return None

        return f'https://raw.githubusercontent.com/{text}/main/bank_catalog.json'

    def _update_status(self, status_label, text, color):
        """安全更新状态标签（主线程）"""
        status_label.text = text
        status_label.color = color

    def _on_fetch_success(self, data, popup, bank_scroll,
                          bank_list_container, status_label):
        """获取题库清单成功回调"""
        self._update_status(
            status_label, f'获取成功！共 {len(data)} 个题库可用', (0, 0.6, 0, 1)
        )
        self._build_bank_list(
            data, popup, bank_scroll,
            bank_list_container, status_label
        )

    def _fetch_catalog(self, popup, bank_scroll, bank_list_container, status_label, repo_input):
        """获取题库清单"""
        # 获取用户输入的仓库地址
        repo_text = repo_input.text.strip()
        if not repo_text:
            Clock.schedule_once(lambda dt: self._update_status(
                status_label, '请先填写GitHub仓库地址', (0.9, 0.3, 0.3, 1)
            ), 0)
            return

        catalog_url = self._build_catalog_url(repo_text)
        if not catalog_url:
            Clock.schedule_once(lambda dt: self._update_status(
                status_label, '仓库地址格式错误！请使用 用户名/仓库名 格式', (0.9, 0.3, 0.3, 1)
            ), 0)
            return

        # 保存用户输入的仓库地址到配置文件
        self.downloader.app_config.set_github_repo(repo_text)

        Clock.schedule_once(lambda dt: self._update_status(
            status_label, f'正在获取题库列表...\n{catalog_url[:60]}...', (0.2, 0.6, 1, 1)
        ), 0)

        def on_result(success, data):
            if success:
                Clock.schedule_once(lambda dt: self._on_fetch_success(
                    data, popup, bank_scroll,
                    bank_list_container, status_label
                ), 0)
            else:
                Clock.schedule_once(lambda dt: self._update_status(
                    status_label, str(data), (0.9, 0.3, 0.3, 1)
                ), 0)

        self.downloader.fetch_catalog(catalog_url, callback=on_result)

    def _build_bank_list(self, banks, popup, bank_scroll,
                         bank_list_container, status_label):
        """构建题库列表UI"""
        bank_list_container.clear_widgets()

        if not banks:
            bank_list_container.add_widget(Label(
                text='暂无可用的题库',
                font_name='chinese',
                font_size=dp(14),
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for bank in banks:
            # 题库卡片
            card = BoxLayout(
                orientation='vertical',
                spacing=dp(3),
                size_hint_y=None,
                height=dp(80),
                padding=[dp(8), dp(5)]
            )

            # 标题行
            title_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(28)
            )

            name_label = Label(
                text=bank.name,
                font_name='chinese',
                font_size=dp(16),
                bold=True,
                color=(0, 0, 0, 1),
                size_hint_x=0.55,
                halign='left',
                valign='middle'
            )
            name_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            title_row.add_widget(name_label)

            # 状态/操作按钮
            if bank.installed:
                if bank.version != bank.local_version:
                    action_btn = Button(
                        text='更新',
                        font_name='chinese',
                        font_size=dp(13),
                        size_hint_x=0.2,
                        background_color=(0.2, 0.7, 0.2, 1)
                    )
                    action_btn.bind(on_press=lambda x, b=bank: self._download_bank(
                        b, popup, bank_scroll, bank_list_container, status_label))
                    title_row.add_widget(action_btn)
                else:
                    title_row.add_widget(Label(
                        text='已安装',
                        font_name='chinese',
                        font_size=dp(12),
                        color=(0, 0.6, 0, 1),
                        size_hint_x=0.2
                    ))
            else:
                install_btn = Button(
                    text='下载',
                    font_name='chinese',
                    font_size=dp(13),
                    size_hint_x=0.2,
                    background_color=(0.2, 0.6, 1, 1)
                )
                install_btn.bind(on_press=lambda x, b=bank: self._download_bank(
                    b, popup, bank_scroll, bank_list_container, status_label))
                title_row.add_widget(install_btn)

            # 题目数量
            type_str = '、'.join(bank.types) if bank.types else '未知'
            info_text = f'{bank.question_count}题 | 题型: {type_str} | {self.downloader.format_size(bank.size)}'
            title_row.add_widget(Label(
                text='',
                font_name='chinese',
                font_size=dp(10),
                size_hint_x=0.25
            ))

            card.add_widget(title_row)

            # 描述行
            desc_label = Label(
                text=bank.description[:60] + ('...' if len(bank.description) > 60 else ''),
                font_name='chinese',
                font_size=dp(13),
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(22),
                halign='left',
                valign='middle'
            )
            desc_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            card.add_widget(desc_label)

            # 信息行
            info_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(20)
            )
            info_row.add_widget(Label(
                text=f'v{bank.version} | {bank.question_count}题 '
                     f'| 题型: {"、".join(bank.types) if bank.types else "未知"} '
                     f'| {self.downloader.format_size(bank.size)}',
                font_name='chinese',
                font_size=dp(11),
                color=(0.5, 0.5, 0.5, 1),
                halign='left',
                valign='middle'
            ))
            card.add_widget(info_row)

            bank_list_container.add_widget(card)

    def _download_bank(self, bank, popup, bank_scroll,
                       bank_list_container, status_label):
        """下载单个题库"""
        if self.downloader.downloading:
            # 显示提示
            Clock.schedule_once(lambda dt: self._show_toast('已有下载任务进行中！'), 0)
            return

        # 显示进度条
        self.dl_progress.value = 0
        self.dl_progress.opacity = 1
        self.dl_progress_label.text = f'正在下载 {bank.name}... 0%'
        self.dl_progress_label.opacity = 1

        # 获取保存目录
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        save_dir = bank_manager.banks_dir

        def on_progress(percent, downloaded, total):
            Clock.schedule_once(lambda dt: self._update_progress(
                percent, bank.name
            ), 0)

        def on_complete(success, data):
            if success:
                Clock.schedule_once(lambda dt: self._on_download_done(
                    bank, data, popup, bank_scroll,
                    bank_list_container, status_label
                ), 0)
            else:
                Clock.schedule_once(lambda dt: self._on_download_failed(
                    bank, data, status_label
                ), 0)

        self.downloader.download_bank(
            bank, save_dir,
            progress_callback=on_progress,
            complete_callback=on_complete
        )

    def _update_progress(self, percent, bank_name):
        """更新下载进度"""
        self.dl_progress.value = percent
        self.dl_progress_label.text = f'正在下载 {bank_name}... {percent:.1f}%'

    def _on_download_done(self, bank, file_path, popup, bank_scroll,
                          bank_list_container, status_label):
        """下载完成回调"""
        self.dl_progress.value = 100
        self.dl_progress_label.text = f'{bank.name} 下载完成！'
        self.dl_progress_label.color = (0, 0.6, 0, 1)

        # 延迟隐藏进度条
        Clock.schedule_once(lambda dt: self._hide_progress(), 2)

        # 刷新主界面题库列表
        self.refresh_info()

        # 刷新下载列表
        status_label.text = f'✓ {bank.name} 安装成功！刷新列表中...'
        status_label.color = (0, 0.6, 0, 1)
        self._fetch_catalog(popup, bank_scroll, bank_list_container, status_label, self._dl_repo_input)

    def _on_download_failed(self, bank, error_msg, status_label):
        """下载失败回调"""
        self.dl_progress.value = 0
        self.dl_progress_label.text = f'下载失败: {error_msg}'
        self.dl_progress_label.color = (0.9, 0.3, 0.3, 1)
        status_label.text = f'✗ {bank.name} 下载失败：{error_msg}'
        status_label.color = (0.9, 0.3, 0.3, 1)
        Clock.schedule_once(lambda dt: self._hide_progress(), 3)

    def _hide_progress(self, *args):
        """隐藏进度条"""
        if hasattr(self, 'dl_progress'):
            self.dl_progress.opacity = 0
        if hasattr(self, 'dl_progress_label'):
            self.dl_progress_label.opacity = 0

    def _show_toast(self, message):
        """显示简短提示"""
        popup = Popup(
            title='提示',
            content=Label(text=message, font_name='chinese', font_size=dp(16)),
            size_hint=(0.7, 0.25)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    # ==================== 代理设置 ====================

    def show_proxy_settings(self, instance):
        """显示代理设置对话框"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))

        # 启用代理开关
        proxy_switch_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        proxy_switch_layout.add_widget(Label(
            text='启用代理：',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_x=0.5
        ))

        proxy_check = CheckBox(
            active=self.downloader.use_proxy,
            size_hint_x=0.5
        )
        proxy_switch_layout.add_widget(proxy_check)
        content.add_widget(proxy_switch_layout)

        # 代理地址输入
        addr_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45)
        )
        addr_layout.add_widget(Label(
            text='代理地址：',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_x=0.3
        ))

        proxy_addr_input = TextInput(
            text=self.downloader.proxy_address,
            multiline=False,
            font_name='chinese',
            font_size=dp(16),
            size_hint_x=0.7,
            hint_text='127.0.0.1:7890'
        )
        addr_layout.add_widget(proxy_addr_input)
        content.add_widget(addr_layout)

        # 状态标签
        result_label = Label(
            text='',
            font_name='chinese',
            font_size=dp(13),
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(result_label)

        # 按钮行
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(45)
        )

        def save_settings(btn):
            self.downloader.use_proxy = proxy_check.active
            self.downloader.proxy_address = proxy_addr_input.text.strip() or '127.0.0.1:7890'
            result_label.text = '设置已保存！'
            result_label.color = (0, 0.6, 0, 1)
            Clock.schedule_once(lambda dt: proxy_popup.dismiss(), 0.8)

        save_btn = Button(
            text='保存',
            font_name='chinese',
            font_size=dp(16),
            background_color=(0.2, 0.6, 1, 1)
        )
        save_btn.bind(on_press=save_settings)
        btn_layout.add_widget(save_btn)

        def test_proxy(btn):
            self.downloader.use_proxy = proxy_check.active
            self.downloader.proxy_address = proxy_addr_input.text.strip() or '127.0.0.1:7890'
            result_label.text = '正在测试代理连接...'
            result_label.color = (0.2, 0.6, 1, 1)

            def on_test_result(success, msg):
                Clock.schedule_once(lambda dt: self._update_test_result(
                    result_label, success, msg
                ), 0)

            self.downloader.test_proxy(callback=on_test_result)

        test_btn = Button(
            text='测试连接',
            font_name='chinese',
            font_size=dp(16),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        test_btn.bind(on_press=test_proxy)
        btn_layout.add_widget(test_btn)

        cancel_btn = Button(
            text='取消',
            font_name='chinese',
            font_size=dp(16),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        cancel_btn.bind(on_press=lambda x: proxy_popup.dismiss())
        btn_layout.add_widget(cancel_btn)

        content.add_widget(btn_layout)

        proxy_popup = Popup(
            title='代理设置',
            content=content,
            size_hint=(0.85, 0.45)
        )
        proxy_popup.open()

    def _update_test_result(self, result_label, success, msg):
        """更新代理测试结果"""
        if success:
            result_label.text = msg
            result_label.color = (0, 0.6, 0, 1)
        else:
            result_label.text = msg
            result_label.color = (0.9, 0.3, 0.3, 1)

    def get_app(self):
        """获取App实例"""
        from kivy.app import App
        return App.get_running_app()
