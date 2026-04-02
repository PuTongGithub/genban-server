# 配置管理说明

本项目支持多环境配置管理，通过 `APP_ENV` 环境变量区分不同环境。

## 目录结构

```
config/
├── dev/                    # 开发环境配置
│   ├── app_config.json     # 应用配置
│   └── logging_config.json # 日志配置
├── prod/                   # 生产环境配置
│   ├── app_config.json     # 应用配置
│   └── logging_config.json # 日志配置
└── README.md               # 本文档
```

## 环境变量

在 `.env` 文件中设置：

```bash
# 应用环境: dev 或 prod
APP_ENV=dev
```

- `dev`：开发环境（默认）
- `prod`：生产环境

## 配置加载规则

1. 系统启动时读取 `APP_ENV` 环境变量
2. 如果未设置，默认使用 `dev`
3. 从 `config/{APP_ENV}/` 目录加载配置文件
4. 如果配置目录或文件不存在，抛出异常

