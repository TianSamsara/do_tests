from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window


class ReviewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(12), dp(8)],
            spacing=dp(6)
        )
        
        self.bank_name = ''
        self.review_mode = 'all'
        self.questions = []
        self.quiz_engine = None
        self.selected_answers = set()

        # 标题
        title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45)
        )
        
        self.title_label = Label(
            text='复习模式',
            font_name='chinese',
            font_size=dp(20),
            bold=True,
            color=(0, 0, 0, 1),  # 黑色文字
            size_hint_x=0.7
        )
        title_layout.add_widget(self.title_label)
        
        back_btn = Button(text='返回', font_name='chinese', size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: self.go_to_main())
        title_layout.add_widget(back_btn)
        
        main_layout.add_widget(title_layout)

        # 复习模式选择
        mode_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(45)
        )
        
        wrong_btn = Button(text='错题', font_name='chinese', background_color=(0.9, 0.3, 0.3, 1))
        wrong_btn.bind(on_press=lambda x: self.start_review('wrong'))
        mode_layout.add_widget(wrong_btn)
        
        fav_btn = Button(text='收藏', font_name='chinese', background_color=(0.9, 0.7, 0.2, 1))
        fav_btn.bind(on_press=lambda x: self.start_review('favorite'))
        mode_layout.add_widget(fav_btn)
        
        random_btn = Button(text='随机', font_name='chinese', background_color=(0.3, 0.7, 0.9, 1))
        random_btn.bind(on_press=lambda x: self.start_review('random'))
        mode_layout.add_widget(random_btn)
        
        all_btn = Button(text='全部', font_name='chinese', background_color=(0.3, 0.8, 0.3, 1))
        all_btn.bind(on_press=lambda x: self.start_review('all'))
        mode_layout.add_widget(all_btn)
        
        main_layout.add_widget(mode_layout)

        # 进度显示
        progress_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35)
        )
        
        self.progress_label = Label(
            text='进度: 0/0',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),  # 黑色文字
            size_hint_x=0.6
        )
        progress_layout.add_widget(self.progress_label)
        
        self.accuracy_label = Label(
            text='',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),  # 黑色文字
            halign='right',
            size_hint_x=0.4
        )
        progress_layout.add_widget(self.accuracy_label)
        
        main_layout.add_widget(progress_layout)

        # 主内容区域（填充所有剩余空间，不使用外层ScrollView）
        from kivy.uix.scrollview import ScrollView
        content_area = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=1)
        
        # 题目显示区域（固定高度，支持内部滚动）
        question_scroll = ScrollView(size_hint_y=None, height=dp(130), do_scroll_x=False, do_scroll_y=True, scroll_type=['bars', 'content'])
        self.question_label = Label(
            text='',
            font_name='chinese',
            font_size=dp(17),
            color=(0, 0, 0, 1),
            valign='top',
            halign='left',
            markup=True,
            size_hint_y=None,
            size_hint_x=1,
            padding=[dp(8), dp(8)]
        )
        
        def update_question_text_size(instance, value):
            if hasattr(instance, 'width') and instance.width > 0:
                instance.text_size = (instance.width - dp(10), None)
        
        Window.bind(size=lambda *args: update_question_text_size(self.question_label, None))
        self.question_label.bind(size=update_question_text_size)
        self.question_label.bind(texture_size=lambda instance, value: setattr(instance, 'size', value))
        
        question_scroll.add_widget(self.question_label)
        content_area.add_widget(question_scroll)
        
        # 选项区域（动态高度：大题=0，选择题=按实际选项数计算）
        self.options_container = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=None,
            height=dp(116)
        )
        
        self.option_buttons = []
        for i in range(4):
            btn = Button(
                text='',
                size_hint_y=None,
                height=dp(26),
                font_name='chinese',
                font_size=dp(15),
                color=(0, 0, 0, 1),
                background_color=(0.95, 0.95, 0.95, 1),
                disabled_color=(0.3, 0.3, 0.3, 1),
                halign='left',
                padding=[dp(10), 0],
                disabled=True
            )
            self.option_buttons.append(btn)
            self.options_container.add_widget(btn)
        
        content_area.add_widget(self.options_container)
        
        # 答案显示区域（填充剩余空间，通过opacity控制显隐）
        answer_scroll = ScrollView(size_hint_y=1, do_scroll_x=False, do_scroll_y=True, scroll_type=['bars', 'content'])
        self.answer_layout = BoxLayout(orientation='vertical', padding=[dp(8), dp(8)], size_hint_y=None)
        self.answer_label = Label(
            text='',
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0.5, 0, 1),
            halign='left',
            valign='top',
            markup=True,
            size_hint_y=None,
            size_hint_x=1,
            padding=[dp(5), dp(5)]
        )
        
        def update_answer_text_size(instance, value):
            if hasattr(instance, 'width') and instance.width > 0:
                instance.text_size = (instance.width - dp(10), None)
        
        Window.bind(size=lambda *args: update_answer_text_size(self.answer_label, None))
        self.answer_label.bind(size=update_answer_text_size)
        self.answer_label.bind(texture_size=lambda instance, value: setattr(instance, 'size', value))
        
        self.answer_label.bind(size=lambda instance, value: setattr(self.answer_layout, 'height', instance.height))
        self.answer_layout.add_widget(self.answer_label)
        answer_scroll.add_widget(self.answer_layout)
        self.answer_scroll = answer_scroll
        self.answer_scroll.opacity = 0  # 初始隐藏
        content_area.add_widget(answer_scroll)
        
        main_layout.add_widget(content_area)
        
        # 操作按钮
        action_area = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(45)
        )
        
        prev_btn = Button(text='上一题', font_name='chinese', background_color=(0.6, 0.6, 0.6, 1))
        prev_btn.bind(on_press=self.previous_question)
        action_area.add_widget(prev_btn)
        
        self.show_answer_btn = Button(text='显示答案', font_name='chinese', background_color=(0.2, 0.6, 1, 1))
        self.show_answer_btn.bind(on_press=self.toggle_answer)
        action_area.add_widget(self.show_answer_btn)
        
        next_btn = Button(text='下一题', font_name='chinese', background_color=(0.2, 0.8, 0.2, 1))
        next_btn.bind(on_press=self.next_question)
        action_area.add_widget(next_btn)
        
        main_layout.add_widget(action_area)
        
        # 底部状态按钮
        bottom_btns = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(42)
        )
        
        self.favorite_btn = Button(text='☆ 收藏', font_name='chinese', background_color=(0.9, 0.7, 0.2, 1))
        self.favorite_btn.bind(on_press=self.toggle_favorite)
        bottom_btns.add_widget(self.favorite_btn)
        
        self.mastered_btn = Button(text='○ 未掌握', font_name='chinese', background_color=(0.3, 0.7, 0.3, 1))
        self.mastered_btn.bind(on_press=self.toggle_mastered)
        bottom_btns.add_widget(self.mastered_btn)
        
        remove_wrong_btn = Button(text='移除错题', font_name='chinese', background_color=(0.8, 0.3, 0.3, 1))
        remove_wrong_btn.bind(on_press=self.remove_from_wrong)
        bottom_btns.add_widget(remove_wrong_btn)
        
        main_layout.add_widget(bottom_btns)
        
        # 将主布局添加到Screen
        self.add_widget(main_layout)

    def setup_review(self, bank_name):
        """设置复习"""
        self.bank_name = bank_name
        self.title_label.text = f'复习: {bank_name}'

    def start_review(self, mode):
        """开始复习"""
        app = self.get_app()
        
        from review_module import ReviewModule
        review = ReviewModule()
        
        questions = review.get_review_questions(
            app.current_user[0],
            self.bank_name,
            mode
        )
        
        if not questions:
            mode_text = {'wrong': '错题', 'favorite': '收藏', 'random': '随机'}.get(mode, '全部')
            popup = Popup(
                title='提示',
                content=Label(text=f'暂无{mode_text}题目', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        self.review_mode = mode
        self.questions = questions
        self.current_index = 0
        self.show_answer = False
        
        self.update_display()

    def update_display(self):
        """更新显示"""
        if not self.questions or self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        
        # 更新进度
        self.progress_label.text = f"进度: {self.current_index + 1}/{len(self.questions)}"
        
        # 复习模式不显示正确率
        self.accuracy_label.text = ""
        
        # 更新题目
        q_type = question.get('type', 'single')
        type_text = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题', 'essay': '大题'}.get(q_type, '单选题')
        self.question_label.text = f"[{type_text}] {question.get('text', '')}"
        
        # 触发 text_size 更新以支持换行
        if hasattr(self.question_label, 'width') and self.question_label.width > 0:
            self.question_label.text_size = (self.question_label.width - dp(10), None)
        
        # 根据题型决定是否显示选项区域
        options = question.get('options', {})
        option_keys = ['A', 'B', 'C', 'D']
        
        # 判断是否是大题（没有选项或选项为空）
        is_essay = (q_type == 'essay' or not options)
        
        # 隐藏或显示选项按钮
        for i, key in enumerate(option_keys):
            if i < len(self.option_buttons):
                if key in options and not is_essay:
                    self.option_buttons[i].text = f"{key}. {options[key]}"
                    self.option_buttons[i].opacity = 1
                    self.option_buttons[i].disabled = False
                else:
                    self.option_buttons[i].text = ''
                    self.option_buttons[i].opacity = 0
                    self.option_buttons[i].disabled = True
        
        # 根据题型动态调整选项区域高度（大题时不占空间）
        if is_essay:
            # 大题：选项区域高度为0，不占空间
            self.options_container.height = dp(0)
        else:
            # 选择题：根据实际可见选项数量计算高度
            visible_count = sum(1 for btn in self.option_buttons if btn.opacity == 1)
            if visible_count > 0:
                # 每个按钮 dp(26) + 间距 dp(4)，最后一个按钮不需要底部间距
                self.options_container.height = dp(26) * visible_count + dp(4) * (visible_count - 1)
            else:
                self.options_container.height = dp(0)
        
        # 重置选项按钮颜色（复习模式下不可点击）
        for btn in self.option_buttons:
            btn.background_color = (0.95, 0.95, 0.95, 1)  # 浅灰白色背景
        
        # 根据题型设置答案对齐方式
        if is_essay:
            # 大题时答案居中
            self.answer_label.halign = 'center'
        else:
            # 选择题时答案左对齐
            self.answer_label.halign = 'left'
        
        # 隐藏答案区域（用opacity控制，保持布局稳定）
        self.show_answer = False
        self.answer_label.text = ''
        self.answer_scroll.opacity = 0
        self.show_answer_btn.text = '显示答案'
        
        # 更新状态按钮
        self.update_status_buttons()

    def toggle_answer(self, instance):
        """切换答案显示/隐藏（使用opacity控制，避免布局跳动）"""
        if not self.questions or self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        
        if not self.show_answer:
            # 显示答案
            answer = question.get('answer', '')
            explanation = question.get('explanation', '')
            
            answer_text = f"[b]答案：[/b] {answer}"
            if explanation:
                answer_text += f"\n\n[b]解析：[/b] {explanation}"
            
            self.answer_label.text = answer_text
            # answer_scroll 已有 size_hint_y=1，始终占据剩余空间
            # Label 的 width 始终正确，text_size 由 size 绑定自动更新
            if hasattr(self.answer_label, 'width') and self.answer_label.width > 0:
                self.answer_label.text_size = (self.answer_label.width - dp(10), None)
            
            self.answer_scroll.opacity = 1
            self.show_answer_btn.text = '隐藏答案'
            self.show_answer = True
        else:
            # 隐藏答案（保持空间不变，仅隐藏内容）
            self.answer_label.text = ''
            self.answer_scroll.opacity = 0
            self.show_answer_btn.text = '显示答案'
            self.show_answer = False

    def next_question(self, instance):
        """下一题"""
        if not self.questions:
            return
        
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.update_display()
        else:
            # 复习结束
            popup = Popup(
                title='提示',
                content=Label(text='已经是最后一题了', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: popup.dismiss(), 1)

    def previous_question(self, instance):
        """上一题"""
        if not self.questions:
            return
        
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def toggle_favorite(self, instance):
        """切换收藏状态"""
        if not self.questions or self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        app = self.get_app()
        
        from review_module import ReviewModule
        review = ReviewModule()
        is_fav = review.toggle_favorite(
            app.current_user[0],
            self.bank_name,
            question.get('index', 0),
            question.get('text', '')
        )
        
        popup = Popup(
            title='提示',
            content=Label(
                text='已加入收藏' if is_fav else '已取消收藏',
                font_name='chinese',
                font_size=dp(18)
            ),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
        
        self.update_status_buttons()

    def toggle_mastered(self, instance):
        """切换掌握状态"""
        if not self.questions or self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        app = self.get_app()
        
        from review_module import ReviewModule
        review = ReviewModule()
        is_mastered = review.toggle_mastered(
            app.current_user[0],
            self.bank_name,
            question.get('index', 0)
        )
        
        popup = Popup(
            title='提示',
            content=Label(
                text='已标记为掌握' if is_mastered else '已取消掌握',
                font_name='chinese',
                font_size=dp(18)
            ),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
        
        self.update_status_buttons()

    def remove_from_wrong(self, instance):
        """从错题本移除"""
        if not self.questions or self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        app = self.get_app()
        
        from database import Database
        db = Database()
        db.remove_wrong_question(
            app.current_user[0],
            self.bank_name,
            question.get('index', 0)
        )
        db.close()
        
        popup = Popup(
            title='提示',
            content=Label(text='已从错题本移除', font_name='chinese', font_size=dp(18)),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)

    def update_status_buttons(self):
        """更新状态按钮"""
        if not self.questions or self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        app = self.get_app()
        
        from database import Database
        db = Database()
        
        is_fav = db.is_favorite(
            app.current_user[0],
            self.bank_name,
            question.get('index', 0)
        )
        
        is_mastered = db.is_mastered(
            app.current_user[0],
            self.bank_name,
            question.get('index', 0)
        )
        
        db.close()
        
        self.favorite_btn.text = '★ 已收藏' if is_fav else '☆ 收藏'
        self.mastered_btn.text = '✓ 已掌握' if is_mastered else '○ 未掌握'

    def go_to_main(self, *args):
        """返回主界面"""
        self.manager.current = 'main'

    def get_app(self):
        """获取App实例"""
        from kivy.app import App
        return App.get_running_app()
