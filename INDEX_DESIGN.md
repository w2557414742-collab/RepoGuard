# 索引设计

## 版本与持久化

`Indexer.version` 使用仓库本地身份、目标 Git SHA 和 `IndexOptions.key` 生成版本。选项键包含 Python 版本、源码根和索引格式版本。SQLite 的 `snapshot` 表保存版本，`indexed_file` 保存文件清单、JSON 语法事实和依赖探测，`edge` 保存带版本、位置、类别及可信度的边。定义位置保存在 `Unit.symbols`。

`Store.save` 在一次写事务发布所有行。读者使用固定版本恢复清单和关系。失败的构建不会暴露半成品快照。格式变化分配新版本，旧版本可留存。当前没有跨版本对象去重或独立数据库迁移框架。 [Store 源码](src/repoguard/store.py)

## 三种构建方式

| 方式 | 语法事实 | 关系 |
|---|---|---|
| `full` | 全量解析 | 全量解析关系 |
| `file` | 复用无变化文件 | 全量解析关系 |
| `dependency` | 复用无变化文件 | 按依赖探测和失效键重新链接 |

重命名路径影响模块、作用域和身份，即使 blob 内容一致也重新处理。未知或未命中的查找保留在探测集合。索引一致性覆盖文件、符号、边、依赖足迹及关键查询。 [增量设计](INCREMENTAL_INDEXING_DESIGN.md) [集成验证](tests/integration/test_index_and_impact.py)
