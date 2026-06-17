from database import Database


class ReviewModule:
    def __init__(self):
        self.db = Database()

    def get_review_questions(self, user_id, bank_name, mode='all'):
        from question_bank import QuestionBankManager
        bank_manager = QuestionBankManager()
        bank_data = bank_manager.load_bank(bank_name)

        if not bank_data:
            return []

        questions = bank_data['questions']

        if mode == 'wrong':
            wrong_list = self.db.get_wrong_questions(user_id, bank_name)
            wrong_indices = [w[3] for w in wrong_list]
            questions = [q for q in questions if q.get('index', 0) in wrong_indices]

        elif mode == 'favorite':
            fav_list = self.db.get_favorites(user_id, bank_name)
            fav_indices = [f[3] for f in fav_list]
            questions = [q for q in questions if q.get('index', 0) in fav_indices]

        elif mode == 'random':
            import random
            import copy
            questions_copy = copy.deepcopy(questions)
            random.shuffle(questions_copy)
            questions = questions_copy[:20]

        return questions

    def toggle_favorite(self, user_id, bank_name, question_index, question_text):
        is_fav = self.db.is_favorite(user_id, bank_name, question_index)

        if is_fav:
            self.db.remove_favorite(user_id, bank_name, question_index)
            return False
        else:
            self.db.add_favorite(user_id, bank_name, question_index, question_text)
            return True

    def toggle_mastered(self, user_id, bank_name, question_index):
        is_mastered = self.db.is_mastered(user_id, bank_name, question_index)

        if is_mastered:
            self.db.unmark_mastered(user_id, bank_name, question_index)
            return False
        else:
            self.db.mark_mastered(user_id, bank_name, question_index)
            self.db.remove_wrong_question(user_id, bank_name, question_index)
            return True
