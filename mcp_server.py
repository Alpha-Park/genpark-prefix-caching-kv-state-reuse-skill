"""
MCP Server for Prefix Caching KV State Reuse Skill.
"""

import json
import sys
from client import PrefixCacheSimulator

SIMULATOR = PrefixCacheSimulator()


def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "insert_prefix",
                    "description": "Insert system prompt or template prefix into the radix cache",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "kv_cache_id": {"type": "string"}
                        },
                        "required": ["prompt", "kv_cache_id"]
                    }
                },
                {
                    "name": "lookup_prompt",
                    "description": "Check prefix cache hit and compute TTFT latency reduction",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "insert_prefix":
            SIMULATOR.insert_prefix(args["prompt"], args["kv_cache_id"])
            return {"content": [{"type": "text", "text": json.dumps({"status": "prefix_cached"})}]}

        elif tool_name == "lookup_prompt":
            res = SIMULATOR.lookup_prompt(args["prompt"])
            return {"content": [{"type": "text", "text": json.dumps(res)}]}

        return {"error": f"Unknown tool: {tool_name}"}

    return {"error": f"Unknown method: {method}"}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            resp["id"] = req.get("id")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
