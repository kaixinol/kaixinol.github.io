+++
title = "没用对LLM 接口导致的烧token过快的反思"
date = 2026-05-04

[taxonomies]
categories = ["思考"]
tags = ["ai","claude"]
+++
很久之前我曾经用 smai.ai 买了一些API额度，然后没一会就用光了，我还觉得这claude也太烧钱了吧……

后来发现：[docs.smai.ai#在-cc-switch-中添加-smaiai-api-供应商](https://docs.smai.ai/docs/smai-api/guides/app-config/opencode#%E5%9C%A8-cc-switch-%E4%B8%AD%E6%B7%BB%E5%8A%A0-smaiai-api-%E4%BE%9B%E5%BA%94%E5%95%86)，下面的`{"setCacheKey":true}`我是没开……所以才烧的那么快……

然后之后阿里云也是一样……用opencode我直接用openai兼容接口了，没走claude专用兼容接口

结果就是花钱如流水……大概多花了100￥吧

\* *怨念*

![](../../static/images/Screenshot_20260504_135752.avif)

![](../../static/images/Screenshot_20260504_140232.avif)

