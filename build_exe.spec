# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['do_test.py'],
    pathex=[],
    binaries=[],
    datas=[('byj.ico', '.'), ('question_banks', 'question_banks')],
    hiddenimports=[
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'sqlite3',
        'json',
        'datetime',
        'random',
        'database',
        'question_bank',
        'quiz_engine',
        'review_module',
        'stats_module',
        'user_manager',
        'ai_template',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'matplotlib.tests'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='白玉京考试周复习系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='byj.ico',
)
