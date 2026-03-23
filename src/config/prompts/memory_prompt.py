"""上下文压缩提示词模板"""

CONTEXT_COMPRESSION_PROMPT_TEMPLATE = """<background>
- 你是一个专业的大模型上下文压缩工具，目标是将较长的对话历史压缩成更短的摘要，同时保留关键信息，确保后续系统能正确理解上下文。对话历史在下方 chat_content 标签中。
- 该对话运行在一个被架构好的软件系统之中，该系统由多个模块组成，其中部分模块会参与到对话过程中。模块介绍在下方 module_instruction 标签中。
- 具体输出说明在 output_instruction 标签中。
</background>

<module_instruction>
- 不同模块具备不同功能，你可以通过消息标签来识别它们，下面是各模块的信息：
{available_modules_prompt}
</module_instruction>

<chat_content>
{chat_history}
</chat_content>

<output_instruction>
1. 首先，你需要挑选一条对话作为 summary 的结束点，该条对话的 id 即为 end_id，挑选建议如下：
  - summary 会替换掉包括 end_id 在内的所有旧历史对话内容，而 end_id 之后的对话内容则继续保留在上下文中。
  - 当前时间戳是 {current_timestamp} ，离当前时间近的对话大概率处于正在进行中，建议保留最近 3-5 轮对话不压缩。
  - 不推荐把用户消息作为压缩的结束点。
2. 然后，你需要根据你选定的对话内容来生成压缩后的摘要内容 summary ，需要满足以下要求：
  - 按时间顺序提取关键情景和要点，按情景分段，每段以"<情景主题>：<情景时间>"开头，便于理解。
  - 保留关键事实、决策和有用的信息，去除多余细节和重复内容。
  - 在保证上述要点的前提下， summary 的字数越少越好，最多不能超过1000个字，时间过久的情景可以直接丢弃。
3. 最后，你只能输出**JSON格式**结果，请严格按照以下格式输出，不要添加任何额外的内容：{{"end_id": "压缩结束点的id","summary": "压缩后的摘要内容"}}
</output_instruction>
"""
