# Android 中文字体配置说明

## 问题
Android 设备上中文可能显示为方块（□□□），这是因为缺少中文字体。

## 解决方案

### 方案一：使用 Kivy 内置字体（推荐）✅

Kivy 自带了 `DroidSansFallback.ttf` 字体，支持中文显示。代码已自动检测并使用该字体。

**无需额外操作**，直接打包即可。

### 方案二：添加自定义中文字体文件

如果方案一无效，可以手动添加中文字体文件：

1. **下载中文字体文件**（推荐思源黑体或 Noto Sans CJK）：
   - [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
   - 或从 Windows 系统复制 `simhei.ttf` / `msyh.ttc`

2. **将字体文件放到项目目录**：
   ```
   quiz_app/
   ├── fonts/
   │   └── chinese.ttf    # 你下载的字体文件
   ├── main.py
   └── ...
   ```

3. **修改 `main.py` 中的字体路径**：
   ```python
   # 在 else 分支（Android/iOS）中添加：
   else:  # Android / iOS
       font_paths = [
           os.path.join(os.path.dirname(__file__), 'fonts', 'chinese.ttf'),
       ]
   ```

4. **更新 `buildozer.spec`**，确保字体文件被打包：
   ```ini
   source.include_exts = py,png,jpg,kv,atlas,json,ttf,ttc
   ```

5. **重新打包 APK**：
   ```bash
   buildozer android debug deploy run
   ```

## 验证方法

打包后运行 App，检查以下位置是否显示正常中文：
- ✅ 登录界面："用户"、"选择用户"等
- ✅ 主界面："题库列表"、"开始刷题"等按钮
- ✅ 刷题界面：题目内容、选项文字
- ✅ 复习界面：题目和答案

如果仍有方块，查看 logcat 日志：
```bash
adb logcat | grep -i "font\|chinese"
```

## 当前配置

代码已支持多平台自动检测：
- **Windows**: simhei.ttf / msyh.ttc / simsun.ttc
- **macOS**: PingFang.ttc / Arial Unicode.ttf
- **Linux**: wqy-zenhei.ttc / DroidSansFallbackFull.ttf
- **Android/iOS**: Kivy 内置 DroidSansFallback.ttf 或系统默认字体
