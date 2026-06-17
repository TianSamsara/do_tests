#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Android版本测试脚本
用于验证核心功能是否正常
"""

import sys
import os

# 添加quiz_app到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'quiz_app'))

def test_database():
    """测试数据库模块"""
    print("测试数据库模块...")
    try:
        from database import Database
        db = Database()
        
        # 测试用户操作
        result = db.add_user("test_user")
        print(f"  ✓ 添加用户: {result}")
        
        user = db.get_user("test_user")
        print(f"  ✓ 查询用户: {user}")
        
        # 清理测试数据
        if user:
            db.delete_user(user[0])
            print(f"  ✓ 删除测试用户")
        
        db.close()
        print("  ✓ 数据库模块测试通过\n")
        return True
    except Exception as e:
        print(f"  ✗ 数据库模块测试失败: {e}\n")
        return False

def test_quiz_engine():
    """测试刷题引擎"""
    print("测试刷题引擎...")
    try:
        from quiz_engine import QuizEngine
        
        questions = [
            {
                'index': 0,
                'type': 'single',
                'text': '测试题目1',
                'options': {'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                'answer': 'A'
            },
            {
                'index': 1,
                'type': 'judge',
                'text': '测试题目2',
                'options': {'A': '正确', 'B': '错误'},
                'answer': 'A'
            }
        ]
        
        engine = QuizEngine()
        count = engine.start_quiz(questions, mode='immediate')
        print(f"  ✓ 开始刷题，题目数: {count}")
        
        question = engine.get_current_question()
        print(f"  ✓ 获取当前题目: {question['text']}")
        
        progress = engine.get_progress()
        print(f"  ✓ 进度信息: {progress}")
        
        print("  ✓ 刷题引擎测试通过\n")
        return True
    except Exception as e:
        print(f"  ✗ 刷题引擎测试失败: {e}\n")
        return False

def test_question_bank():
    """测试题库管理"""
    print("测试题库管理...")
    try:
        from question_bank import QuestionBankManager
        
        manager = QuestionBankManager()
        banks = manager.list_banks()
        print(f"  ✓ 题库列表: {banks}")
        
        print("  ✓ 题库管理测试通过\n")
        return True
    except Exception as e:
        print(f"  ✗ 题库管理测试失败: {e}\n")
        return False

def test_review_module():
    """测试复习模块"""
    print("测试复习模块...")
    try:
        from review_module import ReviewModule
        
        review = ReviewModule()
        print(f"  ✓ 复习模块初始化成功")
        print("  ✓ 复习模块测试通过\n")
        return True
    except Exception as e:
        print(f"  ✗ 复习模块测试失败: {e}\n")
        return False

def test_screens():
    """测试界面模块导入"""
    print("测试界面模块...")
    try:
        # 只测试导入，不实际运行（需要Kivy环境）
        from screens.login_screen import LoginScreen
        print("  ✓ LoginScreen 导入成功")
        
        from screens.main_screen import MainScreen
        print("  ✓ MainScreen 导入成功")
        
        from screens.quiz_screen import QuizScreen
        print("  ✓ QuizScreen 导入成功")
        
        from screens.review_screen import ReviewScreen
        print("  ✓ ReviewScreen 导入成功")
        
        print("  ✓ 界面模块测试通过\n")
        return True
    except Exception as e:
        print(f"  ✗ 界面模块测试失败: {e}\n")
        return False

def main():
    print("=" * 50)
    print("刷题系统 Android版本 - 功能测试")
    print("=" * 50)
    print()
    
    results = []
    
    # 执行测试
    results.append(("数据库模块", test_database()))
    results.append(("刷题引擎", test_quiz_engine()))
    results.append(("题库管理", test_question_bank()))
    results.append(("复习模块", test_review_module()))
    results.append(("界面模块", test_screens()))
    
    # 统计结果
    print("=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15s} : {status}")
    
    print("-" * 50)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！可以开始使用或打包APK。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查错误信息。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
