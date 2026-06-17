import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database
from question_bank import QuestionBankManager
from quiz_engine import QuizEngine
from ai_template import AIQuestionTemplate
import json
import os
from datetime import datetime


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("白玉京考试周复习系统")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self.db = Database()
        self.bank_manager = QuestionBankManager()
        self.quiz_engine = QuizEngine()
        self.ai_template = AIQuestionTemplate()

        self.current_user = None
        self.current_bank = None

        self.setup_menu()
        self.setup_style()
        self.show_login_screen()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 关于菜单
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=about_menu)
        about_menu.add_command(label="应用信息", command=self.show_about)
        about_menu.add_separator()
        about_menu.add_command(label="退出", command=self.root.quit)

    def show_about(self):
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("关于")
        about_dialog.geometry("400x250")
        about_dialog.resizable(False, False)
        about_dialog.transient(self.root)
        about_dialog.grab_set()

        # 居中显示
        x = (about_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (250 // 2)
        about_dialog.geometry(f"+{x}+{y}")

        content_frame = ttk.Frame(about_dialog, padding=20)
        content_frame.pack(fill='both', expand=True)

        # 应用标题
        title_label = ttk.Label(content_frame, text="📚 白玉京考试周复习系统",
                               font=('Microsoft YaHei', 14, 'bold'), foreground='#3498db')
        title_label.pack(pady=(0, 15))

        # 详细信息
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=5)

        details = [
            ("版本号:", "V1.0.1"),
            ("作者:", "兲samsara"),
            ("更新日期:", "2026/6/10")
        ]

        for label, value in details:
            detail_frame = ttk.Frame(info_frame)
            detail_frame.pack(fill='x', pady=3)

            ttk.Label(detail_frame, text=label, font=('Microsoft YaHei', 10),
                     foreground='#34495e').pack(side='left')
            ttk.Label(detail_frame, text=value, font=('Microsoft YaHei', 10, 'bold'),
                     foreground='#2c3e50').pack(side='left', padx=(10, 0))

        # 版权信息
        copyright_label = ttk.Label(content_frame, text="© 2026 白玉京. All rights reserved.",
                                   font=('Microsoft YaHei', 8), foreground='#95a5a6')
        copyright_label.pack(pady=(15, 0))

        # 确定按钮
        ttk.Button(content_frame, text="确定", command=about_dialog.destroy).pack(pady=15)

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Microsoft YaHei', 10))
        style.configure('Title.TLabel', font=('Microsoft YaHei', 14, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei', 11), foreground='#34495e')

        # 增大按钮字体和内边距
        style.configure('TButton', font=('Microsoft YaHei', 10), padding=8)
        style.configure('Primary.TButton', font=('Microsoft YaHei', 11, 'bold'), padding=10)

        style.configure('Header.TFrame', background='#3498db')
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)

        style.map('TButton',
            background=[('active', '#2980b9'), ('!disabled', '#3498db')],
            foreground=[('disabled', '#95a5a6'), ('!disabled', 'white')]
        )


    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x', padx=20, pady=(20, 10))

        title_label = ttk.Label(header, text="📚 白玉京考试周复习系统", style='Title.TLabel', background='#3498db', foreground='white')
        title_label.pack(pady=20)

        card = ttk.Frame(main_frame, style='Card.TFrame')
        card.place(relx=0.5, rely=0.5, anchor='center', width=380, height=280)

        ttk.Label(card, text="用户登录", style='Subtitle.TLabel').pack(pady=15)

        input_frame = ttk.Frame(card)
        input_frame.pack(pady=8, padx=20, fill='x')

        ttk.Label(input_frame, text="用户名：").pack(anchor='w')
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(input_frame, textvariable=self.username_var, font=('Microsoft YaHei', 10))
        username_entry.pack(fill='x', pady=3)
        username_entry.bind('<Return>', lambda e: self.login())

        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="登录", command=self.login, style='Primary.TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="注册", command=self.register).pack(side='left', padx=5)

        user_list_frame = ttk.Frame(card)
        user_list_frame.pack(pady=8, padx=20, fill='both', expand=True)

        ttk.Label(user_list_frame, text="已有用户：", font=('Microsoft YaHei', 9)).pack(anchor='w')

        users = self.db.get_all_users()
        if users:
            for user in users[:5]:
                btn = ttk.Button(user_list_frame, text=user[1],
                               command=lambda u=user[1]: self.quick_login(u))
                btn.pack(fill='x', pady=2)

    def quick_login(self, username):
        self.username_var.set(username)
        self.login()

    def login(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("提示", "请输入用户名")
            return

        user = self.db.get_user(username)
        if user:
            self.current_user = user
            self.show_main_interface()
        else:
            messagebox.showerror("错误", "用户不存在，请先注册")

    def register(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("提示", "请输入用户名")
            return

        if self.db.add_user(username):
            messagebox.showinfo("成功", "注册成功！请登录")
        else:
            messagebox.showerror("错误", "用户名已存在")

    def show_main_interface(self):
        self.root.state('normal')
        self.root.geometry("1000x700")

        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text=f"欢迎，{self.current_user[1]}！",
                 style='Title.TLabel', background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="关于", command=self.show_about).pack(side='right', padx=8, pady=8)
        ttk.Button(header, text="个人中心", command=self.show_profile).pack(side='right', padx=8, pady=8)
        ttk.Button(header, text="退出登录", command=self.logout).pack(side='right', padx=8, pady=8)

        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill='x', padx=15, pady=8)

        buttons = [
            (" 题库管理", self.show_bank_management),
            ("✏️ 开始刷题", self.show_quiz_selection),
            ("🔄 题目复习", self.show_review_selection),
            ("🤖 AI模板", self.show_ai_template)
        ]

        for text, command in buttons:
            btn = ttk.Button(nav_frame, text=text, command=command, style='Primary.TButton')
            btn.pack(side='left', padx=4, pady=4, ipadx=8, ipady=3)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        banks = self.bank_manager.list_banks()

        info_card = ttk.Frame(content_frame, style='Card.TFrame')
        info_card.pack(fill='both', expand=True, padx=8, pady=8)

        ttk.Label(info_card, text="可用题库", style='Subtitle.TLabel').pack(anchor='w', padx=8, pady=8)

        if banks:
            for bank in banks:
                bank_frame = ttk.Frame(info_card)
                bank_frame.pack(fill='x', padx=8, pady=3)

                ttk.Label(bank_frame, text=f"📄 {bank}", font=('Microsoft YaHei', 9)).pack(side='left')
        else:
            ttk.Label(info_card, text="暂无题库，请先创建或导入",
                     font=('Microsoft YaHei', 9), foreground='#95a5a6').pack(pady=15)

    def logout(self):
        self.current_user = None
        self.current_bank = None
        self.show_login_screen()

    def show_bank_management(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text="题库管理", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="返回", command=self.show_main_interface).pack(side='right', padx=8, pady=8)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill='x', pady=8)

        ttk.Button(btn_frame, text="新建题库", command=self.create_bank).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="导入题库", command=self.import_bank).pack(side='left', padx=4)

        banks = self.bank_manager.list_banks()

        for bank in banks:
            bank_card = ttk.Frame(content_frame, style='Card.TFrame')
            bank_card.pack(fill='x', pady=4, padx=4)

            bank_info = ttk.Frame(bank_card)
            bank_info.pack(fill='x', padx=8, pady=6)

            ttk.Label(bank_info, text=f"📄 {bank}", font=('Microsoft YaHei', 10, 'bold')).pack(side='left')

            btn_group = ttk.Frame(bank_info)
            btn_group.pack(side='right')

            ttk.Button(btn_group, text="编辑", command=lambda b=bank: self.edit_bank(b)).pack(side='left', padx=2)
            ttk.Button(btn_group, text="删除", command=lambda b=bank: self.delete_bank(b)).pack(side='left', padx=2)

    def create_bank(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建题库")
        dialog.geometry("350x180")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="题库名称：").pack(pady=15)

        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=25).pack(pady=3)

        def confirm():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入题库名称")
                return

            if self.bank_manager.create_bank(name):
                messagebox.showinfo("成功", "题库创建成功")
                dialog.destroy()
                self.show_bank_management()
            else:
                messagebox.showerror("错误", "题库已存在")

        ttk.Button(dialog, text="确定", command=confirm).pack(pady=15)

    def delete_bank(self, bank_name):
        if messagebox.askyesno("确认", f"确定要删除题库 '{bank_name}' 吗？"):
            self.bank_manager.delete_bank(bank_name)
            messagebox.showinfo("成功", "删除成功")
            self.show_bank_management()

    def edit_bank(self, bank_name):
        self.current_bank = bank_name
        bank_data = self.bank_manager.load_bank(bank_name)

        if not bank_data:
            messagebox.showerror("错误", "题库加载失败")
            return

        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text=f"编辑题库：{bank_name}", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="保存", command=lambda: self.save_bank_changes(bank_data)).pack(side='right', padx=8, pady=8)
        ttk.Button(header, text="返回", command=self.show_bank_management).pack(side='right', padx=8, pady=8)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        ttk.Button(content_frame, text="添加题目", command=lambda: self.add_question_dialog(bank_data)).pack(pady=8)

        list_frame = ttk.Frame(content_frame)
        list_frame.pack(fill='both', expand=True, pady=8)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=canvas.yview)

        questions_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=questions_frame, anchor='nw')

        questions = bank_data.get('questions', [])

        for i, q in enumerate(questions):
            q_frame = ttk.Frame(questions_frame, style='Card.TFrame')
            q_frame.pack(fill='x', pady=4, padx=4)

            type_map = {'single': '单选', 'multiple': '多选', 'judge': '判断', 'essay': '大题'}
            q_type = type_map.get(q.get('type', ''), '未知')

            ttk.Label(q_frame, text=f"{i+1}. [{q_type}] {q.get('text', '')[:50]}...",
                     font=('Microsoft YaHei', 9)).pack(anchor='w', padx=8, pady=4)

            btn_frame = ttk.Frame(q_frame)
            btn_frame.pack(anchor='e', padx=8, pady=4)

            ttk.Button(btn_frame, text="编辑", command=lambda idx=i: self.edit_question_dialog(bank_data, idx)).pack(side='left', padx=2)
            ttk.Button(btn_frame, text="删除", command=lambda idx=i: self.delete_question(bank_data, idx)).pack(side='left', padx=2)

        questions_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))

    def add_question_dialog(self, bank_data):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加题目")
        dialog.geometry("550x480")
        dialog.transient(self.root)
        dialog.grab_set()

        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=15, pady=8)

        ttk.Label(form_frame, text="题型：").pack(anchor='w')
        type_var = tk.StringVar(value='single')
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, values=['single', 'multiple', 'judge', 'essay'], state='readonly')
        type_combo.pack(fill='x', pady=3)

        ttk.Label(form_frame, text="题目：").pack(anchor='w')
        text_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=text_var).pack(fill='x', pady=3)

        ttk.Label(form_frame, text="选项（每行一个，格式：A.选项内容）：").pack(anchor='w')
        options_text = tk.Text(form_frame, height=5)
        options_text.pack(fill='x', pady=3)

        ttk.Label(form_frame, text="答案：").pack(anchor='w')
        answer_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=answer_var).pack(fill='x', pady=3)

        ttk.Label(form_frame, text="解析：").pack(anchor='w')
        explanation_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=explanation_var).pack(fill='x', pady=3)

        def confirm():
            question = {
                'index': len(bank_data['questions']) + 1,
                'type': type_var.get(),
                'text': text_var.get(),
                'options': {},
                'answer': answer_var.get(),
                'explanation': explanation_var.get()
            }

            if question['type'] in ['single', 'multiple', 'judge']:
                options_lines = options_text.get('1.0', 'end').strip().split('\n')
                for line in options_lines:
                    if '.' in line:
                        parts = line.split('.', 1)
                        if len(parts) == 2:
                            question['options'][parts[0].strip()] = parts[1].strip()

            bank_data['questions'].append(question)
            messagebox.showinfo("成功", "题目添加成功")
            dialog.destroy()
            self.edit_bank(self.current_bank)

        ttk.Button(dialog, text="确定", command=confirm).pack(pady=8)

    def edit_question_dialog(self, bank_data, index):
        question = bank_data['questions'][index]

        dialog = tk.Toplevel(self.root)
        dialog.title("编辑题目")
        dialog.geometry("550x480")
        dialog.transient(self.root)
        dialog.grab_set()

        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=15, pady=8)

        ttk.Label(form_frame, text="题型：").pack(anchor='w')
        type_var = tk.StringVar(value=question.get('type', 'single'))
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, values=['single', 'multiple', 'judge', 'essay'], state='readonly')
        type_combo.pack(fill='x', pady=3)

        ttk.Label(form_frame, text="题目：").pack(anchor='w')
        text_var = tk.StringVar(value=question.get('text', ''))
        ttk.Entry(form_frame, textvariable=text_var).pack(fill='x', pady=3)

        ttk.Label(form_frame, text="选项（每行一个，格式：A.选项内容）：").pack(anchor='w')
        options_text = tk.Text(form_frame, height=5)
        options_text.pack(fill='x', pady=3)

        options = question.get('options', {})
        for letter, content in options.items():
            options_text.insert('end', f"{letter}.{content}\n")

        ttk.Label(form_frame, text="答案：").pack(anchor='w')
        answer_var = tk.StringVar(value=question.get('answer', ''))
        ttk.Entry(form_frame, textvariable=answer_var).pack(fill='x', pady=3)

        ttk.Label(form_frame, text="解析：").pack(anchor='w')
        explanation_var = tk.StringVar(value=question.get('explanation', ''))
        ttk.Entry(form_frame, textvariable=explanation_var).pack(fill='x', pady=3)

        def confirm():
            updated_question = {
                'index': index + 1,
                'type': type_var.get(),
                'text': text_var.get(),
                'options': {},
                'answer': answer_var.get(),
                'explanation': explanation_var.get()
            }

            if updated_question['type'] in ['single', 'multiple', 'judge']:
                options_lines = options_text.get('1.0', 'end').strip().split('\n')
                for line in options_lines:
                    if '.' in line:
                        parts = line.split('.', 1)
                        if len(parts) == 2:
                            updated_question['options'][parts[0].strip()] = parts[1].strip()

            bank_data['questions'][index] = updated_question
            messagebox.showinfo("成功", "题目更新成功")
            dialog.destroy()
            self.edit_bank(self.current_bank)

        ttk.Button(dialog, text="确定", command=confirm).pack(pady=8)

    def delete_question(self, bank_data, index):
        if messagebox.askyesno("确认", "确定要删除这道题吗？"):
            bank_data['questions'].pop(index)
            self.bank_manager.save_bank(bank_data)
            self.edit_bank(self.current_bank)

    def save_bank_changes(self, bank_data):
        self.bank_manager.save_bank(bank_data)
        messagebox.showinfo("成功", "题库保存成功")
        self.show_bank_management()

    def import_bank(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(title="选择题库文件", filetypes=[("JSON文件", "*.json")])

        if file_path:
            try:
                bank_name = self.bank_manager.import_from_json(file_path)
                messagebox.showinfo("成功", f"题库导入成功：{bank_name}")
                self.show_bank_management()
            except Exception as e:
                messagebox.showerror("错误", f"导入失败：{str(e)}")

    def show_quiz_selection(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text="选择题库开始刷题", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="返回", command=self.show_main_interface).pack(side='right', padx=8, pady=8)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        settings_frame = ttk.LabelFrame(content_frame, text="刷题设置", padding=8)
        settings_frame.pack(fill='x', pady=8)

        self.shuffle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="随机打乱选项顺序", variable=self.shuffle_var).pack(anchor='w', pady=3)

        self.shuffle_questions_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="随机打乱题目顺序", variable=self.shuffle_questions_var).pack(anchor='w', pady=3)

        self.mode_var = tk.StringVar(value='immediate')
        ttk.Radiobutton(settings_frame, text="即时判题（每题立即显示对错）",
                       variable=self.mode_var, value='immediate').pack(anchor='w', pady=3)
        ttk.Radiobutton(settings_frame, text="批量判题（全部做完后统一判分）",
                       variable=self.mode_var, value='batch').pack(anchor='w', pady=3)

        banks = self.bank_manager.list_banks()

        for bank in banks:
            bank_btn = ttk.Button(content_frame, text=f"📄 {bank}",
                                 command=lambda b=bank: self.start_quiz(b),
                                 style='Primary.TButton')
            bank_btn.pack(fill='x', pady=4, padx=8)

    def start_quiz(self, bank_name):
        bank_data = self.bank_manager.load_bank(bank_name)
        if not bank_data:
            messagebox.showerror("错误", "题库加载失败")
            return

        questions = [q for q in bank_data['questions'] if q.get('type') != 'essay']

        if not questions:
            messagebox.showwarning("提示", "该题库没有可刷的题目")
            return

        shuffle = self.shuffle_var.get()
        shuffle_questions = self.shuffle_questions_var.get()
        mode = self.mode_var.get()

        total = self.quiz_engine.start_quiz(questions, mode=mode, shuffle_options=shuffle, shuffle_questions=shuffle_questions)

        self.current_bank = bank_name
        self.quiz_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.root.state('zoomed')

        self.show_quiz_interface()

    def show_quiz_interface(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        progress = self.quiz_engine.get_progress()

        ttk.Label(header, text=f"刷题中 - 第{progress['current']}/{progress['total']}题",
                 style='Title.TLabel', background='#3498db', foreground='white').pack(side='left', padx=20, pady=8)

        ttk.Button(header, text="结束", command=self.end_quiz).pack(side='right', padx=8, pady=5)

        # 中间内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=5)

        question = self.quiz_engine.get_current_question()
        if not question:
            return

        # 创建可滚动的题目区域
        scroll_frame = ttk.Frame(content_frame)
        scroll_frame.pack(fill='both', expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side='right', fill='y')

        canvas = tk.Canvas(scroll_frame, yscrollcommand=scrollbar.set, bg='white')
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=canvas.yview)

        # 题目内容框架
        q_card = ttk.Frame(canvas, style='Card.TFrame')
        canvas.create_window((0, 0), window=q_card, anchor='nw', width=canvas.winfo_reqwidth())

        # 绑定Canvas大小变化
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)

        canvas.bind('<Configure>', configure_scroll_region)

        type_map = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题'}
        q_type = type_map.get(question.get('type', ''), '未知')

        ttk.Label(q_card, text=f"[{q_type}]", font=('Microsoft YaHei', 11, 'bold'),
                 foreground='#e74c3c').pack(anchor='w', padx=15, pady=(15, 8))

        ttk.Label(q_card, text=question.get('text', ''),
                 font=('Microsoft YaHei', 12), wraplength=850, justify='left').pack(anchor='w', padx=15, pady=8)

        options_frame = ttk.Frame(q_card)
        options_frame.pack(fill='x', padx=15, pady=10)

        self.answer_var = tk.StringVar()

        options = question.get('options', {})

        if question.get('type') == 'multiple':
            self.answer_vars = {}
            for letter, text in options.items():
                var = tk.BooleanVar()
                self.answer_vars[letter] = var
                cb = ttk.Checkbutton(options_frame, text=f"{letter}. {text}", variable=var,
                                    style='TCheckbutton')
                cb.pack(anchor='w', pady=5, padx=5)
        else:
            for letter, text in options.items():
                rb = ttk.Radiobutton(options_frame, text=f"{letter}. {text}",
                                    variable=self.answer_var, value=letter)
                rb.pack(anchor='w', pady=5, padx=5)

        # 底部按钮区域 - 固定在底部，更大更易点击
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill='x', padx=15, pady=10)

        # 收藏按钮
        self.is_favorite = self.db.is_favorite(self.current_user[0], self.current_bank, question.get('index', 0))
        self.favorite_btn = ttk.Button(bottom_frame, text="⭐ 取消收藏" if self.is_favorite else "☆ 收藏",
                                      command=self.toggle_favorite)
        self.favorite_btn.pack(side='left', padx=5, ipadx=15, ipady=8)

        # 上一题按钮
        ttk.Button(bottom_frame, text="上一题", command=self.prev_question).pack(side='left', padx=5, ipadx=15, ipady=8)

        # 提交/下一题按钮（右侧）
        if self.quiz_engine.mode == 'immediate':
            self.submit_btn = ttk.Button(bottom_frame, text="提交答案", command=self.submit_immediate_answer,
                          style='Primary.TButton')
            self.submit_btn.pack(side='right', padx=5, ipadx=20, ipady=8)
        else:
            ttk.Button(bottom_frame, text="下一题", command=self.next_batch_question,
                      style='Primary.TButton').pack(side='right', padx=5, ipadx=20, ipady=8)

        # 结果显示区域
        self.result_label = ttk.Label(bottom_frame, text="", font=('Microsoft YaHei', 11))
        self.result_label.pack(pady=5)




    def toggle_favorite(self):
        question = self.quiz_engine.get_current_question()
        if not question:
            return

        index = question.get('index', 0)

        if self.is_favorite:
            self.db.remove_favorite(self.current_user[0], self.current_bank, index)
            self.is_favorite = False
            self.favorite_btn.config(text="☆ 收藏")
            messagebox.showinfo("提示", "已取消收藏")
        else:
            self.db.add_favorite(self.current_user[0], self.current_bank, index, question.get('text', ''))
            self.is_favorite = True
            self.favorite_btn.config(text="⭐ 取消收藏")
            messagebox.showinfo("提示", "收藏成功")

    def submit_immediate_answer(self):
        question = self.quiz_engine.get_current_question()
        if not question:
            return

        if question.get('type') == 'multiple':
            selected = [letter for letter, var in self.answer_vars.items() if var.get()]
            answer = ''.join(sorted(selected))
        else:
            answer = self.answer_var.get()

        if not answer:
            messagebox.showwarning("提示", "请选择答案")
            return

        is_correct = self.quiz_engine.check_answer_immediate(answer)

        if not is_correct:
            self.db.add_wrong_question(self.current_user[0], self.current_bank,
                                       question.get('index', 0), question.get('text', ''))

        if is_correct:
            self.result_label.config(text="✓ 回答正确！", foreground='#27ae60')
        else:
            correct = question.get('answer', '')
            # 多选题答案格式化显示
            if question.get('type') == 'multiple':
                # 将字符串答案拆分成列表并格式化
                correct_list = sorted(list(correct))
                answer_list = sorted(list(answer)) if answer else []

                correct_display = ', '.join(correct_list)
                answer_display = ', '.join(answer_list) if answer_list else '未作答'

                self.result_label.config(text=f"✗ 回答错误！你的答案：{answer_display} | 正确答案：{correct_display}",
                                         foreground='#e74c3c')
            else:
                self.result_label.config(text=f"✗ 回答错误！正确答案：{correct}", foreground='#e74c3c')

        # 禁用提交按钮
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button) and btn.cget('text') == '提交答案':
                                btn.config(state='disabled', text='已提交')

        # 显示下一题按钮
        ttk.Button(self.result_label.master, text="下一题 →", command=self.next_immediate_question,
                  style='Primary.TButton').pack(side='right', padx=3)


    def prev_question(self):
        if self.quiz_engine.current_index > 0:
            self.quiz_engine.current_index -= 1
            self.show_quiz_interface()
        else:
            messagebox.showinfo("提示", "已经是第一题了")

    def next_immediate_question(self):
        for widget in self.result_label.master.winfo_children():
            if isinstance(widget, ttk.Button) and '下一题' in widget.cget('text'):
                widget.destroy()

        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button) and btn.cget('text') == '已提交':
                                btn.config(state='normal', text='提交答案')

        self.result_label.config(text="")

        has_next = self.quiz_engine.next_question()

        if has_next:
            self.show_quiz_interface()
        else:
            self.finish_quiz()

    def next_batch_question(self):
        question = self.quiz_engine.get_current_question()

        if question.get('type') == 'multiple':
            selected = [letter for letter, var in self.answer_vars.items() if var.get()]
            answer = ''.join(selected)
        else:
            answer = self.answer_var.get()

        self.quiz_engine.submit_answer(answer)

        has_next = self.quiz_engine.next_question()

        if has_next:
            self.show_quiz_interface()
        else:
            self.finish_quiz()

    def end_quiz(self):
        if messagebox.askyesno("确认", "确定要结束本次刷题吗？"):
            self.finish_quiz()

    def finish_quiz(self):
        results = self.quiz_engine.finish_quiz()

        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.db.save_quiz_record(
            self.current_user[0],
            self.current_bank,
            results['total'],
            results['correct'],
            results['accuracy'],
            self.quiz_start_time,
            end_time
        )

        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text="刷题完成", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        result_card = ttk.Frame(content_frame, style='Card.TFrame')
        result_card.pack(fill='x', pady=8)

        ttk.Label(result_card, text="本次成绩", style='Subtitle.TLabel').pack(pady=8)

        stats_frame = ttk.Frame(result_card)
        stats_frame.pack(pady=8)

        ttk.Label(stats_frame, text=f"总题数：{results['total']}", font=('Microsoft YaHei', 10)).pack(pady=2)
        ttk.Label(stats_frame, text=f"正确数：{results['correct']}", font=('Microsoft YaHei', 10)).pack(pady=2)
        ttk.Label(stats_frame, text=f"正确率：{results['accuracy']:.2f}%",
                 font=('Microsoft YaHei', 11, 'bold'), foreground='#27ae60').pack(pady=2)

        wrong_questions = [r for r in results['results'] if not r['is_correct']]

        if wrong_questions:
            wrong_card = ttk.Frame(content_frame, style='Card.TFrame')
            wrong_card.pack(fill='both', pady=8)

            ttk.Label(wrong_card, text=f"❌ 错题详情（共{len(wrong_questions)}题）",
                     style='Subtitle.TLabel', foreground='#e74c3c').pack(anchor='w', padx=8, pady=8)

            wrong_list_frame = ttk.Frame(wrong_card)
            wrong_list_frame.pack(fill='both', expand=True, padx=8, pady=3)

            scrollbar = ttk.Scrollbar(wrong_list_frame)
            scrollbar.pack(side='right', fill='y')

            canvas = tk.Canvas(wrong_list_frame, yscrollcommand=scrollbar.set)
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=canvas.yview)

            wrong_content_frame = ttk.Frame(canvas)
            canvas.create_window((0, 0), window=wrong_content_frame, anchor='nw')

            for i, result in enumerate(wrong_questions, 1):
                q = result['question']

                wrong_item = ttk.Frame(wrong_content_frame, style='Card.TFrame')
                wrong_item.pack(fill='x', pady=4, padx=4)

                ttk.Label(wrong_item, text=f"{i}. {q.get('text', '')}",
                         font=('Microsoft YaHei', 9, 'bold'), wraplength=850, justify='left').pack(anchor='w', padx=8, pady=4)

                # 显示选项
                options = q.get('options', {})
                if options:
                    options_frame = ttk.Frame(wrong_item)
                    options_frame.pack(fill='x', padx=12, pady=2)

                    for letter, text in options.items():
                        ttk.Label(options_frame, text=f"{letter}. {text}",
                                 font=('Microsoft YaHei', 9), wraplength=800, justify='left').pack(anchor='w', pady=1)

                info_frame = ttk.Frame(wrong_item)
                info_frame.pack(fill='x', padx=12, pady=4)

                # 格式化显示答案
                user_answer = result['user_answer']
                correct_answer = result['correct_answer']

                if q.get('type') == 'multiple':
                    # 多选题答案格式化 - 将字符串拆分成字符列表
                    if user_answer and user_answer.strip():
                        # 将字符串 "ABC" 转换成列表 ['A', 'B', 'C']
                        user_list = sorted(list(user_answer.strip()))
                        user_display = ', '.join(user_list)
                    else:
                        user_display = '未作答'

                    # 正确答案也是字符串，需要拆分
                    correct_list = sorted(list(correct_answer.strip()))
                    correct_display = ', '.join(correct_list)

                    ttk.Label(info_frame, text=f"你的答案：{user_display}",
                             font=('Microsoft YaHei', 9, 'bold'), foreground='#e74c3c').pack(side='left', padx=4)
                    ttk.Label(info_frame, text=f"正确答案：{correct_display}",
                             font=('Microsoft YaHei', 9, 'bold'), foreground='#27ae60').pack(side='left', padx=4)
                else:
                    ttk.Label(info_frame, text=f"你的答案：{user_answer if user_answer else '未作答'}",
                             font=('Microsoft YaHei', 9, 'bold'), foreground='#e74c3c').pack(side='left', padx=4)
                    ttk.Label(info_frame, text=f"正确答案：{correct_answer}",
                             font=('Microsoft YaHei', 9, 'bold'), foreground='#27ae60').pack(side='left', padx=4)

                explanation = q.get('explanation', '')
                if explanation:
                    ttk.Label(wrong_item, text=f"解析：{explanation}",
                             font=('Microsoft YaHei', 9), foreground='#34495e',
                             wraplength=850, justify='left').pack(anchor='w', padx=12, pady=4)

            wrong_content_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox('all'))

        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="返回首页", command=self.show_main_interface).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="再来一次", command=lambda: self.start_quiz(self.current_bank)).pack(side='left', padx=4)

    def show_review_selection(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text="题目复习", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="返回", command=self.show_main_interface).pack(side='right', padx=8, pady=8)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        ttk.Label(content_frame, text="选择题库：", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=8)

        banks = self.bank_manager.list_banks()
        self.review_bank_var = tk.StringVar()

        if banks:
            bank_combo = ttk.Combobox(content_frame, textvariable=self.review_bank_var, values=banks, state='readonly')
            bank_combo.pack(fill='x', pady=3)
            bank_combo.set(banks[0])

        ttk.Label(content_frame, text="复习模式：", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(15, 8))

        modes = [
            ("全部题目", "all"),
            ("错题本", "wrong"),
            ("收藏夹", "favorite"),
            ("随机抽题", "random")
        ]

        self.review_mode_var = tk.StringVar(value="all")

        for text, value in modes:
            ttk.Radiobutton(content_frame, text=text, variable=self.review_mode_var, value=value).pack(anchor='w', pady=2)

        ttk.Label(content_frame, text="题目类型（可多选）：", font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(15, 8))

        self.review_type_vars = {
            'single': tk.BooleanVar(value=True),
            'multiple': tk.BooleanVar(value=True),
            'judge': tk.BooleanVar(value=True),
            'essay': tk.BooleanVar(value=True)
        }

        type_checkboxes = ttk.Frame(content_frame)
        type_checkboxes.pack(fill='x', pady=3)

        ttk.Checkbutton(type_checkboxes, text="单选题", variable=self.review_type_vars['single']).pack(side='left', padx=5)
        ttk.Checkbutton(type_checkboxes, text="多选题", variable=self.review_type_vars['multiple']).pack(side='left', padx=5)
        ttk.Checkbutton(type_checkboxes, text="判断题", variable=self.review_type_vars['judge']).pack(side='left', padx=5)
        ttk.Checkbutton(type_checkboxes, text="大题", variable=self.review_type_vars['essay']).pack(side='left', padx=5)

        ttk.Button(content_frame, text="开始复习", command=self.start_review,
                  style='Primary.TButton').pack(pady=20, ipadx=15, ipady=8)

    def start_review(self):
        bank_name = self.review_bank_var.get()
        mode = self.review_mode_var.get()

        if not bank_name:
            messagebox.showwarning("提示", "请选择题库")
            return

        bank_data = self.bank_manager.load_bank(bank_name)
        if not bank_data:
            messagebox.showerror("错误", "题库加载失败")
            return

        questions = bank_data['questions']

        selected_types = [qtype for qtype, var in self.review_type_vars.items() if var.get()]

        if not selected_types:
            messagebox.showwarning("提示", "请至少选择一种题目类型")
            return

        questions = [q for q in questions if q.get('type', '') in selected_types]

        if mode == 'wrong':
            wrong_list = self.db.get_wrong_questions(self.current_user[0], bank_name)
            wrong_indices = [w[3] for w in wrong_list]
            questions = [q for q in questions if q.get('index', 0) in wrong_indices]
        elif mode == 'favorite':
            fav_list = self.db.get_favorites(self.current_user[0], bank_name)
            fav_indices = [f[3] for f in fav_list]
            questions = [q for q in questions if q.get('index', 0) in fav_indices]
        elif mode == 'random':
            import random
            random.shuffle(questions)
            questions = questions[:20]

        if not questions:
            messagebox.showwarning("提示", "没有符合条件的题目")
            return

        self.review_questions = questions
        self.review_index = 0
        self.current_review_bank = bank_name

        self.show_review_interface()

    def show_review_interface(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text=f"复习中 - 第{self.review_index + 1}/{len(self.review_questions)}题",
                 style='Title.TLabel', background='#3498db', foreground='white').pack(side='left', padx=20, pady=8)

        ttk.Button(header, text="返回", command=self.show_review_selection).pack(side='right', padx=8, pady=5)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=5)

        question = self.review_questions[self.review_index]

        q_card = ttk.Frame(content_frame, style='Card.TFrame')
        q_card.pack(fill='both', expand=True, padx=5, pady=5)

        type_map = {'single': '单选题', 'multiple': '多选题', 'judge': '判断题', 'essay': '大题'}
        q_type = type_map.get(question.get('type', ''), '未知')

        ttk.Label(q_card, text=f"[{q_type}]", font=('Microsoft YaHei', 10, 'bold'),
                 foreground='#3498db').pack(anchor='w', padx=10, pady=(6, 2))

        ttk.Label(q_card, text=question.get('text', ''),
                 font=('Microsoft YaHei', 11), wraplength=900, justify='left').pack(anchor='w', padx=10, pady=3)

        if question.get('type') != 'essay':
            options = question.get('options', {})
            for letter, text in options.items():
                ttk.Label(q_card, text=f"{letter}. {text}",
                         font=('Microsoft YaHei', 10)).pack(anchor='w', padx=25, pady=2)

        self.answer_frame = ttk.Frame(q_card)
        self.answer_frame.pack(fill='x', padx=10, pady=5)

        self.show_answer = False

        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=6)

        ttk.Button(btn_frame, text="显示答案", command=self.toggle_answer).pack(side='left', padx=3)

        is_mastered = self.db.is_mastered(self.current_user[0], self.current_review_bank, question.get('index', 0))
        self.mastered_btn = ttk.Button(btn_frame, text="✓ 已掌握" if is_mastered else "○ 标记掌握",
                                      command=self.toggle_mastered)
        self.mastered_btn.pack(side='left', padx=3)

        is_fav = self.db.is_favorite(self.current_user[0], self.current_review_bank, question.get('index', 0))
        ttk.Button(btn_frame, text="⭐ 取消收藏" if is_fav else "☆ 收藏",
                  command=lambda: self.toggle_review_favorite(question)).pack(side='left', padx=3)

        ttk.Button(btn_frame, text="上一题", command=self.prev_review_question).pack(side='left', padx=3)
        ttk.Button(btn_frame, text="下一题", command=self.next_review_question).pack(side='left', padx=3)

    def toggle_answer(self):
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        if not self.show_answer:
            question = self.review_questions[self.review_index]

            ttk.Label(self.answer_frame, text=f"答案：{question.get('answer', '')}",
                     font=('Microsoft YaHei', 10, 'bold'), foreground='#27ae60').pack(anchor='w', pady=3)

            explanation = question.get('explanation', '')
            if explanation:
                ttk.Label(self.answer_frame, text=f"解析：{explanation}",
                         font=('Microsoft YaHei', 9), wraplength=900, justify='left').pack(anchor='w', pady=3)

            self.show_answer = True
        else:
            self.show_answer = False

    def toggle_mastered(self):
        question = self.review_questions[self.review_index]
        index = question.get('index', 0)

        is_mastered = self.db.is_mastered(self.current_user[0], self.current_review_bank, index)

        if is_mastered:
            self.db.unmark_mastered(self.current_user[0], self.current_review_bank, index)
            self.mastered_btn.config(text="○ 标记掌握")
        else:
            self.db.mark_mastered(self.current_user[0], self.current_review_bank, index)
            self.mastered_btn.config(text="✓ 已掌握")

            self.db.remove_wrong_question(self.current_user[0], self.current_review_bank, index)

    def toggle_review_favorite(self, question):
        index = question.get('index', 0)

        is_fav = self.db.is_favorite(self.current_user[0], self.current_review_bank, index)

        if is_fav:
            self.db.remove_favorite(self.current_user[0], self.current_review_bank, index)
            messagebox.showinfo("提示", "已取消收藏")
        else:
            self.db.add_favorite(self.current_user[0], self.current_review_bank, index, question.get('text', ''))
            messagebox.showinfo("提示", "收藏成功")

        self.show_review_interface()

    def prev_review_question(self):
        if self.review_index > 0:
            self.review_index -= 1
            self.show_answer = False
            self.show_review_interface()

    def next_review_question(self):
        if self.review_index < len(self.review_questions) - 1:
            self.review_index += 1
            self.show_answer = False
            self.show_review_interface()
        else:
            messagebox.showinfo("提示", "已经是最后一题了")

    def show_ai_template(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text="AI题库生成助手", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="返回", command=self.show_main_interface).pack(side='right', padx=8, pady=8)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill='both', expand=True, pady=8)

        good_tab = ttk.Frame(notebook)
        notebook.add(good_tab, text="正确模板")

        good_text = tk.Text(good_tab, wrap='word', font=('Consolas', 9))
        good_text.pack(fill='both', expand=True, padx=8, pady=8)
        good_text.insert('1.0', self.ai_template.get_template())
        good_text.config(state='disabled')

        bad_tab = ttk.Frame(notebook)
        notebook.add(bad_tab, text="错误示例")

        bad_text = tk.Text(bad_tab, wrap='word', font=('Consolas', 9))
        bad_text.pack(fill='both', expand=True, padx=8, pady=8)
        bad_text.insert('1.0', self.ai_template.get_bad_example())
        bad_text.config(state='disabled')

        copy_btn = ttk.Button(content_frame, text="复制模板到剪贴板", command=lambda: self.copy_to_clipboard(self.ai_template.get_template()))
        copy_btn.pack(pady=8)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("成功", "已复制到剪贴板")

    def show_profile(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        header = ttk.Frame(main_frame, style='Header.TFrame')
        header.pack(fill='x')

        ttk.Label(header, text="个人中心", style='Title.TLabel',
                 background='#3498db', foreground='white').pack(side='left', padx=20, pady=12)

        ttk.Button(header, text="返回", command=self.show_main_interface).pack(side='right', padx=8, pady=8)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=15, pady=8)

        stats = self.db.get_user_stats(self.current_user[0])

        stats_card = ttk.Frame(content_frame, style='Card.TFrame')
        stats_card.pack(fill='x', pady=8)

        ttk.Label(stats_card, text="学习统计", style='Subtitle.TLabel').pack(anchor='w', padx=8, pady=8)

        stats_frame = ttk.Frame(stats_card)
        stats_frame.pack(fill='x', padx=15, pady=8)

        total_tests = stats[0] or 0
        total_questions = stats[1] or 0
        total_correct = stats[2] or 0
        avg_accuracy = stats[3] or 0

        stat_items = [
            ("刷题次数", total_tests),
            ("总题数", total_questions),
            ("正确数", total_correct),
            ("平均正确率", f"{avg_accuracy:.2f}%")
        ]

        for label, value in stat_items:
            item_frame = ttk.Frame(stats_frame)
            item_frame.pack(fill='x', pady=2)

            ttk.Label(item_frame, text=f"{label}：", font=('Microsoft YaHei', 9)).pack(side='left')
            ttk.Label(item_frame, text=str(value), font=('Microsoft YaHei', 9, 'bold'),
                     foreground='#3498db').pack(side='left')

        chart_frame = ttk.Frame(content_frame, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, pady=8)

        ttk.Label(chart_frame, text="学习曲线", style='Subtitle.TLabel').pack(anchor='w', padx=8, pady=8)

        self.draw_learning_curve(chart_frame)

    def draw_learning_curve(self, parent):
        data = self.db.get_learning_curve_data(self.current_user[0])

        if not data:
            ttk.Label(parent, text="暂无数据，先刷几套题吧~",
                     font=('Microsoft YaHei', 9), foreground='#95a5a6').pack(pady=30)
            return

        fig = Figure(figsize=(9, 4), dpi=100)
        ax = fig.add_subplot(111)

        times = [datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S') for d in data]
        accuracies = [d[1] for d in data]

        ax.plot(times, accuracies, marker='o', linewidth=2, markersize=5, color='#3498db')
        ax.fill_between(times, accuracies, alpha=0.3, color='#3498db')

        ax.set_title('学习曲线 - 正确率变化', fontproperties='Microsoft YaHei', fontsize=12)
        ax.set_xlabel('时间', fontproperties='Microsoft YaHei', fontsize=10)
        ax.set_ylabel('正确率 (%)', fontproperties='Microsoft YaHei', fontsize=10)
        ax.grid(True, alpha=0.3)

        ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=8)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("白玉京考试周复习系统")


    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'byj.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        else:
            print(f"提示：未找到图标文件 {icon_path}，将使用默认图标")
    except Exception as e:
        print(f"设置图标时出错：{e}")

    app = QuizApp(root)
    root.mainloop()

