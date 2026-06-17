from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.core.window import Window
from datetime import datetime


class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 创建主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10)
        )
        
        self.questions = []
        self.bank_name = ''
        self.quiz_engine = None
        self.start_time = None
        self.selected_answers = set()

        # 进度条
        progress_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        self.progress_label = Label(
            text='进度: 0/0',
            font_name='chinese',
            font_size=dp(16),
            size_hint_x=0.6
        )
        progress_layout.add_widget(self.progress_label)
        
        self.accuracy_label = Label(
            text='正确率: 0%',
            font_name='chinese',
            font_size=dp(16),
            halign='right',
            size_hint_x=0.4
        )
        progress_layout.add_widget(self.accuracy_label)
        
        main_layout.add_widget(progress_layout)

        # 题目显示区域
        question_scroll = BoxLayout(
            size_hint_y=0.50,
            padding=[dp(10), dp(10)]
        )
        
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        
        self.question_label = Label(
            text='',
            font_name='chinese',
            font_size=dp(18),
            color=(0, 0, 0, 1),  # 黑色文字
            valign='top',
            halign='left',
            markup=True,
            size_hint_y=None,
            size_hint_x=1,
            padding=[dp(5), dp(5)]
        )

        def update_quiz_text_size(instance, value):
            """动态更新text_size以支持题目文字自动换行"""
            if hasattr(instance, 'width') and instance.width > 0:
                instance.text_size = (instance.width - dp(10), None)

        self.question_label.bind(size=update_quiz_text_size)
        self.question_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'size', value)
        )
        scroll.add_widget(self.question_label)
        question_scroll.add_widget(scroll)
        
        main_layout.add_widget(question_scroll)

        # 选项区域
        options_container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=0.30
        )
        
        # 默认颜色（会被 setup_quiz 中的配置覆盖）
        self.quiz_colors = {
            'selected': [0.5, 0.7, 0.9, 1.0],
            'default': [0.7, 0.7, 0.7, 1.0],
            'correct': [0.2, 0.8, 0.2, 1.0],
            'wrong': [0.9, 0.3, 0.3, 1.0]
        }
        
        self.option_buttons = []
        for i in range(4):
            btn = Button(
                text='',
                size_hint_y=None,
                height=dp(50),
                font_name='chinese',
                font_size=dp(16),
                color=(0, 0, 0, 1),  # 黑色文字
                background_color=self.quiz_colors['default'],
                halign='left',
                padding=[dp(10), 0]
            )
            btn.bind(on_press=lambda instance, idx=i: self.select_option(idx))
            self.option_buttons.append(btn)
            options_container.add_widget(btn)
        
        main_layout.add_widget(options_container)

        # 操作按钮区域
        action_area = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        prev_btn = Button(text='上一题', font_name='chinese', background_color=(0.6, 0.6, 0.6, 1))
        prev_btn.bind(on_press=self.previous_question)
        action_area.add_widget(prev_btn)
        
        self.submit_btn = Button(text='提交', font_name='chinese', background_color=(0.2, 0.8, 0.2, 1))
        self.submit_btn.bind(on_press=self.submit_answer)
        action_area.add_widget(self.submit_btn)
        
        next_btn = Button(text='下一题', font_name='chinese', background_color=(0.2, 0.6, 1, 1))
        next_btn.bind(on_press=self.next_question)
        action_area.add_widget(next_btn)
        
        main_layout.add_widget(action_area)

        # 底部按钮
        bottom_btns = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(45)
        )
        
        exit_btn = Button(text='退出', font_name='chinese', background_color=(0.8, 0.3, 0.3, 1))
        exit_btn.bind(on_press=self.exit_quiz)
        bottom_btns.add_widget(exit_btn)
        
        self.favorite_btn = Button(text='收藏', font_name='chinese', background_color=(0.9, 0.7, 0.2, 1))
        self.favorite_btn.bind(on_press=self.toggle_favorite)
        bottom_btns.add_widget(self.favorite_btn)
        
        self.mastered_btn = Button(text='已掌握', font_name='chinese', background_color=(0.3, 0.7, 0.3, 1))
        self.mastered_btn.bind(on_press=self.toggle_mastered)
        bottom_btns.add_widget(self.mastered_btn)
        
        main_layout.add_widget(bottom_btns)
        
        # 将主布局添加到Screen
        self.add_widget(main_layout)

    def setup_quiz(self, questions, bank_name, mode='immediate', 
                   shuffle_options=False, shuffle_questions=False):
        """设置刷题"""
        from quiz_engine import QuizEngine
        from app_config import AppConfig
        
        self.questions = questions
        self.bank_name = bank_name
        self.quiz_engine = QuizEngine()
        self.quiz_engine.start_quiz(questions, mode, shuffle_options, shuffle_questions)
        self.start_time = datetime.now()
        self.selected_answers = set()
        
        # 加载用户自定义颜色
        config = AppConfig()
        saved_colors = config.get_quiz_colors()
        if saved_colors:
            for key in self.quiz_colors:
                if key in saved_colors:
                    self.quiz_colors[key] = saved_colors[key]
        
        self.update_display()

    def update_display(self):
        """更新显示"""
        if not self.quiz_engine:
            return
        
        question = self.quiz_engine.get_current_question()
        if not question:
            return
        
        # 更新进度
        progress = self.quiz_engine.get_progress()
        self.progress_label.text = f"进度: {progress['current']}/{progress['total']}"
        
        # 更新正确率（即时模式下）
        if self.quiz_engine.mode == 'immediate' and self.quiz_engine.results:
            correct_count = sum(1 for r in self.quiz_engine.results if r['is_correct'])
            accuracy = (correct_count / len(self.quiz_engine.results)) * 100
            self.accuracy_label.text = f"正确率: {accuracy:.1f}%"
        else:
            self.accuracy_label.text = f"正确率: 0%"
        
        # 更新题目
        q_type = question.get('type', 'single')
        type_text = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题', 'essay': '大题'}.get(q_type, '单选题')
        self.question_label.text = f"[{type_text}] {question.get('text', '')}"
        
        # 更新选项
        options = question.get('options', {})
        option_keys = ['A', 'B', 'C', 'D']
        
        # 判断是否是大题（没有选项或选项为空）
        is_essay = (q_type == 'essay' or not options)
        
        for i, key in enumerate(option_keys):
            if i < len(self.option_buttons):
                if key in options and not is_essay:
                    self.option_buttons[i].text = f"{key}. {options[key]}"
                    self.option_buttons[i].disabled = False
                else:
                    self.option_buttons[i].text = ''
                    self.option_buttons[i].disabled = True
        
        # 重置选项按钮颜色
        for btn in self.option_buttons:
            btn.background_color = self.quiz_colors['default']
        
        # 清空选中
        self.selected_answers.clear()
        
        # 更新收藏和掌握状态
        self.update_status_buttons()

    def select_option(self, index):
        """选择选项"""
        if not self.quiz_engine:
            return
        
        question = self.quiz_engine.get_current_question()
        q_type = question.get('type', 'single')
        option_keys = ['A', 'B', 'C', 'D']
        
        if index >= len(option_keys):
            return
        
        selected_key = option_keys[index]
        
        if q_type == 'multiple':
            # 多选题可以选多个
            if selected_key in self.selected_answers:
                self.selected_answers.discard(selected_key)
                self.option_buttons[index].background_color = self.quiz_colors['default']
            else:
                self.selected_answers.add(selected_key)
                self.option_buttons[index].background_color = self.quiz_colors['selected']
        else:
            # 单选和判断只能选一个
            self.selected_answers.clear()
            self.selected_answers.add(selected_key)
            
            # 重置所有按钮颜色
            for btn in self.option_buttons:
                btn.background_color = self.quiz_colors['default']
            
            self.option_buttons[index].background_color = self.quiz_colors['selected']

    def submit_answer(self, instance):
        """提交答案"""
        if not self.quiz_engine:
            return
        
        # 如果是大题，直接跳过（不需要选择答案）
        question = self.quiz_engine.get_current_question()
        q_type = question.get('type', 'single')
        is_essay = (q_type == 'essay' or not question.get('options', {}))
        
        if is_essay:
            # 大题自动标记为正确并进入下一题
            self.quiz_engine.submit_answer('')  # 提交空答案
            popup = Popup(
                title='提示',
                content=Label(text='大题已跳过，请自行练习后查看答案解析', font_name='chinese', font_size=dp(16)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
            Clock.schedule_once(lambda dt: self.next_question(None), 1.5)
            return
        
        if not self.selected_answers:
            popup = Popup(
                title='提示',
                content=Label(text='请先选择一个答案', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        answer = ''.join(sorted(self.selected_answers))
        
        if self.quiz_engine.mode == 'immediate':
            # 即时反馈模式
            is_correct = self.quiz_engine.check_answer_immediate(answer)
            
            # 显示正确答案
            question = self.quiz_engine.get_current_question()
            correct_answer = question.get('answer', '')
            
            if is_correct:
                popup = Popup(
                    title='回答正确',
                    content=Label(text='✓ 正确！', font_name='chinese', font_size=dp(24), color=(0, 0.8, 0, 1)),
                    size_hint=(0.6, 0.3)
                )
            else:
                popup = Popup(
                    title='回答错误',
                    content=Label(
                        text=f'✗ 错误\n正确答案: {correct_answer}',
                        font_name='chinese',
                        font_size=dp(20),
                        color=(0.8, 0, 0, 1)
                    ),
                    size_hint=(0.6, 0.35)
                )
            
            # 记录错题
            if not is_correct:
                app = self.get_app()
                from database import Database
                db = Database()
                db.add_wrong_question(
                    app.current_user[0],
                    self.bank_name,
                    question.get('index', 0),
                    question.get('text', '')
                )
                db.close()
            
            popup.open()
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
            
            # 自动进入下一题
            Clock.schedule_once(lambda dt: self.next_question(None), 1.5)
        else:
            # 批量答题模式，只保存答案
            self.quiz_engine.submit_answer(answer)
            
            popup = Popup(
                title='提示',
                content=Label(text='答案已保存', font_name='chinese', font_size=dp(18)),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: popup.dismiss(), 1)

    def next_question(self, instance):
        """下一题"""
        if not self.quiz_engine:
            return
        
        if self.quiz_engine.next_question():
            self.update_display()
        else:
            # 答题结束
            self.finish_quiz()

    def previous_question(self, instance):
        """上一题"""
        if not self.quiz_engine:
            return
        
        if self.quiz_engine.current_index > 0:
            self.quiz_engine.current_index -= 1
            self.update_display()

    def finish_quiz(self):
        """完成答题"""
        results = self.quiz_engine.finish_quiz()
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # 保存记录和错题到数据库
        app = self.get_app()
        from database import Database
        db = Database()
        db.save_quiz_record(
            app.current_user[0],
            self.bank_name,
            results['total'],
            results['correct'],
            results['accuracy'],
            self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 保存错题到数据库
        wrong_questions_data = [r for r in results['results'] if not r['is_correct']]
        for result in wrong_questions_data:
            q = result['question']
            db.add_wrong_question(
                app.current_user[0],
                self.bank_name,
                q.get('index', 0),
                q.get('text', '')
            )
        
        db.close()
        
        # 构建结果界面
        result_layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        
        # 结果标题和统计
        result_text = (
            f"答题完成！\n"
            f"总题数: {results['total']} | 正确: {results['correct']} | "
            f"错误: {results['total'] - results['correct']} | "
            f"正确率: {results['accuracy']:.1f}% | 用时: {int(duration)}秒"
        )
        
        stats_label = Label(
            text=result_text,
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='middle'
        )
        stats_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        result_layout.add_widget(stats_label)
        
        # 错题详情区域
        if wrong_questions_data:
            wrong_title = Label(
                text=f'错题详情（共{len(wrong_questions_data)}题）',
                font_name='chinese',
                font_size=dp(16),
                color=(0.9, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(30),
                bold=True
            )
            result_layout.add_widget(wrong_title)
            
            # 错题滚动列表
            wrong_scroll = ScrollView(size_hint_y=0.5)
            wrong_content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
            wrong_content.bind(minimum_height=wrong_content.setter('height'))
            
            for i, result in enumerate(wrong_questions_data, 1):
                q = result['question']
                q_type = q.get('type', 'single')
                type_text = {'single': '单选', 'multiple': '多选', 'judge': '判断', 'essay': '大题'}.get(q_type, '单选')
                options = q.get('options', {})
                correct_answer = result['correct_answer']
                user_answer = result['user_answer']
                explanation = q.get('explanation', '')
                
                # 错题卡片
                card = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None,
                                 height=dp(40), padding=[dp(8), dp(5)])
                
                # 题目文本
                q_text = q.get('text', '')
                short_text = q_text[:60] + '...' if len(q_text) > 60 else q_text
                text_label = Label(
                    text=f"{i}. [{type_text}] {short_text}",
                    font_name='chinese',
                    font_size=dp(13),
                    color=(0, 0, 0, 1),
                    size_hint_y=None,
                    height=dp(22),
                    halign='left', valign='middle'
                )
                text_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                card.add_widget(text_label)
                
                # 答案对比
                if q_type == 'multiple':
                    user_display = ', '.join(sorted(list(user_answer))) if user_answer else '未作答'
                    correct_display = ', '.join(sorted(list(correct_answer)))
                else:
                    user_display = user_answer if user_answer else '未作答'
                    correct_display = correct_answer
                
                answer_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(20))
                
                user_ans_label = Label(
                    text=f"你的答案: {user_display}",
                    font_name='chinese',
                    font_size=dp(12),
                    color=(0.9, 0.3, 0.3, 1),
                    halign='left', valign='middle'
                )
                user_ans_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                answer_row.add_widget(user_ans_label)
                
                correct_ans_label = Label(
                    text=f"正确答案: {correct_display}",
                    font_name='chinese',
                    font_size=dp(12),
                    color=(0, 0.6, 0, 1),
                    halign='left', valign='middle'
                )
                correct_ans_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                answer_row.add_widget(correct_ans_label)
                
                card.add_widget(answer_row)
                
                # 查看详情按钮
                detail_btn = Button(
                    text='查看详情',
                    font_name='chinese',
                    font_size=dp(12),
                    size_hint_y=None,
                    height=dp(25),
                    background_color=(0.2, 0.6, 1, 1)
                )
                detail_btn.bind(on_press=lambda instance, question=q: self.show_wrong_detail_popup(question))
                card.add_widget(detail_btn)
                
                card.height = dp(70)
                wrong_content.add_widget(card)
            
            wrong_scroll.add_widget(wrong_content)
            result_layout.add_widget(wrong_scroll)
        else:
            # 全对提示
            perfect_label = Label(
                text='全部正确，太棒了！',
                font_name='chinese',
                font_size=dp(18),
                color=(0, 0.6, 0, 1),
                size_hint_y=None,
                height=dp(40)
            )
            result_layout.add_widget(perfect_label)
        
        # 底部按钮
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        main_btn = Button(text='返回首页', font_name='chinese', background_color=(0.6, 0.6, 0.6, 1))
        main_btn.bind(on_press=lambda x: popup.dismiss() if popup else None)
        main_btn.bind(on_press=lambda x: self.go_to_main())
        btn_layout.add_widget(main_btn)
        
        profile_btn = Button(text='查看错题记录', font_name='chinese', background_color=(0.9, 0.3, 0.3, 1))
        profile_btn.bind(on_press=lambda x: self.go_to_profile())
        btn_layout.add_widget(profile_btn)
        
        retry_btn = Button(text='再来一次', font_name='chinese', background_color=(0.2, 0.6, 1, 1))
        retry_btn.bind(on_press=lambda x: self.retry_quiz())
        btn_layout.add_widget(retry_btn)
        
        result_layout.add_widget(btn_layout)
        
        popup = Popup(title='答题结果', content=result_layout, size_hint=(0.95, 0.9))
        popup.open()
        self.result_popup = popup
    
    def show_wrong_detail_popup(self, question):
        """显示错题详情弹窗"""
        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10))
        
        q_type = question.get('type', 'single')
        type_text = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题', 'essay': '大题'}.get(q_type, '单选题')
        
        # 题目文本
        scroll = ScrollView(size_hint_y=0.35)
        text_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        text_layout.bind(minimum_height=text_layout.setter('height'))
        
        q_label = Label(
            text=f"[{type_text}] {question.get('text', '')}",
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            halign='left', valign='top', markup=True
        )
        q_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        q_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        text_layout.add_widget(q_label)
        scroll.add_widget(text_layout)
        content.add_widget(scroll)
        
        # 选项
        options = question.get('options', {})
        correct_answer = question.get('answer', '')
        if options:
            options_layout = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None,
                                       padding=[dp(5), dp(3)])
            
            for letter, opt_text in options.items():
                is_correct_option = letter in correct_answer if q_type == 'multiple' else letter == correct_answer
                opt_color = (0, 0.6, 0, 1) if is_correct_option else (0, 0, 0, 1)
                
                opt_label = Label(
                    text=f"{letter}. {opt_text}" + (" [正确]" if is_correct_option else ""),
                    font_name='chinese',
                    font_size=dp(14),
                    color=opt_color,
                    size_hint_y=None,
                    height=dp(22),
                    halign='left', valign='middle'
                )
                opt_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                options_layout.add_widget(opt_label)
            
            options_layout.bind(minimum_height=options_layout.setter('height'))
            content.add_widget(options_layout)
        
        # 答案和解析
        info_layout = BoxLayout(orientation='vertical', spacing=dp(3), size_hint_y=None,
                                padding=[dp(5), dp(3)])
        
        answer_label = Label(
            text=f"正确答案: {correct_answer}",
            font_name='chinese',
            font_size=dp(16),
            color=(0, 0.6, 0, 1),
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left', valign='middle'
        )
        answer_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        info_layout.add_widget(answer_label)
        
        explanation = question.get('explanation', '')
        if explanation:
            expl_label = Label(
                text=f"解析: {explanation}",
                font_name='chinese',
                font_size=dp(14),
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                halign='left', valign='top', markup=True
            )
            expl_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            expl_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
            info_layout.add_widget(expl_label)
        
        info_layout.bind(minimum_height=info_layout.setter('height'))
        content.add_widget(info_layout)
        
        # 关闭按钮
        close_btn = Button(text='关闭', font_name='chinese', size_hint_y=None, height=dp(40))
        close_btn.bind(on_press=lambda x: detail_popup.dismiss())
        content.add_widget(close_btn)
        
        detail_popup = Popup(title='错题详情', content=content, size_hint=(0.9, 0.85))
        detail_popup.open()
    
    def go_to_profile(self, *args):
        """跳转到个人中心"""
        if hasattr(self, 'result_popup'):
            self.result_popup.dismiss()
        self.manager.current = 'profile'
    
    def retry_quiz(self, *args):
        """重新刷题"""
        app = self.get_app()
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        bank_data = bank_manager.load_bank(self.bank_name)
        if not bank_data:
            return
        questions = [q for q in bank_data['questions'] if q.get('type', 'single') != 'essay']
        if not questions:
            return
        self.setup_quiz(questions, self.bank_name, self.quiz_engine.mode)

    def toggle_favorite(self, instance):
        """切换收藏状态"""
        if not self.quiz_engine:
            return
        
        question = self.quiz_engine.get_current_question()
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
        if not self.quiz_engine:
            return
        
        question = self.quiz_engine.get_current_question()
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

    def update_status_buttons(self):
        """更新状态按钮"""
        if not self.quiz_engine:
            return
        
        question = self.quiz_engine.get_current_question()
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

    def exit_quiz(self, instance):
        """退出刷题"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text='确定要退出吗？', font_name='chinese', font_size=dp(18)))
        
        btn_layout = BoxLayout(spacing=dp(10))
        
        yes_btn = Button(text='确定', font_name='chinese')
        btn_layout.add_widget(yes_btn)
        
        no_btn = Button(text='取消', font_name='chinese')
        btn_layout.add_widget(no_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='退出', content=content, size_hint=(0.8, 0.4))
        
        # 绑定按钮事件（使用闭包捕获 popup 引用）
        yes_btn.bind(on_press=lambda x: (popup.dismiss(), self.go_to_main()))
        no_btn.bind(on_press=lambda x: popup.dismiss())
        
        popup.open()

    def get_app(self):
        """获取App实例"""
        from kivy.app import App
        return App.get_running_app()
