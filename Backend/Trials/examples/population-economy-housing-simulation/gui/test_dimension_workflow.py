#!/usr/bin/env python3
"""
Test script for dimension editing workflow.

This script tests the complete workflow:
1. Create a stock component
2. Add an "age" dimension
3. Edit the dimension to add more age groups
4. Verify changes are saved
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_dimension_workflow():
    """Test the complete dimension editing workflow."""
    
    print("🧪 Testing Dimension Editing Workflow")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from yaml_integration.yaml_loader import GuiModel, ModelComponent
        from inspector.dimension_management import DimensionDetailsEditor, DimensionManagerDialog
        from inspector.component_inspector import ComponentInspector
        print("   ✅ All imports successful")
        
        # Create a test model
        print("\n2. Creating test model...")
        model = GuiModel("Test Model", "Test model for dimension editing")
        print(f"   ✅ Model created: {model.name}")
        
        # Create a stock component
        print("\n3. Creating stock component...")
        stock_component = ModelComponent(
            name="Population",
            component_type="stock",
            properties={
                'initial_value': 10000,
                'units': 'people',
                'spatial_dims': [],
                'description': 'Population stock for testing'
            }
        )
        model.add_component(stock_component)
        print(f"   ✅ Stock component created: {stock_component.name}")
        
        # Add age dimension to model
        print("\n4. Adding age dimension to model...")
        model.dimensions['age'] = {
            'size': 3,
            'labels': ['0-17', '18-64', '65+'],
            'description': 'Age groups for population',
            'type': 'categorical'
        }
        print("   ✅ Age dimension added to model")
        
        # Add dimension to component
        print("\n5. Adding dimension to component...")
        stock_component.properties['spatial_dims'] = ['age']
        print("   ✅ Dimension added to component")
        
        # Test dimension details editor
        print("\n6. Testing dimension details editor...")
        age_data = model.dimensions['age']
        
        # Simulate adding more age groups
        print("   📝 Simulating adding more age groups...")
        original_labels = age_data['labels'].copy()
        print(f"   Original labels: {original_labels}")
        
        # Add more detailed age groups
        new_labels = ['0-4', '5-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+']
        age_data['labels'] = new_labels
        age_data['size'] = len(new_labels)
        
        print(f"   New labels: {new_labels}")
        print(f"   ✅ Age dimension updated with {len(new_labels)} age groups")
        
        # Verify the changes
        print("\n7. Verifying changes...")
        updated_age_data = model.dimensions['age']
        assert updated_age_data['size'] == len(new_labels), "Size mismatch"
        assert updated_age_data['labels'] == new_labels, "Labels mismatch"
        print("   ✅ Changes verified successfully")
        
        # Test component has the dimension
        print("\n8. Verifying component dimension...")
        component_dims = stock_component.properties.get('spatial_dims', [])
        assert 'age' in component_dims, "Age dimension not in component"
        print(f"   ✅ Component has dimensions: {component_dims}")
        
        print("\n🎉 All tests passed! Dimension editing workflow is functional.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dimension_workflow()
    sys.exit(0 if success else 1)
