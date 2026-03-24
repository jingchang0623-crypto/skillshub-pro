# SkillsHub Pro Scraper

多平台技能数据爬虫

## 功能

抓取以下平台的技能数据：
1. **skills.sh** - 通过API获取技能列表
2. **clawhub.ai** - 爬取技能列表页
3. **xiaping.coze.site** - API: GET /api/skills
4. **skillhub.tencent.com** - 爬取技能列表

## 使用方法

```bash
# 运行爬虫
python3 scraper.py

# 指定输出路径（默认：/var/www/skillshub-pro/data/skills.json）
python3 scraper.py --output /path/to/output.json
```

## 数据格式

输出为JSON数组，每条记录包含：

```json
{
  "id": "unique-id",
  "name": "技能名称",
  "description": "技能描述",
  "source": "来源平台",
  "url": "技能详情URL",
  "tags": ["标签1", "标签2"],
  "stars": 0,
  "downloads": 0,
  "updated_at": "2024-03-24T12:00:00"
}
```

## 技术栈

- Python 3
- requests - HTTP请求
- beautifulsoup4 - HTML解析

## 运行结果

**首次运行 (2026-03-24)**

```
✅ xiaping.coze.site: 12 skills (API)
✅ clawhub.ai: 1 skill (网页爬取)
❌ skills.sh: 0 skills (API 404)
❌ skillhub.tencent.com: 0 skills (未找到数据)

总计: 13 skills
```

## 注意事项

- 各平台可能有反爬机制，建议设置合理的请求频率
- 部分平台需要API密钥或认证
- 网页爬取逻辑可能需要根据实际页面结构调整选择器
