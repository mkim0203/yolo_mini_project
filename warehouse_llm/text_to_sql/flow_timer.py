import time
from contextlib import contextmanager
from langchain_core.callbacks import BaseCallbackHandler


class FlowTimer(BaseCallbackHandler):
    def __init__(self):
        self.t0 = time.perf_counter()
        self._open = {}       # run_id -> (이름, 시작시각, 부가정보)
        self.steps = []

    # ---------- 내부 유틸 ----------
    def _start(self, run_id, name, extra=None):
        self._open[run_id] = (name, time.perf_counter(), extra or {})

    def _end(self, run_id, extra=None):
        item = self._open.pop(run_id, None)
        if not item:
            return
        name, st, base = item
        now = time.perf_counter()
        self.steps.append({
            "step": name,
            "start_ms": int((st - self.t0) * 1000),
            "duration_ms": int((now - st) * 1000),
            **base, **(extra or {}),
        })

    @contextmanager
    def stage(self, name):
        """LLM/Tool이 아닌 구간(룰·스키마 조회 등)을 직접 측정"""
        st = time.perf_counter()
        try:
            yield
        finally:
            self.steps.append({
                "step": f"STAGE {name}",
                "start_ms": int((st - self.t0) * 1000),
                "duration_ms": int((time.perf_counter() - st) * 1000),
            })

    # ---------- LLM ----------
    def on_chat_model_start(self, serialized, messages, *, run_id, tags=None, **kw):
        self._start(run_id, f"LLM[{(tags or ['llm'])[0]}]")

    def on_llm_start(self, serialized, prompts, *, run_id, tags=None, **kw):
        self._start(run_id, f"LLM[{(tags or ['llm'])[0]}]")

    def on_llm_end(self, response, *, run_id, **kw):
        extra = {}
        try:
            msg = response.generations[0][0].message
            u = msg.usage_metadata or {}
            extra = {"in": u.get("input_tokens"), "out": u.get("output_tokens")}
            if getattr(msg, "tool_calls", None):
                extra["next"] = "tool: " + ",".join(tc["name"] for tc in msg.tool_calls)
        except Exception:
            pass
        self._end(run_id, extra)

    def on_llm_error(self, error, *, run_id, **kw):
        self._end(run_id, {"error": str(error)[:100]})

    # ---------- Tool ----------
    def on_tool_start(self, serialized, input_str, *, run_id, **kw):
        self._start(run_id, f"TOOL {serialized.get('name')}", {"input": str(input_str)[:200]})

    def on_tool_end(self, output, *, run_id, **kw):
        self._end(run_id)

    def on_tool_error(self, error, *, run_id, **kw):
        self._end(run_id, {"error": str(error)[:100]})

    # ---------- 출력 ----------
    def report(self, session_id="", route="") -> str:
        total = int((time.perf_counter() - self.t0) * 1000)
        lines = [f"[flow] session={session_id} route={route} total={total}ms"]
        for s in sorted(self.steps, key=lambda x: x["start_ms"]):
            detail = "  ".join(f"{k}={v}" for k, v in s.items()
                if k not in ("step", "start_ms", "duration_ms") and v is not None)
            lines.append(f"  {s['start_ms']:>6}ms +{s['duration_ms']:>5}ms  {s['step']:<22} {detail}")
        return "\n".join(lines)