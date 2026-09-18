"""LRU Cache: O(1) Least Recently Used Cache using Doubly Linked List and Hash Map.

Implements constant time get and put operations, capacity eviction governance,
hit and miss telemetry tracking, and cache order inspection.
"""

import sys
from typing import Any, Dict, List, Optional, Tuple


class Node:
    """Doubly-linked list node holding key, value, and neighbor pointers."""

    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None


class LRUCache:
    """Least Recently Used (LRU) Cache with O(1) get and put operations."""

    def __init__(self, capacity: int = 4):
        if capacity <= 0:
            raise ValueError("Cache capacity must be a positive integer.")
        self.capacity = capacity
        self.cache: Dict[Any, Node] = {}

        # Sentinel dummy nodes
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

        # Telemetry metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _remove(self, node: Node) -> None:
        """Unlink node from doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        if prev_node and next_node:
            prev_node.next = next_node
            next_node.prev = prev_node

    def _add_to_head(self, node: Node) -> None:
        """Insert node right after head sentinel (MRU position)."""
        node.next = self.head.next
        node.prev = self.head
        if self.head.next:
            self.head.next.prev = node
        self.head.next = node

    def get(self, key: Any) -> Optional[Any]:
        """Retrieve value for key and mark as most recently used."""
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_head(node)
            self.hits += 1
            return node.value
        self.misses += 1
        return None

    def put(self, key: Any, value: Any) -> Optional[Tuple[Any, Any]]:
        """Insert or update key-value pair. Returns (evicted_key, evicted_val) if eviction occurs."""
        evicted = None
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                # Evict LRU node right before tail sentinel
                lru_node = self.tail.prev
                if lru_node and lru_node != self.head:
                    self._remove(lru_node)
                    del self.cache[lru_node.key]
                    self.evictions += 1
                    evicted = (lru_node.key, lru_node.value)

            new_node = Node(key, value)
            self._add_to_head(new_node)
            self.cache[key] = new_node

        return evicted

    def delete(self, key: Any) -> bool:
        """Explicitly remove an entry from cache."""
        if key in self.cache:
            node = self.cache.pop(key)
            self._remove(node)
            return True
        return False

    def get_order(self) -> List[Tuple[Any, Any]]:
        """Return list of (key, value) pairs from MRU to LRU."""
        items = []
        curr = self.head.next
        while curr and curr != self.tail:
            items.append((curr.key, curr.value))
            curr = curr.next
        return items

    def get_stats(self) -> Dict[str, Any]:
        """Return performance statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100.0) if total_requests > 0 else 0.0
        return {
            "capacity": self.capacity,
            "current_size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "evictions": self.evictions,
        }


def run_tests() -> bool:
    """Automated tests checking LRU order, eviction, and cache hits."""
    cache = LRUCache(capacity=3)

    # Initial puts
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert cache.get_order() == [("c", 3), ("b", 2), ("a", 1)]

    # Access "a" -> "a" moves to head (MRU)
    val = cache.get("a")
    assert val == 1
    assert cache.get_order() == [("a", 1), ("c", 3), ("b", 2)]

    # Put "d" -> capacity exceeded, "b" (LRU) must be evicted
    evicted = cache.put("d", 4)
    assert evicted == ("b", 2)
    assert cache.get("b") is None  # Miss
    assert cache.get_order() == [("d", 4), ("a", 1), ("c", 3)]

    # Test update existing
    cache.put("a", 99)
    assert cache.get("a") == 99
    assert cache.get_order() == [("a", 99), ("d", 4), ("c", 3)]

    # Test deletion
    assert cache.delete("d") is True
    assert cache.get("d") is None
    assert len(cache.cache) == 2

    # Verify telemetry
    stats = cache.get_stats()
    assert stats["hits"] >= 2
    assert stats["misses"] >= 2
    assert stats["evictions"] == 1

    print("All LRU cache test assertions passed successfully.")
    return True


def display_cache_state(cache: LRUCache) -> None:
    """Display visual representation of the doubly linked list and metrics."""
    items = cache.get_order()
    stats = cache.get_stats()

    print("\n" + "=" * 60)
    print("                    LRU Cache State Inspection                 ")
    print("=" * 60)
    print(f"Capacity: {stats['capacity']} | Size: {stats['current_size']} | Evictions: {stats['evictions']}")
    print(f"Hits: {stats['hits']} | Misses: {stats['misses']} | Hit Rate: {stats['hit_rate_percent']}%")
    print("-" * 60)
    if not items:
        print("Cache is currently empty.")
    else:
        print("Order (Most Recently Used -> Least Recently Used):")
        chain_repr = " [HEAD/MRU] "
        for idx, (k, v) in enumerate(items):
            chain_repr += f"-> [{k}: {v}] "
        chain_repr += "-> [TAIL/LRU]"
        print(chain_repr)
    print("=" * 60)


def main() -> None:
    """CLI interactive simulator for LRUCache."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        cap_input = input("Enter cache capacity (default 4): ").strip()
        cap = int(cap_input) if cap_input else 4
    except ValueError:
        cap = 4

    cache = LRUCache(capacity=cap)

    while True:
        print("\n================================")
        print("     LRU Cache Simulator        ")
        print("================================")
        print("1. Put (Insert / Update key-value)")
        print("2. Get (Retrieve value by key)")
        print("3. Delete key")
        print("4. Inspect Cache State & Telemetry")
        print("5. Run Automated Self-Tests")
        print("6. Exit")

        choice = input("\nSelect an option (1-6): ").strip()
        if choice == "1":
            key = input("Enter key: ").strip()
            val = input("Enter value: ").strip()
            if not key:
                print("Key cannot be empty.")
                continue
            evicted = cache.put(key, val)
            if evicted:
                print(f"Inserted ({key}: {val}). Evicted least recently used entry: {evicted[0]} -> {evicted[1]}")
            else:
                print(f"Inserted / Updated ({key}: {val}).")
            display_cache_state(cache)

        elif choice == "2":
            key = input("Enter key to retrieve: ").strip()
            res = cache.get(key)
            if res is not None:
                print(f"Cache Hit: {key} => {res}")
            else:
                print(f"Cache Miss: key '{key}' not present in cache.")
            display_cache_state(cache)

        elif choice == "3":
            key = input("Enter key to delete: ").strip()
            if cache.delete(key):
                print(f"Key '{key}' successfully deleted.")
            else:
                print(f"Key '{key}' was not found.")

        elif choice == "4":
            display_cache_state(cache)

        elif choice == "5":
            run_tests()

        elif choice == "6":
            print("Exiting LRU Cache Simulator. Goodbye.")
            break
        else:
            print("Invalid option. Please choose from 1 to 6.")


if __name__ == "__main__":
    main()
