import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database
from datetime import datetime


class StatsModule:
    def __init__(self):
        self.db = Database()

    def get_user_statistics(self, user_id):
        stats = self.db.get_user_stats(user_id)

        total_tests = stats[0] or 0
        total_questions = stats[1] or 0
        total_correct = stats[2] or 0
        avg_accuracy = stats[3] or 0

        return {
            'total_tests': total_tests,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'avg_accuracy': avg_accuracy
        }

    def create_learning_curve_chart(self, parent_widget, user_id, bank_name=None):
        data = self.db.get_learning_curve_data(user_id, bank_name)

        if not data:
            return None

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        times = [datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S') for d in data]
        accuracies = [d[1] for d in data]

        ax.plot(times, accuracies, marker='o', linewidth=2, markersize=6, color='#3498db')
        ax.fill_between(times, accuracies, alpha=0.3, color='#3498db')

        ax.set_title('学习曲线 - 正确率变化', fontproperties='Microsoft YaHei', fontsize=14)
        ax.set_xlabel('时间', fontproperties='Microsoft YaHei', fontsize=11)
        ax.set_ylabel('正确率 (%)', fontproperties='Microsoft YaHei', fontsize=11)
        ax.grid(True, alpha=0.3)

        ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, parent_widget)
        canvas.draw()

        return canvas
