import json
import os


class QuestionBankManager:
    def __init__(self):
        # 使用exe所在目录作为题库存储位置
        if getattr(os.sys, 'frozen', False):
            # 打包后的exe
            base_dir = os.path.dirname(os.sys.executable)
        else:
            # 开发环境
            base_dir = os.path.dirname(__file__)

        self.banks_dir = os.path.join(base_dir, 'question_banks')
        if not os.path.exists(self.banks_dir):
            os.makedirs(self.banks_dir)

    def get_bank_path(self, bank_name):
        safe_name = bank_name.replace('/', '_').replace('\\', '_')
        return os.path.join(self.banks_dir, f'{safe_name}.json')




    def create_bank(self, bank_name):
        path = self.get_bank_path(bank_name)
        if os.path.exists(path):
            return False

        bank_data = {
            'name': bank_name,
            'questions': [],
            'created_at': self.get_current_time()
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(bank_data, f, ensure_ascii=False, indent=2)

        return True

    def load_bank(self, bank_name):
        path = self.get_bank_path(bank_name)
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_bank(self, bank_data):
        path = self.get_bank_path(bank_data['name'])
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(bank_data, f, ensure_ascii=False, indent=2)

    def delete_bank(self, bank_name):
        path = self.get_bank_path(bank_name)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def list_banks(self):
        banks = []
        if not os.path.exists(self.banks_dir):
            return banks

        for filename in os.listdir(self.banks_dir):
            if filename.endswith('.json'):
                bank_name = filename[:-5]
                banks.append(bank_name)

        return sorted(banks)

    def add_question(self, bank_name, question):
        bank_data = self.load_bank(bank_name)
        if bank_data is None:
            return False

        bank_data['questions'].append(question)
        self.save_bank(bank_data)
        return True

    def update_question(self, bank_name, index, question):
        bank_data = self.load_bank(bank_name)
        if bank_data is None:
            return False

        if 0 <= index < len(bank_data['questions']):
            bank_data['questions'][index] = question
            self.save_bank(bank_data)
            return True
        return False

    def delete_question(self, bank_name, index):
        bank_data = self.load_bank(bank_name)
        if bank_data is None:
            return False

        if 0 <= index < len(bank_data['questions']):
            bank_data['questions'].pop(index)
            self.save_bank(bank_data)
            return True
        return False

    def import_from_json(self, json_file_path, bank_name=None):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if bank_name is None:
            bank_name = data.get('name', 'imported_bank')

        bank_data = {
            'name': bank_name,
            'questions': data.get('questions', []),
            'created_at': self.get_current_time()
        }

        path = self.get_bank_path(bank_name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(bank_data, f, ensure_ascii=False, indent=2)

        return bank_name

    def export_to_json(self, bank_name, output_path):
        bank_data = self.load_bank(bank_name)
        if bank_data is None:
            return False

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bank_data, f, ensure_ascii=False, indent=2)

        return True

    def get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')