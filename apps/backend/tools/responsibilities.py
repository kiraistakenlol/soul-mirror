# Responsibilities management tool
from repository.responsibilities import ResponsibilitiesRepository
from typing import Optional

class ResponsibilitiesManager:
    def __init__(self):
        self.repo = ResponsibilitiesRepository()

    def list_responsibilities(self, user_id: str) -> str:
        """List all responsibilities"""
        print(f"    🔧 list_responsibilities(user={user_id})")
        responsibilities = self.repo.get_all_responsibilities(user_id)

        if not responsibilities:
            print(f"    ↳ No responsibilities found")
            return "No responsibilities found."

        result = []
        for resp in responsibilities:
            result.append(
                f"- [{resp['id']}] {resp['title']}\n"
                f"  Description: {resp['description']}\n"
                f"  Created: {resp['created_at']}, Updated: {resp['updated_at']}"
            )

        print(f"    ↳ Found {len(responsibilities)} responsibilities")
        return "\n\n".join(result)

    def add_responsibility(self, user_id: str, title: str, description: str) -> str:
        """Create a new responsibility"""
        print(f"    🔧 add_responsibility(user={user_id}, title=\"{title}\")")
        responsibility_id = self.repo.create_responsibility(user_id, title, description)
        print(f"    ↳ Created responsibility [{responsibility_id}]")
        return f"Created responsibility [{responsibility_id}]: {title}"

    def update_responsibility(self, user_id: str, responsibility_id: int,
                            title: Optional[str] = None,
                            description: Optional[str] = None) -> str:
        """Update an existing responsibility"""
        print(f"    🔧 update_responsibility(user={user_id}, id={responsibility_id})")
        if self.repo.update_responsibility(user_id, responsibility_id, title, description):
            print(f"    ↳ Updated responsibility [{responsibility_id}]")
            return f"Updated responsibility [{responsibility_id}]"
        print(f"    ↳ Responsibility not found")
        return f"Responsibility {responsibility_id} not found."

    def remove_responsibility(self, user_id: str, responsibility_id: int) -> str:
        """Remove a responsibility"""
        print(f"    🔧 remove_responsibility(user={user_id}, id={responsibility_id})")
        if self.repo.delete_responsibility(user_id, responsibility_id):
            print(f"    ↳ Removed responsibility [{responsibility_id}]")
            return f"Removed responsibility [{responsibility_id}]"
        print(f"    ↳ Responsibility not found")
        return f"Responsibility {responsibility_id} not found."


# Global responsibilities manager instance
responsibilities_manager = ResponsibilitiesManager()
