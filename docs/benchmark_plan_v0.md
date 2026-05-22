# SkillAdmit Benchmark Plan v0

## 1. 当前目标

本阶段只做最小闭环，不追求大规模 benchmark。

目标是构造一个可控的 Python import/debug 任务族，用来验证 SkillAdmit 是否能判断 agent 经验应该被：

```text
discard / store_as_memory / distill_into_skill / promote_to_rule / defer
```
第一版只做：
```text
任务族：Python import/debug
bug 模板：5 个
每个模板：4 个变体
总任务数：20 个
```

## 2. 为什么先选 Python import/debug

选择该任务族的原因：

1. 错误常见，agent 轨迹容易产生重复模式；
2. 成功与否容易用 pytest 或命令退出码验证；
3. 很容易构造负迁移样本；
4. 可以清楚区分 memory、skill、rule；
5. 不需要复杂外部依赖。
## 3. 五个 bug 模板
### T1: missing third-party package

**错误现象**

代码导入一个确实未安装的第三方包，例如：
```python
import yaml
```
但当前环境没有安装对应依赖，运行时报：
```python
ModuleNotFoundError: No module named 'yaml'
```
**正确修复逻辑**

正确修复应该是：
```text
检查该模块是否为第三方依赖；
如果确实是第三方包，则添加 requirements.txt 或安装依赖；
重新运行 verifier。
```
**可生成的变体**

- 变体 1：缺少 yaml
- 变体 2：缺少 dotenv
- 变体 3：缺少 requests
- 变体 4：缺少 pydantic
**可能产生的经验**
memory:
```text
当前任务环境中某个项目缺少具体第三方依赖。
```
skill:
```text
遇到 ModuleNotFoundError 时，先判断缺失模块是第三方包还是本地模块，再决定是否安装依赖。
```
rule:
```
不要在确认模块来源前直接安装同名包。
```
---
### T2: local module mistaken as missing package
**错误现象**

项目中本来有本地模块，但 import 写法或运行路径错误导致：
```text
ModuleNotFoundError: No module named 'utils'
```
例如文件结构：
```text
repo/
  app/
    main.py
    utils.py
```
`main.py` 中写：
```python
from utils import helper
```
但从项目根目录运行时失败。

**正确修复逻辑**

正确修复不是 pip install utils，而是：
```text
检查 utils 是否属于本地项目；
检查运行命令和 Python import path；
改成包内导入或调整启动方式。
```
**可生成的变体**

- 变体 1：from utils import helper
- 变体 2：from config import settings
- 变体 3：from service import run
- 变体 4：from parser import parse_text

**可能产生的经验**

memory:
```text
某个具体项目的本地模块路径写错。
```
skill:
```text
遇到 ModuleNotFoundError 时，先检查缺失模块是否是本地文件或本地包。
```
rule:
```text
不能把所有 ModuleNotFoundError 都当成缺少第三方
包处理。
```
**负迁移点**
坏 skill:
```text
遇到 ModuleNotFoundError 就 pip install 同名包。
```
该 skill 在本模板中应该被拒绝。

---
### T3: relative import executed as script
**错误现象**

包内文件使用相对导入：
```python
from .utils import helper
```

但用户直接运行：
```bash
python app/main.py
```
导致：
```text
ImportError: attempted relative import with no known parent package
```
**正确修复逻辑**
正确修复可以是：
```text
使用 python -m app.main 从包上下文运行；
或将代码改成适合当前启动方式的绝对导入；
确保测试命令从项目根目录执行。
```
**可生成的变体**

- 变体 1：app/main.py 相对导入 utils.py
- 变体 2：src/cli.py 相对导入 core.py
- 变体 3：package/runner.py 相对导入 worker.py
- 变体 4：两层包结构中的相对导入失败
**可能产生的经验**
memory:
```text
某个具体项目需要使用 python -m app.main 启动。
```
skill:
```text
诊断 relative import 错误时，应先判断文件是被当作脚本运行还是作为模块运行。
```
rule:
```text
修改 import 前先确认程序的预期启动方式。
```

### T4: wrong current working directory
**错误现象**

代码中使用相对路径或本地 import，只有在项目根目录运行才成功。用户在子目录运行导致失败：
```text
ModuleNotFoundError
FileNotFoundError
```
**正确修复逻辑**

正确修复应该是：
```text
检查当前工作目录；
检查命令是否应该从项目根目录执行；
必要时使用 pathlib 根据 __file__ 构造稳定路径；
更新 README 或测试命令。
```
**可生成的变体**

- 变体 1：从 repo/app 运行，找不到 data/config.json
- 变体 2：从错误目录运行 pytest
- 变体 3：相对 import 依赖项目根目录
- 变体 4：脚本读取相对路径文件失败

**可能产生的经验**

memory:
```text
某个具体项目的测试必须从 repo 根目录运行。
```
skill:
```text
遇到路径或 import 错误时，应检查 cwd 与命令执行位置。
```
rule:
```text
不要在没有确认 cwd 的情况下修改 import 或文件路径。
```
---
### T5: broken package-qualified import

#### 错误现象

项目本身具有明确的 package 结构：

```text
repo/
  app_pkg/
    __init__.py
    core/
      __init__.py
      worker.py
    main.py
```
测试代码从 package 顶层导入：

```python
from app_pkg.main import run
```
但 `main.py` 内部错误地使用裸导入：
```python
from core.worker import work
```
在项目根目录运行测试时，Python 不会把 `app_pkg/core` 当作顶层包` core`，因此报错：
```text
ModuleNotFoundError: No module named 'core'
```
**正确修复逻辑**

正确修复应该是：
```text
检查 package 结构和导入上下文；
确认 main.py 是作为 package 的一部分被导入；
将裸导入改为 package-qualified import 或相对导入；
例如 from app_pkg.core.worker import work 或 from .core.worker import work。
```
**可生成的变体**
- 变体 1：app_pkg/main.py 错误导入 core.worker
- 变体 2：toolkit/main.py 错误导入 engine.worker
- 变体 3：projectpkg/main.py 错误导入 services.worker
- 变体 4：samplepkg/main.py 错误导入 workers.worker

**可能产生的经验**

memory:
```text
某个具体项目的 main.py 在 package 导入上下文中使用了错误的裸导入。
```
skill:
```text
诊断包结构相关导入失败时，应检查导入语句是否与运行上下文一致：作为 package 被导入时，内部模块应使用相对导入或 package-qualified import。
```
rule:
```text
不要只根据 ModuleNotFoundError 判断缺包；先确认缺失名称是否是包内子模块。
```
**负迁移点**
坏 skill:
```text
遇到缺失模块名就安装同名包。
```
---
## 4. 第一批任务数量
第一版任务数：

| 模板 | 变体数 |
|---|---:|
| T1 missing third-party package | 4 |
| T2 local module mistaken as package | 4 |
| T3 relative import executed as script | 4 |
| T4 wrong current working directory | 4 |
| T5 broken package-qualified import | 4 |
| **total** | **20** |


## 5. 每个任务目录结构
每个任务目录采用统一结构：
```text
benchmark/tasks/py_import_001/
  repo/
    ...
  task.json
  verifier.sh
```
`task.json` 字段：
```json
{
  "task_id": "py_import_001",
  "family": "python_import_debug",
  "template": "T3_relative_import_script_mode",
  "instruction": "Fix the project so that the verifier passes.",
  "failing_command": "python app/main.py",
  "verifier": "bash verifier.sh",
  "expected_failure": "ImportError: attempted relative import with no known parent package"
}
```
`verifier.sh` 要满足：
```text
bug 未修复时失败；
bug 正确修复后通过；
输出足够清楚，方便 agent 诊断。
```

## 6. 第一版 admission label 规则
### distill_into_skill
满足：
```text
多条轨迹支持同一稳定调试流程；
该流程能迁移到 held-out 任务；
使用 skill 后成功率提升；
坏 skill 风险较低。
```
### store_as_memory
满足：
```text
经验有用；
但绑定具体项目、路径、命令、端口或环境；
不适合抽象为通用 skill。
```
### promote_to_rule
满足：
```text
经验不是具体步骤；
而是跨任务都应遵守的约束；
例如不要在确认模块来源前 pip install。
```
### discard
满足：
```text
经验来自偶然失败；
无长期复用价值；
存储会增加噪声。
```
### defer
满足：
```text
经验看起来可能有用；
但证据不足；
或者 validation 结果不稳定。
```
## 7. 第一版负迁移设计
最重要的坏 skill：
```text
遇到 ModuleNotFoundError 就 pip install 同名包。
```
它在 T1 中可能有效，但在 T2、T3、T4、T5 中大概率错误。

因此，benchmark 必须包含足够多 T2-T5 样本，用来检验 SkillAdmit 是否能拒绝该坏 skill。

## 8. 当前阶段完成标准
本阶段完成后，应能回答：
```text
20 个任务如何生成？
每个任务如何验证？
哪些经验可能变成 memory？
哪些经验可能变成 skill？
哪些经验可能变成 rule？
哪些经验应该被拒绝或 defer？
坏 skill 如何被测试？
```