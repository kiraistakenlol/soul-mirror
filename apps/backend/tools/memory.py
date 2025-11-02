# Core memory management tool
from repository.memory import MemoryRepository

class MemoryManager:
    def __init__(self):
        self.repo = MemoryRepository()

    def update_core_memory(self, user_id: str, new_content: str) -> str:
        """Update core memory with important information"""
        print(f"    🔧 update_core_memory(user={user_id})")
        print(f"    ↳ New content: {new_content[:100]}...")
        self.repo.update_memory(user_id, new_content)
        return f"Core memory updated"

    def get_core_memory(self, user_id: str) -> str:
        """Get current core memory content"""
        return self.repo.get_memory(user_id) or ""

    def clear_core_memory(self, user_id: str) -> bool:
        """Clear all core memory"""
        print(f"    🔧 clear_core_memory(user={user_id})")
        result = self.repo.clear_memory(user_id)
        print(f"    ↳ {'Cleared' if result else 'Nothing to clear'}")
        return result


# Global memory manager instance
memory_manager = MemoryManager()
