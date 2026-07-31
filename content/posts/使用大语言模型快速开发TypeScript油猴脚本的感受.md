+++
title = "使用大语言模型快速开发TypeScript油猴脚本的感受"
date = 2026-02-02
slug = "developing-typescript-userscript-with-llm"
aliases = ["/posts/shi-yong-da-yu-yan-mo-xing-kuai-su-kai-fa-typescriptyou-hou-jiao-ben-de-gan-shou/"]
description = "一篇开发TypeScript油猴脚本感想"
[taxonomies]
categories = ["tech"]
tags = ["ai", "typescript", "userscript","alpinejs"]
+++

最近今天我完全零基础编写了一个[TypeScript油猴脚本](https://github.com/kaixinol/Bilibili-User-Memo/)，并且使用了大语言模型来帮助我快速生成脚本的代码，样式从[这个脚本](https://greasyfork.org/zh-CN/scripts/563444)借鉴，因为我发现似乎AI不是很会写样式……笨笨的。……幸好别人已经提前写好了样式

目前发现的坑有两个：

- 把alpinejs v2当成v3，引用了过时的属性
- 乱写`build.externalGlobals`和`build.exterexternalResource`，用了非常蹩脚的写法（AI幻觉+过时的文档？），而且最后还让我的油猴脚本挂不上去了……讨厌。

反正第一个我花了好长时间才解决，好讨厌莫名其妙搞这种breaking change，第二个我去查了`vite-plugin-monkey`的示例现代用法才修复过来。

浪费了好多时间啊，人果然不能太习惯AI，AI太偷懒了，不知道去搜索网址，及时更新。

快写完了，应该就差wbi签名更新UP主信息这方面难写一点，相信难不倒我的。
