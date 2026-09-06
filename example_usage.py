"""
Example usage of Prefix Caching KV State Reuse Skill.
"""

from client import PrefixCacheSimulator


def main():
    print("=== Prefix Caching KV State Reuse Demonstration ===")
    sim = PrefixCacheSimulator()

    # Pre-cache system prompt and tool definitions
    system_prompt = "You are an autonomous AI software engineer agent capable of using bash, python, and git."
    sim.insert_prefix(system_prompt, kv_cache_id="sys_kv_001")

    # Query 1: Identical prefix + unique user instruction
    user_query_1 = "You are an autonomous AI software engineer agent capable of using bash, python, and git. Please write a test."
    res1 = sim.lookup_prompt(user_query_1)
    print("Query 1 Lookup:")
    print(f"  Total Tokens:  {res1['total_tokens']}")
    print(f"  Cached Tokens: {res1['cached_tokens']}")
    print(f"  Hit Ratio:     {res1['hit_ratio'] * 100:.1f}%")
    print(f"  TTFT Savings:  {res1['estimated_ttft_reduction']}")

    # Query 2: Completely new prompt
    user_query_2 = "What is the weather today in Tokyo?"
    res2 = sim.lookup_prompt(user_query_2)
    print("\nQuery 2 Lookup (Cold Start):")
    print(f"  Total Tokens:  {res2['total_tokens']}")
    print(f"  Cached Tokens: {res2['cached_tokens']}")
    print(f"  Hit Ratio:     {res2['hit_ratio'] * 100:.1f}%")


if __name__ == "__main__":
    main()
