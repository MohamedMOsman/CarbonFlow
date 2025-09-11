# How to Use the Multidimensional Editor

## Quick Fix for the QComboBox Error

The error you encountered (`name 'QComboBox' is not defined`) has been **FIXED**. The issue was a missing import in the multidimensional editor. I've updated the code to handle import errors gracefully and provide helpful error messages.

## What Was Added to Your GUI

### 1. **Visual Indicators on Components**
- Components with multidimensional data now show **orange indicators** with dimension counts
- Look for small orange badges on stocks, flows, and calculators

### 2. **Double-Click to Edit**
- **Double-click any component** on the canvas to open the multidimensional editor
- This works for stocks, flows, and calculators

### 3. **Inspector Button**
- Select any component and look for the **"Edit Dimensions..."** button in the component inspector
- This provides another way to access the editor

### 4. **Comprehensive Editor Dialog**
- Spreadsheet-like table for editing dimensions and coordinates
- Tabs for metadata, preview, and validation
- Real-time YAML configuration preview

## Step-by-Step Usage

### Step 1: Install Dependencies (If Needed)
```bash
cd examples/population-economy-housing-simulation/gui
python install_dependencies.py
```

### Step 2: Run the GUI
```bash
python main.py
```

### Step 3: Create or Load a Model
- Create a new model or load an existing one
- Add some components (stocks, flows, calculators)

### Step 4: Access the Multidimensional Editor

**Method 1: Double-Click**
1. Double-click any component on the canvas
2. The multidimensional editor dialog will open

**Method 2: Inspector Button**
1. Click to select a component
2. Look at the component inspector panel
3. Click the "Edit Dimensions..." button

### Step 5: Use the Editor

**Adding Dimensions:**
1. Right-click in the table → "Add Dimension"
2. Enter a name like "parcel", "age", "building_type"
3. The dimension appears as a new column

**Adding Coordinates:**
1. Right-click → "Add Coordinate"
2. Fill in values for each dimension
3. Example: parcel="1001", building_type="residential"

**Editing Data:**
- Click any cell to edit directly
- Use copy/paste for bulk operations
- Double-click column headers to rename dimensions

**Validation:**
- Click the "Validation" tab to check for errors
- The "Preview" tab shows the YAML configuration
- Status bar shows real-time feedback

## Example: Climate Adaptation Model

Let's say you want to model flood protection measures:

1. **Create a stock** called "flood_protection_measures"
2. **Double-click it** to open the editor
3. **Add dimensions:**
   - parcel: 1001, 1002, 1003
   - building_type: residential, commercial, industrial
   - year_built_cohort: pre_1980, 1980_2000, post_2000
4. **Set metadata:**
   - Descriptions for each dimension
   - Types (categorical, numerical, temporal)
5. **Apply changes**

The result is a multidimensional stock that can track flood protection measures by parcel, building type, and construction era.

## Troubleshooting

### "QComboBox not defined" Error
✅ **FIXED** - This error has been resolved with proper imports and error handling.

### "Import Error" Messages
If you see import error dialogs:
1. Run `python install_dependencies.py`
2. Or manually install: `pip install PyQt6 PyYAML`

### Editor Won't Open
1. Make sure you have components in your model
2. Try both double-click and inspector button methods
3. Check the console for error messages

### No Visual Changes
The changes are **event-driven**:
- Visual indicators only appear on components with multidimensional data
- The editor only opens when you interact with components
- Make sure you have a model loaded with components

## What Files Were Changed

### New Files:
- `inspector/multidimensional_editor.py` - Main editor implementation
- `test_multidimensional_editor.py` - GUI test with examples
- `install_dependencies.py` - Dependency installer
- Various documentation and test files

### Modified Files:
- `canvas/graphics_items.py` - Added double-click handlers and visual indicators
- `inspector/component_inspector.py` - Added "Edit Dimensions..." button
- `inspector/property_editors.py` - Enhanced imports

## Testing the Changes

### Quick Test (No GUI):
```bash
python test_dimension_validation.py
```
This validates all core functionality without requiring the GUI.

### Full GUI Test:
```bash
python test_multidimensional_editor.py
```
This opens a test window with example components you can edit.

## Success Indicators

You'll know the multidimensional editor is working when you see:

1. **Orange indicators** on multidimensional components
2. **"Edit Dimensions..." button** in the component inspector
3. **Double-click opens editor** dialog with spreadsheet-like table
4. **Tabs for editing, metadata, preview, validation**
5. **Real-time YAML preview** of dimensional structure

The multidimensional editor is now fully integrated into your GUI and ready to use for climate adaptation modeling!
