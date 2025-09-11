#!/usr/bin/env python3
"""
Verification script for enhanced dimension management features in main GUI.
"""

import sys
from pathlib import Path

def verify_enhanced_features():
    """Verify that all enhanced features are properly integrated."""

    print("🔍 Enhanced Features Verification")
    print("=" * 50)

    # Create QApplication for GUI tests
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    results = {}
    
    # Test 1: Import verification
    print("1. Testing imports...")
    try:
        from inspector.spreadsheet_editor import SpreadsheetDataEditor, EnhancedDimensionSelector, DimensionFiltersWidget
        from inspector.dimension_management import AddDimensionDialog, DraggableDimensionItem, DropZone
        results['imports'] = True
        print("   ✅ All enhanced classes import successfully")
    except ImportError as e:
        results['imports'] = False
        print(f"   ❌ Import error: {e}")
    
    # Test 2: YAML model loading
    print("2. Testing YAML model loading...")
    try:
        from yaml_integration.yaml_loader import YAMLModelLoader

        model_path = "../population-dynamics/model_structure.yaml"
        scenario_path = "../population-dynamics/scenario_parameters.yaml"

        if Path(model_path).exists():
            loader = YAMLModelLoader()
            gui_model, sd_model = loader.load_model_from_file(model_path, scenario_path)
            results['yaml_loading'] = True
            print(f"   ✅ YAML model loaded: {len(gui_model.dimensions)} dimensions, {len(gui_model.components)} components")
        else:
            results['yaml_loading'] = False
            print(f"   ❌ YAML model file not found: {model_path}")

    except Exception as e:
        results['yaml_loading'] = False
        print(f"   ❌ YAML loading error: {e}")
    
    # Test 3: Enhanced editor creation
    print("3. Testing enhanced editor creation...")
    try:
        if results.get('imports') and results.get('yaml_loading'):
            from yaml_integration.yaml_loader import ModelComponent
            
            # Create test component
            component = ModelComponent(
                name="test_component",
                component_type="stock",
                properties={
                    'spatial_dims': ['age_group', 'income_bracket'],
                    'initial_value': 1000,
                    'units': 'people'
                }
            )
            
            # Create enhanced editor
            editor = SpreadsheetDataEditor([component], gui_model)
            
            # Check enhanced features
            has_add_button = hasattr(editor.dimension_selector, 'add_dimension_btn')
            has_drop_zones = hasattr(editor.dimension_selector, 'x_axis_zone') and hasattr(editor.dimension_selector, 'y_axis_zone')
            has_filters = hasattr(editor, 'dimension_filters')
            
            if has_add_button and has_drop_zones and has_filters:
                results['enhanced_editor'] = True
                print("   ✅ Enhanced editor created with all features")
            else:
                results['enhanced_editor'] = False
                print(f"   ❌ Enhanced editor missing features: add_button={has_add_button}, drop_zones={has_drop_zones}, filters={has_filters}")
                
            editor.close()
            
        else:
            results['enhanced_editor'] = False
            print("   ❌ Cannot test enhanced editor - dependencies failed")
            
    except Exception as e:
        results['enhanced_editor'] = False
        print(f"   ❌ Enhanced editor error: {e}")
    
    # Test 4: Graphics item integration
    print("4. Testing graphics item integration...")
    try:
        from canvas.graphics_items import StockItem
        from yaml_integration.yaml_loader import ModelComponent
        
        component = ModelComponent("test_stock", "stock", {'initial_value': 100})
        stock_item = StockItem(component)
        
        # Check if it has the enhanced editor method
        has_editor_method = hasattr(stock_item, 'open_multidimensional_editor')
        
        if has_editor_method:
            results['graphics_integration'] = True
            print("   ✅ Graphics items have enhanced editor integration")
        else:
            results['graphics_integration'] = False
            print("   ❌ Graphics items missing enhanced editor method")
            
    except Exception as e:
        results['graphics_integration'] = False
        print(f"   ❌ Graphics integration error: {e}")
    
    # Test 5: Component inspector integration
    print("5. Testing component inspector integration...")
    try:
        from inspector.component_inspector import ComponentInspector
        
        # Check if it has the enhanced editor method
        inspector = ComponentInspector()
        has_editor_method = hasattr(inspector, 'open_spreadsheet_editor')
        
        if has_editor_method:
            results['inspector_integration'] = True
            print("   ✅ Component inspector has enhanced editor integration")
        else:
            results['inspector_integration'] = False
            print("   ❌ Component inspector missing enhanced editor method")
            
    except Exception as e:
        results['inspector_integration'] = False
        print(f"   ❌ Inspector integration error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("Enhanced dimension management features are properly integrated!")
        print("\nTo use in main GUI:")
        print("1. Run: python main.py")
        print("2. Load a YAML model with dimensions")
        print("3. Double-click any component")
        print("4. Enhanced spreadsheet editor should open with:")
        print("   • Add Dimension button")
        print("   • Drag-and-drop dimension assignment")
        print("   • Dimension filters for extra dimensions")
        print("   • Proper row/column table structure")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} TESTS FAILED!")
        print("Some enhanced features may not work properly in main GUI.")
        print("Check the error messages above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = verify_enhanced_features()
    sys.exit(0 if success else 1)
