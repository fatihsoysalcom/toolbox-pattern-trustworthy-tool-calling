import functools
import time

# --- 1. Define Tool Functions (the "tools" in the toolbox) ---
def process_data(data: dict) -> dict:
    """Simulates processing some data."""
    if not isinstance(data, dict) or "value" not in data:
        raise ValueError("Invalid data format for process_data: 'value' key missing or not a dict.")
    print(f"  [Tool] Processing data: {data['value']}")
    time.sleep(0.1) # Simulate work
    return {"processed_value": data["value"].upper(), "timestamp": time.time()}

def send_notification(message: str, recipient: str) -> bool:
    """Simulates sending a notification."""
    if not message or not recipient:
        raise ValueError("Message and recipient cannot be empty for send_notification.")
    print(f"  [Tool] Sending notification to {recipient}: '{message}'")
    time.sleep(0.05) # Simulate work
    return True

def log_event(event_name: str, details: dict) -> bool:
    """Simulates logging an event."""
    if not event_name:
        raise ValueError("Event name cannot be empty for log_event.")
    print(f"  [Tool] Logging event '{event_name}' with details: {details}")
    time.sleep(0.02) # Simulate work
    return True

# --- 2. Implement the Toolbox Pattern for Trustworthy Calling ---
class Toolbox:
    """
    Implements the Toolbox Pattern for trustworthy tool calling.
    Manages registration, authorization, validation, and error handling for tools.
    """
    def __init__(self, authorized_users: dict):
        self._tools = {}
        self._authorized_users = authorized_users # User permissions for tools

    def register_tool(self, name: str, func, required_permissions: list = None):
        """Registers a tool with optional required permissions."""
        if not callable(func):
            raise TypeError(f"Tool '{name}' must be a callable function.")
        self._tools[name] = {
            "func": func,
            "permissions": required_permissions if required_permissions is not None else []
        }
        print(f"[Toolbox] Registered tool: '{name}' with permissions: {self._tools[name]['permissions']}")

    def _check_authorization(self, user_id: str, tool_name: str) -> bool:
        """
        Ensures the calling user has the necessary permissions for the tool.
        This is a core aspect of 'trustworthy tool calling' by preventing unauthorized access.
        """
        if user_id not in self._authorized_users:
            print(f"  [Auth] User '{user_id}' is unknown.")
            return False

        tool_permissions = self._tools[tool_name]["permissions"]
        user_roles = self._authorized_users[user_id].get("roles", [])

        if not tool_permissions: # No specific permissions required for this tool
            return True

        # Check if user has at least one required permission
        if any(perm in user_roles for perm in tool_permissions):
            print(f"  [Auth] User '{user_id}' authorized for '{tool_name}'.")
            return True
        else:
            print(f"  [Auth] User '{user_id}' NOT authorized for '{tool_name}'. Required: {tool_permissions}, User roles: {user_roles}")
            return False

    def call_tool(self, user_id: str, tool_name: str, *args, **kwargs):
        """
        Calls a registered tool after performing authorization, validation, and error handling.
        This method embodies the 'trustworthy' aspect by centralizing control and reliability checks.
        """
        print(f"\n[Toolbox] Attempting to call tool '{tool_name}' by user '{user_id}'...")

        if tool_name not in self._tools:
            print(f"  [Error] Tool '{tool_name}' not found in the toolbox.")
            return {"status": "error", "message": f"Tool '{tool_name}' not found.", "user": user_id}

        # 1. Authorization Check: Crucial for security in distributed systems.
        if not self._check_authorization(user_id, tool_name):
            return {"status": "error", "message": "Unauthorized access to tool.", "user": user_id}

        tool_func = self._tools[tool_name]["func"]

        try:
            # 2. Input Validation: Handled by the tool functions themselves, caught here.
            #    Ensures tools receive valid data, preventing crashes or incorrect operations.
            print(f"  [Call] Executing tool '{tool_name}'...")
            result = tool_func(*args, **kwargs)
            print(f"  [Call] Tool '{tool_name}' executed successfully.")
            return {"status": "success", "result": result, "user": user_id}
        except Exception as e:
            # 3. Robust Error Handling: Catches and manages exceptions from tool execution.
            #    Prevents a single tool failure from cascading and crashing the entire system.
            print(f"  [Error] An error occurred during tool '{tool_name}' execution: {e}")
            return {"status": "error", "message": str(e), "user": user_id}

# --- 3. Example Usage ---
if __name__ == "__main__":
    # Define authorized users and their roles/permissions
    users = {
        "admin_user": {"roles": ["admin", "data_processor", "notifier", "logger"]},
        "data_analyst": {"roles": ["data_processor", "logger"]},
        "guest_user": {"roles": []}
    }

    # Initialize the Toolbox
    my_toolbox = Toolbox(users)

    # Register tools with their required permissions
    my_toolbox.register_tool("process_data", process_data, ["data_processor"])
    my_toolbox.register_tool("send_notification", send_notification, ["notifier"])
    my_toolbox.register_tool("log_event", log_event) # No specific permissions, anyone can log

    print("\n--- Demonstrating Trustworthy Tool Calling ---")

    # Scenario 1: Authorized user, valid call
    print("\n--- Scenario 1: Admin user processing data (authorized, valid) ---")
    response = my_toolbox.call_tool("admin_user", "process_data", {"value": "raw_data_123"})
    print(f"Full Response: {response}")

    # Scenario 2: Unauthorized user attempting to process data
    print("\n--- Scenario 2: Guest user processing data (unauthorized) ---")
    response = my_toolbox.call_tool("guest_user", "process_data", {"value": "sensitive_data"})
    print(f"Full Response: {response}")

    # Scenario 3: Authorized user, but not for this specific tool
    print("\n--- Scenario 3: Data analyst sending notification (unauthorized for 'notifier' role) ---")
    response = my_toolbox.call_tool("data_analyst", "send_notification", "Urgent alert!", "ops@example.com")
    print(f"Full Response: {response}")

    # Scenario 4: Authorized user, valid call to a tool without specific permissions
    print("\n--- Scenario 4: Data analyst logging an event (authorized, no specific role needed) ---")
    response = my_toolbox.call_tool("data_analyst", "log_event", "UserActivity", {"user": "data_analyst", "action": "view_report"})
    print(f"Full Response: {response}")

    # Scenario 5: Authorized user, invalid input for a tool (error handling from tool's validation)
    print("\n--- Scenario 5: Admin user sending notification with missing recipient (error handling) ---")
    response = my_toolbox.call_tool("admin_user", "send_notification", "System update!", "") # Missing recipient
    print(f"Full Response: {response}")

    # Scenario 6: Calling a non-existent tool
    print("\n--- Scenario 6: Admin user calling a non-existent tool ---")
    response = my_toolbox.call_tool("admin_user", "non_existent_tool")
    print(f"Full Response: {response}")
