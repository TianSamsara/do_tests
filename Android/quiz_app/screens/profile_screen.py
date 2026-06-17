from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )
        
        # 顶部标题栏
        title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        
        title_label = Label(
            text='个人中心',
            font_name='chinese',
            font_size=dp(22),
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_x=0.7
        )
        title_layout.add_widget(title_label)
        
        back_btn = Button(text='返回', font_name='chinese', size_hint_x=0.3,
                          background_color=(0.6, 0.6, 0.6, 1))
        back_btn.bind(on_press=lambda x: self.go_to_main())
        title_layout.add_widget(back_btn)
        
        main_layout.add_widget(title_layout)
        
        # 用户信息区域
        self.user_info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(160),
            padding=[dp(10), dp(5)]
        )
        
        self.user_name_label = Label(
            text='用户名: ',
            font_name='chinese',
            font_size=dp(18),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        self.user_name_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        self.user_info_layout.add_widget(self.user_name_label)
        
        # 统计数据卡片
        self.stats_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            height=dp(120),
            padding=[dp(5), dp(5)]
        )
        
        self.stats_title = Label(
            text='学习统计',
            font_name='chinese',
            font_size=dp(16),
            bold=True,
            color=(0.2, 0.6, 1, 1),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        self.stats_title.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        self.stats_layout.add_widget(self.stats_title)
        
        self.tests_label = Label(text='刷题次数: 0', font_name='chinese', font_size=dp(14),
                                 color=(0, 0, 0, 1), size_hint_y=None, height=dp(22),
                                 halign='left', valign='middle')
        self.tests_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        self.stats_layout.add_widget(self.tests_label)
        
        self.questions_label = Label(text='总题数: 0', font_name='chinese', font_size=dp(14),
                                     color=(0, 0, 0, 1), size_hint_y=None, height=dp(22),
                                     halign='left', valign='middle')
        self.questions_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        self.stats_layout.add_widget(self.questions_label)
        
        self.correct_label = Label(text='正确数: 0', font_name='chinese', font_size=dp(14),
                                   color=(0, 0, 0, 1), size_hint_y=None, height=dp(22),
                                   halign='left', valign='middle')
        self.correct_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        self.stats_layout.add_widget(self.correct_label)
        
        self.accuracy_label = Label(text='平均正确率: 0%', font_name='chinese', font_size=dp(14),
                                    color=(0.2, 0.6, 1, 1), size_hint_y=None, height=dp(22),
                                    halign='left', valign='middle')
        self.accuracy_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        self.stats_layout.add_widget(self.accuracy_label)
        
        self.user_info_layout.add_widget(self.stats_layout)
        main_layout.add_widget(self.user_info_layout)
        
        # 设置按钮区域
        settings_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(42),
            spacing=dp(10),
            padding=[dp(10), dp(0)]
        )
        
        settings_label = Label(
            text='界面设置：',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_x=0.35,
            halign='left',
            valign='middle'
        )
        settings_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        settings_layout.add_widget(settings_label)
        
        color_btn = Button(
            text='🎨 刷题颜色',
            font_name='chinese',
            font_size=dp(14),
            size_hint_x=0.4,
            background_color=(0.3, 0.5, 0.9, 1)
        )
        color_btn.bind(on_press=self.show_color_settings)
        settings_layout.add_widget(color_btn)
        
        reset_color_btn = Button(
            text='还原默认',
            font_name='chinese',
            font_size=dp(14),
            size_hint_x=0.25,
            background_color=(0.6, 0.6, 0.6, 1)
        )
        reset_color_btn.bind(on_press=self.reset_colors)
        settings_layout.add_widget(reset_color_btn)
        
        main_layout.add_widget(settings_layout)
        
        # 错题记录区域标题
        wrong_title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        wrong_title = Label(
            text='错题记录',
            font_name='chinese',
            font_size=dp(18),
            bold=True,
            color=(0.9, 0.3, 0.3, 1),
            size_hint_x=0.5
        )
        wrong_title_layout.add_widget(wrong_title)
        
        self.wrong_count_label = Label(
            text='共0题',
            font_name='chinese',
            font_size=dp(14),
            color=(0, 0, 0, 1),
            size_hint_x=0.3
        )
        wrong_title_layout.add_widget(self.wrong_count_label)
        
        # 题库筛选按钮
        self.filter_btn = Button(
            text='筛选题库',
            font_name='chinese',
            font_size=dp(14),
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.filter_btn.bind(on_press=self.show_bank_filter)
        wrong_title_layout.add_widget(self.filter_btn)
        
        main_layout.add_widget(wrong_title_layout)
        
        # 错题列表滚动区域
        self.wrong_scroll = ScrollView(size_hint_y=0.55)
        self.wrong_list = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None
        )
        self.wrong_list.bind(minimum_height=self.wrong_list.setter('height'))
        self.wrong_scroll.add_widget(self.wrong_list)
        main_layout.add_widget(self.wrong_scroll)
        
        # 将主布局添加到Screen
        self.add_widget(main_layout)
    
    def on_enter(self):
        """进入屏幕时刷新数据"""
        self.refresh_data()
    
    def refresh_data(self):
        """刷新所有数据"""
        app = self.get_app()
        
        if not app.current_user:
            return
        
        # 更新用户名
        self.user_name_label.text = f"用户名: {app.current_user[1]}"
        
        # 更新统计数据
        from database import Database
        db = Database()
        stats = db.get_user_stats(app.current_user[0])
        db.close()
        
        total_tests = stats[0] or 0
        total_questions = stats[1] or 0
        total_correct = stats[2] or 0
        avg_accuracy = stats[3] or 0
        
        self.tests_label.text = f"刷题次数: {total_tests}"
        self.questions_label.text = f"总题数: {total_questions}"
        self.correct_label.text = f"正确数: {total_correct}"
        self.accuracy_label.text = f"平均正确率: {avg_accuracy:.1f}%"
        
        # 加载错题列表（默认显示所有题库的错题）
        self.load_wrong_questions()
    
    def load_wrong_questions(self, bank_name=None):
        """加载错题列表"""
        app = self.get_app()
        
        from database import Database
        db = Database()
        wrong_list = db.get_wrong_questions(app.current_user[0], bank_name)
        db.close()
        
        self.wrong_list.clear_widgets()
        self.wrong_count_label.text = f'共{len(wrong_list)}题'
        
        if bank_name:
            self.filter_btn.text = bank_name
        else:
            self.filter_btn.text = '筛选题库'
        
        if not wrong_list:
            no_data = Label(
                text='暂无错题记录',
                font_name='chinese',
                font_size=dp(16),
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(40)
            )
            self.wrong_list.add_widget(no_data)
            return
        
        # 获取题库数据以显示选项和解析
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        
        for wrong in wrong_list:
            # wrong结构: (id, user_id, bank_name, question_index, question_text, wrong_count, last_wrong_time)
            wrong_id = wrong[0]
            wrong_bank = wrong[2]
            q_index = wrong[3]
            q_text = wrong[4]
            wrong_count = wrong[5]
            
            # 加载题目详细信息
            bank_data = bank_manager.load_bank(wrong_bank)
            question = None
            if bank_data:
                for q in bank_data['questions']:
                    if q.get('index', 0) == q_index:
                        question = q
                        break
            
            # 创建错题卡片
            card = BoxLayout(
                orientation='vertical',
                spacing=dp(3),
                size_hint_y=None,
                height=dp(40),  # 最小高度，后面动态计算
                padding=[dp(8), dp(5)]
            )
            
            # 题目文本（第一行）
            q_header = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(25)
            )
            
            bank_tag = Label(
                text=f'[{wrong_bank}]',
                font_name='chinese',
                font_size=dp(12),
                color=(0.2, 0.6, 1, 1),
                size_hint_x=0.3,
                halign='left',
                valign='middle'
            )
            bank_tag.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
            q_header.add_widget(bank_tag)
            
            count_label = Label(
                text=f'错{wrong_count}次',
                font_name='chinese',
                font_size=dp(12),
                color=(0.9, 0.3, 0.3, 1),
                size_hint_x=0.15
            )
            q_header.add_widget(count_label)
            
            detail_btn = Button(
                text='查看详情',
                font_name='chinese',
                font_size=dp(12),
                size_hint_x=0.25,
                background_color=(0.2, 0.6, 1, 1),
                height=dp(25)
            )
            detail_btn.bind(on_press=lambda instance, q=question, w=wrong: self.show_wrong_detail(q, w))
            q_header.add_widget(detail_btn)
            
            remove_btn = Button(
                text='移除',
                font_name='chinese',
                font_size=dp(12),
                size_hint_x=0.15,
                background_color=(0.8, 0.3, 0.3, 1),
                height=dp(25)
            )
            remove_btn.bind(on_press=lambda instance, bank=wrong_bank, idx=q_index: self.remove_wrong(bank, idx))
            q_header.add_widget(remove_btn)
            
            q_header.add_widget(Label(size_hint_x=0.15))  # 空位
            
            card.add_widget(q_header)
            
            # 题目简略文本（第二行）
            short_text = q_text[:50] + '...' if len(q_text) > 50 else q_text
            text_label = Label(
                text=short_text,
                font_name='chinese',
                font_size=dp(13),
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            text_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
            card.add_widget(text_label)
            
            # 设置卡片总高度
            card.height = dp(50)
            
            self.wrong_list.add_widget(card)
    
    def show_wrong_detail(self, question, wrong_info):
        """显示错题详情弹窗"""
        if not question:
            popup = Popup(
                title='提示',
                content=Label(text='题目数据不存在', font_name='chinese', font_size=dp(16)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))
        
        # 题目类型
        q_type = question.get('type', 'single')
        type_text = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题', 'essay': '大题'}.get(q_type, '单选题')
        
        # 题目文本
        scroll = ScrollView(size_hint_y=0.4)
        text_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        text_layout.bind(minimum_height=text_layout.setter('height'))
        
        q_label = Label(
            text=f"[{type_text}] {question.get('text', '')}",
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            halign='left',
            valign='top',
            markup=True
        )
        q_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        q_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        text_layout.add_widget(q_label)
        scroll.add_widget(text_layout)
        content.add_widget(scroll)
        
        # 选项
        options = question.get('options', {})
        if options:
            options_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(3),
                size_hint_y=None,
                padding=[dp(5), dp(3)]
            )
            
            for letter, opt_text in options.items():
                # 标记正确答案为绿色
                correct_answer = question.get('answer', '')
                is_correct_option = letter in correct_answer if q_type == 'multiple' else letter == correct_answer
                
                opt_color = (0, 0.6, 0, 1) if is_correct_option else (0, 0, 0, 1)
                
                opt_label = Label(
                    text=f"{letter}. {opt_text}" + (" [正确答案]" if is_correct_option else ""),
                    font_name='chinese',
                    font_size=dp(14),
                    color=opt_color,
                    size_hint_y=None,
                    height=dp(22),
                    halign='left',
                    valign='middle'
                )
                opt_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                options_layout.add_widget(opt_label)
            
            options_layout.bind(minimum_height=options_layout.setter('height'))
            content.add_widget(options_layout)
        
        # 答案和解析
        answer_text = question.get('answer', '')
        explanation = question.get('explanation', '')
        
        info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None,
            padding=[dp(5), dp(3)]
        )
        
        answer_label = Label(
            text=f"正确答案: {answer_text}",
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0.6, 0, 1),
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left',
            valign='middle'
        )
        answer_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        info_layout.add_widget(answer_label)
        
        if explanation:
            expl_label = Label(
                text=f"解析: {explanation}",
                font_name='chinese',
                font_size=dp(14),
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                halign='left',
                valign='top',
                markup=True
            )
            expl_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            expl_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
            info_layout.add_widget(expl_label)
        
        wrong_count = wrong_info[5]  # wrong_count
        count_label = Label(
            text=f"错误次数: {wrong_count}",
            font_name='chinese',
            font_size=dp(14),
            color=(0.9, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        count_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        info_layout.add_widget(count_label)
        
        info_layout.bind(minimum_height=info_layout.setter('height'))
        content.add_widget(info_layout)
        
        # 关闭按钮
        close_btn = Button(text='关闭', font_name='chinese', size_hint_y=None, height=dp(40))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(title='错题详情', content=content, size_hint=(0.9, 0.85))
        popup.open()
    
    def remove_wrong(self, bank_name, question_index):
        """移除错题"""
        app = self.get_app()
        
        from database import Database
        db = Database()
        db.remove_wrong_question(app.current_user[0], bank_name, question_index)
        db.close()
        
        # 刷新错题列表
        self.load_wrong_questions()
    
    def show_bank_filter(self, instance):
        """显示题库筛选弹窗"""
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        banks = bank_manager.list_banks()
        
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        
        all_btn = Button(text='所有题库', font_name='chinese', size_hint_y=None, height=dp(45),
                         background_color=(0.2, 0.6, 1, 1))
        all_btn.bind(on_press=lambda x: (popup.dismiss(), self.load_wrong_questions()))
        content.add_widget(all_btn)
        
        for bank_name in banks:
            btn = Button(text=bank_name, font_name='chinese', size_hint_y=None, height=dp(45),
                         background_color=(0.3, 0.7, 0.3, 1))
            btn.bind(on_press=lambda instance, name=bank_name: (popup.dismiss(), self.load_wrong_questions(name)))
            content.add_widget(btn)
        
        close_btn = Button(text='关闭', font_name='chinese', size_hint_y=None, height=dp(40),
                           background_color=(0.6, 0.6, 0.6, 1))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(title='选择题库', content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def reset_colors(self, instance):
        """重置颜色为默认值"""
        from app_config import AppConfig
        config = AppConfig()
        config.reset_quiz_colors()
        
        popup = Popup(
            title='提示',
            content=Label(text='颜色已恢复默认！', font_name='chinese', font_size=dp(16)),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
    
    def show_color_settings(self, instance):
        """显示颜色设置弹窗"""
        from app_config import AppConfig
        config = AppConfig()
        current_colors = config.get_quiz_colors()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # 说明文字
        tip_label = Label(
            text='选择选项选中时的颜色：',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        tip_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        content.add_widget(tip_label)
        
        # 当前颜色预览
        preview_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        preview_label = Label(
            text='当前颜色：',
            font_name='chinese',
            font_size=dp(15),
            color=(0, 0, 0, 1),
            size_hint_x=0.4,
            halign='left',
            valign='middle'
        )
        preview_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        preview_layout.add_widget(preview_label)
        
        self._create_color_preview(preview_layout, current_colors['selected'])
        content.add_widget(preview_layout)
        
        # 预设颜色网格
        color_grid = GridLayout(
            cols=4,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(200)
        )
        
        # 预设颜色选项
        preset_colors = [
            ("蓝色", [0.2, 0.6, 1.0, 1.0]),
            ("绿色", [0.2, 0.8, 0.3, 1.0]),
            ("橙色", [1.0, 0.6, 0.2, 1.0]),
            ("紫色", [0.6, 0.3, 0.9, 1.0]),
            ("粉色", [1.0, 0.4, 0.6, 1.0]),
            ("青色", [0.2, 0.8, 0.8, 1.0]),
            ("红色", [1.0, 0.3, 0.3, 1.0]),
            ("灰色", [0.5, 0.5, 0.5, 1.0]),
        ]
        
        for name, rgba in preset_colors:
            color_btn = Button(
                text=name,
                font_name='chinese',
                font_size=dp(14),
                background_color=rgba,
                color=(1, 1, 1, 1) if sum(rgba[:3]) / 3 < 0.5 else (0, 0, 0, 1),
                size_hint_y=None,
                height=dp(42)
            )
            color_btn.bind(on_press=lambda x, c=rgba, n=name: self._apply_color(
                c, n, preview_layout, color_popup, current_colors
            ))
            color_grid.add_widget(color_btn)
        
        content.add_widget(color_grid)
        
        # 底部按钮
        close_btn = Button(
            text='关闭',
            font_name='chinese',
            size_hint_y=None,
            height=dp(42),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        close_btn.bind(on_press=lambda x: color_popup.dismiss())
        content.add_widget(close_btn)
        
        color_popup = Popup(title='刷题颜色设置', content=content, size_hint=(0.9, 0.7))
        color_popup.open()
    
    def _create_color_preview(self, parent_layout, rgba):
        """创建颜色预览块"""
        preview_box = Button(
            text='',
            size_hint_x=0.55,
            background_color=rgba,
            disabled=True
        )
        parent_layout.add_widget(preview_box)
        return preview_box
    
    def _apply_color(self, rgba, name, preview_layout, popup, current_colors):
        """应用选中的颜色"""
        from app_config import AppConfig
        config = AppConfig()
        config.set_quiz_color('selected', rgba)
        
        # 更新预览（替换预览块）
        old_preview = preview_layout.children[0]
        preview_layout.remove_widget(old_preview)
        self._create_color_preview(preview_layout, rgba)
        
        # 显示提示
        tip = Popup(
            title='已设置',
            content=Label(
                text=f'选项选中颜色已设为：{name}',
                font_name='chinese',
                font_size=dp(16)
            ),
            size_hint=(0.7, 0.3)
        )
        tip.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: tip.dismiss(), 1.2)
    
    def go_to_main(self, *args):
        """返回主界面"""
        self.manager.current = 'main'
    
    def get_app(self):
        """获取App实例"""
        from kivy.app import App
        return App.get_running_app()
