# 优酷电影爬虫与展示页面

这是一个用于爬取优酷电影信息并展示的应用程序。它包含两个主要部分：
1. 爬虫脚本：用于获取优酷电影数据
2. 展示页面：一个现代化的网页界面，用于展示爬取到的电影信息

## 功能特点

- 自动滚动页面获取更多电影信息
- 提取电影标题、图片、播放链接、评分和VIP状态
- 响应式设计的现代化展示界面
- 支持VIP标识和评分显示
- 优雅的动画效果

## 安装步骤

1. 确保已安装 Python 3.7 或更高版本
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装 Playwright 浏览器：
   ```bash
   playwright install chromium
   ```

## 使用方法

1. 运行爬虫脚本获取电影数据：
   ```bash
   python scraper.py
   ```
   这将生成 `movies.json` 文件

2. 使用任意 HTTP 服务器打开 `index.html`，例如：
   ```bash
   python -m http.server 8000
   ```
   然后在浏览器中访问 `http://localhost:8000`

## 注意事项

- 爬虫脚本需要稳定的网络连接
- 请遵守优酷的使用条款和爬虫规则
- 建议适当控制爬取频率，避免对服务器造成压力

## 技术栈

- Python
- Playwright
- HTML5
- Tailwind CSS
- JavaScript (ES6+) 