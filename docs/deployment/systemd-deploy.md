# Genban Server Systemd 部署文档

## 部署信息

- **部署目录**: `/var/genban/genban-server`
- **虚拟环境**: `/var/genban/genban-server/.venv`
- **环境变量文件**: `/var/genban/genban-server/.env`
- **服务用户**: `genban`

---

## 完整部署流程

### 1. 创建专用用户

```bash
# 创建系统用户（无登录权限）
sudo useradd -r -s /bin/false -d /var/genban genban

# 设置目录权限
sudo chown -R genban:genban /var/genban/genban-server
sudo chmod 750 /var/genban/genban-server
```

---

### 2. 创建 Systemd Service 文件

```bash
sudo nano /etc/systemd/system/genban.service
```

写入以下内容：

```ini
[Unit]
Description=Genban AI Server
Documentation=https://github.com/your-repo/genban-server
After=network.target
Wants=network.target

[Service]
Type=simple
User=genban
Group=genban
WorkingDirectory=/var/genban/genban-server

# 加载环境变量文件
EnvironmentFile=/var/genban/genban-server/.env

# 启动命令
ExecStart=/var/genban/genban-server/.venv/bin/python main.py

# 优雅停止
ExecStop=/bin/kill -TERM $MAINPID
TimeoutStopSec=30

# 自动重启策略
Restart=always
RestartSec=5
StartLimitInterval=60s
StartLimitBurst=3

# 日志输出
StandardOutput=journal
StandardError=journal
SyslogIdentifier=genban

# 资源限制（可选）
# MemoryLimit=512M
# CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

---

### 3. 配置环境变量

```bash
# 编辑 .env 文件
sudo nano /var/genban/genban-server/.env
```

**安全设置**：

```bash
# 确保 .env 文件只有服务用户可读
sudo chown genban:genban /var/genban/genban-server/.env
sudo chmod 600 /var/genban/genban-server/.env
```

---

### 4. 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 设置开机自启
sudo systemctl enable genban

# 启动服务
sudo systemctl start genban

# 查看状态
sudo systemctl status genban
```

---

### 5. 常用管理命令

```bash
# 查看服务状态
sudo systemctl status genban

# 查看实时日志
sudo journalctl -u genban -f

# 查看最近 100 条日志
sudo journalctl -u genban -n 100

# 查看今天日志
sudo journalctl -u genban --since today

# 重启服务
sudo systemctl restart genban

# 停止服务
sudo systemctl stop genban

# 重载配置（修改 .env 后）
sudo systemctl restart genban
```

---

### 6. 日志轮转配置（可选）

防止日志文件过大：

```bash
sudo nano /etc/logrotate.d/genban
```

写入：

```
/var/log/genban/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 genban genban
    sharedscripts
    postrotate
        systemctl reload genban
    endscript
}
```

## 文件清单

| 文件 | 路径 | 权限 |
|------|------|------|
| 服务文件 | `/etc/systemd/system/genban.service` | 644 |
| 环境变量 | `/var/genban/genban-server/.env` | 600 |
| 应用目录 | `/var/genban/genban-server` | 750 |
| 日志 | `journalctl -u genban` | - |

---

## 更新部署

```bash
# 1. 停止服务
sudo systemctl stop genban

# 2. 更新代码（git pull 或其他方式）
cd /var/genban/genban-server
sudo -u genban git pull

# 3. 更新依赖（如有变化）
sudo -u genban /var/genban/genban-server/.venv/bin/pip install -r requirements.txt

# 4. 启动服务
sudo systemctl start genban

# 5. 检查状态
sudo systemctl status genban
```
