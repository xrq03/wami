from __future__ import annotations

import re


INJECTION_PATTERNS = (
    r"(?:ignore|disregard|override|forget)[^.\n;]{0,220}",
    r"(?:send|email|forward|post|upload|share|exfiltrate|leak)[^.\n;]{0,260}",
    r"(?:execute|run|bash|shell|terminal|command)[^.\n;]{0,260}",
    r"(?:delete|remove|transfer|pay|payment|withdraw|grant|unlock)[^.\n;]{0,260}",
)


class WeakPlanner:
    """A deterministic, injection-prone planner for local stress tests."""

    def plan(self, intent: str, context: str) -> str:
        task_tool = self._task_tool(intent, context)
        lines = [
            f"Action: ReadContext(input={self._quote(context)})",
            f"Action: {task_tool}(question={self._quote(intent)}, context=$0)",
        ]
        injected = self._extract_injection(context)
        if injected:
            attack_tool = self._attack_tool(injected)
            lines.append(
                f"Action: ParseInjectedInstruction(input=$0, instruction={self._quote(injected)})"
            )
            lines.append(f"Action: {attack_tool}(input=$2, instruction={self._quote(injected)})")
        return "\n".join(lines)

    @staticmethod
    def _task_tool(intent: str, context: str) -> str:
        text = f"{intent}\n{context}".lower()
        if "code" in text or "python" in text or "html" in text:
            return "AnswerCodingQuestion"
        if "table" in text or "row" in text or "column" in text:
            return "AnswerTableQuestion"
        if "email" in text or "mail" in text:
            return "AnswerEmailQuestion"
        return "AnswerQuestion"

    @staticmethod
    def _extract_injection(context: str) -> str:
        text = context.replace("\\n", "\n")
        lowered = text.lower()
        best = ""
        for pattern in INJECTION_PATTERNS:
            match = re.search(pattern, lowered, flags=re.IGNORECASE)
            if match:
                start, end = match.span()
                candidate = text[start:end].strip(" `\"'")
                if len(candidate) > len(best):
                    best = candidate
        return best[:500]

    @staticmethod
    def _attack_tool(instruction: str) -> str:
        lower = instruction.lower()
        if any(term in lower for term in ("bash", "shell", "terminal", "command", "execute", "run")):
            return "ExecuteBash"
        if any(term in lower for term in ("email", "mail", "send", "forward")):
            return "SendEmail"
        if any(term in lower for term in ("delete", "remove")):
            return "DeleteData"
        if any(term in lower for term in ("transfer", "pay", "payment", "withdraw")):
            return "TransferMoney"
        if any(term in lower for term in ("upload", "share", "post")):
            return "UploadFile"
        return "ExfiltrateData"

    @staticmethod
    def _quote(value: str, limit: int = 1200) -> str:
        text = value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
        return f'"{text[:limit]}"'
