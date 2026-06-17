import random


class QuizEngine:
    def __init__(self):
        self.current_questions = []
        self.current_index = 0
        self.user_answers = []
        self.results = []

    def start_quiz(self, questions, mode='immediate', shuffle_options=False, shuffle_questions=False):
        self.current_questions = []

        # 先处理题目列表
        processed_questions = list(questions)

        # 如果需要打乱题目顺序
        if shuffle_questions:
            random.shuffle(processed_questions)

        for q in processed_questions:
            question_copy = dict(q)

            if shuffle_options and q.get('type') in ['single', 'multiple', 'judge']:
                options = q.get('options', {})
                correct_answer = q.get('answer', '')

                # 获取选项内容列表
                option_contents = list(options.values())

                # 打乱选项内容
                random.shuffle(option_contents)

                # 重新分配 ABCD 标签（从上到下固定为 A、B、C、D）
                letters = ['A', 'B', 'C', 'D']
                new_options = {}
                new_answer = ''

                # 按 ABCD 顺序重新分配打乱后的内容
                for i, content in enumerate(option_contents):
                    letter = letters[i]
                    new_options[letter] = content

                # 处理多选题答案：需要找出所有正确答案对应的新标签
                if q.get('type') == 'multiple':
                    # 获取所有正确答案字母
                    correct_letters = list(correct_answer)
                    correct_contents = [options.get(letter, '') for letter in correct_letters]

                    # 找出这些内容在新选项中的标签
                    new_answer_list = []
                    for content in correct_contents:
                        for letter, new_content in new_options.items():
                            if new_content == content:
                                new_answer_list.append(letter)
                                break

                    # 排序并拼接成新答案
                    new_answer = ''.join(sorted(new_answer_list))
                else:
                    # 单选题和判断题：找到正确答案对应的新标签
                    correct_content = options.get(correct_answer, '')
                    for letter, content in new_options.items():
                        if content == correct_content:
                            new_answer = letter
                            break

                question_copy['options'] = new_options
                question_copy['answer'] = new_answer

            self.current_questions.append(question_copy)

        self.current_index = 0
        self.user_answers = [None] * len(self.current_questions)
        self.results = []
        self.mode = mode

        return len(self.current_questions)

    def get_current_question(self):
        if self.current_index < len(self.current_questions):
            return self.current_questions[self.current_index]
        return None

    def submit_answer(self, answer):
        if self.current_index < len(self.current_questions):
            self.user_answers[self.current_index] = answer

    def check_answer_immediate(self, answer):
        question = self.current_questions[self.current_index]
        correct = question.get('answer', '')

        is_correct = False

        if question.get('type') == 'judge':
            is_correct = (answer == correct)
        elif question.get('type') == 'single':
            is_correct = (answer.upper() == correct.upper())
        elif question.get('type') == 'multiple':
            user_ans = set(answer.upper().replace(',', '').replace('，', ''))
            correct_ans = set(correct.upper().replace(',', '').replace('，', ''))
            is_correct = (user_ans == correct_ans)

        result = {
            'question': question,
            'user_answer': answer,
            'correct_answer': correct,
            'is_correct': is_correct
        }

        self.results.append(result)

        return is_correct

    def next_question(self):
        self.current_index += 1
        if self.current_index < len(self.current_questions):
            return True
        return False

    def finish_quiz(self):
        if self.mode == 'batch':
            for i, question in enumerate(self.current_questions):
                answer = self.user_answers[i]
                correct = question.get('answer', '')

                is_correct = False

                if question.get('type') == 'judge':
                    is_correct = (answer == correct)
                elif question.get('type') == 'single':
                    if answer and correct:
                        is_correct = (answer.upper() == correct.upper())
                elif question.get('type') == 'multiple':
                    if answer and correct:
                        user_ans = set(answer.upper().replace(',', '').replace('，', ''))
                        correct_ans = set(correct.upper().replace(',', '').replace('，', ''))
                        is_correct = (user_ans == correct_ans)

                result = {
                    'question': question,
                    'user_answer': answer,
                    'correct_answer': correct,
                    'is_correct': is_correct
                }

                self.results.append(result)

        total = len(self.results)
        correct_count = sum(1 for r in self.results if r['is_correct'])
        accuracy = (correct_count / total * 100) if total > 0 else 0

        return {
            'total': total,
            'correct': correct_count,
            'accuracy': accuracy,
            'results': self.results
        }

    def get_progress(self):
        return {
            'current': self.current_index + 1,
            'total': len(self.current_questions)
        }
