# Python 源码函数索引

由 `python scripts/generate_source_guide.py` 从 AST 生成。调用列为函数体的前四个直接调用表达式，链接定位调用点。动态方法的运行时目标需要另外验证。

## [benchmarks/contracts/risk_contracts.py](benchmarks/contracts/risk_contracts.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`bounded_step`](benchmarks/contracts/risk_contracts.py#L4-L8) 4–8 | `(score: float, weight: float, uncertain: bool) → float` | pre: 0.0 <= score <= 5.0 and 0.0 <= weight <= 1.0 | [`risk_step`](benchmarks/contracts/risk_contracts.py#L8) |
| [`reversed_uncertainty`](benchmarks/contracts/risk_contracts.py#L11-L15) 11–15 | `(score: float) → float` | pre: 1.0 <= score <= 5.0 | [`risk_step`](benchmarks/contracts/risk_contracts.py#L15) |

## [benchmarks/run_click.py](benchmarks/run_click.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`score`](benchmarks/run_click.py#L32-L42) 32–42 | `(found: set, expected: set) → dict` | — | [`len`](benchmarks/run_click.py#L33)、[`len`](benchmarks/run_click.py#L34)、[`len`](benchmarks/run_click.py#L35)、[`sorted`](benchmarks/run_click.py#L40) |
| [`dump`](benchmarks/run_click.py#L45-L46) 45–46 | `(path: Path, payload: object) → None` | — | [`path.write_text`](benchmarks/run_click.py#L46)、[`json.dumps`](benchmarks/run_click.py#L46) |
| [`snapshot_sources`](benchmarks/run_click.py#L49-L54) 49–54 | `(repo: Repository, snap) → dict[str, str]` | — | [`blob.decode`](benchmarks/run_click.py#L52)、[`zip`](benchmarks/run_click.py#L53)、[`repo.blobs`](benchmarks/run_click.py#L53) |
| [`navigation`](benchmarks/run_click.py#L57-L136) 57–136 | `(view: View, sources: dict[str, str], manifest: dict) → dict` | — | [`ast.parse`](benchmarks/run_click.py#L59)、[`sources.items`](benchmarks/run_click.py#L59)、[`tuple`](benchmarks/run_click.py#L62)、[`query.rsplit`](benchmarks/run_click.py#L63) |
| [`measure_index`](benchmarks/run_click.py#L139-L176) 139–176 | `(engine: RepoGuard, base: str, target: str, repeats: int) → dict` | — | [`engine.indexer.index`](benchmarks/run_click.py#L141)、[`range`](benchmarks/run_click.py#L144)、[`perf_counter`](benchmarks/run_click.py#L145)、[`engine.indexer.index`](benchmarks/run_click.py#L146) |
| [`git`](benchmarks/run_click.py#L179-L189) 179–189 | `(root: Path, *args: str, data: bytes \| None=None) → str` | — | [`subprocess.run`](benchmarks/run_click.py#L180)、[`str`](benchmarks/run_click.py#L181)、[`RuntimeError`](benchmarks/run_click.py#L188)、[`result.stderr.decode`](benchmarks/run_click.py#L188) |
| [`commit_variant`](benchmarks/run_click.py#L192-L221) 192–221 | `(root: Path, base: str) → str` | — | [`git`](benchmarks/run_click.py#L193)、[`git`](benchmarks/run_click.py#L194)、[`subprocess.run`](benchmarks/run_click.py#L200)、[`str`](benchmarks/run_click.py#L204) |
| [`variant`](benchmarks/run_click.py#L224-L233) 224–233 | `(root: Path, base: str, edits: dict[str, str], patch: bytes \| None=None) → str` | — | [`git`](benchmarks/run_click.py#L225)、[`edits.items`](benchmarks/run_click.py#L226)、[`(root / path).write_bytes`](benchmarks/run_click.py#L227)、[`value.encode`](benchmarks/run_click.py#L227) |
| [`brief`](benchmarks/run_click.py#L236-L244) 236–244 | `(run: TestRun) → dict` | — | [`asdict`](benchmarks/run_click.py#L237)、[`len`](benchmarks/run_click.py#L240)、[`sum`](benchmarks/run_click.py#L241)、[`bool`](benchmarks/run_click.py#L241) |
| [`evaluate_tests`](benchmarks/run_click.py#L247-L271) 247–271 | `(engine, old, new, inputs, image: str, baseline: TestRun, full: TestRun) → dict` | — | [`select`](benchmarks/run_click.py#L250)、[`asdict`](benchmarks/run_click.py#L253)、[`run_tests`](benchmarks/run_click.py#L255)、[`run_tests`](benchmarks/run_click.py#L257) |
| [`evaluate_impact`](benchmarks/run_click.py#L274-L292) 274–292 | `(old, new, files, truth: set[str]) → dict` | — | [`set`](benchmarks/run_click.py#L278)、[`analyze`](benchmarks/run_click.py#L283)、[`list`](benchmarks/run_click.py#L284)、[`dict.fromkeys`](benchmarks/run_click.py#L285) |
| [`evaluate_rename`](benchmarks/run_click.py#L295-L355) 295–355 | `(root, engine, snap, sources, manifest, output, image)` | — | [`query.rsplit`](benchmarks/run_click.py#L299)、[`View(snap).find_definition`](benchmarks/run_click.py#L300)、[`View`](benchmarks/run_click.py#L300)、[`tuple`](benchmarks/run_click.py#L302) |
| [`evaluate_rename.BlindRename`](benchmarks/run_click.py#L304-L310) 304–310 | `class BlindRename(cst.CSTTransformer)` | 类型定义。成员职责见下方对应条目。 | — |
| [`evaluate_rename.BlindRename.leave_Name`](benchmarks/run_click.py#L305-L310) 305–310 | `(self, original_node, updated_node)` | — | [`updated_node.with_changes`](benchmarks/run_click.py#L307) |
| [`main`](benchmarks/run_click.py#L358-L464) 358–464 | `() → None` | — | [`argparse.ArgumentParser`](benchmarks/run_click.py#L359)、[`parser.add_argument`](benchmarks/run_click.py#L360)、[`parser.add_argument`](benchmarks/run_click.py#L361)、[`Path`](benchmarks/run_click.py#L361) |

## [infra/runner_entry.py](infra/runner_entry.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`extract`](infra/runner_entry.py#L8-L12) 8–12 | `() → None` | — | [`tarfile.open`](infra/runner_entry.py#L9)、[`member.isfile`](infra/runner_entry.py#L11)、[`member.isdir`](infra/runner_entry.py#L11)、[`archive.extract`](infra/runner_entry.py#L12) |
| [`main`](infra/runner_entry.py#L15-L44) 15–44 | `() → int` | — | [`json.loads`](infra/runner_entry.py#L16)、[`sys.stdin.buffer.readline`](infra/runner_entry.py#L16)、[`extract`](infra/runner_entry.py#L17)、[`Path`](infra/runner_entry.py#L18) |

## [infra/service_entry.py](infra/service_entry.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`main`](infra/service_entry.py#L9-L12) 9–12 | `() → None` | — | [`RepoGuard`](infra/service_entry.py#L10)、[`engine.index`](infra/service_entry.py#L11)、[`os.environ.get`](infra/service_entry.py#L11)、[`uvicorn.run`](infra/service_entry.py#L12) |

## [scripts/generate_source_guide.py](scripts/generate_source_guide.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`git_paths`](scripts/generate_source_guide.py#L17-L26) 17–26 | `() → list[str]` | 列出已跟踪或可提交的路径，排除本地忽略项。首提交之前也可运行。 | [`subprocess.run`](scripts/generate_source_guide.py#L19)、[`result.stdout.decode('utf-8').split`](scripts/generate_source_guide.py#L25)、[`result.stdout.decode`](scripts/generate_source_guide.py#L25)、[`sorted`](scripts/generate_source_guide.py#L26) |
| [`source_tree`](scripts/generate_source_guide.py#L29-L44) 29–44 | `(paths: list[str]) → str` | 把按路径排序的候选清单转成文本树。目录字典按前缀共享。 | [`path.split`](scripts/generate_source_guide.py#L34)、[`current.setdefault`](scripts/generate_source_guide.py#L35)、[`'\n'.join`](scripts/generate_source_guide.py#L44)、[`render`](scripts/generate_source_guide.py#L44) |
| [`source_tree.render`](scripts/generate_source_guide.py#L37-L42) 37–42 | `(items: dict, prefix: str) → Iterator[str]` | — | [`sorted`](scripts/generate_source_guide.py#L38)、[`items.items`](scripts/generate_source_guide.py#L38)、[`bool`](scripts/generate_source_guide.py#L38)、[`item[0].lower`](scripts/generate_source_guide.py#L38) |
| [`definitions`](scripts/generate_source_guide.py#L47-L55) 47–55 | `(node: ast.AST, parents: tuple[str, ...]=()) → Iterator[tuple[str, Definition]]` | 按词法定义路径遍历 AST。局部定义用外层函数名限定。 | [`ast.iter_child_nodes`](scripts/generate_source_guide.py#L49)、[`isinstance`](scripts/generate_source_guide.py#L50)、[`'.'.join`](scripts/generate_source_guide.py#L52)、[`definitions`](scripts/generate_source_guide.py#L53) |
| [`Calls`](scripts/generate_source_guide.py#L58-L77) 58–77 | `class Calls(ast.NodeVisitor)` | 收集函数体直接写出的调用点，跳过嵌套定义的作用域。 | — |
| [`Calls.__init__`](scripts/generate_source_guide.py#L61-L62) 61–62 | `(self) → None` | — | — |
| [`Calls.visit_Call`](scripts/generate_source_guide.py#L64-L69) 64–69 | `(self, node: ast.Call) → None` | — | [`isinstance`](scripts/generate_source_guide.py#L65)、[`ast.unparse`](scripts/generate_source_guide.py#L66)、[`len`](scripts/generate_source_guide.py#L67)、[`self.sites.append`](scripts/generate_source_guide.py#L68) |
| [`Calls.visit_FunctionDef`](scripts/generate_source_guide.py#L71-L72) 71–72 | `(self, node: ast.FunctionDef \| ast.AsyncFunctionDef) → None` | 嵌套函数有自己的参考条目。 | — |
| [`Calls.visit_ClassDef`](scripts/generate_source_guide.py#L76-L77) 76–77 | `(self, node: ast.ClassDef) → None` | 由相应的类和方法条目记录内部调用。 | — |
| [`escape`](scripts/generate_source_guide.py#L80-L81) 80–81 | `(value: str) → str` | — | [`value.replace('\|', '\\\|').replace('\n', ' ').replace`](scripts/generate_source_guide.py#L81)、[`value.replace('\|', '\\\|').replace`](scripts/generate_source_guide.py#L81)、[`value.replace`](scripts/generate_source_guide.py#L81) |
| [`reference`](scripts/generate_source_guide.py#L84-L137) 84–137 | `(paths: list[str]) → str` | 输出定义、签名、行区间与调用点。调用链接仅描述语法位置。 | [`file.endswith`](scripts/generate_source_guide.py#L93)、[`file.split`](scripts/generate_source_guide.py#L93)、[`ast.parse`](scripts/generate_source_guide.py#L95)、[`(ROOT / file).read_text`](scripts/generate_source_guide.py#L95) |
| [`main`](scripts/generate_source_guide.py#L140-L159) 140–159 | `() → int` | 生成两份导航文件或在 CI 检查其内容是否与源码同步。 | [`argparse.ArgumentParser`](scripts/generate_source_guide.py#L142)、[`parser.add_argument`](scripts/generate_source_guide.py#L143)、[`parser.parse_args`](scripts/generate_source_guide.py#L144)、[`git_paths`](scripts/generate_source_guide.py#L145) |

## [scripts/package_audit.py](scripts/package_audit.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`git`](scripts/package_audit.py#L17-L24) 17–24 | `(*args: str, data: bytes \| None=None) → bytes` | — | [`subprocess.run`](scripts/package_audit.py#L18) |
| [`inventory`](scripts/package_audit.py#L27-L60) 27–60 | `() → tuple[dict[str, int], dict[str, int], list[str]]` | 遍历普通本地文件，汇总逻辑字节数并记录跳过的路径。 | [`getattr`](scripts/package_audit.py#L32)、[`walk`](scripts/package_audit.py#L59)、[`sorted`](scripts/package_audit.py#L60) |
| [`inventory.walk`](scripts/package_audit.py#L34-L57) 34–57 | `(path: Path) → int` | — | [`os.scandir`](scripts/package_audit.py#L37)、[`Path`](scripts/package_audit.py#L39)、[`absolute.relative_to(ROOT).as_posix`](scripts/package_audit.py#L40)、[`absolute.relative_to`](scripts/package_audit.py#L40) |
| [`duplicates`](scripts/package_audit.py#L63-L92) 63–92 | `(files: dict[str, int]) → tuple[list[tuple[int, list[str]]], int]` | 先按大小和前缀筛选，再对候选做完整 SHA-256 比较。 | [`defaultdict`](scripts/package_audit.py#L65)、[`files.items`](scripts/package_audit.py#L66)、[`sized[size].append`](scripts/package_audit.py#L68)、[`sized.items`](scripts/package_audit.py#L71) |
| [`history_blobs`](scripts/package_audit.py#L95-L117) 95–117 | `() → list[tuple[int, str, str]]` | 用对象 ID 查询本地 refs 可达 blob 的未压缩大小。 | [`git('rev-list', '--objects', '--all').decode('utf-8').splitlines`](scripts/package_audit.py#L97)、[`git('rev-list', '--objects', '--all').decode`](scripts/package_audit.py#L97)、[`git`](scripts/package_audit.py#L97)、[`dict`](scripts/package_audit.py#L98) |
| [`ranked`](scripts/package_audit.py#L120-L121) 120–121 | `(values: dict[str, int]) → list[tuple[str, int]]` | — | [`sorted`](scripts/package_audit.py#L121)、[`values.items`](scripts/package_audit.py#L121) |
| [`amount`](scripts/package_audit.py#L124-L125) 124–125 | `(size: int) → str` | — | — |
| [`main`](scripts/package_audit.py#L128-L205) 128–205 | `() → None` | 生成发布留档。只写报告，第三方克隆和历史数据保留原样。 | [`inventory`](scripts/package_audit.py#L130)、[`git_paths`](scripts/package_audit.py#L131)、[`git('ls-files', '-z').decode().split`](scripts/package_audit.py#L132)、[`git('ls-files', '-z').decode`](scripts/package_audit.py#L132) |

## [scripts/profile_index.py](scripts/profile_index.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`main`](scripts/profile_index.py#L16-L52) 16–52 | `() → None` | — | [`argparse.ArgumentParser`](scripts/profile_index.py#L17)、[`cli.add_argument`](scripts/profile_index.py#L18)、[`cli.add_argument`](scripts/profile_index.py#L19)、[`cli.add_argument`](scripts/profile_index.py#L20) |

## [scripts/research_sources.py](scripts/research_sources.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`get`](scripts/research_sources.py#L41-L45) 41–45 | `(url: str) → str` | — | [`Request`](scripts/research_sources.py#L42)、[`urlopen`](scripts/research_sources.py#L43)、[`response.read`](scripts/research_sources.py#L44)、[`data.decode`](scripts/research_sources.py#L45) |
| [`collect`](scripts/research_sources.py#L48-L100) 48–100 | `(item: tuple[str, tuple[str, ...]]) → dict` | — | [`subprocess.run`](scripts/research_sources.py#L53)、[`line.split`](scripts/research_sources.py#L68)、[`listing.splitlines`](scripts/research_sources.py#L68)、[`refs.get`](scripts/research_sources.py#L69) |

## [scripts/smoke_http.py](scripts/smoke_http.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`main`](scripts/smoke_http.py#L9-L53) 9–53 | `() → None` | — | [`argparse.ArgumentParser`](scripts/smoke_http.py#L10)、[`parser.add_argument`](scripts/smoke_http.py#L11)、[`parser.parse_args`](scripts/smoke_http.py#L12)、[`fetch`](scripts/smoke_http.py#L27) |
| [`main.fetch`](scripts/smoke_http.py#L14-L25) 14–25 | `(route: str, body: dict \| None=None, **params: str)` | — | [`args.url.rstrip`](scripts/smoke_http.py#L15)、[`urlencode`](scripts/smoke_http.py#L17)、[`Request`](scripts/smoke_http.py#L18)、[`json.dumps(body).encode`](scripts/smoke_http.py#L20) |

## [scripts/verify_contracts.py](scripts/verify_contracts.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`check`](scripts/verify_contracts.py#L10-L44) 10–44 | `(function: str) → dict` | — | [`perf_counter`](scripts/verify_contracts.py#L23)、[`subprocess.run`](scripts/verify_contracts.py#L25)、[`perf_counter`](scripts/verify_contracts.py#L41)、[`output.strip`](scripts/verify_contracts.py#L42) |

## [src/repoguard/api.py](src/repoguard/api.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`IndexRequest`](src/repoguard/api.py#L23-L25) 23–25 | `class IndexRequest(BaseModel)` | 类型定义。成员职责见下方对应条目。 | — |
| [`RefactorRequest`](src/repoguard/api.py#L28-L33) 28–33 | `class RefactorRequest(BaseModel)` | 类型定义。成员职责见下方对应条目。 | — |
| [`create_app`](src/repoguard/api.py#L36-L181) 36–181 | `(repository: str \| Path, database: str \| Path, *, write_token: str='', rules: Path \| None=None, benchmark: Path \| None=None) → FastAPI` | 为一个仓库和索引地址装配 HTTP 应用。对索引写入校验令牌，查询从已发布快照读取。 | [`RepoGuard`](src/repoguard/api.py#L45)、[`FastAPI`](src/repoguard/api.py#L46) |
| [`create_app.invalid_input`](src/repoguard/api.py#L50-L51) 50–51 | `async invalid_input(_request: Request, exc: Exception) → JSONResponse` | — | [`JSONResponse`](src/repoguard/api.py#L51)、[`str`](src/repoguard/api.py#L51) |
| [`create_app.health`](src/repoguard/api.py#L54-L55) 54–55 | `() → dict` | — | — |
| [`create_app.index`](src/repoguard/api.py#L58-L63) 58–63 | `(body: IndexRequest, x_repoguard_token: str=Header(default='')) → dict` | — | [`HTTPException`](src/repoguard/api.py#L60)、[`secrets.compare_digest`](src/repoguard/api.py#L61)、[`write_token.encode`](src/repoguard/api.py#L61)、[`x_repoguard_token.encode`](src/repoguard/api.py#L61) |
| [`create_app.snapshot`](src/repoguard/api.py#L66-L71) 66–71 | `(revision: str='HEAD') → dict` | — | [`engine.view`](src/repoguard/api.py#L67)、[`asdict`](src/repoguard/api.py#L70)、[`current.files.values`](src/repoguard/api.py#L70) |
| [`create_app.symbols`](src/repoguard/api.py#L74-L75) 74–75 | `(q: str, revision: str='HEAD', limit: int=Query(20, ge=1, le=100))` | — | [`asdict`](src/repoguard/api.py#L75)、[`engine.view(revision).search_symbols`](src/repoguard/api.py#L75)、[`engine.view`](src/repoguard/api.py#L75) |
| [`create_app.definitions`](src/repoguard/api.py#L78-L79) 78–79 | `(q: str, revision: str='HEAD')` | — | [`asdict`](src/repoguard/api.py#L79)、[`engine.view(revision).find_definition`](src/repoguard/api.py#L79)、[`engine.view`](src/repoguard/api.py#L79) |
| [`create_app.references`](src/repoguard/api.py#L82-L83) 82–83 | `(symbol_id: str, revision: str='HEAD')` | — | [`asdict`](src/repoguard/api.py#L83)、[`engine.view(revision).find_references`](src/repoguard/api.py#L83)、[`engine.view`](src/repoguard/api.py#L83) |
| [`create_app.graph`](src/repoguard/api.py#L86-L100) 86–100 | `(symbol_id: str, revision: str='HEAD', depth: int=Query(2, ge=0, le=10), limit: int=Query(60, ge=1, le=200), reverse: bool=True, kinds: Annotated[list[EdgeType] \| None, Query()]=None)` | — | [`engine.view(revision).get_dependency_graph`](src/repoguard/api.py#L94)、[`engine.view`](src/repoguard/api.py#L94)、[`tuple`](src/repoguard/api.py#L99) |
| [`create_app.file`](src/repoguard/api.py#L103-L111) 103–111 | `(path: str, revision: str='HEAD')` | — | [`safe_relative`](src/repoguard/api.py#L104)、[`HTTPException`](src/repoguard/api.py#L105)、[`engine.view`](src/repoguard/api.py#L106)、[`snapshot.files.get`](src/repoguard/api.py#L107) |
| [`create_app.impact`](src/repoguard/api.py#L114-L115) 114–115 | `(base: str, target: str, depth: int=Query(5, ge=0, le=15))` | — | [`asdict`](src/repoguard/api.py#L115)、[`engine.analyze_change_impact`](src/repoguard/api.py#L115) |
| [`create_app.diff`](src/repoguard/api.py#L118-L145) 118–145 | `(base: str, target: str, path: str)` | — | [`safe_relative`](src/repoguard/api.py#L119)、[`HTTPException`](src/repoguard/api.py#L120)、[`engine.view`](src/repoguard/api.py#L121)、[`engine.repository.changes`](src/repoguard/api.py#L122) |
| [`create_app.tests`](src/repoguard/api.py#L148-L149) 148–149 | `(base: str, target: str, mode: str='hybrid')` | — | [`asdict`](src/repoguard/api.py#L149)、[`engine.select_related_tests`](src/repoguard/api.py#L149) |
| [`create_app.architecture`](src/repoguard/api.py#L152-L155) 152–155 | `(base: str, target: str)` | — | [`HTTPException`](src/repoguard/api.py#L154)、[`compare`](src/repoguard/api.py#L155)、[`engine.view`](src/repoguard/api.py#L155)、[`load_rules`](src/repoguard/api.py#L155) |
| [`create_app.refactor`](src/repoguard/api.py#L158-L167) 158–167 | `(body: RefactorRequest)` | — | [`asdict`](src/repoguard/api.py#L159)、[`engine.plan_refactoring`](src/repoguard/api.py#L160) |
| [`create_app.benchmark_summary`](src/repoguard/api.py#L170-L179) 170–179 | `()` | — | [`benchmark.is_file`](src/repoguard/api.py#L171)、[`HTTPException`](src/repoguard/api.py#L172)、[`json.loads`](src/repoguard/api.py#L173)、[`benchmark.read_text`](src/repoguard/api.py#L173) |
| [`from_environment`](src/repoguard/api.py#L184-L191) 184–191 | `() → FastAPI` | — | [`create_app`](src/repoguard/api.py#L185)、[`os.environ.get`](src/repoguard/api.py#L187)、[`os.environ.get`](src/repoguard/api.py#L188)、[`os.environ.get`](src/repoguard/api.py#L189) |

## [src/repoguard/architecture.py](src/repoguard/architecture.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`Rule`](src/repoguard/architecture.py#L13-L21) 13–21 | `class Rule` | 架构约束的数据结构，包括来源、目标限制、白名单和耦合数。 | — |
| [`Violation`](src/repoguard/architecture.py#L25-L31) 25–31 | `class Violation` | 用规则和模块身份描述一个架构关系，并保存影响地点。 | — |
| [`load_rules`](src/repoguard/architecture.py#L34-L72) 34–72 | `(path: Path) → list[Rule]` | 用安全 YAML 载入大小受限的规则文件，转换为明确的数据结构并检查名称及参数。 | [`path.open`](src/repoguard/architecture.py#L38)、[`stream.read`](src/repoguard/architecture.py#L39)、[`len`](src/repoguard/architecture.py#L40)、[`ValueError`](src/repoguard/architecture.py#L41) |
| [`matches`](src/repoguard/architecture.py#L75-L76) 75–76 | `(module: str, prefix: str) → bool` | — | [`module.startswith`](src/repoguard/architecture.py#L76) |
| [`dependencies`](src/repoguard/architecture.py#L79-L86) 79–86 | `(snapshot: Snapshot) → list[tuple[Symbol, Symbol, Edge]]` | — | [`snapshot.edges.values`](src/repoguard/architecture.py#L83) |
| [`evaluate`](src/repoguard/architecture.py#L89-L150) 89–150 | `(snapshot: Snapshot, rules: list[Rule]) → dict[tuple[str, str, str], Violation]` | 对单个快照应用依赖、边界、环和耦合规则，返回与源码行独立的违规键。 | [`CodeGraph`](src/repoguard/architecture.py#L91)、[`dependencies`](src/repoguard/architecture.py#L92)、[`graph.cycles`](src/repoguard/architecture.py#L96)、[`set`](src/repoguard/architecture.py#L97) |
| [`compare`](src/repoguard/architecture.py#L153-L165) 153–165 | `(base: Snapshot, target: Snapshot, rules: list[Rule]) → dict[str, list[Violation]]` | 分别评估基线和目标，按违规键计算差集和交集。new_dependency 只关注引入项。 | [`evaluate`](src/repoguard/architecture.py#L155)、[`sorted`](src/repoguard/architecture.py#L158)、[`new.keys`](src/repoguard/architecture.py#L158)、[`old.keys`](src/repoguard/architecture.py#L158) |

## [src/repoguard/cli.py](src/repoguard/cli.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`load_coverage`](src/repoguard/cli.py#L21-L27) 21–27 | `(path: Path) → CoverageMap` | — | [`opener`](src/repoguard/cli.py#L23)、[`stream.read`](src/repoguard/cli.py#L24)、[`len`](src/repoguard/cli.py#L25)、[`ValueError`](src/repoguard/cli.py#L26) |
| [`output`](src/repoguard/cli.py#L30-L31) 30–31 | `(value: Any) → None` | — | [`print`](src/repoguard/cli.py#L31)、[`json.dumps`](src/repoguard/cli.py#L31) |
| [`encode`](src/repoguard/cli.py#L34-L37) 34–37 | `(value: Any) → Any` | — | [`is_dataclass`](src/repoguard/cli.py#L35)、[`isinstance`](src/repoguard/cli.py#L35)、[`asdict`](src/repoguard/cli.py#L36)、[`TypeError`](src/repoguard/cli.py#L37) |
| [`parser`](src/repoguard/cli.py#L40-L92) 40–92 | `() → argparse.ArgumentParser` | — | [`argparse.ArgumentParser`](src/repoguard/cli.py#L41)、[`root.add_argument`](src/repoguard/cli.py#L42)、[`root.add_argument`](src/repoguard/cli.py#L43)、[`Path`](src/repoguard/cli.py#L43) |
| [`require_id`](src/repoguard/cli.py#L95-L101) 95–101 | `(view, query: str) → str` | — | [`view.find_definition`](src/repoguard/cli.py#L96)、[`len`](src/repoguard/cli.py#L97)、[`ValueError`](src/repoguard/cli.py#L98)、[`len`](src/repoguard/cli.py#L99) |
| [`dispatch`](src/repoguard/cli.py#L104-L192) 104–192 | `(engine: RepoGuard, args: argparse.Namespace) → int` | 把解析后的命令交给一个 RepoGuard 实例。需要 Git 差异、补丁或测试时委派给相应适配器。 | [`output`](src/repoguard/cli.py#L108)、[`engine.index`](src/repoguard/cli.py#L108)、[`engine.analyze_change_impact`](src/repoguard/cli.py#L111)、[`hasattr`](src/repoguard/cli.py#L113) |
| [`main`](src/repoguard/cli.py#L195-L203) 195–203 | `(argv: list[str] \| None=None) → int` | — | [`parser().parse_args`](src/repoguard/cli.py#L196)、[`parser`](src/repoguard/cli.py#L196)、[`IndexOptions`](src/repoguard/cli.py#L198)、[`tuple`](src/repoguard/cli.py#L198) |

## [src/repoguard/graph.py](src/repoguard/graph.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`CodeGraph`](src/repoguard/graph.py#L26-L151) 26–151 | `class CodeGraph` | 将 Snapshot 的文件、符号和边投影为 MultiDiGraph；无目标边另存作为诊断。 | — |
| [`CodeGraph.__init__`](src/repoguard/graph.py#L29-L63) 29–63 | `(self, snapshot: Snapshot, extra_edges: Iterable[Edge]=()) → None` | — | [`nx.MultiDiGraph`](src/repoguard/graph.py#L32)、[`self.graph.add_node`](src/repoguard/graph.py#L34)、[`identity`](src/repoguard/graph.py#L36)、[`self.graph.add_node`](src/repoguard/graph.py#L37) |
| [`CodeGraph.adjacent`](src/repoguard/graph.py#L65-L77) 65–77 | `(self, sid: str, *, reverse: bool=False, kinds: Iterable[EdgeType]=RELATIONS) → list[Edge]` | 按邻接方向和边类型返回关系。空间取决于匹配边数，未知节点返回空列表。 | [`set`](src/repoguard/graph.py#L76)、[`view`](src/repoguard/graph.py#L77) |
| [`CodeGraph.walk`](src/repoguard/graph.py#L79-L124) 79–124 | `(self, seeds: Iterable[str], *, reverse: bool=False, depth: int=4, kinds: Iterable[EdgeType]=RELATIONS, max_nodes: int=1000) → dict[str, tuple[Edge, ...]]` | 执行有深度和节点预算的多源 BFS。每节点保存首次到达的边序列，reverse 决定边的使用方向。 | [`ValueError`](src/repoguard/graph.py#L93)、[`dict.fromkeys`](src/repoguard/graph.py#L94)、[`islice`](src/repoguard/graph.py#L95)、[`dict.fromkeys`](src/repoguard/graph.py#L95) |
| [`CodeGraph.shortest_path`](src/repoguard/graph.py#L126-L137) 126–137 | `(self, source: str, target: str, kinds: Iterable[EdgeType]=RELATIONS, *, depth: int=30) → tuple[Edge, ...] \| None` | 从单源 BFS 取目标见证。路径度量为跳数，未在深度预算内到达返回 None。 | [`self.walk([source], kinds=kinds, depth=depth, max_nodes=max(1, len(self.graph))).get`](src/repoguard/graph.py#L135)、[`self.walk`](src/repoguard/graph.py#L135)、[`max`](src/repoguard/graph.py#L135)、[`len`](src/repoguard/graph.py#L135) |
| [`CodeGraph.cycles`](src/repoguard/graph.py#L139-L151) 139–151 | `(self, kinds: Iterable[EdgeType]=(EdgeType.DEPENDS_ON,)) → list[list[str]]` | 筛选指定关系投影后取强连通分量，单节点只有自环时才报告为环。 | [`set`](src/repoguard/graph.py#L141)、[`nx.DiGraph`](src/repoguard/graph.py#L142)、[`self.graph.edges`](src/repoguard/graph.py#L144)、[`sorted`](src/repoguard/graph.py#L147) |

## [src/repoguard/impact.py](src/repoguard/impact.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`SymbolChange`](src/repoguard/impact.py#L44-L49) 44–49 | `class SymbolChange` | 类型定义。成员职责见下方对应条目。 | — |
| [`Finding`](src/repoguard/impact.py#L53-L60) 53–60 | `class Finding` | 类型定义。成员职责见下方对应条目。 | — |
| [`ImpactReport`](src/repoguard/impact.py#L64-L74) 64–74 | `class ImpactReport` | 变更、排序风险、循环关系、不确定边和回退条件的报告。 | — |
| [`is_public`](src/repoguard/impact.py#L77-L83) 77–83 | `(symbol: Symbol \| None) → bool` | — | [`symbol.name.startswith`](src/repoguard/impact.py#L78)、[`any`](src/repoguard/impact.py#L80)、[`part.startswith`](src/repoguard/impact.py#L81)、[`symbol.qualified_name.removeprefix(symbol.module + '.').split`](src/repoguard/impact.py#L82) |
| [`is_config`](src/repoguard/impact.py#L86-L87) 86–87 | `(path: str) → bool` | — | [`bool`](src/repoguard/impact.py#L87)、[`CONFIG.fullmatch`](src/repoguard/impact.py#L87)、[`PurePosixPath`](src/repoguard/impact.py#L87)、[`path.startswith`](src/repoguard/impact.py#L87) |
| [`risk_step`](src/repoguard/impact.py#L90-L92) 90–92 | `(score: float, weight: float, uncertain: bool) → float` | 对单条关系按类型权重、固定距离衰减和可信度折扣更新风险。 | — |
| [`_imports`](src/repoguard/impact.py#L95-L99) 95–99 | `(snapshot: Snapshot, path: str) → set[tuple[str, str]]` | — | [`snapshot.units.get`](src/repoguard/impact.py#L96)、[`set`](src/repoguard/impact.py#L99) |
| [`classify`](src/repoguard/impact.py#L102-L174) 102–174 | `(base: Snapshot, target: Snapshot, files: list[FileChange]) → list[SymbolChange]` | 比较双侧 Unit 的符号 ID、签名、内容摘要及导入事实。分类包括签名、实现、增删、配置和未知变更。 | [`base.units.get`](src/repoguard/impact.py#L111)、[`target.units.get`](src/repoguard/impact.py#L111)、[`is_config`](src/repoguard/impact.py#L114)、[`result.append`](src/repoguard/impact.py#L115) |
| [`analyze`](src/repoguard/impact.py#L177-L276) 177–276 | `(base: Snapshot, target: Snapshot, files: list[FileChange], *, depth: int=5, kinds: Iterable[EdgeType]=RELATIONS, max_nodes: int=2000, base_coverage_edges: Iterable[Edge]=()) → ImpactReport` | 接受基线、目标、文件改动与遍历参数，进行两版反向 BFS，并按证据与衰减排序。 | [`ValueError`](src/repoguard/impact.py#L193)、[`ValueError`](src/repoguard/impact.py#L195)、[`classify`](src/repoguard/impact.py#L196)、[`CodeGraph`](src/repoguard/impact.py#L197) |
| [`markdown`](src/repoguard/impact.py#L279-L330) 279–330 | `(report: ImpactReport) → str` | 把结构化影响报告转换为可审查 Markdown，列出位置、边证据、不确定性及验证建议。 | [`lines.append`](src/repoguard/impact.py#L298)、[`escaped`](src/repoguard/impact.py#L299)、[`lines.extend`](src/repoguard/impact.py#L301)、[`' ← '.join`](src/repoguard/impact.py#L311) |
| [`markdown.escaped`](src/repoguard/impact.py#L282-L283) 282–283 | `(value: str) → str` | — | [`value.replace('\|', '\\\|').replace`](src/repoguard/impact.py#L283)、[`value.replace`](src/repoguard/impact.py#L283) |

## [src/repoguard/import_migration.py](src/repoguard/import_migration.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`ImportRewrite`](src/repoguard/import_migration.py#L20-L120) 20–120 | `class ImportRewrite(cst.CSTTransformer)` | 根据旧、新模块名和源码位置更新直接或相对导入，保留适用的本地别名。 | — |
| [`ImportRewrite.__init__`](src/repoguard/import_migration.py#L25-L39) 25–39 | `(self, unit: Unit, old: str, new: str, attributes: set[tuple[int, int]]) → None` | — | [`old.rpartition`](src/repoguard/import_migration.py#L33)、[`new.rpartition`](src/repoguard/import_migration.py#L34)、[`unit.path.endswith`](src/repoguard/import_migration.py#L36)、[`unit.module.rpartition`](src/repoguard/import_migration.py#L36) |
| [`ImportRewrite.leave_Import`](src/repoguard/import_migration.py#L41-L54) 41–54 | `(self, original_node: cst.Import, updated_node: cst.Import) → cst.Import` | — | [`get_full_name_for_node`](src/repoguard/import_migration.py#L44)、[`cst.AsName`](src/repoguard/import_migration.py#L47)、[`cst.Name`](src/repoguard/import_migration.py#L47)、[`self.problems.append`](src/repoguard/import_migration.py#L49) |
| [`ImportRewrite.leave_ImportFrom`](src/repoguard/import_migration.py#L56-L105) 56–105 | `(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) → cst.BaseSmallStatement` | — | [`get_full_name_for_node`](src/repoguard/import_migration.py#L61)、[`self.package.split`](src/repoguard/import_migration.py#L63)、[`len`](src/repoguard/import_migration.py#L64)、[`len`](src/repoguard/import_migration.py#L65) |
| [`ImportRewrite.leave_Attribute`](src/repoguard/import_migration.py#L107-L120) 107–120 | `(self, original_node: cst.Attribute, updated_node: cst.Attribute) → cst.Attribute` | — | [`self.get_metadata`](src/repoguard/import_migration.py#L112)、[`get_full_name_for_node`](src/repoguard/import_migration.py#L113)、[`self.problems.append`](src/repoguard/import_migration.py#L117)、[`updated_node.with_changes`](src/repoguard/import_migration.py#L119) |
| [`plan_module_move`](src/repoguard/import_migration.py#L123-L260) 123–260 | `(repo: Repository, snapshot: Snapshot, old: str, new: str) → Plan` | 预览普通模块的跨文件迁移。验证路径与导入形态、运行 LibCST 写出补丁草稿，再验证重解析和确定引用计数。 | [`any`](src/repoguard/import_migration.py#L128)、[`part.isidentifier`](src/repoguard/import_migration.py#L129)、[`keyword.iskeyword`](src/repoguard/import_migration.py#L129)、[`module.split`](src/repoguard/import_migration.py#L131) |
| [`plan_module_move.result`](src/repoguard/import_migration.py#L150-L159) 150–159 | `(patch: str='') → Plan` | — | [`Plan`](src/repoguard/import_migration.py#L151)、[`sorted`](src/repoguard/import_migration.py#L154)、[`sorted`](src/repoguard/import_migration.py#L155)、[`set`](src/repoguard/import_migration.py#L155) |

## [src/repoguard/indexer.py](src/repoguard/indexer.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`IndexOptions`](src/repoguard/indexer.py#L23-L38) 23–38 | `class IndexOptions` | 规定源码根和单个文件字节上限，参与缓存版本键。 | — |
| [`IndexOptions.__post_init__`](src/repoguard/indexer.py#L29-L33) 29–33 | `(self) → None` | — | [`any`](src/repoguard/indexer.py#L30)、[`safe_relative`](src/repoguard/indexer.py#L30)、[`ValueError`](src/repoguard/indexer.py#L31)、[`ValueError`](src/repoguard/indexer.py#L33) |
| [`IndexOptions.key`](src/repoguard/indexer.py#L36-L38) 36–38 | `(self) → str` | 序列化索引格式、解释器版本和分析选项。任一变化会生成不同的快照版本。 | [`serialize`](src/repoguard/indexer.py#L38)、[`list`](src/repoguard/indexer.py#L38)、[`asdict`](src/repoguard/indexer.py#L38) |
| [`Indexer`](src/repoguard/indexer.py#L44-L236) 44–236 | `class Indexer` | 合并 Git 对象、缓存语法事实和依赖失效，协调存储层发布索引。 | — |
| [`Indexer.__init__`](src/repoguard/indexer.py#L47-L56) 47–56 | `(self, repository: Repository, store: Store, options: IndexOptions=DEFAULT_OPTIONS, workers: int=4) → None` | — | [`ValueError`](src/repoguard/indexer.py#L55) |
| [`Indexer.version`](src/repoguard/indexer.py#L58-L59) 58–59 | `(self, commit: str) → str` | — | [`identity`](src/repoguard/indexer.py#L59) |
| [`Indexer.load`](src/repoguard/indexer.py#L61-L62) 61–62 | `(self, revision: str='HEAD') → Snapshot \| None` | — | [`self.store.load`](src/repoguard/indexer.py#L62)、[`self.version`](src/repoguard/indexer.py#L62)、[`self.repo.commit`](src/repoguard/indexer.py#L62) |
| [`Indexer.index`](src/repoguard/indexer.py#L64-L199) 64–199 | `(self, target: str='HEAD', *, base: str \| None=None, persist: bool=True, mode: str='dependency') → Snapshot` | 按目标提交构建 Snapshot，可选使用基线提交。full 全量处理，file 复用文件事实，dependency 还复用未失效的链接。 | [`ValueError`](src/repoguard/indexer.py#L78)、[`perf_counter`](src/repoguard/indexer.py#L79)、[`self.repo.commit`](src/repoguard/indexer.py#L80)、[`self.version`](src/repoguard/indexer.py#L81) |
| [`Indexer._changed_paths`](src/repoguard/indexer.py#L202-L210) 202–210 | `(files: dict[str, File], previous: Snapshot \| None) → set[str]` | 比较双侧文件清单，保留新增、删除、对象变化及处理状态变动的路径。 | [`set`](src/repoguard/indexer.py#L205)、[`files.keys`](src/repoguard/indexer.py#L208)、[`previous.files.keys`](src/repoguard/indexer.py#L208)、[`files.get`](src/repoguard/indexer.py#L209) |
| [`Indexer._changed_modules`](src/repoguard/indexer.py#L212-L236) 212–236 | `(self, paths: set[str], units: dict[str, Unit], previous: Snapshot \| None, catalog: Catalog) → set[str]` | 用两版模块、命名空间和动态成员集合计算失效键。旧链接探测到的空模块也可能与新键匹配。 | [`set`](src/repoguard/indexer.py#L221)、[`module_name`](src/repoguard/indexer.py#L223)、[`previous.units.values`](src/repoguard/indexer.py#L229)、[`module_prefixes`](src/repoguard/indexer.py#L230) |
| [`_parse_entry`](src/repoguard/indexer.py#L239-L245) 239–245 | `(entry: tuple[File, bytes], *, repo: str, roots: tuple[str, ...]) → tuple[File, Unit \| None]` | — | [`parse`](src/repoguard/indexer.py#L245) |

## [src/repoguard/mcp_server.py](src/repoguard/mcp_server.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`create_server`](src/repoguard/mcp_server.py#L15-L84) 15–84 | `(engine: RepoGuard, revision: str) → FastMCP` | 创建 FastMCP 适配层并固定一个已发布的仓库版本，工具将 SDK 记录转为结构化响应。 | [`FastMCP`](src/repoguard/mcp_server.py#L17)、[`engine.view`](src/repoguard/mcp_server.py#L18) |
| [`create_server.search_symbols`](src/repoguard/mcp_server.py#L22-L27) 22–27 | `(query: str, limit: int=20) → dict[str, object]` | Search a pinned commit using exact names, BM25 and dependency evidence. | [`asdict`](src/repoguard/mcp_server.py#L26)、[`view.search_symbols`](src/repoguard/mcp_server.py#L26) |
| [`create_server.find_definition`](src/repoguard/mcp_server.py#L30-L35) 30–35 | `(query: str) → dict[str, object]` | Return matching definitions at the pinned commit with path and line range. | [`asdict`](src/repoguard/mcp_server.py#L34)、[`view.find_definition`](src/repoguard/mcp_server.py#L34) |
| [`create_server.find_references`](src/repoguard/mcp_server.py#L38-L43) 38–43 | `(symbol_id: str) → dict[str, object]` | Return import and lexical references to a known symbol. | [`asdict`](src/repoguard/mcp_server.py#L42)、[`view.find_references`](src/repoguard/mcp_server.py#L42) |
| [`create_server.get_callers`](src/repoguard/mcp_server.py#L46-L48) 46–48 | `(symbol_id: str) → dict[str, object]` | Return statically known and possible incoming calls. | [`asdict`](src/repoguard/mcp_server.py#L48)、[`view.get_callers`](src/repoguard/mcp_server.py#L48) |
| [`create_server.get_callees`](src/repoguard/mcp_server.py#L51-L53) 51–53 | `(symbol_id: str) → dict[str, object]` | Return statically known and possible outgoing calls. | [`asdict`](src/repoguard/mcp_server.py#L53)、[`view.get_callees`](src/repoguard/mcp_server.py#L53) |
| [`create_server.get_dependency_graph`](src/repoguard/mcp_server.py#L56-L62) 56–62 | `(symbol_id: str, depth: int=2, limit: int=100) → dict[str, object]` | Return a bounded subgraph with confidence and source evidence. | [`view.get_dependency_graph`](src/repoguard/mcp_server.py#L58)、[`encode`](src/repoguard/mcp_server.py#L60)、[`asdict`](src/repoguard/mcp_server.py#L61) |
| [`create_server.analyze_change_impact`](src/repoguard/mcp_server.py#L65-L67) 65–67 | `(base_commit: str, depth: int=5) → dict[str, object]` | Compare a published base snapshot with this server's pinned commit. | [`asdict`](src/repoguard/mcp_server.py#L67)、[`engine.analyze_change_impact`](src/repoguard/mcp_server.py#L67) |
| [`create_server.select_related_tests`](src/repoguard/mcp_server.py#L70-L72) 70–72 | `(base_commit: str) → dict[str, object]` | Return static test evidence and conservative fallback information. | [`asdict`](src/repoguard/mcp_server.py#L72)、[`engine.select_related_tests`](src/repoguard/mcp_server.py#L72) |
| [`create_server.plan_refactoring`](src/repoguard/mcp_server.py#L75-L77) 75–77 | `(symbol_id: str, new_name: str) → dict[str, object]` | Preview a symbol rename and report validation without writing repository files. | [`asdict`](src/repoguard/mcp_server.py#L77)、[`engine.plan_refactoring`](src/repoguard/mcp_server.py#L77) |
| [`create_server.validate_patch`](src/repoguard/mcp_server.py#L80-L82) 80–82 | `(patch: str) → dict[str, object]` | Check a unified Python diff against the pinned commit in memory. | [`asdict`](src/repoguard/mcp_server.py#L82)、[`engine.validate_patch`](src/repoguard/mcp_server.py#L82) |
| [`main`](src/repoguard/mcp_server.py#L87-L93) 87–93 | `() → None` | — | [`argparse.ArgumentParser`](src/repoguard/mcp_server.py#L88)、[`parser.add_argument`](src/repoguard/mcp_server.py#L89)、[`parser.add_argument`](src/repoguard/mcp_server.py#L90)、[`parser.add_argument`](src/repoguard/mcp_server.py#L91) |

## [src/repoguard/model.py](src/repoguard/model.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`digest`](src/repoguard/model.py#L10-L11) 10–11 | `(data: bytes) → str` | — | [`sha256(data).hexdigest`](src/repoguard/model.py#L11)、[`sha256`](src/repoguard/model.py#L11) |
| [`identity`](src/repoguard/model.py#L14-L16) 14–16 | `(*parts: str) → str` | 用 NUL 分隔的身份组件形成确定性摘要，供仓库、符号与提交快照共同标识。 | [`digest`](src/repoguard/model.py#L16)、[`'\x00'.join(parts).encode`](src/repoguard/model.py#L16)、[`'\x00'.join`](src/repoguard/model.py#L16) |
| [`Confidence`](src/repoguard/model.py#L19-L22) 19–22 | `class Confidence(StrEnum)` | 类型定义。成员职责见下方对应条目。 | — |
| [`EdgeType`](src/repoguard/model.py#L25-L34) 25–34 | `class EdgeType(StrEnum)` | 类型定义。成员职责见下方对应条目。 | — |
| [`File`](src/repoguard/model.py#L38-L49) 38–49 | `class File` | 保存 Git 文件的路径、对象 ID、大小、状态和分析诊断。 | — |
| [`Symbol`](src/repoguard/model.py#L53-L71) 53–71 | `class Symbol` | 符号定义的稳定 ID、作用域、父符号、位置、签名和内容摘要。 | — |
| [`Binding`](src/repoguard/model.py#L75-L86) 75–86 | `class Binding` | 记录名字能绑定到的定义或导入位置，包含出现时间与条件分支标记。 | — |
| [`Scope`](src/repoguard/model.py#L90-L99) 90–99 | `class Scope` | 词法作用域记录，包含父作用域、所有者、名字绑定表与 global/nonlocal 声明。 | — |
| [`Usage`](src/repoguard/model.py#L103-L113) 103–113 | `class Usage` | 第一遍遍历采集的引用事实。解析器随后决定边的目标和可信度。 | — |
| [`Unit`](src/repoguard/model.py#L117-L125) 117–125 | `class Unit` | 单个 Python 文件的语法事实缓存，包含模块、符号、作用域及引用。 | — |
| [`Edge`](src/repoguard/model.py#L129-L140) 129–140 | `class Edge` | 跨快照可序列化的有向边证据。target 为空时保留源码位置和不确定性。 | — |
| [`Snapshot`](src/repoguard/model.py#L144-L160) 144–160 | `class Snapshot` | 一个 Git 提交和一组选项的文件清单、语法事实、关系、探测集合与收据。 | — |
| [`Snapshot.symbols`](src/repoguard/model.py#L158-L160) 158–160 | `(self) → dict[str, Symbol]` | 按符号 ID 汇总各文件的符号。每次访问都创建字典，时间与额外空间均为 O(S)。 | [`self.units.values`](src/repoguard/model.py#L160)、[`unit.symbols.items`](src/repoguard/model.py#L160) |
| [`FileChange`](src/repoguard/model.py#L164-L171) 164–171 | `class FileChange` | 两个 Git 树之间的文件状态、双侧路径和双侧行闭区间。 | — |

## [src/repoguard/parser.py](src/repoguard/parser.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`decode_python`](src/repoguard/parser.py#L18-L20) 18–20 | `(raw: bytes) → tuple[str, str]` | — | [`tokenize.detect_encoding`](src/repoguard/parser.py#L19)、[`io.BytesIO`](src/repoguard/parser.py#L19)、[`raw.decode`](src/repoguard/parser.py#L20) |
| [`physical_lines`](src/repoguard/parser.py#L23-L27) 23–27 | `(text: str) → list[str]` | — | [`re.split`](src/repoguard/parser.py#L26)、[`text.endswith`](src/repoguard/parser.py#L27) |
| [`dotted`](src/repoguard/parser.py#L30-L37) 30–37 | `(node: ast.AST) → str \| None` | — | [`isinstance`](src/repoguard/parser.py#L32)、[`names.append`](src/repoguard/parser.py#L33)、[`isinstance`](src/repoguard/parser.py#L35)、[`'.'.join`](src/repoguard/parser.py#L37) |
| [`parse`](src/repoguard/parser.py#L40-L68) 40–68 | `(file: File, raw: bytes, repository_id: str, roots: tuple[str, ...]) → tuple[File, Unit \| None]` | 解析一个 Git 文件。输入包含原始字节、文件信息、仓库 ID 和源码根，输出带状态的 File 与可选 Unit。 | [`replace`](src/repoguard/parser.py#L51)、[`digest`](src/repoguard/parser.py#L51)、[`replace`](src/repoguard/parser.py#L53)、[`decode_python`](src/repoguard/parser.py#L55) |
| [`Collector`](src/repoguard/parser.py#L71-L474) 71–474 | `class Collector(ast.NodeVisitor)` | 在 AST 遍历中维护当前 Scope，将定义、绑定、引用和导入拆成可序列化的 Unit 事实。 | — |
| [`Collector.__init__`](src/repoguard/parser.py#L74-L101) 74–101 | `(self, repo: str, path: str, module: str, text: str) → None` | — | [`line.encode`](src/repoguard/parser.py#L76)、[`physical_lines`](src/repoguard/parser.py#L76)、[`identity`](src/repoguard/parser.py#L82)、[`Scope`](src/repoguard/parser.py#L83) |
| [`Collector.column`](src/repoguard/parser.py#L103-L105) 103–105 | `(self, line: int, offset: int) → int` | 把 CPython UTF-8 字节列偏移转换为 Unicode 字符列，供 LibCST 和界面使用。 | [`len`](src/repoguard/parser.py#L105)、[`self.lines[line - 1][:offset].decode`](src/repoguard/parser.py#L105) |
| [`Collector.add_symbol`](src/repoguard/parser.py#L107-L145) 107–145 | `(self, name: str, kind: str, node: ast.expr \| ast.stmt \| ast.arg, signature: str='', uncertain: bool=False) → Symbol` | 用仓库、文件、作用域、名字、种类与同名序号派生符号 ID。 | [`self.counts.get`](src/repoguard/parser.py#L120)、[`identity`](src/repoguard/parser.py#L122)、[`str`](src/repoguard/parser.py#L122)、[`isinstance`](src/repoguard/parser.py#L125) |
| [`Collector.bind`](src/repoguard/parser.py#L147-L150) 147–150 | `(self, local: str, binding: Binding) → None` | — | [`self.scope.bindings.setdefault(local, []).append`](src/repoguard/parser.py#L148)、[`self.scope.bindings.setdefault`](src/repoguard/parser.py#L148)、[`replace`](src/repoguard/parser.py#L149)、[`bool`](src/repoguard/parser.py#L149) |
| [`Collector.bind_symbol`](src/repoguard/parser.py#L152-L167) 152–167 | `(self, symbol: Symbol, available: ast.AST \| None=None) → None` | 记录绑定位置和赋值或定义结束后的可用位置，供模块或类体中的按行查找。 | [`getattr`](src/repoguard/parser.py#L155)、[`self.column`](src/repoguard/parser.py#L156)、[`self.bind`](src/repoguard/parser.py#L157)、[`Binding`](src/repoguard/parser.py#L159) |
| [`Collector.use`](src/repoguard/parser.py#L169-L196) 169–196 | `(self, kind: str, node: ast.AST, text: str, *, module: str='', name: str='', owner: str \| None=None) → None` | 把 AST 引用转换为位置明确的 Usage，不在本阶段决定目标。 | [`isinstance`](src/repoguard/parser.py#L182)、[`len`](src/repoguard/parser.py#L184)、[`node.attr.encode`](src/repoguard/parser.py#L184)、[`self.usages.append`](src/repoguard/parser.py#L185) |
| [`Collector.enter`](src/repoguard/parser.py#L198-L203) 198–203 | `(self, sid: str, kind: str, owner: str) → tuple[Scope, int]` | — | [`Scope`](src/repoguard/parser.py#L200) |
| [`Collector.visit_Global`](src/repoguard/parser.py#L205-L206) 205–206 | `(self, node: ast.Global) → None` | — | [`self.scope.globals.extend`](src/repoguard/parser.py#L206) |
| [`Collector.visit_Nonlocal`](src/repoguard/parser.py#L208-L209) 208–209 | `(self, node: ast.Nonlocal) → None` | — | [`self.scope.nonlocals.extend`](src/repoguard/parser.py#L209) |
| [`Collector.arguments`](src/repoguard/parser.py#L211-L217) 211–217 | `(self, args: ast.arguments) → list[ast.arg]` | — | — |
| [`Collector.defaults`](src/repoguard/parser.py#L219-L225) 219–225 | `(self, args: ast.arguments) → None` | — | [`self.visit`](src/repoguard/parser.py#L222)、[`self.arguments`](src/repoguard/parser.py#L223)、[`self.visit`](src/repoguard/parser.py#L225) |
| [`Collector.visit_FunctionDef`](src/repoguard/parser.py#L227-L276) 227–276 | `(self, node: Function) → None` | 先在外层采集装饰器、默认值与注解，再建立函数定义并进入参数和函数体作用域。 | [`self.visit`](src/repoguard/parser.py#L233)、[`self.defaults`](src/repoguard/parser.py#L234)、[`self.visit`](src/repoguard/parser.py#L236)、[`self.path.rsplit`](src/repoguard/parser.py#L238) |
| [`Collector.visit_ClassDef`](src/repoguard/parser.py#L280-L295) 280–295 | `(self, node: ast.ClassDef) → None` | 在外层记录类基类和装饰器，切入类体作用域后记录成员。 | [`self.visit`](src/repoguard/parser.py#L283)、[`ast.unparse`](src/repoguard/parser.py#L284)、[`ast.Tuple`](src/repoguard/parser.py#L284)、[`ast.Load`](src/repoguard/parser.py#L284) |
| [`Collector.visit_Lambda`](src/repoguard/parser.py#L297-L304) 297–304 | `(self, node: ast.Lambda) → None` | — | [`self.defaults`](src/repoguard/parser.py#L298)、[`identity`](src/repoguard/parser.py#L299)、[`str`](src/repoguard/parser.py#L299)、[`self.enter`](src/repoguard/parser.py#L300) |
| [`Collector.visit_ListComp`](src/repoguard/parser.py#L306-L328) 306–328 | `(self, node: Comprehension) → None` | 在外层访问推导式第一个迭代对象，再建立推导式作用域记录后续绑定。 | [`self.visit`](src/repoguard/parser.py#L309)、[`identity`](src/repoguard/parser.py#L310)、[`str`](src/repoguard/parser.py#L310)、[`self.enter`](src/repoguard/parser.py#L311) |
| [`Collector.visit_Name`](src/repoguard/parser.py#L332-L340) 332–340 | `(self, node: ast.Name) → None` | — | [`isinstance`](src/repoguard/parser.py#L333)、[`self.use`](src/repoguard/parser.py#L334)、[`isinstance`](src/repoguard/parser.py#L335)、[`self.bind_symbol`](src/repoguard/parser.py#L336) |
| [`Collector.visit_Assign`](src/repoguard/parser.py#L342-L345) 342–345 | `(self, node: ast.Assign) → None` | — | [`self.visit`](src/repoguard/parser.py#L343)、[`self.assignment`](src/repoguard/parser.py#L345) |
| [`Collector.visit_AnnAssign`](src/repoguard/parser.py#L347-L353) 347–353 | `(self, node: ast.AnnAssign) → None` | — | [`self.visit`](src/repoguard/parser.py#L348)、[`self.visit`](src/repoguard/parser.py#L350)、[`self.assignment`](src/repoguard/parser.py#L351)、[`isinstance`](src/repoguard/parser.py#L352) |
| [`Collector.assignment`](src/repoguard/parser.py#L355-L364) 355–364 | `(self, target: ast.expr, statement: ast.AST) → None` | — | [`isinstance`](src/repoguard/parser.py#L356)、[`self.bind_symbol`](src/repoguard/parser.py#L357)、[`self.add_symbol`](src/repoguard/parser.py#L357)、[`isinstance`](src/repoguard/parser.py#L358) |
| [`Collector.visit_NamedExpr`](src/repoguard/parser.py#L366-L374) 366–374 | `(self, node: ast.NamedExpr) → None` | — | [`self.visit`](src/repoguard/parser.py#L367)、[`int`](src/repoguard/parser.py#L371)、[`self.assignment`](src/repoguard/parser.py#L372)、[`int`](src/repoguard/parser.py#L373) |
| [`Collector.visit_Attribute`](src/repoguard/parser.py#L376-L381) 376–381 | `(self, node: ast.Attribute) → None` | — | [`isinstance`](src/repoguard/parser.py#L377)、[`self.use`](src/repoguard/parser.py#L378)、[`dotted`](src/repoguard/parser.py#L378)、[`dotted`](src/repoguard/parser.py#L379) |
| [`Collector.visit_Call`](src/repoguard/parser.py#L383-L410) 383–410 | `(self, node: ast.Call) → None` | 为调用保存点分表达式，反射和无法表示的调用保留动态事实供解析器降级。 | [`dotted`](src/repoguard/parser.py#L385)、[`len`](src/repoguard/parser.py#L396)、[`isinstance`](src/repoguard/parser.py#L399)、[`isinstance`](src/repoguard/parser.py#L400) |
| [`Collector.visit_Import`](src/repoguard/parser.py#L412-L417) 412–417 | `(self, node: ast.Import) → None` | — | [`alias.name.split`](src/repoguard/parser.py#L414)、[`self.bind`](src/repoguard/parser.py#L416)、[`Binding`](src/repoguard/parser.py#L416)、[`self.use`](src/repoguard/parser.py#L417) |
| [`Collector.visit_ImportFrom`](src/repoguard/parser.py#L419-L448) 419–448 | `(self, node: ast.ImportFrom) → None` | 依据当前模块的包路径和相对导入级别记录绝对模块猜测，别名独立保存在绑定表。 | [`self.module.split`](src/repoguard/parser.py#L421)、[`self.path.endswith`](src/repoguard/parser.py#L422)、[`package.pop`](src/repoguard/parser.py#L423)、[`len`](src/repoguard/parser.py#L426) |
| [`Collector.guarded`](src/repoguard/parser.py#L450-L454) 450–454 | `(self, node: ast.AST) → None` | 在条件、循环和异常等结构内部标记可能执行的绑定，随后恢复外层条件层级。 | [`self.generic_visit`](src/repoguard/parser.py#L453) |
| [`Collector.visit_ExceptHandler`](src/repoguard/parser.py#L459-L462) 459–462 | `(self, node: ast.ExceptHandler) → None` | — | [`self.bind`](src/repoguard/parser.py#L461)、[`Binding`](src/repoguard/parser.py#L461)、[`self.generic_visit`](src/repoguard/parser.py#L462) |
| [`Collector.visit_MatchAs`](src/repoguard/parser.py#L464-L467) 464–467 | `(self, node: ast.MatchAs) → None` | — | [`self.bind`](src/repoguard/parser.py#L466)、[`Binding`](src/repoguard/parser.py#L466)、[`self.generic_visit`](src/repoguard/parser.py#L467) |
| [`Collector.visit_MatchMapping`](src/repoguard/parser.py#L471-L474) 471–474 | `(self, node: ast.MatchMapping) → None` | — | [`self.bind`](src/repoguard/parser.py#L473)、[`Binding`](src/repoguard/parser.py#L473)、[`self.generic_visit`](src/repoguard/parser.py#L474) |

## [src/repoguard/pytest_coverage.py](src/repoguard/pytest_coverage.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`pytest_sessionstart`](src/repoguard/pytest_coverage.py#L18-L30) 18–30 | `(session: pytest.Session) → None` | 初始化测试会话计数；请求覆盖时创建仅针对仓库根的 Coverage 对象。 | [`_failures.clear`](src/repoguard/pytest_coverage.py#L21)、[`_collected.clear`](src/repoguard/pytest_coverage.py#L22)、[`os.environ.get`](src/repoguard/pytest_coverage.py#L24)、[`Coverage`](src/repoguard/pytest_coverage.py#L25) |
| [`pytest_collection_finish`](src/repoguard/pytest_coverage.py#L33-L34) 33–34 | `(session: pytest.Session) → None` | — | [`_collected.extend`](src/repoguard/pytest_coverage.py#L34) |
| [`pytest_collectreport`](src/repoguard/pytest_coverage.py#L37-L39) 37–39 | `(report: pytest.CollectReport) → None` | — | — |
| [`pytest_runtest_protocol`](src/repoguard/pytest_coverage.py#L43-L51) 43–51 | `(item: pytest.Item, nextitem: pytest.Item \| None)` | 在完整 pytest 用例协议周围切换 Coverage 上下文，nodeid 包括参数，覆盖 setup 到 teardown。 | [`_coverage.switch_context`](src/repoguard/pytest_coverage.py#L46)、[`_coverage.switch_context`](src/repoguard/pytest_coverage.py#L51) |
| [`pytest_runtest_logreport`](src/repoguard/pytest_coverage.py#L54-L56) 54–56 | `(report: pytest.TestReport) → None` | — | [`_failures.add`](src/repoguard/pytest_coverage.py#L56) |
| [`pytest_sessionfinish`](src/repoguard/pytest_coverage.py#L59-L90) 59–90 | `(session: pytest.Session, exitstatus: int) → None` | 把 Coverage 的行上下文汇总为用例映射，并记录未归因行、失败用例和采集完整性。 | [`_coverage.stop`](src/repoguard/pytest_coverage.py#L65)、[`_coverage.get_data`](src/repoguard/pytest_coverage.py#L66)、[`session.config.rootpath.resolve`](src/repoguard/pytest_coverage.py#L67)、[`data.measured_files`](src/repoguard/pytest_coverage.py#L68) |

## [src/repoguard/refactoring.py](src/repoguard/refactoring.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`Plan`](src/repoguard/refactoring.py#L31-L40) 31–40 | `class Plan` | 记录候选改动文件、阻塞原因、检查结果和统一差异；计划对象本身不写入项目。 | — |
| [`Rewrite`](src/repoguard/refactoring.py#L43-L170) 43–170 | `class Rewrite(cst.CSTTransformer)` | 根据可信位置改写 CST 名称、函数定义和调用，保留结构化格式和注释。 | — |
| [`Rewrite.__init__`](src/repoguard/refactoring.py#L48-L60) 48–60 | `(self, target: Position \| None, positions: set[Position], operation: str, name: str, value: cst.BaseExpression \| None, original: str) → None` | — | [`set`](src/repoguard/refactoring.py#L59) |
| [`Rewrite.position`](src/repoguard/refactoring.py#L62-L64) 62–64 | `(self, node: cst.CSTNode) → Position` | — | [`self.get_metadata`](src/repoguard/refactoring.py#L63) |
| [`Rewrite.leave_Name`](src/repoguard/refactoring.py#L66-L75) 66–75 | `(self, original_node: cst.Name, updated_node: cst.Name) → cst.Name` | 仅在匹配的源码坐标上替换原标识符，将修改位置登记给规划器逐项核对。 | [`self.position`](src/repoguard/refactoring.py#L71)、[`self.changed.add`](src/repoguard/refactoring.py#L73)、[`updated_node.with_changes`](src/repoguard/refactoring.py#L74) |
| [`Rewrite.leave_ImportAlias`](src/repoguard/refactoring.py#L77-L96) 77–96 | `(self, original_node: cst.ImportAlias, updated_node: cst.ImportAlias) → cst.ImportAlias` | — | [`isinstance`](src/repoguard/refactoring.py#L86)、[`self.position`](src/repoguard/refactoring.py#L89)、[`updated_node.with_changes`](src/repoguard/refactoring.py#L91)、[`alias.with_changes`](src/repoguard/refactoring.py#L92) |
| [`Rewrite.leave_Assign`](src/repoguard/refactoring.py#L98-L118) 98–118 | `(self, original_node: cst.Assign, updated_node: cst.Assign) → cst.Assign` | — | [`any`](src/repoguard/refactoring.py#L101)、[`isinstance`](src/repoguard/refactoring.py#L102)、[`isinstance`](src/repoguard/refactoring.py#L105)、[`isinstance`](src/repoguard/refactoring.py#L111) |
| [`Rewrite.leave_FunctionDef`](src/repoguard/refactoring.py#L120-L136) 120–136 | `(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) → cst.FunctionDef` | 按目标定义坐标重命名或添加仅关键字参数，保留原参数节点。 | [`self.position`](src/repoguard/refactoring.py#L126)、[`self.changed.add`](src/repoguard/refactoring.py#L128)、[`updated_node.with_changes`](src/repoguard/refactoring.py#L130)、[`updated_node.name.with_changes`](src/repoguard/refactoring.py#L130) |
| [`Rewrite.leave_ClassDef`](src/repoguard/refactoring.py#L138-L146) 138–146 | `(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) → cst.ClassDef` | — | [`self.position`](src/repoguard/refactoring.py#L143)、[`self.changed.add`](src/repoguard/refactoring.py#L145)、[`updated_node.with_changes`](src/repoguard/refactoring.py#L146)、[`updated_node.name.with_changes`](src/repoguard/refactoring.py#L146) |
| [`Rewrite.leave_Call`](src/repoguard/refactoring.py#L148-L170) 148–170 | `(self, original_node: cst.Call, updated_node: cst.Call) → cst.Call` | 在可确认的调用点补入用户提供的字面量。现有同名关键字或参数展开进入阻塞记录。 | [`self.position`](src/repoguard/refactoring.py#L153)、[`isinstance`](src/repoguard/refactoring.py#L153)、[`any`](src/repoguard/refactoring.py#L156)、[`self.problems.append`](src/repoguard/refactoring.py#L160) |
| [`unified_patch`](src/repoguard/refactoring.py#L173-L196) 173–196 | `(changed: dict[str, tuple[str \| None, str \| None]]) → str` | 将原旧与新内容映射生成统一差异，保留无末尾换行标记；拒绝不安全路径。 | [`sorted`](src/repoguard/refactoring.py#L176)、[`changed.items`](src/repoguard/refactoring.py#L176)、[`safe_relative`](src/repoguard/refactoring.py#L177)、[`any`](src/repoguard/refactoring.py#L177) |
| [`semantic_counts`](src/repoguard/refactoring.py#L199-L222) 199–222 | `(symbols: dict[str, Symbol], edges: list[Edge], renamed: dict[str, str], moved_paths: dict[str, str] \| None=None) → Counter[tuple]` | 按映射后的定义身份和边种类统计确定关系，供 before/after 对照。 | [`Counter`](src/repoguard/refactoring.py#L215)、[`label`](src/repoguard/refactoring.py#L216) |
| [`semantic_counts.label`](src/repoguard/refactoring.py#L207-L213) 207–213 | `(sid: str) → tuple[str, str, str]` | — | [`(moved_paths or {}).get`](src/repoguard/refactoring.py#L210)、[`renamed.get`](src/repoguard/refactoring.py#L211) |
| [`plan`](src/repoguard/refactoring.py#L225-L401) 225–401 | `(repo: Repository, snapshot: Snapshot, symbol_id: str, name: str, *, operation: str='rename', value: str \| None=None) → Plan` | 输入仓库快照、符号 ID 与重构选项，输出候选补丁及逐项检查状态。 | [`ValueError`](src/repoguard/refactoring.py#L241)、[`name.isidentifier`](src/repoguard/refactoring.py#L244)、[`keyword.iskeyword`](src/repoguard/refactoring.py#L245)、[`ValueError`](src/repoguard/refactoring.py#L247) |
| [`plan.result`](src/repoguard/refactoring.py#L322-L325) 322–325 | `(patch: str='') → Plan` | — | [`Plan`](src/repoguard/refactoring.py#L323)、[`sorted`](src/repoguard/refactoring.py#L324)、[`set`](src/repoguard/refactoring.py#L324) |

## [src/repoguard/repository.py](src/repoguard/repository.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`RepositoryError`](src/repoguard/repository.py#L39-L40) 39–40 | `class RepositoryError(RuntimeError)` | 类型定义。成员职责见下方对应条目。 | — |
| [`safe_relative`](src/repoguard/repository.py#L43-L49) 43–49 | `(path: str) → bool` | 检查 Git 路径是否能作为相对路径使用。拒绝空组件、上跳、控制字符和 Windows 分隔符。 | [`path.split`](src/repoguard/repository.py#L45)、[`all`](src/repoguard/repository.py#L46)、[`any`](src/repoguard/repository.py#L47)、[`ord`](src/repoguard/repository.py#L47) |
| [`module_name`](src/repoguard/repository.py#L52-L63) 52–63 | `(path: str, roots: tuple[str, ...]) → str` | 按最长匹配源码根把 .py 路径转换为点分模块名，包的 __init__.py 映射到包名。 | [`sorted`](src/repoguard/repository.py#L55)、[`root.rstrip`](src/repoguard/repository.py#L56)、[`path.startswith`](src/repoguard/repository.py#L57)、[`len`](src/repoguard/repository.py#L58) |
| [`Repository`](src/repoguard/repository.py#L66-L230) 66–230 | `class Repository` | 在受限 Git 环境中读取固定仓库，仓库身份从规范化本地路径派生。 | — |
| [`Repository.__init__`](src/repoguard/repository.py#L69-L83) 69–83 | `(self, root: str \| Path) → None` | — | [`Path(root).resolve`](src/repoguard/repository.py#L70)、[`Path`](src/repoguard/repository.py#L70)、[`os.environ.items`](src/repoguard/repository.py#L71)、[`key.startswith`](src/repoguard/repository.py#L71) |
| [`Repository.git`](src/repoguard/repository.py#L85-L97) 85–97 | `(self, *args: str, data: bytes \| None=None) → bytes` | 以参数数组执行 git -C，返回标准输出字节。Git 非零退出时报 RepositoryError，超时由 subprocess 上报。调用层负责修订和路径验证。 | [`subprocess.run`](src/repoguard/repository.py#L87)、[`str`](src/repoguard/repository.py#L88)、[`RepositoryError`](src/repoguard/repository.py#L96)、[`result.stderr.decode('utf-8', 'replace').strip`](src/repoguard/repository.py#L96) |
| [`Repository.commit`](src/repoguard/repository.py#L99-L105) 99–105 | `(self, revision: str) → str` | 把 revision 解析为经过验证的完整提交对象 ID，供全部树、blob 和差异查询使用。 | [`self.git`](src/repoguard/repository.py#L101)、[`oid.decode('ascii').strip`](src/repoguard/repository.py#L102)、[`oid.decode`](src/repoguard/repository.py#L102)、[`OBJECT_ID.fullmatch`](src/repoguard/repository.py#L103) |
| [`Repository.inventory`](src/repoguard/repository.py#L107-L131) 107–131 | `(self, commit: str, max_bytes: int) → dict[str, File]` | 读取提交的 NUL 分隔 Git 树，返回按路径索引的文件状态与 blob ID。扫描成本与树条目数和路径总长成正比。链接、子模块、超限文件及无效路径保留跳过诊断。 | [`self.commit`](src/repoguard/repository.py#L109)、[`self.git('ls-tree', '-r', '-l', '-z', commit).split`](src/repoguard/repository.py#L111)、[`self.git`](src/repoguard/repository.py#L111)、[`record.split`](src/repoguard/repository.py#L114) |
| [`Repository.blobs`](src/repoguard/repository.py#L133-L144) 133–144 | `(self, files: Iterable[File], batch_size: int=4 * 1024 * 1024) → Iterator[bytes]` | 按总字节预算打包 blob 请求，保持输入顺序。批响应由 _batch 验证对象 ID、类型和长度。空间由单批字节与调用方保留的对象共同决定。 | [`self._batch`](src/repoguard/repository.py#L139)、[`batch.append`](src/repoguard/repository.py#L141)、[`self._batch`](src/repoguard/repository.py#L144) |
| [`Repository._batch`](src/repoguard/repository.py#L146-L162) 146–162 | `(self, files: list[File]) → Iterator[bytes]` | 用 cat-file --batch 读取原始 blob。响应头或预期长度不符会中止该批，避免数据错配。 | [`any`](src/repoguard/repository.py#L148)、[`OBJECT_ID.fullmatch`](src/repoguard/repository.py#L148)、[`RepositoryError`](src/repoguard/repository.py#L149)、[`'\n'.join((file.oid for file in files)).encode`](src/repoguard/repository.py#L150) |
| [`Repository.changes`](src/repoguard/repository.py#L164-L192) 164–192 | `(self, base: str, target: str, *, with_lines: bool=False, max_bytes: int=1000000) → list[FileChange]` | 比较两个提交，返回 Git 增删改和重命名记录。with_lines 开启时映射双方的一基闭区间。Git 的重命名结果是相似度判定，行映射受计算预算限制。 | [`self.commit`](src/repoguard/repository.py#L173)、[`self.git`](src/repoguard/repository.py#L174)、[`iter`](src/repoguard/repository.py#L177)、[`raw.removesuffix(b'\x00').split`](src/repoguard/repository.py#L177) |
| [`Repository._changed_lines`](src/repoguard/repository.py#L194-L230) 194–230 | `(self, change: FileChange, base: dict[str, File], target: dict[str, File], max_bytes: int) → FileChange` | 用 SequenceMatcher 为文本生成双方的变更范围。大文件、二进制或非普通文件保留文件级结果，行数乘积过大时用整文件范围保守近似。 | [`base.get`](src/repoguard/repository.py#L202)、[`target.get`](src/repoguard/repository.py#L203)、[`any`](src/repoguard/repository.py#L207)、[`iter`](src/repoguard/repository.py#L209) |

## [src/repoguard/resolution.py](src/repoguard/resolution.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`Candidate`](src/repoguard/resolution.py#L14-L19) 14–19 | `class Candidate` | 解析中的候选目标及不确定性标记，可能表示符号、模块或命名空间。 | — |
| [`mutations`](src/repoguard/resolution.py#L22-L23) 22–23 | `(units: Iterable[Unit]) → set[str]` | — | — |
| [`mutation_key`](src/repoguard/resolution.py#L26-L27) 26–27 | `(name: str) → str` | — | — |
| [`Catalog`](src/repoguard/resolution.py#L30-L61) 30–61 | `class Catalog` | 按模块、符号 ID、基类和动态写入组织全部文件事实，为 Resolver 提供查找目录。 | — |
| [`Catalog.__init__`](src/repoguard/resolution.py#L33-L58) 33–58 | `(self, units: dict[str, Unit]) → None` | — | [`defaultdict`](src/repoguard/resolution.py#L34)、[`set`](src/repoguard/resolution.py#L35)、[`defaultdict`](src/repoguard/resolution.py#L37)、[`mutations`](src/repoguard/resolution.py#L40) |
| [`Catalog.symbol`](src/repoguard/resolution.py#L60-L61) 60–61 | `(self, sid: str) → Symbol` | — | — |
| [`Resolver`](src/repoguard/resolution.py#L64-L383) 64–383 | `class Resolver` | 解析单个文件的词法与模块关系，同时收集命中和未命中探测。 | — |
| [`Resolver.__init__`](src/repoguard/resolution.py#L67-L70) 67–70 | `(self, catalog: Catalog) → None` | — | [`set`](src/repoguard/resolution.py#L69) |
| [`Resolver.modules`](src/repoguard/resolution.py#L72-L82) 72–82 | `(self, name: str) → list[Candidate]` | 按模块名查目录，已存在、命名空间和未命中均登记探测。同名模块保留多个候选。 | [`self.footprint.add`](src/repoguard/resolution.py#L76)、[`self.catalog.modules.get`](src/repoguard/resolution.py#L77)、[`Candidate`](src/repoguard/resolution.py#L79)、[`len`](src/repoguard/resolution.py#L79) |
| [`Resolver.imported`](src/repoguard/resolution.py#L84-L114) 84–114 | `(self, module: str, name: str, seen: frozenset[tuple[str, str]]) → list[Candidate]` | 查找模块导出、别名和子模块，递归追踪重导出。递归链用 seen 和深度上限截断。 | [`self.modules`](src/repoguard/resolution.py#L91)、[`self.bindings`](src/repoguard/resolution.py#L100)、[`scope.bindings.get`](src/repoguard/resolution.py#L101)、[`exports.extend`](src/repoguard/resolution.py#L109) |
| [`Resolver.mark`](src/repoguard/resolution.py#L117-L120) 117–120 | `(values: list[Candidate], uncertain: bool) → list[Candidate]` | — | [`Candidate`](src/repoguard/resolution.py#L120) |
| [`Resolver.bindings`](src/repoguard/resolution.py#L122-L149) 122–149 | `(self, options: list[Binding] \| tuple[()], unit: Unit, scope: Scope, name: str, seen: frozenset[tuple[str, str]]=frozenset()) → list[Candidate]` | 把同名绑定解释为若干候选；分支、多个赋值或运行时写入使候选降级。 | [`len`](src/repoguard/resolution.py#L133)、[`any`](src/repoguard/resolution.py#L133)、[`values.extend`](src/repoguard/resolution.py#L141)、[`self.modules`](src/repoguard/resolution.py#L141) |
| [`Resolver.lookup`](src/repoguard/resolution.py#L151-L187) 151–187 | `(self, unit: Unit, use: Usage, name: str) → list[Candidate]` | 由引用位置往外查词法作用域。优先处理 global、nonlocal 与绑定生效位置，再查绑定候选。 | [`scope.bindings.get`](src/repoguard/resolution.py#L165)、[`self.bindings`](src/repoguard/resolution.py#L180) |
| [`Resolver.member`](src/repoguard/resolution.py#L189-L225) 189–225 | `(self, value: Candidate, name: str, visited: frozenset[str]=frozenset()) → list[Candidate]` | 解析模块、类和方法接收者的成员，递归查询基类并限制访问次数。 | [`self.footprint.add`](src/repoguard/resolution.py#L199)、[`mutation_key`](src/repoguard/resolution.py#L199)、[`self.mark`](src/repoguard/resolution.py#L202)、[`self.modules`](src/repoguard/resolution.py#L202) |
| [`Resolver.expression`](src/repoguard/resolution.py#L227-L240) 227–240 | `(self, unit: Unit, use: Usage, visited: frozenset[str]=frozenset()) → list[Candidate]` | 分解限定名，先查根绑定，再逐段解析成员。高分支的候选会放大查找量。 | [`use.text.split`](src/repoguard/resolution.py#L236)、[`self.lookup`](src/repoguard/resolution.py#L237)、[`self.member`](src/repoguard/resolution.py#L239) |
| [`Resolver.edge_for`](src/repoguard/resolution.py#L242-L296) 242–296 | `(self, unit: Unit, use: Usage, values: list[Candidate]) → list[Edge]` | 按用途将候选转成边。无候选时输出没有目标的 UNRESOLVED 边，保留调用点。 | [`EdgeType`](src/repoguard/resolution.py#L244)、[`self.catalog.symbol`](src/repoguard/resolution.py#L249)、[`self.catalog.symbol`](src/repoguard/resolution.py#L256)、[`candidates.get`](src/repoguard/resolution.py#L262) |
| [`Resolver.resolve`](src/repoguard/resolution.py#L298-L383) 298–383 | `(self, unit: Unit) → tuple[list[Edge], set[str]]` | 把文件 Unit 转成关系边和依赖探测集合。输出定义、引用、导入、调用及类关系。 | [`identity`](src/repoguard/resolution.py#L305)、[`edges.append`](src/repoguard/resolution.py#L306)、[`Edge`](src/repoguard/resolution.py#L307)、[`unit.symbols.values`](src/repoguard/resolution.py#L318) |
| [`module_prefixes`](src/repoguard/resolution.py#L386-L388) 386–388 | `(module: str) → set[str]` | — | [`module.split`](src/repoguard/resolution.py#L387)、[`'.'.join`](src/repoguard/resolution.py#L388)、[`range`](src/repoguard/resolution.py#L388)、[`len`](src/repoguard/resolution.py#L388) |
| [`test_nodeid`](src/repoguard/resolution.py#L391-L393) 391–393 | `(symbol: Symbol) → str` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`symbol.qualified_name.removeprefix`](src/repoguard/resolution.py#L392)、[`str`](src/repoguard/resolution.py#L393)、[`PurePosixPath`](src/repoguard/resolution.py#L393)、[`package.replace`](src/repoguard/resolution.py#L393) |

## [src/repoguard/retrieval.py](src/repoguard/retrieval.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`tokens`](src/repoguard/retrieval.py#L15-L17) 15–17 | `(text: str) → list[str]` | — | [`re.sub`](src/repoguard/retrieval.py#L16)、[`token.casefold`](src/repoguard/retrieval.py#L17)、[`re.findall`](src/repoguard/retrieval.py#L17) |
| [`reciprocal_rank`](src/repoguard/retrieval.py#L20-L28) 20–28 | `(rankings: Iterable[Iterable[str]], k: int=60) → dict[str, float]` | 按每个排名列表的倒数位置融合候选分数，单列表重复 ID 只贡献一次。k 必须大于零。 | [`ValueError`](src/repoguard/retrieval.py#L23)、[`defaultdict`](src/repoguard/retrieval.py#L24)、[`enumerate`](src/repoguard/retrieval.py#L26)、[`dict.fromkeys`](src/repoguard/retrieval.py#L26) |
| [`Hit`](src/repoguard/retrieval.py#L32-L38) 32–38 | `class Hit` | 检索命中记录，含来源方法、融合得分、符号和可选图证据。 | — |
| [`Search`](src/repoguard/retrieval.py#L41-L109) 41–109 | `class Search` | 为符号名称、签名和种类建立词项倒排表及文档长度统计。 | — |
| [`Search.__init__`](src/repoguard/retrieval.py#L44-L53) 44–53 | `(self, symbols: dict[str, Symbol]) → None` | — | [`defaultdict`](src/repoguard/retrieval.py#L46)、[`symbols.items`](src/repoguard/retrieval.py#L48)、[`tokens`](src/repoguard/retrieval.py#L49)、[`len`](src/repoguard/retrieval.py#L50) |
| [`Search.exact`](src/repoguard/retrieval.py#L55-L70) 55–70 | `(self, query: str) → list[Symbol]` | 按 ID、限定名或短名扫描候选并稳定排序。短名可能返回多个符号。 | [`sorted`](src/repoguard/retrieval.py#L57)、[`self.symbols.values`](src/repoguard/retrieval.py#L60) |
| [`Search.bm25`](src/repoguard/retrieval.py#L72-L84) 72–84 | `(self, query: str) → dict[str, float]` | 遍历查询词对应倒排表，累加逆文档频率和长度归一化词频得分。 | [`defaultdict`](src/repoguard/retrieval.py#L77)、[`dict.fromkeys`](src/repoguard/retrieval.py#L78)、[`tokens`](src/repoguard/retrieval.py#L78)、[`self.postings.get`](src/repoguard/retrieval.py#L79) |
| [`Search.hybrid`](src/repoguard/retrieval.py#L86-L109) 86–109 | `(self, query: str, limit: int=20, graph: CodeGraph \| None=None) → list[Hit]` | 合并精确、BM25 和可选图扩展，用 RRF 排序并限制返回数量。 | [`ValueError`](src/repoguard/retrieval.py#L92)、[`self.exact`](src/repoguard/retrieval.py#L93)、[`self.bm25`](src/repoguard/retrieval.py#L94)、[`sorted`](src/repoguard/retrieval.py#L95) |

## [src/repoguard/sandbox.py](src/repoguard/sandbox.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`OutputLimitExceeded`](src/repoguard/sandbox.py#L24-L25) 24–25 | `class OutputLimitExceeded(RuntimeError)` | 类型定义。成员职责见下方对应条目。 | — |
| [`bounded_exchange`](src/repoguard/sandbox.py#L28-L79) 28–79 | `(command: list[str], payload: bytes, timeout: int, stdout_limit: int=16 * 1024 * 1024, stderr_limit: int=1024 * 1024) → subprocess.CompletedProcess[bytes]` | 并发写入子进程 stdin 并排空 stdout、stderr。两个输出缓冲区独立限流，超时或溢出时终止宿主客户端。 | [`Event`](src/repoguard/sandbox.py#L39)、[`subprocess.Popen`](src/repoguard/sandbox.py#L40)、[`ThreadPoolExecutor`](src/repoguard/sandbox.py#L65)、[`pool.submit`](src/repoguard/sandbox.py#L66) |
| [`bounded_exchange.drain`](src/repoguard/sandbox.py#L50-L59) 50–59 | `(stream: BinaryIO, limit: int) → bytes` | — | [`bytearray`](src/repoguard/sandbox.py#L51)、[`stream.read1`](src/repoguard/sandbox.py#L52)、[`len`](src/repoguard/sandbox.py#L53)、[`overflow.set`](src/repoguard/sandbox.py#L54) |
| [`bounded_exchange.send`](src/repoguard/sandbox.py#L61-L63) 61–63 | `(stream: BinaryIO) → None` | — | [`suppress`](src/repoguard/sandbox.py#L62)、[`stream.write`](src/repoguard/sandbox.py#L63) |
| [`TestRun`](src/repoguard/sandbox.py#L83-L94) 83–94 | `class TestRun` | 记录测试运行状态、时间、提交、镜像、pytest 失败与覆盖明细。 | — |
| [`run_tests`](src/repoguard/sandbox.py#L97-L246) 97–246 | `(repo: Repository, revision: str, *, image: str, nodeids: list[str] \| None=None, timeout: int=120, collect_coverage: bool=False) → TestRun` | 将提交归档、测试选择器及覆盖开关传给固定 Docker 镜像。校验相对测试路径、镜像摘要和归档大小。 | [`IMAGE.fullmatch`](src/repoguard/sandbox.py#L110)、[`ValueError`](src/repoguard/sandbox.py#L111)、[`any`](src/repoguard/sandbox.py#L113)、[`safe_relative`](src/repoguard/sandbox.py#L114) |

## [src/repoguard/sdk.py](src/repoguard/sdk.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`View`](src/repoguard/sdk.py#L18-L79) 18–79 | `class View` | 面向固定快照的查询视图。图与检索目录按需构造并缓存。 | — |
| [`View.__init__`](src/repoguard/sdk.py#L21-L22) 21–22 | `(self, snapshot: Snapshot) → None` | — | — |
| [`View.graph`](src/repoguard/sdk.py#L25-L26) 25–26 | `(self) → CodeGraph` | — | [`CodeGraph`](src/repoguard/sdk.py#L26) |
| [`View.searcher`](src/repoguard/sdk.py#L29-L30) 29–30 | `(self) → Search` | — | [`Search`](src/repoguard/sdk.py#L30) |
| [`View.find_definition`](src/repoguard/sdk.py#L32-L33) 32–33 | `(self, query: str) → list[Symbol]` | — | [`self.searcher.exact`](src/repoguard/sdk.py#L33) |
| [`View.search_symbols`](src/repoguard/sdk.py#L35-L36) 35–36 | `(self, query: str, limit: int=20) → list[Hit]` | — | [`self.searcher.hybrid`](src/repoguard/sdk.py#L36) |
| [`View.find_references`](src/repoguard/sdk.py#L38-L43) 38–43 | `(self, symbol_id: str) → list[Edge]` | — | [`self.graph.adjacent`](src/repoguard/sdk.py#L39) |
| [`View.get_callers`](src/repoguard/sdk.py#L45-L46) 45–46 | `(self, symbol_id: str) → list[Edge]` | — | [`self.graph.adjacent`](src/repoguard/sdk.py#L46) |
| [`View.get_callees`](src/repoguard/sdk.py#L48-L49) 48–49 | `(self, symbol_id: str) → list[Edge]` | — | [`self.graph.adjacent`](src/repoguard/sdk.py#L49) |
| [`View.get_dependency_graph`](src/repoguard/sdk.py#L51-L79) 51–79 | `(self, symbol_id: str, *, depth: int=2, limit: int=100, reverse: bool=False, kinds: tuple[EdgeType, ...] \| None=None) → dict[str, object]` | 对固定快照进行有界邻接遍历并返回路径证据。最多探测 limit+1 个节点以识别截断。 | [`ValueError`](src/repoguard/sdk.py#L62)、[`self.graph.walk`](src/repoguard/sdk.py#L64)、[`self.graph.symbols.get`](src/repoguard/sdk.py#L73)、[`list`](src/repoguard/sdk.py#L76) |
| [`RepoGuard`](src/repoguard/sdk.py#L82-L180) 82–180 | `class RepoGuard` | 配置仓库、SQLite 和索引器，提供事务发布、只读视图和跨版本工作流。 | — |
| [`RepoGuard.__init__`](src/repoguard/sdk.py#L85-L94) 85–94 | `(self, repository: str \| Path, database: str \| Path, *, options: IndexOptions=DEFAULT_OPTIONS, workers: int=4) → None` | — | [`Repository`](src/repoguard/sdk.py#L93)、[`Indexer`](src/repoguard/sdk.py#L94)、[`Store`](src/repoguard/sdk.py#L94) |
| [`RepoGuard.index`](src/repoguard/sdk.py#L96-L98) 96–98 | `(self, revision: str='HEAD', *, base: str \| None=None) → View` | 发布或复用固定提交的索引，返回受该快照限制的 View。 | [`View`](src/repoguard/sdk.py#L98)、[`self.indexer.index`](src/repoguard/sdk.py#L98) |
| [`RepoGuard.view`](src/repoguard/sdk.py#L100-L105) 100–105 | `(self, revision: str='HEAD') → View` | 打开已发布的提交视图，快照未发布时给出明确错误。 | [`self.indexer.load`](src/repoguard/sdk.py#L102)、[`ValueError`](src/repoguard/sdk.py#L104)、[`View`](src/repoguard/sdk.py#L105) |
| [`RepoGuard.analyze_change_impact`](src/repoguard/sdk.py#L107-L125) 107–125 | `(self, base: str, target: str, *, depth: int=5, coverage: CoverageMap \| None=None, environment: str='') → ImpactReport` | 加载基线和目标快照，匹配可选覆盖环境，再把文件差异交给双版本影响分析。 | [`self.view`](src/repoguard/sdk.py#L117)、[`self.repository.changes`](src/repoguard/sdk.py#L118)、[`coverage.evidence_edges`](src/repoguard/sdk.py#L124)、[`analyze`](src/repoguard/sdk.py#L125) |
| [`RepoGuard.select_related_tests`](src/repoguard/sdk.py#L127-L148) 127–148 | `(self, base: str, target: str, *, mode: str='hybrid', coverage: CoverageMap \| None=None, environment: str='') → Selection` | 将影响报告、目标快照和可选覆盖交给选择器，返回用例和回退理由。 | [`select`](src/repoguard/sdk.py#L137)、[`self.analyze_change_impact`](src/repoguard/sdk.py#L138)、[`self.view`](src/repoguard/sdk.py#L144) |
| [`RepoGuard.plan_refactoring`](src/repoguard/sdk.py#L150-L168) 150–168 | `(self, revision: str, symbol_id: str, name: str, *, operation: str='rename', value: str \| None=None)` | — | [`plan`](src/repoguard/sdk.py#L161)、[`self.view`](src/repoguard/sdk.py#L163) |
| [`RepoGuard.plan_import_migration`](src/repoguard/sdk.py#L170-L175) 170–175 | `(self, revision: str, source_module: str, destination_module: str)` | — | [`plan_module_move`](src/repoguard/sdk.py#L173)、[`self.view`](src/repoguard/sdk.py#L174) |
| [`RepoGuard.validate_patch`](src/repoguard/sdk.py#L177-L180) 177–180 | `(self, revision: str, patch: str)` | — | [`validate_patch`](src/repoguard/sdk.py#L180)、[`self.view`](src/repoguard/sdk.py#L180) |

## [src/repoguard/store.py](src/repoguard/store.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`serialize`](src/repoguard/store.py#L50-L51) 50–51 | `(value: Any) → str` | — | [`json.dumps`](src/repoguard/store.py#L51) |
| [`decode_unit`](src/repoguard/store.py#L54-L68) 54–68 | `(raw: str) → Unit` | 把数据库中的 JSON 恢复成 Unit 和各级数据记录。调用方只读已经发布的版本。 | [`json.loads`](src/repoguard/store.py#L56)、[`payload['scopes'].values`](src/repoguard/store.py#L57)、[`Binding`](src/repoguard/store.py#L59)、[`scope['bindings'].items`](src/repoguard/store.py#L59) |
| [`Store`](src/repoguard/store.py#L71-L196) 71–196 | `class Store` | 用稳定版本键隔离 SQLite 中的提交快照、文件和边。 | — |
| [`Store.__init__`](src/repoguard/store.py#L74-L80) 74–80 | `(self, database: str \| Path) → None` | — | [`Path`](src/repoguard/store.py#L75)、[`str`](src/repoguard/store.py#L76)、[`ValueError`](src/repoguard/store.py#L77)、[`self.database.parent.mkdir`](src/repoguard/store.py#L78) |
| [`Store.connect`](src/repoguard/store.py#L82-L85) 82–85 | `(self) → sqlite3.Connection` | — | [`sqlite3.connect`](src/repoguard/store.py#L83)、[`connection.execute`](src/repoguard/store.py#L84) |
| [`Store.save`](src/repoguard/store.py#L87-L139) 87–139 | `(self, snapshot: Snapshot) → bool` | 在同一个 BEGIN IMMEDIATE 事务写入快照、文件和边。版本已存在时返回 False，由 Indexer 读取获胜快照。 | [`closing`](src/repoguard/store.py#L92)、[`self.connect`](src/repoguard/store.py#L92)、[`connection.execute`](src/repoguard/store.py#L93)、[`connection.execute`](src/repoguard/store.py#L94) |
| [`Store.load`](src/repoguard/store.py#L141-L196) 141–196 | `(self, version: str) → Snapshot \| None` | 在同一个读取事务恢复特定版本的元数据、文件和边，并重建数据记录。不存在的版本返回 None。 | [`closing`](src/repoguard/store.py#L146)、[`self.connect`](src/repoguard/store.py#L146)、[`connection.execute`](src/repoguard/store.py#L147)、[`connection.execute`](src/repoguard/store.py#L148) |

## [src/repoguard/test_selection.py](src/repoguard/test_selection.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`CoverageMap`](src/repoguard/test_selection.py#L13-L75) 13–75 | `class CoverageMap` | 按提交、运行环境和 pytest nodeid 保存覆盖路径与执行行，并记录归因局限。 | — |
| [`CoverageMap.evidence_edges`](src/repoguard/test_selection.py#L22-L75) 22–75 | `(self, base: Snapshot, environment: str) → list[Edge]` | 确认基线提交和环境标识后，将覆盖行映射到窄的符号范围并生成 COVERS 边。 | [`test_nodeid`](src/repoguard/test_selection.py#L34)、[`base.symbols.values`](src/repoguard/test_selection.py#L34)、[`self.tests.items`](src/repoguard/test_selection.py#L37)、[`tests.get`](src/repoguard/test_selection.py#L38) |
| [`Selection`](src/repoguard/test_selection.py#L79-L86) 79–86 | `class Selection` | 选择模式、候选用例及理由，以及要求执行全量套件的标记。 | — |
| [`select`](src/repoguard/test_selection.py#L89-L160) 89–160 | `(report: ImpactReport, snapshot: Snapshot, *, mode: str='hybrid', coverage: CoverageMap \| None=None, environment: str='') → Selection` | 按 file、static、coverage 或 hybrid 生成用例与可追溯依据。 | [`ValueError`](src/repoguard/test_selection.py#L103)、[`ValueError`](src/repoguard/test_selection.py#L105)、[`snapshot.symbols.values`](src/repoguard/test_selection.py#L112)、[`set`](src/repoguard/test_selection.py#L113) |
| [`select.add`](src/repoguard/test_selection.py#L116-L117) 116–117 | `(nodeid: str, criterion: str) → None` | — | [`evidence.setdefault(nodeid, set()).add`](src/repoguard/test_selection.py#L117)、[`evidence.setdefault`](src/repoguard/test_selection.py#L117)、[`set`](src/repoguard/test_selection.py#L117) |

## [src/repoguard/verification.py](src/repoguard/verification.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`PatchValidation`](src/repoguard/verification.py#L20-L28) 20–28 | `class PatchValidation` | 独立补丁预检的状态、诊断、公开接口差异和新增未解析调用。 | — |
| [`path_header`](src/repoguard/verification.py#L31-L41) 31–41 | `(line: bytes, label: bytes) → str \| None` | 仅解析统一差异中的可接受根路径或 /dev/null。非法路径产生 ValueError。 | [`line.startswith`](src/repoguard/verification.py#L33)、[`ValueError`](src/repoguard/verification.py#L34)、[`line[len(label):].rstrip(b'\r\n').removesuffix(b'\t').decode`](src/repoguard/verification.py#L35)、[`line[len(label):].rstrip(b'\r\n').removesuffix`](src/repoguard/verification.py#L35) |
| [`lf_lines`](src/repoguard/verification.py#L44-L46) 44–46 | `(raw: bytes) → list[bytes]` | — | [`raw.split`](src/repoguard/verification.py#L45) |
| [`apply_hunks`](src/repoguard/verification.py#L49-L80) 49–80 | `(before: bytes, hunks: list[tuple[re.Match[bytes], list[bytes]]]) → bytes` | 按旧侧上下文和目标坐标顺序应用变更块，输出内存字节。重叠、计数或上下文不匹配时报错。 | [`lf_lines`](src/repoguard/verification.py#L51)、[`header.groups`](src/repoguard/verification.py#L55)、[`int`](src/repoguard/verification.py#L57)、[`int`](src/repoguard/verification.py#L58) |
| [`patch_entries`](src/repoguard/verification.py#L83-L134) 83–134 | `(patch: str) → list[tuple[str \| None, str \| None, list]]` | 读取受限大小的统一 diff，按头和 hunk 解析双侧 Python 路径，校验声明跨度和缺换行标记。 | [`patch.encode`](src/repoguard/verification.py#L85)、[`len`](src/repoguard/verification.py#L86)、[`ValueError`](src/repoguard/verification.py#L87)、[`lf_lines`](src/repoguard/verification.py#L89) |
| [`validate_patch`](src/repoguard/verification.py#L137-L209) 137–209 | `(repo: Repository, snapshot: Snapshot, patch: str) → PatchValidation` | 在固定提交的 blob 上匹配补丁并重解析改动文件。对照公开签名与新增未解析调用，返回状态与诊断。 | [`ValueError`](src/repoguard/verification.py#L143)、[`dict`](src/repoguard/verification.py#L144)、[`tuple`](src/repoguard/verification.py#L145)、[`json.loads`](src/repoguard/verification.py#L145) |
| [`validate_patch.unresolved`](src/repoguard/verification.py#L199-L204) 199–204 | `(part)` | — | [`Counter`](src/repoguard/verification.py#L200) |

## [tests/conftest.py](tests/conftest.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`GitFixture`](tests/conftest.py#L9-L35) 9–35 | `class GitFixture` | 类型定义。成员职责见下方对应条目。 | — |
| [`GitFixture.__init__`](tests/conftest.py#L10-L16) 10–16 | `(self, root: Path) → None` | — | [`root.mkdir`](tests/conftest.py#L12)、[`self.git`](tests/conftest.py#L13)、[`self.git`](tests/conftest.py#L14)、[`self.git`](tests/conftest.py#L15) |
| [`GitFixture.git`](tests/conftest.py#L18-L25) 18–25 | `(self, *args: str, data: bytes \| None=None) → str` | — | [`subprocess.run`](tests/conftest.py#L19)、[`str`](tests/conftest.py#L20)、[`result.stdout.decode().strip`](tests/conftest.py#L25)、[`result.stdout.decode`](tests/conftest.py#L25) |
| [`GitFixture.write`](tests/conftest.py#L27-L30) 27–30 | `(self, path: str, text: str \| bytes) → None` | — | [`file.parent.mkdir`](tests/conftest.py#L29)、[`file.write_bytes`](tests/conftest.py#L30)、[`isinstance`](tests/conftest.py#L30)、[`text.encode`](tests/conftest.py#L30) |
| [`GitFixture.commit`](tests/conftest.py#L32-L35) 32–35 | `(self) → str` | — | [`self.git`](tests/conftest.py#L33)、[`self.git`](tests/conftest.py#L34)、[`self.git`](tests/conftest.py#L35) |
| [`repository`](tests/conftest.py#L39-L40) 39–40 | `(tmp_path)` | — | [`GitFixture`](tests/conftest.py#L40) |
| [`history`](tests/conftest.py#L44-L84) 44–84 | `(repository)` | — | [`files.items`](tests/conftest.py#L74)、[`repository.write`](tests/conftest.py#L75)、[`repository.commit`](tests/conftest.py#L76)、[`repository.write`](tests/conftest.py#L77) |

## [tests/e2e/test_cli.py](tests/e2e/test_cli.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`test_cli_roundtrip`](tests/e2e/test_cli.py#L6-L27) 6–27 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`str`](tests/e2e/test_cli.py#L13)、[`str`](tests/e2e/test_cli.py#L15)、[`subprocess.run`](tests/e2e/test_cli.py#L18)、[`json.loads`](tests/e2e/test_cli.py#L19) |

## [tests/e2e/test_transports.py](tests/e2e/test_transports.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`test_api_paths_and_read_only_index_policy`](tests/e2e/test_transports.py#L13-L40) 13–40 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard`](tests/e2e/test_transports.py#L16)、[`sdk.index`](tests/e2e/test_transports.py#L17)、[`sdk.index`](tests/e2e/test_transports.py#L18)、[`TestClient`](tests/e2e/test_transports.py#L19) |
| [`test_mcp_stdio_protocol`](tests/e2e/test_transports.py#L43-L71) 43–71 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard(repo.root, database).index`](tests/e2e/test_transports.py#L46)、[`RepoGuard`](tests/e2e/test_transports.py#L46)、[`anyio.run`](tests/e2e/test_transports.py#L71) |
| [`test_mcp_stdio_protocol.exchange`](tests/e2e/test_transports.py#L48-L69) 48–69 | `async exchange()` | — | [`StdioServerParameters`](tests/e2e/test_transports.py#L49)、[`str`](tests/e2e/test_transports.py#L50)、[`Path`](tests/e2e/test_transports.py#L50)、[`str`](tests/e2e/test_transports.py#L55) |

## [tests/integration/test_index_and_impact.py](tests/integration/test_index_and_impact.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`one`](tests/integration/test_index_and_impact.py#L16-L19) 16–19 | `(view, name)` | — | [`view.find_definition`](tests/integration/test_index_and_impact.py#L17)、[`len`](tests/integration/test_index_and_impact.py#L18) |
| [`test_reference_resolution_and_graph`](tests/integration/test_index_and_impact.py#L22-L44) 22–44 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard(repo.root, tmp_path / 'db').index`](tests/integration/test_index_and_impact.py#L24)、[`RepoGuard`](tests/integration/test_index_and_impact.py#L24)、[`one`](tests/integration/test_index_and_impact.py#L25)、[`len`](tests/integration/test_index_and_impact.py#L26) |
| [`test_incremental_matches_full_and_resolves_former_miss`](tests/integration/test_index_and_impact.py#L47-L69) 47–69 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard`](tests/integration/test_index_and_impact.py#L49)、[`engine.index`](tests/integration/test_index_and_impact.py#L50)、[`engine.index`](tests/integration/test_index_and_impact.py#L51)、[`engine.indexer.index`](tests/integration/test_index_and_impact.py#L52) |
| [`test_impact_evidence_and_hybrid_fallback`](tests/integration/test_index_and_impact.py#L72-L118) 72–118 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard`](tests/integration/test_index_and_impact.py#L74)、[`engine.index`](tests/integration/test_index_and_impact.py#L75)、[`engine.index`](tests/integration/test_index_and_impact.py#L76)、[`engine.analyze_change_impact`](tests/integration/test_index_and_impact.py#L77) |
| [`test_tracked_source_from_commit_and_diagnostics`](tests/integration/test_index_and_impact.py#L121-L141) 121–141 | `(repository, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`repository.write`](tests/integration/test_index_and_impact.py#L122)、[`repository.write`](tests/integration/test_index_and_impact.py#L123)、[`repository.write`](tests/integration/test_index_and_impact.py#L124)、[`repository.write`](tests/integration/test_index_and_impact.py#L125) |
| [`test_graph_walk_bounds`](tests/integration/test_index_and_impact.py#L144-L161) 144–161 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard`](tests/integration/test_index_and_impact.py#L146)、[`engine.index`](tests/integration/test_index_and_impact.py#L147)、[`CodeGraph`](tests/integration/test_index_and_impact.py#L148)、[`one`](tests/integration/test_index_and_impact.py#L149) |
| [`test_runtime_binding_changes_invalidate_dependent_confidence`](tests/integration/test_index_and_impact.py#L164-L177) 164–177 | `(repository, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`repository.write`](tests/integration/test_index_and_impact.py#L165)、[`repository.write`](tests/integration/test_index_and_impact.py#L166)、[`repository.commit`](tests/integration/test_index_and_impact.py#L167)、[`RepoGuard`](tests/integration/test_index_and_impact.py#L168) |
| [`test_concurrent_publication_keeps_one_complete_snapshot`](tests/integration/test_index_and_impact.py#L180-L188) 180–188 | `(history, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`RepoGuard`](tests/integration/test_index_and_impact.py#L182)、[`engine.index`](tests/integration/test_index_and_impact.py#L183)、[`ThreadPoolExecutor`](tests/integration/test_index_and_impact.py#L184)、[`list`](tests/integration/test_index_and_impact.py#L185) |
| [`test_reciprocal_rank_ignores_duplicate_results`](tests/integration/test_index_and_impact.py#L192-L198) 192–198 | `(order)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`list`](tests/integration/test_index_and_impact.py#L195)、[`dict.fromkeys`](tests/integration/test_index_and_impact.py#L195)、[`reciprocal_rank`](tests/integration/test_index_and_impact.py#L196)、[`list`](tests/integration/test_index_and_impact.py#L197) |
| [`test_possible_edge_never_increases_risk`](tests/integration/test_index_and_impact.py#L202-L205) 202–205 | `(score, weight)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`risk_step`](tests/integration/test_index_and_impact.py#L205) |

## [tests/integration/test_refactoring.py](tests/integration/test_refactoring.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`test_rename_preserves_comments_and_aliases`](tests/integration/test_refactoring.py#L7-L39) 7–39 | `(repository, tmp_path, newline)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`items.items`](tests/integration/test_refactoring.py#L18)、[`repository.write`](tests/integration/test_refactoring.py#L19)、[`source.replace`](tests/integration/test_refactoring.py#L19)、[`repository.commit`](tests/integration/test_refactoring.py#L20) |
| [`test_signature_uses_only_explicit_values_and_flags_unpacked_calls`](tests/integration/test_refactoring.py#L42-L64) 42–64 | `(repository, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`repository.write`](tests/integration/test_refactoring.py#L43)、[`repository.write`](tests/integration/test_refactoring.py#L44)、[`repository.commit`](tests/integration/test_refactoring.py#L45)、[`RepoGuard`](tests/integration/test_refactoring.py#L46) |
| [`test_move_module_preserves_local_import_names`](tests/integration/test_refactoring.py#L67-L87) 67–87 | `(repository, tmp_path)` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`repository.write`](tests/integration/test_refactoring.py#L68)、[`repository.write`](tests/integration/test_refactoring.py#L69)、[`repository.write`](tests/integration/test_refactoring.py#L70)、[`repository.commit`](tests/integration/test_refactoring.py#L75) |

## [tests/unit/test_parser.py](tests/unit/test_parser.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`scan`](tests/unit/test_parser.py#L7-L9) 7–9 | `(text)` | — | [`isinstance`](tests/unit/test_parser.py#L8)、[`text.encode`](tests/unit/test_parser.py#L8)、[`parse`](tests/unit/test_parser.py#L9)、[`File`](tests/unit/test_parser.py#L9) |
| [`test_encoding_binary_and_compiler_diagnostics`](tests/unit/test_parser.py#L12-L19) 12–19 | `()` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`scan`](tests/unit/test_parser.py#L13)、[`any`](tests/unit/test_parser.py#L15)、[`unit.symbols.values`](tests/unit/test_parser.py#L15)、[`scan`](tests/unit/test_parser.py#L16) |
| [`test_scope_shadow_class_globals_and_comprehension`](tests/unit/test_parser.py#L22-L45) 22–45 | `()` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`scan`](tests/unit/test_parser.py#L23)、[`Resolver(Catalog({'a.py': unit})).resolve`](tests/unit/test_parser.py#L39)、[`Resolver`](tests/unit/test_parser.py#L39)、[`Catalog`](tests/unit/test_parser.py#L39) |
| [`test_safe_paths`](tests/unit/test_parser.py#L48-L51) 48–51 | `()` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`safe_relative`](tests/unit/test_parser.py#L50)、[`safe_relative`](tests/unit/test_parser.py#L51) |

## [tests/unit/test_sandbox_io.py](tests/unit/test_sandbox_io.py)

| 定义和源码范围 | 签名 | 职责 | 调用点 |
|---|---|---|---|
| [`test_runner_captures_output_and_caps_excessive_streams`](tests/unit/test_sandbox_io.py#L8-L18) 8–18 | `()` | pytest 回归用例。验证目标见用例名与源文件中的断言。 | [`bounded_exchange`](tests/unit/test_sandbox_io.py#L14)、[`pytest.raises`](tests/unit/test_sandbox_io.py#L17)、[`bounded_exchange`](tests/unit/test_sandbox_io.py#L18) |
