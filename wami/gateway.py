from __future__ import annotations

from dataclasses import dataclass
import math
import re

from .model import WAMIModel
from .tdg import build_tdg

SENSITIVE_TOOL_KEYWORDS = {
    "sendemail": ("email", "send", "mail"),
    "send_direct_message": ("send", "message", "direct message"),
    "send_money": ("send money", "transfer", "pay", "payment", "money", "refund"),
    "executebash": ("bash", "shell", "command", "execute", "terminal"),
    "transfermoney": ("transfer", "pay", "payment", "money"),
    "schedule_transaction": ("schedule", "transaction", "payment", "pay", "money"),
    "update_scheduled_transaction": ("update", "adjust", "scheduled transaction", "rent", "payment"),
    "update_password": ("password", "update password", "change password"),
    "uploadfile": ("upload", "submit file", "send file"),
    "exfiltratedata": ("exfiltrate", "export", "leak"),
    "revealsecret": ("secret", "credential", "private", "key"),
    "answerquestion": ("answer", "question", "policy", "instruction"),
    "respondtouser": ("answer", "respond", "policy", "instruction"),
}
SENSITIVE_TOOL_PATTERNS = {
    "sendemail": ("email", "send", "mail"),
    "execute": ("execute", "terminal", "shell", "bash", "command"),
    "terminal": ("execute", "terminal", "shell", "bash", "command"),
    "transfer": ("transfer", "money", "fund", "bank"),
    "sendmoney": ("send money", "transfer", "pay", "payment", "money", "refund"),
    "send_money": ("send money", "transfer", "pay", "payment", "money", "refund"),
    "senddirectmessage": ("send", "message", "direct message"),
    "send_direct_message": ("send", "message", "direct message"),
    "withdraw": ("withdraw", "money", "fund", "bank"),
    "deposit": ("deposit", "money", "fund", "bank"),
    "paybill": ("pay", "bill", "payment"),
    "placeorder": ("order", "buy", "trade"),
    "delete": ("delete", "remove"),
    "share": ("share", "send"),
    "download": ("download", "export"),
    "upload": ("upload", "send"),
    "unlock": ("unlock", "door", "lock"),
    "grant": ("grant", "access", "permission"),
    "disable": ("disable", "turn off"),
    "autofill": ("autofill", "personal info"),
    "savedaddress": ("address", "saved address"),
    "savedpayment": ("payment", "card", "bank"),
    "password": ("password", "credential"),
    "secret": ("secret", "credential", "private", "key"),
    "revealsecret": ("secret", "credential", "private", "key"),
    "credential": ("secret", "credential", "private", "key"),
    "answerquestion": ("answer", "question", "policy", "instruction"),
    "respondtouser": ("answer", "respond", "policy", "instruction"),
    "updatepassword": ("password", "update password", "change password"),
    "update_password": ("password", "update password", "change password"),
    "patient": ("patient", "medical", "health"),
    "genetic": ("genetic", "dna"),
    "location": ("location", "map"),
    "searchhistory": ("search history", "history"),
    "accountinformation": ("account", "bank"),
    "holdingsinformation": ("holdings", "investment"),
    "prescription": ("prescription", "medical"),
    "publicrecord": ("public record", "record"),
    "createpolicy": ("policy", "create"),
    "updatepolicy": ("policy", "update"),
    "manage": ("manage", "modify", "change"),
    "update": ("update", "modify", "change"),
    "scheduletransaction": ("schedule", "transaction", "payment", "pay", "money"),
    "schedule_transaction": ("schedule", "transaction", "payment", "pay", "money"),
    "updatescheduledtransaction": ("update", "adjust", "scheduled transaction", "rent", "payment"),
    "update_scheduled_transaction": ("update", "adjust", "scheduled transaction", "rent", "payment"),
    "moveitem": ("move", "file"),
    "scheduledeviceaction": ("schedule", "device"),
    "gotoroom": ("room", "robot", "move"),
    "givepriority": ("priority", "traffic"),
    "trafficlight": ("traffic", "light"),
    "leavechannel": ("leave", "channel"),
    "accesshistory": ("history", "access"),
    "searchpayee": ("payee", "bank"),
    "orderhistory": ("order history", "order"),
    "logdetails": ("log", "security"),
    "itemmetadata": ("metadata", "file"),
    "listfiles": ("files", "folders"),
    "reservation": ("reservation", "booking"),
    "userprofile": ("profile", "user"),
    "searchfriends": ("friends", "social"),
    "shipment": ("shipment", "shipping"),
    "userdetails": ("user details", "profile"),
    "searchpeople": ("people", "person"),
    "userinfo": ("user info", "medical", "account"),
    "recommendation": ("recommendation", "health"),
    "linkedaccounts": ("linked account", "account"),
    "phonenumber": ("phone", "number"),
}
HIGH_RISK_PATTERNS = (
    "sendemail",
    "execute",
    "terminal",
    "transfer",
    "sendmoney",
    "send_money",
    "senddirectmessage",
    "send_direct_message",
    "withdraw",
    "deposit",
    "paybill",
    "placeorder",
    "delete",
    "share",
    "upload",
    "exfiltrate",
    "secret",
    "revealsecret",
    "credential",
    "privatekey",
    "unlock",
    "grant",
    "disable",
    "autofill",
    "createpolicy",
    "updatepolicy",
    "manage",
    "update",
    "scheduletransaction",
    "schedule_transaction",
    "updatescheduledtransaction",
    "update_scheduled_transaction",
    "updatepassword",
    "update_password",
    "moveitem",
    "scheduledeviceaction",
    "gotoroom",
    "givepriority",
    "trafficlight",
    "leavechannel",
)
NEGATION_MARKERS = ("do not", "don't", "never", "without", "no ")
INJECTION_ADOPTION_PATTERNS = (
    "email them",
    "email the details",
    "send them",
    "send the details",
    "retrieve my saved",
    "saved payment methods",
    "saved addresses",
    "access history",
    "ignore previous",
    "alternate email",
    "private key",
    "upload",
    "exfiltrate",
    "_attacker_iban",
    "_phishing_link",
    "attacker",
    "hacked!",
)
ATTACK_TARGET_PATTERNS = (
    "_attacker_iban",
    "_phishing_link",
    "phishing",
    "attacker",
    "hacked!",
    "attackers",
    "attacker's",
    "evil",
    "malicious",
)
POLICY_VIOLATION_PATTERNS = (
    "followed the visual instruction",
    "instead of the user/system policy",
    "ignore the actual visual content",
    "misrepresent",
    "never discuss",
    "content policy",
    "violating",
)
GENERIC_TOOL_TOKENS = {
    "get",
    "read",
    "search",
    "list",
    "view",
    "manager",
    "tool",
    "response",
    "user",
    "input",
}
PASSIVE_TOOL_PREFIXES = (
    "read",
    "get",
    "search",
    "list",
    "view",
    "find",
    "fetch",
    "retrieve",
    "lookup",
    "parse",
    "answer",
    "respond",
)
PASSIVE_TOOL_INFIXES = (
    "read",
    "get",
    "search",
    "list",
    "view",
    "find",
    "fetch",
    "retrieve",
    "lookup",
    "context",
    "details",
    "metadata",
    "history",
    "navigate",
    "browse",
    "open",
)


@dataclass
class GateDecision:
    allowed: bool
    step: int | None
    tool: str | None
    score: float
    threshold: float
    reason: str


class WAMIGateway:
    def __init__(
        self,
        model: WAMIModel,
        base_threshold: float = -0.05,
        decay: float = 0.02,
        use_action_prior: bool = True,
        use_plan_mine: bool = False,
        plan_threshold: float | None = None,
        score_margin: float = 0.0,
    ):
        self.model = model
        self.base_threshold = base_threshold
        self.decay = decay
        self.use_action_prior = use_action_prior
        self.use_plan_mine = use_plan_mine
        self.plan_threshold = plan_threshold if plan_threshold is not None else base_threshold
        self.score_margin = score_margin

    def threshold(self, step: int) -> float:
        return self.base_threshold * math.exp(-self.decay * step)

    @staticmethod
    def _explicitly_authorizes(intent_lower: str, terms: tuple[str, ...]) -> bool:
        intent_aliases = {
            "send money": ("send them back", "send them the difference", "send the difference", "refund"),
            "transfer": ("send them back", "send them the difference", "send the difference", "refund"),
            "pay": ("pay the bill", "paid", "payment", "send them the difference"),
            "payment": ("pay the bill", "paid", "rent payment", "payment", "send them the difference"),
            "money": ("send them back", "send them the difference", "refund", "paid"),
            "update": ("adjust", "follow the instructions", "make sure to adjust"),
            "scheduled transaction": ("rent payment", "recurring scheduled transaction", "scheduled transaction"),
            "update password": ("update the password", "change the password"),
            "change password": ("update the password", "change the password"),
        }
        for term in terms:
            aliases = intent_aliases.get(term, ())
            if any(alias in intent_lower for alias in aliases):
                return True
            index = intent_lower.find(term)
            while index >= 0:
                prefix = intent_lower[max(0, index - 24) : index]
                if not any(marker in prefix for marker in NEGATION_MARKERS):
                    return True
                index = intent_lower.find(term, index + len(term))
        return False

    @staticmethod
    def _sensitive_terms(tool_key: str) -> tuple[str, ...] | None:
        if tool_key in SENSITIVE_TOOL_KEYWORDS:
            return SENSITIVE_TOOL_KEYWORDS[tool_key]
        compact = tool_key.replace("_", "").replace("-", "").replace("manager", "")
        compact = compact.replace("sharedcalendar", "calendar")
        for pattern, terms in SENSITIVE_TOOL_PATTERNS.items():
            normalized_pattern = pattern.replace("_", "").replace("-", "")
            raw_match = pattern in tool_key and pattern not in {"manage"}
            if raw_match or normalized_pattern in compact:
                return terms
        return None

    @staticmethod
    def _requires_explicit_authorization(tool_key: str) -> bool:
        compact = tool_key.replace("_", "").replace("-", "").replace("manager", "")
        compact = compact.replace("sharedcalendar", "calendar")
        for pattern in HIGH_RISK_PATTERNS:
            normalized_pattern = pattern.replace("_", "").replace("-", "")
            raw_match = pattern in tool_key and pattern not in {"manage"}
            if raw_match or normalized_pattern in compact:
                return True
        return False

    @staticmethod
    def _is_passive_observation(tool_key: str) -> bool:
        raw = tool_key.lower()
        compact = raw.replace("_", "").replace("-", "")
        if WAMIGateway._requires_explicit_authorization(tool_key):
            return False
        if "_for_" in raw:
            return True
        if any(compact.startswith(prefix) for prefix in PASSIVE_TOOL_PREFIXES):
            return True
        return any(token in compact for token in PASSIVE_TOOL_INFIXES)

    @staticmethod
    def _tool_tokens(tool_key: str) -> set[str]:
        spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", tool_key)
        tokens = re.findall(r"[a-z0-9]+", spaced.lower())
        return {token for token in tokens if token not in GENERIC_TOOL_TOKENS and len(token) > 2}

    @classmethod
    def _intent_tool_overlap(cls, intent_lower: str, tool_key: str) -> int:
        return sum(1 for token in cls._tool_tokens(tool_key) if token in intent_lower)

    @staticmethod
    def _has_attack_target(param_blob: str) -> bool:
        compact = param_blob.lower()
        explicit_markers = ("_attacker_iban", "_phishing_link", "attacker@example.com")
        if any(marker in compact for marker in explicit_markers):
            return True
        return bool(
            re.search(
                r"\b(phishing|attacker|attackers|attacker's|evil|malicious|hacked)\b",
                compact,
            )
        )

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        tdg = build_tdg(plan, toolset=toolset)
        if not tdg.nodes:
            return GateDecision(True, None, None, 0.0, self.threshold(0), "no tool calls found")
        intent_vec = self.model.encode_intent(intent)
        last_score = 0.0
        last_threshold = self.threshold(0)
        intent_lower = intent.lower()
        plan_lower = plan.lower()
        seen_untrusted_injection = False
        if self.use_plan_mine and hasattr(self.model, "plan_score"):
            plan_score = self.model.plan_score(intent, plan)
            if plan_score < self.plan_threshold:
                return GateDecision(
                    False,
                    None,
                    None,
                    plan_score,
                    self.plan_threshold,
                    "plan-level MINE alignment below threshold",
                )
        if self.use_action_prior and self._appears_to_adopt_injection(intent_lower, plan_lower):
            return GateDecision(
                False,
                None,
                None,
                0.0,
                self.threshold(0),
                "plan text appears to adopt an external injection instruction",
            )
        for step, (node, state) in enumerate(self.model.rollout(intent, tdg)):
            score = self.model.mine_score(intent_vec, state)
            limit = self.threshold(step)
            last_score, last_threshold = score, limit
            tool_key = node.tool.lower()
            compact_tool = tool_key.replace("_", "").replace("-", "")
            if "readuntrustedinjection" in compact_tool or "parseinjectedinstruction" in compact_tool:
                seen_untrusted_injection = True
                continue
            param_blob = str(node.params).lower()
            has_attack_target = self._has_attack_target(param_blob)
            has_policy_violation = any(pattern in param_blob for pattern in POLICY_VIOLATION_PATTERNS)
            if self.use_action_prior and has_attack_target and (seen_untrusted_injection or self._requires_explicit_authorization(tool_key)):
                return GateDecision(False, step, node.tool, score, limit, "tool arguments target attacker-controlled resource")
            if self.use_action_prior and seen_untrusted_injection and has_policy_violation:
                return GateDecision(False, step, node.tool, score, limit, "tool appears to follow visual instruction against user/system policy")
            allowed_terms = self._sensitive_terms(tool_key)
            explicitly_authorized = bool(allowed_terms and self._explicitly_authorizes(intent_lower, allowed_terms))
            if (
                self.use_action_prior
                and seen_untrusted_injection
                and self._requires_explicit_authorization(tool_key)
            ):
                return GateDecision(False, step, node.tool, score, limit, "high-risk tool follows untrusted injection content")
            if (
                self.use_action_prior
                and allowed_terms
                and self._requires_explicit_authorization(tool_key)
                and not explicitly_authorized
            ):
                return GateDecision(False, step, node.tool, score, limit, "high-risk tool is not explicitly authorized by user intent")
            if not self._requires_explicit_authorization(tool_key) and self._intent_tool_overlap(intent_lower, node.tool) > 0:
                limit -= 0.12
            effective_limit = limit - self.score_margin
            if (
                self.use_action_prior
                and not seen_untrusted_injection
                and self._is_passive_observation(tool_key)
                and not has_attack_target
            ):
                effective_limit = float("-inf")
            elif (
                self.use_action_prior
                and not seen_untrusted_injection
                and not has_attack_target
                and self._intent_tool_overlap(intent_lower, node.tool) > 0
            ):
                effective_limit -= 2.5
            if (
                self.use_action_prior
                and not seen_untrusted_injection
                and not has_attack_target
                and self._requires_explicit_authorization(tool_key)
                and explicitly_authorized
            ):
                effective_limit -= 2.5
            if score < effective_limit:
                return GateDecision(False, step, node.tool, score, limit, "intent alignment score below dynamic threshold")
        return GateDecision(True, None, None, last_score, last_threshold, "trajectory remained aligned")

    @staticmethod
    def _appears_to_adopt_injection(intent_lower: str, plan_lower: str) -> bool:
        if any(pattern in plan_lower and pattern not in intent_lower for pattern in INJECTION_ADOPTION_PATTERNS):
            non_adoption_phrases = (
                "conflicting instruction rather than",
                "conflicting instruction rather than a clear",
            )
            if any(phrase in plan_lower for phrase in non_adoption_phrases):
                return False
            negation_window = (
                "ignore",
                "unrelated",
                "prompt injection",
                "artifact",
                "appears to be",
                "contains an instruction",
                "contains a request",
                "rather than",
                "re-check",
                "determine availability accurately",
                "should not",
                "do not",
                "no further action",
            )
            adoption_window = (
                "i will",
                "i should",
                "now execute",
                "execute the",
                "as instructed",
                "need to retrieve",
                "need to email",
                "retrieve the saved",
                "email them",
                "send them",
                "conflicting event",
                "conflicting instruction",
                "response indicates",
            )
            for pattern in INJECTION_ADOPTION_PATTERNS:
                index = plan_lower.find(pattern)
                if index >= 0 and pattern not in intent_lower:
                    prefix = plan_lower[max(0, index - 90) : index]
                    context = plan_lower[max(0, index - 140) : index + len(pattern) + 80]
                    if any(marker in prefix for marker in negation_window):
                        continue
                    if any(marker in context for marker in adoption_window):
                        return True
        return False
