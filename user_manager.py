from database import Database


class UserManager:
    def __init__(self):
        self.db = Database()

    def register_user(self, username):
        return self.db.add_user(username)

    def login_user(self, username):
        return self.db.get_user(username)

    def get_all_users(self):
        return self.db.get_all_users()

    def delete_user(self, user_id):
        self.db.delete_user(user_id)

    def get_user_stats(self, user_id):
        return self.db.get_user_stats(user_id)

    def get_quiz_records(self, user_id, limit=50):
        return self.db.get_quiz_records(user_id, limit)

    def get_learning_curve_data(self, user_id, bank_name=None):
        return self.db.get_learning_curve_data(user_id, bank_name)
