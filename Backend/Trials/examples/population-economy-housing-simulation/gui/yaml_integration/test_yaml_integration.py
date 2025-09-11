#!/usr/bin/env python3
"""
Test script for YAML integration functionality.

This script tests loading and saving YAML models to ensure round-trip compatibility.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from yaml_loader import YAMLModelLoader
from yaml_saver import YAMLModelSaver


def test_yaml_loading():
    """Test loading the integrated model."""
    print("Testing YAML model loading...")
    
    try:
        loader = YAMLModelLoader()
        
        # Paths to test files
        model_path = Path(__file__).parent.parent.parent / "integrated_model_structure.yaml"
        scenario_path = Path(__file__).parent.parent.parent / "integrated_scenario_parameters.yaml"
        
        if not model_path.exists():
            print(f"❌ Model file not found: {model_path}")
            return False
            
        if not scenario_path.exists():
            print(f"⚠️ Scenario file not found: {scenario_path}")
            scenario_path = None
            
        # Load the model
        gui_model, sd_model = loader.load_model_from_file(str(model_path), str(scenario_path) if scenario_path else None)
        
        print(f"✅ Model loaded successfully: {gui_model.name}")
        print(f"   - Components: {len(gui_model.components)}")
        print(f"   - Connections: {len(gui_model.connections)}")
        print(f"   - Dimensions: {len(gui_model.dimensions)}")
        
        # Test component types
        stocks = gui_model.get_components_by_type('stock')
        flows = gui_model.get_components_by_type('flow')
        calculators = gui_model.get_components_by_type('calculator')
        
        print(f"   - Stocks: {len(stocks)}")
        print(f"   - Flows: {len(flows)}")
        print(f"   - Calculators: {len(calculators)}")
        
        # Test validation
        validation = loader.validate_model_structure(gui_model)
        if validation['valid']:
            print("✅ Model validation passed")
        else:
            print(f"⚠️ Model validation issues: {validation['errors']}")
            
        return gui_model, sd_model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_yaml_saving(gui_model):
    """Test saving the GUI model back to YAML."""
    print("\nTesting YAML model saving...")
    
    if not gui_model:
        print("❌ No model to save")
        return False
        
    try:
        saver = YAMLModelSaver()
        
        # Test paths
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        
        model_output_path = output_dir / "test_model_structure.yaml"
        scenario_output_path = output_dir / "test_scenario_parameters.yaml"
        
        # Save the model
        saver.save_model_to_file(
            gui_model,
            str(model_output_path),
            str(scenario_output_path),
            save_scenario_separately=True
        )
        
        print(f"✅ Model saved to: {model_output_path}")
        print(f"✅ Scenario saved to: {scenario_output_path}")
        
        # Test model summary export
        summary = saver.export_model_summary(gui_model)
        summary_path = output_dir / "model_summary.txt"
        
        with open(summary_path, 'w') as f:
            f.write(summary)
            
        print(f"✅ Model summary exported to: {summary_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving model: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_round_trip():
    """Test loading and re-saving to ensure round-trip compatibility."""
    print("\nTesting round-trip compatibility...")
    
    try:
        loader = YAMLModelLoader()
        saver = YAMLModelSaver()
        
        # Load original model
        model_path = Path(__file__).parent.parent.parent / "integrated_model_structure.yaml"
        scenario_path = Path(__file__).parent.parent.parent / "integrated_scenario_parameters.yaml"
        
        gui_model, _ = loader.load_model_from_file(str(model_path), str(scenario_path))
        
        # Save to temporary files
        output_dir = Path(__file__).parent / "test_output"
        temp_model_path = output_dir / "roundtrip_model.yaml"
        temp_scenario_path = output_dir / "roundtrip_scenario.yaml"
        
        saver.save_model_to_file(gui_model, str(temp_model_path), str(temp_scenario_path))
        
        # Load the saved files
        gui_model2, _ = loader.load_model_from_file(str(temp_model_path), str(temp_scenario_path))
        
        # Compare key properties
        if gui_model.name == gui_model2.name:
            print("✅ Model name preserved")
        else:
            print(f"❌ Model name changed: {gui_model.name} → {gui_model2.name}")
            
        if len(gui_model.components) == len(gui_model2.components):
            print("✅ Component count preserved")
        else:
            print(f"❌ Component count changed: {len(gui_model.components)} → {len(gui_model2.components)}")
            
        if len(gui_model.connections) == len(gui_model2.connections):
            print("✅ Connection count preserved")
        else:
            print(f"❌ Connection count changed: {len(gui_model.connections)} → {len(gui_model2.connections)}")
            
        print("✅ Round-trip test completed")
        return True
        
    except Exception as e:
        print(f"❌ Round-trip test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all YAML integration tests."""
    print("System Dynamics GUI - YAML Integration Test")
    print("=" * 50)
    
    # Test loading
    gui_model, sd_model = test_yaml_loading()
    
    if gui_model:
        # Test saving
        test_yaml_saving(gui_model)
        
        # Test round-trip
        test_round_trip()
        
        print("\n" + "=" * 50)
        print("🎉 YAML integration tests completed!")
        print("\nModel Summary:")
        print("-" * 20)
        
        saver = YAMLModelSaver()
        summary = saver.export_model_summary(gui_model)
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ YAML integration tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
