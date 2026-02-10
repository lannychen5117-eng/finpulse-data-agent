---
trigger: always_on
---

# AI Agent 编码规范
本文档旨在统一 AI Agent 编码风格、提升代码可维护性、保障系统稳定性与安全性，适用于所有 AI Agent 相关代码开发（含核心逻辑、交互模块、工具调用、数据处理等），覆盖 Python、JavaScript 等主流开发语言，兼顾通用性与 AI Agent 专属场景需求。

# 一、通用编码原则

1. **可读性优先**：代码首要目标是让人读懂，其次是机器执行；避免过度精简、晦涩的语法，变量/函数命名需见名知义，拒绝无意义命名（如 `x1`、`temp2`）。

2. **模块化与单一职责**：AI Agent 核心模块（感知、决策、执行、交互、记忆）拆分清晰，每个函数/类仅负责一项具体功能，避免“大而全”的代码块（单个函数代码量不超过 100 行，特殊场景可适当放宽）。

3. **可扩展性**：预留工具调用、模型切换、场景适配的扩展接口，避免硬编码（如模型地址、工具参数、触发条件等需抽离为配置文件）。

4. **安全性底线**：严格校验输入输出、防范注入攻击、保护用户隐私与敏感数据，禁止直接暴露密钥、令牌等核心信息。

5. **一致性**：全程遵循本规范，同一项目内编码风格、命名规则、注释格式保持统一，不随意变更。

# 二、命名规范

## 2.1 通用规则

- 禁止使用拼音、中文、特殊字符（除下划线 `_` 外），禁止使用编程语言关键字、保留字。

- 命名长度适中（3-20 字符），简洁且不冗余，避免过度缩写（通用缩写如 AI、Agent、API 可使用）。

- 区分大小写（严格遵循对应语言规范），不依赖大小写区分变量含义。

## 2.2 具体命名要求

|命名类型|命名风格|AI Agent 专属示例|禁止示例|
|---|---|---|---|
|变量|小写字母 + 下划线（snake_case）|`agent_name`、`task_queue`、`user_query`、`memory_cache`|`AgentName`、`yonghuxinxi`、`q1`|
|函数/方法|小写字母 + 下划线（snake_case），动词开头|`execute_task`、`parse_user_query`、`update_memory`、`call_tool`|`TaskExecute`、`getdata`、`处理请求`|
|类|首字母大写 + 驼峰（PascalCase）|`AI_Agent`、`TaskExecutor`、`MemoryManager`、`ToolCaller`|`ai_agent`、`taskexecutor`、`UserMemory`（无意义拼接）|
|常量|全大写 + 下划线（UPPER_SNAKE_CASE）|`MAX_TASK_NUM`、`MODEL_TIMEOUT`、`TOOL_API_KEY`|`maxTaskNum`、`modelTimeout`、`key`|
|模块/文件|小写字母 + 下划线（snake_case）|`agent_core.py`、`tool_manager.js`、`memory_store.py`|`AgentCore.py`、`工具管理.js`、`memo1.py`|
|接口/路由|小写字母 + 横杠（kebab-case）（API 场景）|`/agent/query`、`/agent/task/add`、`/agent/memory/update`|`/Agent/Query`、`/agentTaskAdd`|
# 三、代码结构规范

## 3.1 整体目录结构（通用模板）

```markdown
# AI Agent 项目目录结构（示例）
ai_agent/
├── config/                # 配置文件目录（统一管理，禁止硬编码）
│   ├── __init__.py
│   ├── agent_config.py    # Agent 核心配置（模型参数、超时时间等）
│   ├── tool_config.py     # 工具配置（工具地址、密钥等，建议加密存储）
│   └── log_config.py      # 日志配置
├── core/                  # Agent 核心逻辑目录
│   ├── __init__.py
│   ├── agent.py           # Agent 主类（整合感知、决策、执行）
│   ├── perception.py      # 感知模块（解析用户输入、环境信息）
│   ├── decision.py        # 决策模块（任务分配、工具选择、逻辑判断）
│   └── execution.py       # 执行模块（执行任务、调用工具、返回结果）
├── memory/                # 记忆模块目录（短期/长期记忆）
│   ├── __init__.py
│   ├── short_term_memory.py  # 短期记忆（会话级）
│   └── long_term_memory.py   # 长期记忆（持久化，如数据库存储）
├── tools/                 # 工具调用目录（插件化管理）
│   ├── __init__.py
│   ├── base_tool.py       # 工具基类（统一接口，所有工具继承）
│   ├── file_tool.py       # 具体工具（文件操作）
│   └── api_tool.py        # 具体工具（第三方 API 调用）
├── utils/                 # 工具函数目录（通用工具，不依赖 Agent 核心）
│   ├── __init__.py
│   ├── log_utils.py       # 日志工具
│   ├── encrypt_utils.py   # 加密工具（敏感信息处理）
│   └── validate_utils.py  # 校验工具（输入/输出校验）
├── api/                   # 接口层目录（对外提供服务，如 HTTP 接口）
│   ├── __init__.py
│   ├── router.py          # 路由配置
│   └── controller.py      # 接口逻辑实现
├── tests/                 # 测试目录（全覆盖，禁止无测试代码上线）
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_memory.py
├── main.py                # 项目入口（简洁，仅负责启动和初始化）
└── README.md              # 项目说明（Agent 功能、部署步骤、接口文档）
```

## 3.2 代码文件结构

1. 每个文件顶部添加文件说明注释（注明功能、作者、创建日期，可选：修改记录）。

2. 导入模块规范：
        

    - 先导入标准库，再导入第三方库，最后导入自定义模块，各组之间用空行分隔。

    - 导入时禁止使用 `from xxx import *`（避免命名冲突），按需导入指定内容。

3. 代码块分隔：函数、类之间用 2 个空行分隔，同一函数内不同逻辑块用 1 个空行分隔，避免代码拥挤。

4. AI Agent 核心类结构：必须包含初始化方法（__init__），核心方法（感知、决策、执行）拆分清晰，不耦合。

## 3.3 异常处理结构

- 禁止使用 `try-except-pass`（忽略异常，难以排查问题），必须捕获具体异常（如 `ValueError`、`ConnectionError`）。

- 异常处理需包含：异常信息打印（日志输出，含错误栈）、异常降级策略（如工具调用失败时切换备用工具、返回友好提示）。

- AI Agent 专属异常：自定义异常类（如 `AgentTaskError`、`ToolCallError`），统一继承基础异常类，便于全局捕获和处理。

```python
# 异常处理示例（Python）
from utils.log_utils import logger

class ToolCallError(Exception):
    """自定义工具调用异常"""
    pass

def call_tool(tool_name, params):
    try:
        # 工具调用逻辑
        tool = get_tool(tool_name)
        return tool.run(params)
    except ConnectionError as e:
        logger.error(f"工具{tool_name}连接失败：{str(e)}", exc_info=True)  # 打印错误栈
        raise ToolCallError(f"工具{tool_name}暂时不可用，请稍后再试") from e
    except Exception as e:
        logger.error(f"工具{tool_name}调用异常：{str(e)}", exc_info=True)
        return {"status": "fail", "msg": "操作失败，请联系管理员"}
```

# 四、注释规范

## 4.1 通用规则

- 注释语言：统一使用中文（除非代码面向国际团队，可使用英文），语法正确、简洁明了，不冗余。

- 注释时机：核心逻辑、复杂判断、异常处理、工具调用逻辑、配置参数必须加注释；简单逻辑（如变量赋值、简单返回）可省略。

- 禁止注释无效代码：无用代码直接删除，不保留“注释掉的代码”（版本控制工具可追溯历史代码）。

- 注释与代码同步更新：修改代码时，必须同步修改对应注释，避免注释与代码不一致。

- **禁止硬编码与模拟数据**：所有配置项（如 API Key、URL、超时时间）、环境敏感参数必须从配置文件或环境变量中读取；业务逻辑中严禁包含硬编码的模拟返回结果（Mock Data），确保代码具备生产环境的通用性。

## 4.2 具体注释要求

1. **文件注释**：位于文件顶部，说明文件功能、作者、创建日期，可选添加修改记录。
        `# -*- coding: utf-8 -*-
"""
文件名称：agent.py
文件功能：AI Agent 主类，整合感知、决策、执行三大核心模块，负责接收用户请求、调度工具、返回结果
作    者：XXX
创建日期：2024-05-20
修改记录：2024-05-22  XXX  新增记忆模块调用逻辑，优化决策算法
"""`

2. **类注释**：位于类定义上方，说明类的功能、核心属性、使用场景，可选添加示例。
        `class AI_Agent:
    """
    AI Agent 主类，负责统筹所有核心模块，实现端到端的用户交互与任务执行
    
    核心属性：
        - name (str): Agent 名称
        - memory (MemoryManager): 记忆管理实例（整合短期/长期记忆）
        - tool_caller (ToolCaller): 工具调用实例（负责调用各类外部工具）
        - config (dict): Agent 配置参数（从 config/agent_config.py 加载）
    
    使用示例：
        agent = AI_Agent(name="DemoAgent", config=agent_config)
        result = agent.run(user_query="帮我查询今天的天气")
    """
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.memory = MemoryManager()
        self.tool_caller = ToolCaller()`

3. **函数/方法注释**：位于函数定义上方，说明函数功能、参数（名称、类型、含义、可选/必选）、返回值（类型、含义）、异常信息。
        `def execute_task(self, task_id, task_params):
    """
    执行指定任务，调度对应工具，更新任务状态与记忆
    
    参数：
        task_id (str): 任务唯一标识（必选）
        task_params (dict): 任务参数（必选），格式：{"tool_name": "xxx", "params": {...}}
    
    返回：
        dict: 任务执行结果，格式：{"status": "success/fail", "data": {...}, "msg": "..."}
    
    异常：
        TaskExecuteError: 任务执行失败（如工具调用失败、参数错误）
        ValueError: 任务参数格式不正确
    """
    # 校验任务参数
    if not isinstance(task_params, dict) or "tool_name" not in task_params:
        raise ValueError("任务参数格式错误，需包含 tool_name 字段")
    # 调度工具执行任务
    try:
        tool_result = self.tool_caller.call(task_params["tool_name"], task_params["params"])
        # 更新记忆
        self.memory.update(f"任务{task_id}执行结果：{tool_result}")
        return {"status": "success", "data": tool_result, "msg": "任务执行成功"}
    except Exception as e:
        logger.error(f"任务{task_id}执行失败：{str(e)}")
        raise TaskExecuteError(f"任务执行失败：{str(e)}")`

4. **关键代码注释**：复杂逻辑、决策分支、工具调用、异常处理处添加注释，说明逻辑意图。
        `# 决策逻辑：根据用户查询类型，选择对应处理方式
if query_type == "task":
    # 任务类查询：调度执行模块，分配任务ID
    task_id = generate_task_id()
    result = self.execute_task(task_id, query_params)
elif query_type == "query":
    # 问答类查询：先查询记忆，无结果则调用问答工具
    memory_result = self.memory.query(query_params["keyword"])
    if memory_result:
        result = {"status": "success", "data": memory_result, "msg": "从记忆中获取结果"}
    else:
        result = self.tool_caller.call("qa_tool", query_params)
else:
    # 未知查询类型：返回友好提示，不执行多余操作
    result = {"status": "fail", "data": None, "msg": "未知查询类型，请重新输入"}`

# 五、AI Agent 专属编码规范

## 5.1 核心模块编码要求

1. **感知模块**：
        

    - 必须对用户输入进行校验（类型、格式、长度），过滤恶意输入（如注入语句、违规字符）。

    - 解析用户意图时，需添加意图识别日志，便于后续优化意图识别逻辑。

    - 支持多格式输入（文本、语音转文字等）时，统一转换为标准文本格式后再处理。

2. **决策模块**：
        

    - 决策逻辑需可追溯，每个决策步骤需有日志记录（如“选择工具A，原因：用户查询需要文件操作”）。

    - 避免硬编码决策规则，可将决策条件抽离为配置文件，支持动态调整。

    - 多任务并发时，需实现任务优先级排序（如紧急任务优先执行），避免任务阻塞。

3. **执行模块**：
        

    - 工具调用采用“基类 + 子类”模式，所有工具继承统一基类，实现统一接口（如 `run()` 方法），便于扩展新工具。

    - 工具调用超时时间可配置，超时后自动触发降级策略（如重试、切换备用工具、返回提示）。

    - 执行结果需格式化输出，确保返回格式统一（便于前端展示、其他模块调用）。

4. **记忆模块**：
       

    - 短期记忆与长期记忆拆分清晰，短期记忆（会话级）无需持久化，长期记忆需定期清理冗余数据。

    - 敏感记忆数据（如用户隐私信息）必须加密存储，查询时需校验权限。

    - 记忆更新、查询操作需添加日志，便于追溯记忆变更记录。

## 5.2 工具调用规范

- 工具注册：所有工具需在`tool_config.py` 中注册，明确工具名称、接口地址、参数格式、权限要求，禁止未注册工具被调用。

- 参数传递：工具调用时，参数需校验（类型、必填项、取值范围），避免因参数错误导致工具调用失败。

- 工具隔离：不同工具的代码独立存放，禁止工具之间直接耦合（如需交互，通过 Agent 主类中转）。

## 5.3 模型调用规范（如涉及大模型）

- 模型参数（如温度、最大token数、超时时间）统一配置在 `agent_config.py` 中，禁止硬编码。

- 模型调用需添加重试机制（如网络异常时重试 2-3 次），重试间隔可配置。

- 模型返回结果需过滤（如敏感信息），确保输出安全合规。

- 模型调用日志需记录（请求内容、返回结果、调用耗时），便于优化模型参数和调用逻辑。

# 六、安全规范

1. **敏感信息保护**：
        

    - 密钥、令牌、数据库密码等敏感信息，禁止硬编码在代码中，需存储在环境变量或加密配置文件中，通过工具类读取。

    - 用户隐私信息（如姓名、手机号、邮箱）需加密存储、脱敏展示（如手机号显示为 138****1234）。

2. **输入输出校验**：
        

    - 所有用户输入、第三方接口返回数据，必须进行校验（类型、格式、长度、内容），防范 SQL 注入、XSS 攻击、命令注入等。


3. **权限控制**：


    - 工具调用、记忆查询、任务执行等操作，需添加权限校验（如管理员权限、普通用户权限），禁止越权操作。


4. **日志安全**：

    - 日志中禁止打印敏感信息（如密钥、用户隐私），如需调试，可临时打印脱敏后的信息，上线前删除。

    - 日志文件需设置访问权限，禁止公开访问，定期清理日志文件（避免日志泄露）。

# 七、性能规范

1. **执行效率**：


    - 避免冗余计算（如重复查询记忆、重复调用工具），可使用缓存（如 Redis）存储高频访问数据。

    - 循环逻辑需优化，避免无限循环、大量循环（单个循环迭代次数不超过 1000 次，特殊场景需说明）。

2. **资源占用**：
        

    - 内存占用控制：避免大量创建临时对象，无用对象及时释放（遵循对应语言的垃圾回收机制）。

    - CPU 占用控制：复杂逻辑（如决策算法、模型调用）可异步执行，避免阻塞主线程。

3. **并发处理**：
        

    - 多用户并发请求时，需实现并发控制（如线程池、协程），避免资源竞争。

    - 工具调用、模型调用等耗时操作，采用异步方式执行，提升响应速度。

# 八、测试规范

1. 测试覆盖率：核心模块（Agent 主类、决策模块、工具调用、记忆模块）测试覆盖率不低于 80%，关键接口测试覆盖率 100%。

2. 测试类型：
        

    - 单元测试：针对单个函数、类进行测试，验证逻辑正确性。

    - 集成测试：测试模块之间的交互（如 Agent 调用工具、记忆模块与执行模块协同）。

    - 异常测试：测试异常场景（如参数错误、工具调用失败、模型超时），验证异常处理逻辑有效性。

3. 测试代码规范：测试文件、测试函数命名遵循 `test_xxx.py`、`test_xxx()` 格式，测试用例清晰，包含正常场景、异常场景。

# 九、附则

1. 本规范适用于所有 AI Agent 相关代码开发、修改、维护工作，所有开发人员必须严格遵循。

2. 本规范将根据项目迭代、技术升级适时更新，更新后将通知所有开发人员，统一执行新版本规范。

3. 若存在特殊场景（如紧急开发、第三方接口适配），需偏离本规范，需提前报备负责人，经同意后方可执行。

4. 本规范最终解释权归项目开发团队所有。

**补充说明**：本规范为通用版，具体项目可根据开发语言、技术栈、业务场景，在本规范基础上补充专属条款（如 Python 语言专属编码细节、前端交互相关编码规范等）。

# 十、Python语言专属编码补充规范

## 10.1 基础语法规范（遵循PEP 8标准）

- 缩进：统一使用4个空格缩进，禁止使用制表符（Tab），避免缩进不一致导致的语法错误（AI Agent核心模块需严格遵守，避免因缩进问题导致任务执行异常）。

- 行宽：单个代码行长度不超过79字符，注释行长度不超过72字符；超长行需合理换行，优先在逗号、运算符后换行，换行后缩进对齐（如函数参数、列表推导式）。

- 空行：模块级代码（导入、常量定义）与类/函数定义之间用2个空行分隔；类内方法之间用1个空行分隔；函数内逻辑块用1个空行分隔，禁止多余空行（如连续3个及以上空行）。

- 引号使用：字符串统一使用双引号（""），若字符串内包含双引号，可使用单引号（''）包裹，禁止混合使用（如AI Agent的配置参数、日志信息、用户提示文本）；多行字符串优先使用三重双引号（"""），避免使用反斜杠换行。

- 分号：禁止在一行内写多个语句（用分号分隔），每个语句单独成行，提升可读性（如禁止`task_id = 1; execute_task(task_id)`）。

## 10.2 导入规范（基于通用规则细化）

- 导入顺序：标准库 → 第三方库 → 自定义模块，各组之间用1个空行分隔；同一组内导入按模块名称字母顺序排列。

- 绝对导入与相对导入：项目内核心模块（core、memory、tools）使用绝对导入（如`from core.agent import AI_Agent`）；同一模块下的子模块可使用相对导入（如`from .base_tool import BaseTool`），禁止混合使用导致导入混乱。

- 导入优化：禁止导入未使用的模块/函数；若导入模块名称过长，可使用简洁别名（如`import pandas as pd`、`from utils.log_utils import logger as log`），别名需统一，避免随意变更。

- 特殊导入：AI Agent中需动态导入工具、模型等模块时，需使用`importlib`模块，禁止使用`__import__`函数，确保导入可追溯、可维护。

## 10.3 变量与数据类型规范

- 变量初始化：定义变量时需明确初始化（禁止`task_result = None`后无赋值直接使用）；AI Agent中会话级变量（如`current_session`）需标注类型提示，提升可读性。

- 类型提示：核心函数、类方法必须添加类型提示（参数类型、返回值类型），使用`typing`模块补充复杂类型（如`List[Dict[str, Any]]`、`Optional[str]`），示例：`from typing import List, Dict, Optional

def parse_user_query(query: str) -> Optional[Dict[str, str]]:
    """解析用户查询，返回查询类型和参数"""
    if not query.strip():
        return None
    # 解析逻辑
` `    return {"query_type": "task", "params": {"keyword": query}}`

- 数据结构选择：AI Agent中任务队列优先使用`collections.deque`（高效进出队），记忆缓存优先使用`dict`或`functools.lru_cache`（避免冗余计算）；禁止使用列表模拟队列（效率低下）。

- 常量与魔术变量：禁止使用魔术变量（如`__all__`）暴露模块内私有内容；AI Agent的核心常量（如模型超时时间）需定义在对应配置文件，禁止在代码中直接定义常量。

## 10.4 函数与类规范（基于通用规则细化）

- 函数参数：函数参数个数不超过5个，多余参数使用`**kwargs`（需标注类型）；AI Agent中工具调用、任务执行相关函数，必选参数在前，可选参数在后，可选参数需设置合理默认值（避免默认值为可变对象，如`def func(params: dict = {})`，需改为`def func(params: Optional[dict] = None)`）。

- 类的继承：AI Agent工具类统一继承`BaseTool`基类，禁止多继承（特殊场景需多继承时，需报备负责人，确保无继承冲突）；基类中抽象方法使用`abc.ABCMeta`和`@abstractmethod`装饰器，强制子类实现。

- 装饰器使用：AI Agent中工具注册、权限校验、日志记录等场景可使用装饰器，装饰器需定义在`utils`模块，统一管理；禁止过度使用装饰器（如单个函数添加3个及以上装饰器），避免逻辑晦涩。示例：`from abc import ABCMeta, abstractmethod
from utils.decorators import tool_register

class BaseTool(metaclass=ABCMeta):
    @abstractmethod
    def run(self, params: dict) -> dict:
        """工具执行核心方法，子类必须实现"""
        pass

@tool_register(tool_name="file_tool")  # 工具注册装饰器
class FileTool(BaseTool):
    def run(self, params: dict) -> dict:
        # 文件操作逻辑
` `        return {"status": "success", "data": "文件操作完成"}`

- 私有成员：类内私有方法、私有属性统一以双下划线（__）开头（如`__validate_params`），禁止外部直接调用；禁止使用单下划线（_）作为私有标识（单下划线仅表示“不建议外部调用”，非强制限制）。