"""
Prefix Caching KV State Reuse Skill Client
Pure Python Standard Library implementation of Radix Tree Prefix Caching (vLLM / SGLang).
Indexes common system prompts, tool schemas, and few-shot examples in a token prefix tree
to simulate KV-cache state reuse and calculate time-to-first-token (TTFT) latency reductions.
"""

from typing import List, Dict, Any, Tuple, Optional


class RadixNode:
    """Node in token prefix radix tree."""
    def __init__(self, token_seq: Tuple[str, ...]):
        self.token_seq = token_seq
        self.children: Dict[str, 'RadixNode'] = {}
        self.kv_cache_id: Optional[str] = None
        self.hit_count: int = 0


class PrefixCacheSimulator:
    """
    Radix tree prefix cache managing cached KV-states.
    """

    def __init__(self):
        self.root = RadixNode(token_seq=())
        self.total_tokens_requested = 0
        self.total_cached_tokens_hit = 0
        self.cache_entries = 0

    def insert_prefix(self, prompt: str, kv_cache_id: str):
        """Insert prompt tokens into radix tree."""
        tokens = tuple(prompt.split())
        curr = self.root

        i = 0
        while i < len(tokens):
            first_tok = tokens[i]
            if first_tok not in curr.children:
                # Add child
                child = RadixNode(token_seq=tokens[i:])
                child.kv_cache_id = kv_cache_id
                curr.children[first_tok] = child
                self.cache_entries += 1
                return
            else:
                child = curr.children[first_tok]
                edge_tokens = child.token_seq
                # Find common prefix length
                common = 0
                while common < len(edge_tokens) and i + common < len(tokens) and edge_tokens[common] == tokens[i + common]:
                    common += 1

                if common == len(edge_tokens):
                    # Exact edge match, move down
                    curr = child
                    i += common
                else:
                    # Split edge
                    split_node = RadixNode(token_seq=edge_tokens[:common])
                    split_node.children[edge_tokens[common]] = child
                    child.token_seq = edge_tokens[common:]

                    curr.children[first_tok] = split_node

                    if i + common < len(tokens):
                        new_child = RadixNode(token_seq=tokens[i + common:])
                        new_child.kv_cache_id = kv_cache_id
                        split_node.children[tokens[i + common]] = new_child
                    else:
                        split_node.kv_cache_id = kv_cache_id

                    self.cache_entries += 1
                    return

    def lookup_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Lookup prompt in radix tree and compute longest cached prefix.
        """
        tokens = tuple(prompt.split())
        curr = self.root
        matched_tokens = 0
        i = 0

        while i < len(tokens) and tokens[i] in curr.children:
            child = curr.children[tokens[i]]
            edge_tokens = child.token_seq
            common = 0
            while common < len(edge_tokens) and i + common < len(tokens) and edge_tokens[common] == tokens[i + common]:
                common += 1

            matched_tokens += common
            child.hit_count += 1
            if common == len(edge_tokens):
                curr = child
                i += common
            else:
                break

        total_req = len(tokens)
        self.total_tokens_requested += total_req
        self.total_cached_tokens_hit += matched_tokens

        hit_ratio = matched_tokens / total_req if total_req > 0 else 0.0
        ttft_reduction = hit_ratio * 0.85  # Cached prefix reduces TTFT by up to 85%

        return {
            "total_tokens": total_req,
            "cached_tokens": matched_tokens,
            "hit_ratio": round(hit_ratio, 3),
            "estimated_ttft_reduction": f"{ttft_reduction * 100:.1f}%",
            "is_full_cache_hit": matched_tokens == total_req
        }
