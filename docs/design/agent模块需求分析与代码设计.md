# Agent 模块需求分析与代码设计文档

## 一、需求分析

### 1.1 背景

Genban 是一个以「应用可视化、模块化」为核心架构的 AI 个人助理系统。Agent 模块负责单次 AI 调用的流程编排，基于消息管道架构实现异步处理，包括模型调用、工具调用和生命周期钩子管理。

### 1.2 目标

实现一个基于消息管道的 Agent 流程控制模块，支持：
- 消息管道架构（输入/输出管道解耦）
- 多模型统一调用接口
- 工具调用框架
- 生命周期钩子机制
- 流式输出支持
- 工具调用循环（最大50次迭代）
- 双模式消息拉取（阻塞/非阻塞）

### 1.3 流程图

见 `agent流程图.drawio.png`

### 1.4 核心需求

#### 1.4.1 消息管道架构
- **输入管道 (in_message_pipe)**: 接收外部输入的 Chat 消息
- **输出管道 (out_message_pipe)**: 推送处理过程中产生的所有 Chat 消息
- **异步解耦**: 调用方和 Agent 通过管道异步通信，无需等待完成

#### 1.4.2 模型调用 (Model)
- 统一封装不同 LLM Provider 的调用接口
- 支持配置化模型切换
- 支持流式输出

#### 1.4.3 工具调用 (Tools)
- 工具注册与发现机制
- 工具参数解析与执行
- 工具执行结果回传
- 支持多轮工具调用循环

#### 1.4.4 生命周期钩子 (Hooks)
- 支持在关键节点插入自定义逻辑
- 钩子类型：model_hook, prompt_hook, chats_hook, confirmed_chat_hook
- 支持多个钩子函数链式执行
- 支持同步和异步执行

---

## 二、代码设计

### 2.1 模块结构

```
src/agent/
├── entities.py           # Chat/Message/AgentContext/MessagePipeContent 数据定义
├── agent.py              # Agent 主流程控制器
├── chat_factory.py       # Chat 工厂类
├── exceptions.py         # 异常定义
├── model/
│   ├── model_caller.py   # 模型调用器
│   ├── model_provider.py # 模型提供者接口
│   ├── entities.py       # CallResponse 等实体
│   └── providers/        # 各模型提供商实现
├── tools/
│   ├── tool_caller.py    # 工具调用器
│   ├── tool_registry.py  # 工具注册中心
│   ├── base_tool.py      # 工具基类
│   └── entities.py       # ToolCall/ToolResult 等实体
└── hooks/
    ├── hook_manager.py   # 钩子管理器
    ├── hook_registry.py  # 钩子注册中心
    ├── base_hook.py      # 钩子基类
│   └── entities.py       # ModelConfig 等实体
```

### 2.2 核心类职责

#### 2.2.1 Agent (主控制器)

职责：基于消息管道架构，编排单次 Agent 调用的完整流程

主要功能：
- 维护输入/输出消息管道，实现异步解耦
- 运行主循环，支持阻塞和非阻塞两种消息拉取模式
- 按顺序执行前置钩子链（model → prompt → chats）
- 调用大模型并处理流式响应
- 判断是否需要工具调用，如需则循环执行（最大50次）
- 管理单次调用的生命周期
- 提供工具和钩子的注册接口

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
- 创建 prompt/user/assistant/tool/error/stop Chat
- 自动生成唯一 Chat ID

### 2.3 数据定义

#### 2.3.1 核心实体

- `Message` - 大模型消息实体（role, content, tool_calls, tool_call_id）
- `MessageRole` - 消息角色枚举（system/user/assistant/tool）
- `CallResponse` - 模型调用返回封装
- `Chat` - Agent 层对话内容封装（type, id, time, message, total_tokens）
- `ChatType` - 对话类型枚举（PROMPT/USER/ASSISTANT/TOOL/SYSTEM_REMAINDER/MEMORY/ERROR/STOP）
- `AgentContext` - Agent 单次执行上下文（model_config, user_id, prompt_chats, history_chats, new_chats, modules）
- `MessagePipeContent` - 消息管道内容封装（chat）

#### 2.3.2 工具相关

- `ToolParameter` - 工具参数定义
- `ToolCall` - 工具调用定义
- `ToolResult` - 工具执行结果

#### 2.3.3 钩子相关

- `ModelConfig` - 模型配置（model_key, enable_thinking）

### 2.4 钩子点位（按执行顺序）

| 钩子类型 | 入参类型 | 出参类型 | 执行方式 | 说明 |
|---------|---------|---------|---------|------|
| ModelHook | ModelConfig | ModelConfig | 同步 | 决定使用哪个模型配置（首个执行） |
| PromptHook | list[Chat] | list[Chat] | 同步 | 处理提示词对话列表 |
| HistoryChatsHook | list[Chat] | list[Chat] | 同步 | 处理历史对话列表 |
| ConfirmedChatHook | Chat | Chat | 异步 | 处理已确认的新增对话（包括新消息、模型响应、工具结果） |

### 2.5 对外接口

Agent 模块为内部模块，不直接对外暴露 HTTP 接口，供其他后端模块调用：

```python
from src.agent.agent import Agent
from src.agent.chat_factory import chat_factory

# 创建 Agent 实例，传入模块（模块自动注入 tools 和 hooks）
agent = Agent(
    user_id="user001",
    modules=[FileSystemModule(), ShellModule()]
)

# 或动态注册工具和钩子
agent.register_tool(WeatherTool())
agent.register_hook(LoggingHook())

# 创建用户输入 Chat
input_chat = chat_factory.create_user_chat(
    user_id="user001",
    user_input="今天天气如何？"
)

# 发送消息到 Agent（异步，立即返回）
agent.send_chat(input_chat)

# 从输出管道接收消息（在独立线程中循环接收）
output_chat = agent.recv_chat()
```

### 2.6 执行流程

见 agent流程图.drawio.png

**流程说明**:

1. **流程1（阻塞模式）**: 首次启动或工具调用链结束后，Agent 阻塞等待用户新输入，节省系统资源
2. **流程2（非阻塞模式）**: 工具调用后，Agent 非阻塞检查是否有新消息，然后立即继续处理工具结果，支持连续工具调用
3. **停止消息**: 当接收到 `ChatType.STOP` 类型的消息时，Agent 跳过处理直接返回流程1
4. **流式输出**: 模型响应通过流式方式实时推送到输出管道，无需等待完整响应
5. **异步钩子**: `ConfirmedChatHook` 采用异步执行，适合用于消息持久化、日志记录等不阻塞主流程的操作

---

*文档版本: v2.0*
*更新日期: 2026-03-17*
