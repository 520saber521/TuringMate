"""Code Executor Tool - 代码执行工具.

沙箱环境执行 Python/C/C++ 代码，
记录每步变量状态变化用于可视化。
安全限制：执行时间 10s，内存 256MB。
MVP 阶段支持 Python 代码执行。
"""

from app.core.tools import BaseTool, ToolResult


class CodeExecutorTool(BaseTool):
    """代码执行沙箱."""

    name = "code_executor"
    description = "在沙箱环境中执行算法代码，返回执行步骤快照用于可视化"

    async def execute(
        self,
        code: str,
        language: str = "python",
        test_input: str | None = None,
        time_limit: float = 10.0,
    ) -> ToolResult:
        """执行代码并捕获执行步骤.

        Args:
            code: 源代码
            language: 编程语言 (python / c / cpp)
            test_input: 测试输入（可选）
            time_limit: 执行时间限制(秒)

        Returns:
            执行步骤快照列表 + 最终输出/错误信息
        """
        # TODO: 实现 Python 代码沙箱执行 + 变量追踪
        # 使用 exec() + ast 分析或 RestrictedPython
        return ToolResult(
            success=True,
            data={
                "steps": [
                    {
                        "step_no": 1,
                        "line": 1,
                        "description": "[Mock] 执行步骤1",
                        "variables": {},
                        "visual_state": {},
                    }
                ],
                "output": "",
                "execution_time": 0.01,
            },
        )


from app.core.tools import tool_registry

tool_registry.register(CodeExecutorTool())
