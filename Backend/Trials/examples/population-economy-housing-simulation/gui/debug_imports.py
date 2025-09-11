#!/usr/bin/env python3
"""Debug import issues with project management."""

import sys
import traceback

print("🔍 Debugging project management imports...")
print("=" * 50)

# Test individual imports
imports_to_test = [
    "project_management",
    "project_management.project_manager",
    "project_management.component_manager", 
    "project_management.informants_manager",
    "project_management.project_tree_widget"
]

for import_name in imports_to_test:
    try:
        __import__(import_name)
        print(f"✅ {import_name}")
    except ImportError as e:
        print(f"❌ {import_name}: {e}")
        traceback.print_exc()
        print()

# Test specific classes
print("\n🔍 Testing specific class imports...")
print("-" * 30)

try:
    from project_management.project_manager import ProjectManager, Project, SystemModel
    print("✅ ProjectManager, Project, SystemModel")
except ImportError as e:
    print(f"❌ ProjectManager classes: {e}")
    traceback.print_exc()

try:
    from project_management.project_tree_widget import ProjectTreeWidget
    print("✅ ProjectTreeWidget")
except ImportError as e:
    print(f"❌ ProjectTreeWidget: {e}")
    traceback.print_exc()

try:
    from project_management.component_manager import ComponentManager
    print("✅ ComponentManager")
except ImportError as e:
    print(f"❌ ComponentManager: {e}")
    traceback.print_exc()

try:
    from project_management.informants_manager import InformantsManager
    print("✅ InformantsManager")
except ImportError as e:
    print(f"❌ InformantsManager: {e}")
    traceback.print_exc()

print("\n✅ Import debugging complete!")
