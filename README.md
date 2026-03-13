# Genban

## 项目概述

Genban 是一个以「应用可视化、模块化」为核心架构的 AI 个人助理系统。系统内置的每个应用都具备双重形态—— AI 可调用的接口，以及用户可视化的界面，双方由此基于同一套应用进行交互，实现人与 AI 的认知对齐。本项目是 Genban 的服务端项目。

## 技术栈

- **编程语言**: Python
- **Web 框架**: FastAPI
- **数据库**: sqlite

## 核心功能

- **多用户系统**：具备完善的用户管理系统，支持多用户使用
- **多模型支持**：统一对接多家模型平台，支持模型切换
- **应用模块化**：提供模块化的应用系统，用户可以自行选择使用哪些应用
- **多AGENT调度**：具备多AGENT的调度管理能力
- **记忆管理**：实现记忆管理机制，具备长期记忆能力

## 初始化（首次运行前）

### 虚拟环境设置

```bash
python -m venv .venv
```
激活虚拟环境：
```bash
source .venv/bin/activate
```
或在 Windows 上使用：
```bash
.venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 执行初始化脚本

```bash
python scripts/init_project.py
```

## 打包指令

```bash
pip freeze > requirements.txt
```