from datetime import datetime


class AIQuestionTemplate:
    @staticmethod
    def get_template():
        template = """
========================================
AI题库生成提示词模板
========================================

请按照以下格式提供题目信息，我会帮你生成标准的JSON题库文件：

【JSON格式要求】
题库文件是一个JSON对象，包含以下字段：
{
  "name": "题库名称",
  "questions": [
    {
      "index": 1,
      "type": "single",
      "text": "题目内容",
      "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
      "answer": "正确答案",
      "explanation": "答案解析"
    }
  ],
  "created_at": "创建时间"
}

【题目类型说明】
- single: 单选题
- multiple: 多选题  
- judge: 判断题
- essay: 大题（不可刷题）

【题目格式示例】

1. 单选题示例（type: "single"）：
{
  "index": 1,
  "type": "single",
  "text": "Python中哪个关键字用于定义函数？",
  "options": {
    "A": "class",
    "B": "def", 
    "C": "function",
    "D": "define"
  },
  "answer": "B",
  "explanation": "Python使用def关键字来定义函数。"
}

2. 多选题示例（type: "multiple"）：
{
  "index": 2,
  "type": "multiple",
  "text": "以下哪些是Python的数据类型？",
  "options": {
    "A": "list",
    "B": "dict",
    "C": "array", 
    "D": "tuple"
  },
  "answer": "ABD",
  "explanation": "list、dict、tuple都是Python内置数据类型，array需要导入模块。"
}

3. 判断题示例（type: "judge"）：
{
  "index": 3,
  "type": "judge",
  "text": "Python是一种编译型语言。",
  "options": {},
  "answer": "错误",
  "explanation": "Python是解释型语言，代码在运行时被解释执行。"
}

4. 大题示例（type: "essay"）：
{
  "index": 4,
  "type": "essay",
  "text": "请简述Python中的垃圾回收机制。",
  "options": {},
  "answer": "",
  "explanation": "Python主要使用引用计数进行垃圾回收，辅以标记-清除和分代回收来处理循环引用等问题。当对象引用计数为0时，内存会被自动释放。"
}

【重要说明】
1. index: 题目序号，从1开始连续编号
2. type: 题目类型（single/multiple/judge/essay）
3. text: 题目内容
4. options: 选项对象，键为A/B/C/D，值为选项内容（判断题和大题可为空对象{}）
5. answer: 正确答案
   - 单选题：单个字母如 "A"
   - 多选题：多个字母组合如 "ABD"
   - 判断题："正确" 或 "错误"
   - 大题：空字符串 ""
6. explanation: 答案解析，可为空字符串
7. 大题(type: "essay")不参与刷题，但可在复习中查看

【完整题库示例】
{
  "name": "Python基础知识",
  "questions": [
    {
      "index": 1,
      "type": "single",
      "text": "Python中哪个关键字用于定义函数？",
      "options": {"A": "class", "B": "def", "C": "function", "D": "define"},
      "answer": "B",
      "explanation": "Python使用def关键字来定义函数。"
    },
    {
      "index": 2,
      "type": "judge", 
      "text": "Python是一种编译型语言。",
      "options": {},
      "answer": "错误",
      "explanation": "Python是解释型语言。"
    }
  ],
  "created_at": "2024-01-01 12:00:00"
}

【使用方法】
将你的题目按照上述JSON格式提供给AI，AI会帮你生成完整的题库文件！
"""
        return template

    @staticmethod
    def get_bad_example():
        bad_example = """
========================================
错误的题目格式示例（不要这样写）
========================================

❌ 错误1：缺少必要的JSON字段
{
  "text": "题目内容"
}
（缺少index、type、options、answer等字段）

❌ 错误2：选项格式不正确
{
  "options": ["选项A", "选项B"]
}
（应该是对象格式 {"A": "选项A", "B": "选项B"}）

❌ 错误3：答案格式混乱
{
  "answer": "b"
}
（应该用大写字母 "B"）

❌ 错误4：判断题答案格式错误
{
  "answer": "false"
}
（应该是中文 "错误" 或 "正确"）

❌ 错误5：大题包含不必要的字段
{
  "type": "essay",
  "options": {"A": "错误选项"},
  "answer": "A"
}
（大题不应有选项和答案，只保留题目和解析）

正确的做法请参考上面的JSON格式模板！
"""
        return bad_example

    @staticmethod
    def convert_text_to_json(text_content, bank_name):
        """将文本格式转换为JSON题库格式（保留用于兼容）"""
        lines = text_content.strip().split('\n')
        questions = []
        current_question = None
        current_type = None
        options = {}

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith('题目：'):
                if current_question:
                    current_question['options'] = options
                    questions.append(current_question)

                question_text = line[3:]
                current_question = {
                    'index': len(questions) + 1,
                    'text': question_text,
                    'type': '',
                    'options': {},
                    'answer': '',
                    'explanation': ''
                }
                options = {}

            elif line.startswith(('A.', 'B.', 'C.', 'D.')):
                letter = line[0]
                content = line[2:]
                options[letter] = content

            elif line.startswith('答案：'):
                answer = line[3:].strip()
                if current_question:
                    if answer in ['正确', '错误']:
                        current_question['type'] = 'judge'
                        current_question['answer'] = answer
                    elif len(answer) == 1:
                        current_question['type'] = 'single'
                        current_question['answer'] = answer.upper()
                    elif len(answer) > 1:
                        current_question['type'] = 'multiple'
                        current_question['answer'] = answer.upper()

            elif line.startswith('解析：'):
                if current_question:
                    current_question['explanation'] = line[3:]

        if current_question:
            current_question['options'] = options
            questions.append(current_question)

        bank_data = {
            'name': bank_name,
            'questions': questions,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return bank_data
