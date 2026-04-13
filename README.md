# 北京协和医院教学平台 - 自动评教脚本 (PUMC autoeval)
## 脚本运行流程：
  0. 用户运行 autoeval_chrome.py（如果使用的是 Chrome 浏览器）或 autoeval_firefox.py（如果使用的是 Firefox 浏览器）
  1. 用户指定月份，输入账号、密码授权登录
  2. 脚本将打开指定月份列表页，自动抓取所有「未评价」项
  3. 脚本将逐个打开评分页，自动打分并提交，评分策略：每题在 7-9 之间随机打分
  4. 脚本将关闭浏览器

## 脚本环境配置方法：
你的设备需要安装 Chrome 浏览器或者 Firefox 浏览器。

您的设备需要具备基本的 python 环境，如果没有，请参考网上的 python 环境安装教程，如[1](https://zhuanlan.zhihu.com/p/1908614432663250054).

本脚本依赖 selenium 爬虫，需要在您使用的 python 工作环境中下载相关依赖，请在命令行中输入指令
```bash
pip install selenium webdriver-manager
```

您需要将本项目下载到本地。如果您熟悉 github 的使用，可以将使用 git clone。如果您不熟悉，也可以直接下载本项目的[压缩包形式](https://github.com/srzer/pumc-autoeval/archive/refs/heads/main.zip)，或者直接下载 autoeval_chrome.py 和 autoeval_firefox.py。

## 常见问题
> Q1: 使用本脚本会有泄露个人信息的风险吗？

A1: 脚本本身不会记录密码，但在他人设备上使用脚本登录自己的账号依旧存在风险，请在自己的设备上使用。

> Q2: 如何修改脚本的打分策略？

A2: 您可以修改代码中的 SCORE_MIN, SCORE_MAX 的值从而修改打分范围，其他方面的修改需要修改 my_strategy() 函数本社。

> Q3: 由于网络原因使用不了 Chrome Driver 怎么办？

A3: 您可以考虑使用 Firefox 浏览器，对应代码为 autoeval_firefox.py。

> Q4: 有别的问题？

A4: 请在[此处](https://github.com/srzer/pumc-autoeval/issues/new)提出 issue。

## 致谢
本项目绝大部分代码由 Claude Code 生成。