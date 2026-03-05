# Agent 模块需求分析与代码设计文档

## 一、需求分析

### 1.1 背景

Genban 是一个以「应用可视化、模块化」为核心架构的 AI 个人助理系统。Agent 模块负责单次 AI 调用的流程编排，包括模型调用、工具调用和生命周期钩子管理。

### 1.2 目标

实现一个专注单次调用的 Agent 流程控制模块，支持：
- 多模型统一调用接口
- 工具调用框架
- 生命周期钩子机制
- 流式输出支持
- 工具调用循环（最大50次迭代）

### 1.3 流程图

见 `agent流程图.drawio.png`

### 1.4 核心需求

#### 1.4.1 模型调用 (Model)
- 统一封装不同 LLM Provider 的调用接口
- 支持配置化模型切换
- 支持流式输出

#### 1.4.2 工具调用 (Tools)
- 工具注册与发现机制
- 工具参数解析与执行
- 工具执行结果回传
- 支持多轮工具调用循环

#### 1.4.3 生命周期钩子 (Hooks)
- 支持在关键节点插入自定义逻辑
- 钩子类型：model_hook, chat_hook, prompt_hook, chats_hook, tools_hook, new_chat_hook, complete_hook
- 支持多个钩子函数链式执行
- 支持同步和异步执行

---

## 二、代码设计

### 2.1 模块结构

```
src/agent/
├── entities.py           # Chat/Message/AgentContext 数据定义
├── agent.py              # Agent 主流程控制器
├── chat_factory.py       # Chat 工厂类
├── model/
│   ├── model_caller.py   # 模型调用器
│   └── model_provider.py # 模型提供者接口
├── tools/
│   ├── tool_caller.py    # 工具调用器
│   ├── tool_registry.py  # 工具注册中心
│   ├── tool_parser.py    # 工具调用解析器
│   └── base_tool.py      # 工具基类
└── hooks/
    ├── hook_manager.py   # 钩子管理器
    ├── hook_registry.py  # 钩子注册中心
    └── base_hook.py      # 钩子基类
```

### 2.2 核心类职责

#### 2.2.1 Agent (主控制器)

职责：编排单次 Agent 调用的完整流程

主要功能：
- 接收输入参数，组装模型调用参数
- 按顺序执行前置钩子链（model → chat → prompt → chats → tools）
- 调用大模型并处理流式响应
- 判断是否需要工具调用，如需则循环执行（最大50次）
- 管理单次调用的生命周期
- 提供工具和钩子的注册接口
- 返回本次调用新增的 Chat 列表

#### 2.2.2 ModelCaller (模型调用器)

职责：统一封装不同 LLM Provider 的调用

主要功能：
- 管理多个模型提供者
- 根据配置路由到对应 Provider
- 支持流式调用

#### 2.2.3 ToolCaller (工具调用器)

职责：执行工具调用

主要功能：
- 从注册中心获取工具
- 解析工具参数并执行
- 封装工具执行结果
- 支持从模型响应解析工具调用

#### 2.2.4 HookManager (钩子管理器)

职责：管理生命周期钩子

主要功能：
- 注册/注销钩子
- 按类型执行钩子链（同步）
- 异步执行钩子（不阻塞主流程）
- 支持钩子数据传递

#### 2.2.5 chat_factory (Chat 工厂)

职责：创建各种 Chat 和 Message 对象

主要功能：
- 创建系统/用户/助手/工具消息
- 创建 prompt/user/assistant/tool/error Chat
- 自动生成唯一 Chat ID

### 2.3 数据定义

#### 2.3.1 核心实体

- `Message` - 大模型消息实体（role, content, tool_calls, tool_call_id）
- `MessageRole` - 消息角色枚举（system/user/assistant/tool）
- `CallResponse` - 模型调用返回封装
- `Chat` - Agent 层对话内容封装（type, id, time, message, total_tokens）
- `ChatType` - 对话类型枚举（PROMPT/USER/ASSISTANT/TOOL/COMMAND/MEMORY/TOOL_SUMMARY/ERROR）
- `AgentContext` - Agent 单次执行上下文（model_key, user_id, input_chat, prompt_chat, history_chats, new_chats）

#### 2.3.2 工具相关

- `ToolParameter` - 工具参数定义
- `ToolCall` - 工具调用定义
- `ToolResult` - 工具执行结果

### 2.4 钩子点位（按执行顺序）

| 钩子类型 | 入参类型 | 出参类型 | 执行方式 | 说明 |
|---------|---------|---------|---------|------|
| ModelHook | str | str | 同步 | 决定使用哪个模型 key |
| ChatHook | Chat | Chat | 同步 | 处理输入对话 |
| PromptHook | Chat | Chat | 同步 | 处理提示词对话 |
| ChatsHook | list[Chat] | list[Chat] | 同步 | 处理历史对话列表 |
| ToolsHook | ToolRegistry | ToolRegistry | 同步 | 处理工具注册表 |
| NewChatHook | Chat | Chat | 异步 | 处理新增的 Chat（模型响应、工具结果） |
| CompleteHook | list[Chat] | list[Chat] | 异步 | 处理完成时的所有新增 Chat |

### 2.5 对外接口

Agent 模块为内部模块，不直接对外暴露 HTTP 接口，供其他后端模块调用：

```python
from src.agent.agent import Agent
from src.agent.chat_factory import chat_factory

# 方式一：创建 Agent 实例时传入工具和钩子
agent = Agent(
    user_id="user001",
    tools=[WeatherTool(), CalculatorTool()],
    hooks=[LoggingHook(), MetricsHook()]
)

# 方式二：通过 Agent 提供的快捷方法注册
agent = Agent(user_id="user001")
agent.register_tool(WeatherTool())
agent.register_hook(LoggingHook())

# 创建用户输入 Chat
input_chat = chat_factory.create_user_chat(
    user_id="user001",
    user_input="今天天气如何？"
)

# 执行调用（同步，返回本次新增的 Chat 列表）
new_chats = agent.run(chat=input_chat)
# new_chats 包含：assistant 响应 Chat、tool 调用结果 Chat 等
```

### 2.6 执行流程

```
用户输入 Chat
    ↓
[ModelHook] 决定模型 key（首个执行）
    ↓
[ChatHook] 处理输入对话
    ↓
[PromptHook] 处理提示词对话
    ↓
[ChatsHook] 处理历史对话列表
    ↓
[ToolsHook] 处理工具注册表
    ↓
调用大模型（流式）
    ↓
[NewChatHook] 处理模型响应（异步）
    ↓
判断是否需要工具调用：
    ├── 是 → 执行工具 → [NewChatHook] 处理工具结果（异步）
    │           ↓
    │       再次调用模型（循环，最大50次）
    │
    └── 否 → [CompleteHook] 处理完成（异步）
            ↓
        返回本次新增的 Chat 列表
```

---

## 三、依赖关系

```
Agent
├── ModelCaller (单例)
│   └── ModelProvider (abstract)
│       ├── DashScopeProvider
│       └── ... (other providers)
├── ToolCaller
│   └── ToolRegistry
│       └── BaseTool (abstract)
├── HookManager
│   ├── HookRegistry
│   └── BaseHook (abstract)
│       ├── ModelHook
│       ├── ChatHook
│       ├── PromptHook
│       ├── ChatsHook
│       ├── ToolsHook
│       ├── NewChatHook
│       └── CompleteHook
└── chat_factory (单例)
```

---

## 四、与现有系统集成

Agent 模块通过 `ModelCaller` 调用 Provider 层已实现的 API 封装：
- `src/provider/api/api_dashscope.py` - 阿里云 DashScope
- `src/provider/api/api_zai_sdk.py` - 智谱 AI

---

*文档版本: v1.3*
*更新日期: 2026-03-05*
