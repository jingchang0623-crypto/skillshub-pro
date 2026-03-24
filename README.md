# SkillsHub Pro

技能聚合平台 - 整合 skills.sh, clawhub.ai, xiaping.coze.site, skillhub.tencent.com 四大平台技能

## 项目结构

```
skillshub-pro/
├── frontend/          # Next.js前端
├── scraper/           # 爬虫脚本
├── data/              # JSON数据
├── scripts/           # 部署脚本
└── docker-compose.yml # Docker配置
```

## 快速开始

```bash
# 本地开发
docker-compose up -d

# 访问前端
open http://localhost:3000
```

## 数据更新

- 自动：GitHub Actions 每6小时更新
- 手动：运行 `python scraper/main.py`
