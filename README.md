# AI/机器学习/大模型每日论文进展

这个项目每天自动检索 AI、机器学习、深度学习、大模型和具身智能相关论文，覆盖 arXiv、OpenAlex、Crossref、Semantic Scholar、Europe PMC，以及按 ISSN 定向扫描的重点期刊 watchlist，做跨源去重、关键词相关性排序，并生成中文 Markdown 日报。配置 `OPENAI_API_KEY` 后会调用 OpenAI 生成结构化摘要；未配置时会使用保守的本地摘要，不会编造摘要中没有的数据集、指标或实验结果。

## 功能

- 从 arXiv、OpenAlex、Crossref、Semantic Scholar、Europe PMC 抓取最近论文和更新
- 按 ISSN 定向扫描 Nature Machine Intelligence、JMLR、TMLR、IEEE TPAMI、TNNLS、T-RO、RA-L、Science Robotics、TACL 等重点期刊
- 用关键词、学科分类和排除词进行相关性过滤
- SQLite 保存论文和摘要，避免重复处理
- 生成 `reports/YYYY/YYYY-MM-DD.md` 日报
- GitHub Actions 模板已保留，后续上传 GitHub 后可每日自动运行

## 本地运行

```bash
python -m pip install -e .
ai-paper-digest --no-openai
```

如果你想调用 OpenAI 生成更高质量的结构化摘要：

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-5.5"
ai-paper-digest
```

可选地设置数据源联系信息和 API key，以获得更稳定的限流额度：

```bash
export CONTACT_EMAIL="your.email@example.com"
export OPENALEX_API_KEY="..."
export S2_API_KEY="..."
```

调试时可以只打印报告，不写入文件：

```bash
ai-paper-digest --no-openai --dry-run --max-papers 5
```

如果只是做本地 smoke test，也可以缩短回看范围并跳过请求等待：

```bash
ai-paper-digest --no-openai --dry-run --max-papers 5 --lookback-days 1 --pause-seconds 0
```

## GitHub 自动化

`.github/workflows/daily.yml` 已配置每日 `00:30 UTC` 运行，即北京时间 `08:30`。当前项目先在本地生成，暂不上传 GitHub；后续如果创建仓库并推送上去，添加 `OPENAI_API_KEY` secret 后即可自动运行。

## 调整检索范围

编辑 `configs/queries.json`：

- `queries`：arXiv 检索词
- `sources.enabled`：启用的数据源，当前支持 `arxiv`、`openalex`、`crossref`、`semantic_scholar`、`europe_pmc`、`journal_watchlist`
- `sources.external_queries`：OpenAlex、Crossref、Semantic Scholar、Europe PMC 使用的通用检索词
- `sources.journal_watchlist.journals`：重点期刊列表，按 ISSN 从 Crossref 定向抓取近期文章，再交给相关性排序过滤
- `arxiv.categories`：arXiv 分类
- `ranking.strong_terms`：强相关词
- `ranking.support_terms`：辅助相关词
- `ranking.exclude_terms`：排除无关方向
- `ranking.minimum_score`：入选阈值

当前 watchlist 覆盖几类重点来源：

- 综合高影响力期刊：Nature、Science、Science Advances、PNAS、Nature Communications
- AI/ML 核心期刊：Nature Machine Intelligence、JMLR、TMLR、Machine Learning、Artificial Intelligence、AI Open
- IEEE/ACM：IEEE TPAMI、TNNLS、Transactions on Artificial Intelligence、TKDE、ACM Computing Surveys、ACM TIST
- 具身智能/机器人：IEEE RA-L、IEEE T-RO、IJRR、Science Robotics、Autonomous Robots
- NLP/视觉/数据挖掘：TACL、Computational Linguistics、Pattern Recognition、CVIU、Data Mining and Knowledge Discovery

## 报告字段

每篇论文会尽量整理：

- 一句话结论
- 方向分类
- 方法类型
- 研究类型
- 任务/领域
- 数据集或基准
- 模型或系统
- 评价指标
- 主要贡献
- 局限或注意点
- 为什么重要

如果摘要中没有对应信息，报告会写“摘要中未明确说明”。

## 注意事项

- 各论文数据源通常按日更新，不需要高频请求。
- 连续检索多个关键词时，外部数据源默认每次请求间隔 2 秒，arXiv 默认 3 秒；遇到 429/5xx 会自动短暂重试，单个查询失败不会中断整个日报。
- 当前版本只解析标题、摘要和元数据；如果要做全文级总结，可以后续增加 PDF 下载与解析模块。
