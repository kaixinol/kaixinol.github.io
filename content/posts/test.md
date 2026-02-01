+++
title = "无标题"
date = 2026-01-09
[extra]
mermaid = true
code = true
[taxonomies]
categories = ["测试"]
tags = ["测试"]
+++

这是一个为您准备的 **Markdown 综合测试文本**。它涵盖了常用的语法元素，您可以将其复制到编辑器中测试渲染效果。

---

# 一级标题 (H1)

## 二级标题 (H2)

### 三级标题 (H3)

这是一段普通文本。Markdown 支持 **加粗**、_斜体_、~~删除线~~ 以及 `行内代码`。

---

## 1. 列表测试
**无序列表：**

- 西瓜
- 苹果
- 香蕉

**有序列表：**

1. 第一步：打开冰箱
2. 第二步：把大象放进去
3. 第三步：关上冰箱

**任务列表：**

- [x] 已完成任务
- [ ] 待办任务

---

## 2. 表格测试

| 姓名 | 年龄 | 职业   |
| ---- | ---- | ------ |
| 张三 | 25   | 工程师 |
| 李四 | 30   | 设计师 |
| 王五 | 28   | 教师   |

---

## 3. 链接与图片

- **外部链接：** [点击访问 Google](https://www.google.com)
- **图片演示：** ![示例图片](https://www.gstatic.com/webp/gallery/1.sm.jpg)

{{ figure(src="https://github.com/link-u/avif-sample-images/raw/refs/heads/master/fox.profile1.10bpc.yuv444.avif", alt="alt text", caption="caption text", width="300", height="400") }}

---

## 4. 其他元素

撤回是： <kbd>Ctrl+Z</kbd>

`dir c:`

<samp>Volume in drive C has no label.
Volume Serial Number is 1234-ABCD
Directory of C:\ </samp>

输出是<samp class="inline">OK</samp>

**脚注：**
这是一个带有脚注的句子[^1]

{% quote(cite="") %}
// content...
{% end %}

{% mermaid() %}
flowchart LR
A[Hard] -->|Text| B(Round)
B --> C{Decision}
C -->|One| D[Result 1]
C -->|Two| E[Result 2]
{% end %}
{{ youtube(id="dCKeXuVHl1o") }}

{{ bilibili(id="BV1NV4y1U7LR") }}
{{ bili_dynamic(id="932886473164718087") }}
{{ x(id="1465347002426867720", mode="archive") }}
{% note(title="Note") %}
note text
{% end %}
{% warning(title="Warning") %}
warning text
{% end %}
{% tip(title="Tip") %}
tip text
{% end %}
{% important(title="Important") %}
important text
{% end %}
{% caution(title="Caution") %}
caution text
{% end %}

```rs,linenos,,name=src/main.rs
fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}

let five = Some(5);
let six = plus_one(five);
let none = plus_one(None);
```

```text,bash=true
#!/bin/bash
$ echo hello
# sudo pacman -S zola
 # comment
$ ls -la
```

[^1]: 这是脚注的内容。
