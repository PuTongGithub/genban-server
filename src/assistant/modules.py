"""模块集合定义

集中定义所有模块实例
"""

from src.modules.conversation.conversation_module import ConversationModule
from src.modules.file_system.file_system_module import FileSystemModule
from src.modules.memory.memory_module import MemoryModule
from src.modules.schedule.schedule_module import ScheduleModule
from src.modules.settings.settings_module import SettingsModule
from src.modules.shell.shell_module import ShellModule
from src.modules.skills.skills_module import SkillsModule
from src.modules.system_remainder.system_remainder_module import SystemRemainderModule
from src.modules.user_message.user_message_module import UserMessageModule
from src.modules.web.web_module import WebModule

ASSISTANT_MODULES = [
    UserMessageModule(),
    SystemRemainderModule(),
    FileSystemModule(),
    ShellModule(),
    SettingsModule(),
    SkillsModule(),
    WebModule(),
    ConversationModule(),
    ScheduleModule(),
    MemoryModule(),
]
