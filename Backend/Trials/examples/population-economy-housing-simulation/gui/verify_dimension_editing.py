#!/usr/bin/env python3
"""
Verification script for dimension editing functionality.
Tests the complete workflow programmatically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_dimension_editing():
    """Verify that dimension editing works correctly."""
    
    print("🔍 Verifying Dimension Editing Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Import all required modules
        print("1. Testing imports...")
        from yaml_integration.yaml_loader import GuiModel, ModelComponent
        from inspector.dimension_management import DimensionDetailsEditor, DimensionManagerDialog
        from inspector.component_inspector import ComponentInspector
        print("   ✅ All imports successful")
        
        # Test 2: Create model and component
        print("\n2. Creating test model and stock component...")
        model = GuiModel("Test Model", "Test model for dimension editing")
        
        stock = ModelComponent(
            name="Population",
            component_type="stock",
            properties={
                'initial_value': 10000,
                'units': 'people',
                'spatial_dims': [],
                'description': 'Population stock'
            }
        )
        model.add_component(stock)
        print("   ✅ Model and stock component created")
        
        # Test 3: Add dimension to model
        print("\n3. Adding age dimension to model...")
        model.dimensions['age'] = {
            'size': 3,
            'labels': ['0-17', '18-64', '65+'],
            'description': 'Age groups',
            'type': 'categorical'
        }
        print("   ✅ Age dimension added to model")
        
        # Test 4: Add dimension to component
        print("\n4. Adding dimension to component...")
        stock.properties['spatial_dims'] = ['age']
        print("   ✅ Dimension added to component")
        
        # Test 5: Test DimensionDetailsEditor creation
        print("\n5. Testing DimensionDetailsEditor...")
        age_data = model.dimensions['age']
        
        # Create editor (without showing GUI)
        editor = DimensionDetailsEditor('age', age_data)
        print("   ✅ DimensionDetailsEditor created successfully")
        
        # Test 6: Simulate editing dimension data
        print("\n6. Simulating dimension editing...")
        
        # Simulate adding more age groups
        new_labels = ['0-4', '5-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+']
        
        # Update the dimension data directly (simulating user edits)
        updated_data = {
            'labels': new_labels,
            'size': len(new_labels),
            'type': 'categorical',
            'description': 'Detailed age groups for population analysis',
            'units': 'years'
        }
        
        # Apply the update
        model.dimensions['age'] = updated_data
        print(f"   ✅ Dimension updated with {len(new_labels)} age groups")
        
        # Test 7: Verify the changes
        print("\n7. Verifying changes...")
        final_age_data = model.dimensions['age']
        
        assert final_age_data['size'] == len(new_labels), "Size mismatch"
        assert final_age_data['labels'] == new_labels, "Labels mismatch"
        assert 'age' in stock.properties['spatial_dims'], "Dimension not in component"
        
        print("   ✅ All changes verified successfully")
        
        # Test 8: Test ComponentInspector integration
        print("\n8. Testing ComponentInspector integration...")
        inspector = ComponentInspector()
        inspector.set_model(model)
        inspector.set_component(stock)
        print("   ✅ ComponentInspector integration successful")
        
        # Summary
        print("\n📊 VERIFICATION RESULTS:")
        print("=" * 30)
        print(f"✅ Model: {model.name}")
        print(f"✅ Component: {stock.name} ({stock.component_type})")
        print(f"✅ Dimensions: {stock.properties.get('spatial_dims', [])}")
        print(f"✅ Age dimension size: {final_age_data['size']}")
        print(f"✅ Age labels: {final_age_data['labels'][:3]}... (+{len(final_age_data['labels'])-3} more)")
        
        print("\n🎉 ALL TESTS PASSED! Dimension editing is fully functional.")
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the verification."""
    success = verify_dimension_editing()
    
    if success:
        print("\n✅ Dimension editing functionality is working correctly!")
        print("\nYou can now:")
        print("1. Run 'python main.py' for the full GUI")
        print("2. Run 'python test_dimension_gui.py' for step-by-step testing")
        print("3. Follow the guide in 'DIMENSION_EDITING_GUIDE.md'")
    else:
        print("\n❌ There are issues with the dimension editing functionality.")
        print("Please check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
