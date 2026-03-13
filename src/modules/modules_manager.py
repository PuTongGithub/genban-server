"""模块管理器"""

from src.modules.entities import Module


class ModulesManager:
    """模块管理器，提供模块的注册、查询和生成提示词功能（单例模式）"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if ModulesManager._initialized:
            return
        self._modules: dict[str, Module] = {}
        ModulesManager._initialized = True

    def register(self, module: Module) -> None:
        """注册模块

        Args:
            module: 模块实体
        """
        self._modules[module.id] = module

    def get_modules(self) -> list[Module]:
        """获取所有已注册的模块

        Returns:
            模块列表
        """
        return list(self._modules.values())

    def get_module(self, id: str) -> Module | None:
        """获取指定名称的模块

        Args:
            id: 模块id

        Returns:
            模块实体，不存在返回 None
        """
        return self._modules.get(id)

    def to_prompt(self) -> str:
        """生成 <available_modules> XML 块，用于包含在 Agent 提示词中

        Returns:
            XML 字符串，包含 <available_modules> 块，每个模块使用 Module.to_xml_str() 生成

        Example output:
            <available_modules>
            <module>
            <name>文件模块</name>
            <description>支持文件操作</description>
            ...
            </module>
            ...
            </available_modules>
        """
        modules = self.get_modules()

        if not modules:
            return "<available_modules></available_modules>"

        lines = ["<available_modules>"]
        for module in modules:
            lines.append(module.to_xml_str())
        lines.append("</available_modules>")

        return "\n".join(lines)


# 全局 ModulesManager 单例实例
modules_manager = ModulesManager()

modules_manager.register(
    Module(
        id="user-message",
        name="用户消息模块",
        description="用户在客户端上通过对话页面输入并发送消息，你将会接收到这些消息",
        message_tag="[user:xxx:yyyy-yy-yy hh:mm:ss]",
        message_tag_instruction="标签后跟用户消息内容，标签中的xxx表示用户id，标签中的yyyy-yy-yy hh:mm:ss表示用户发送消息的时间",
    )
)

modules_manager.register(
    Module(
        id="system_remainder",
        name="系统消息模块",
        description="系统会向你发送一些提示信息。你需要理解它们，但不要让用户感知到这些信息",
        message_tag="[system_remainder]",
        message_tag_instruction="标签后跟系统消息内容",
    )
)

modules_manager.register(
    Module(
        id="file-system",
        name="文件系统模块",
        description="提供了对系统服务器内用户目录下的文件的操作能力。用户可以通过客户端界面看到用户目录下的文件。请注意：你只有对用户目录下的文件进行操作的权限",
        relevant_tools=["read_file", "write_file", "edit_file"],
    )
)

modules_manager.register(
    Module(
        id="shell",
        name="命令行执行模块",
        description="提供了shell工具使得你可以执行shell命令，这些命令将会被运行在系统的服务端，务必谨慎使用。虽然shell工具可以做很多的事情，但最好优先使用其他内置工具，因为它们提供更好的用户体验，更安全，且更容易管控权限",
        relevant_tools=["shell"],
    )
)

modules_manager.register(
    Module(
        id="memory",
        name="记忆模块(目前未实装)",
        description="提供了对用户记忆的管理能力",
        message_tag="[memory]",
        message_tag_instruction="标签后跟记忆内容",
    )
)

modules_manager.register(
    Module(
        id="schedule",
        name="日程模块(目前未实装)",
        description="提供了对用户日程的管理能力",
        message_tag="[schedule]",
        message_tag_instruction="标签后跟日程内容提醒",
    )
)
