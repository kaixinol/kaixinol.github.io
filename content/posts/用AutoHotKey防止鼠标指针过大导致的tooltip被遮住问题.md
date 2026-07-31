+++
title = "用AutoHotKey防止鼠标指针过大导致的tooltip被遮住问题"
date = 2026-05-23
slug = "autohotkey-tooltip-hidden-by-large-cursor"
aliases = ["/posts/yong-autohotkeyfang-zhi-shu-biao-zhi-zhen-guo-da-dao-zhi-de-tooltipbei-zhe-zhu-wen-ti/"]

[taxonomies]
categories = ["tech"]
tags = ["AutoHotKey", "Windows","Linux"]
+++
{{ bilibili(id="BV13U8CzeE74") }}
笔者安装此视频提及的鼠标时，发现普通鼠标大小会看不清，设置大号鼠标又会导致tooltip被遮住。
解决方法：
# Windows
1. 安装`AutoHotKey`
2. 在explorer，输入`shell:startup`
3. 找到`AutoHotKey64.exe`，并为其新建快捷方式
4. 下载下面的Gist
{{ gist(id="96099ab479445a486f6a928278763efd") }}
5. 修改ink，让`AutoHotKey64.exe`会打开这个ahk脚本
6. 放到`shell:startup`中。
# Linux （KDE）

Windows 的指针和Linux的指针不通用，需要先用`cargo install currust@1.4.2`安装，并按照指示转换。
```bash
mv /tmp/<你的鼠标指针> ~/.local/share/icons/
```
1. 确保系统是KDE 6 或者更高。
2. 在用户文件夹下新建下列脚本：
```bash,name=wayland_cursor_hide.sh
#!/bin/bash
IS_LOADED=$(qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.isEffectLoaded "hidecursor")

if [ "$IS_LOADED" = "true" ]; then
    # --- 执行关闭逻辑 ---
    qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect "hidecursor"
    # 同步修改配置，确保下次重启依然是“默认禁用”
    kwriteconfig6 --file kwinrc --group Plugins --key hidecursorEnabled false
    notify-send -t 1000 -h string:x-canonical-private-synchronous:cursor "鼠标自动隐藏" "已禁用 ❌"
else
    kwriteconfig6 --file kwinrc --group Plugins --key hidecursorEnabled true

    qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect "hidecursor"
    notify-send -t 1000 -h string:x-canonical-private-synchronous:cursor "鼠标自动隐藏" "已开启 ✅"
fi

# 刷新 KWin 状态
qdbus6 org.kde.KWin /KWin reconfigure
```
3. `chmod +x wayland_cursor_hide.sh`

4. 设置开机自启动，并添加对于<kbd>Ctrl + Shift</kbd>的快捷键，此快捷键指向`wayland_cursor_hide.sh`的触发。

---
此时，按<kbd>Ctrl + Shift</kbd>，即可不受遮挡的查看ToolTip了。

