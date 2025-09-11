# Component Properties Dialog Guide

This guide explains how to use the new integrated component properties dialog that includes dimension management directly within the stock component window.

## 🎯 Overview

The Component Properties Dialog provides a comprehensive interface for editing all aspects of a component, including:
- Basic properties (name, description, initial values, etc.)
- Dimension management (add, edit, remove dimensions)
- Data editing capabilities
- Integration with advanced dimension editors

## 🔧 How to Access the Component Properties Dialog

### Method 1: Double-Click
1. **Double-click** on any stock component on the canvas
2. The Component Properties Dialog opens immediately

### Method 2: Right-Click Context Menu
1. **Right-click** on any stock component
2. Select **"📝 Properties..."** from the context menu
3. The Component Properties Dialog opens

### Method 3: Test Dialog
Run the test dialog to see all features:
```bash
python test_component_dialog.py
```

## 📊 Dialog Structure

The dialog has three main tabs:

### 📝 Properties Tab
**Basic component settings:**
- **Name:** Component name (editable)
- **Description:** Detailed description of the component
- **Initial Value:** Starting value for stocks (10,000 people, etc.)
- **Units:** Units of measurement (people, dollars, items, etc.)
- **Min/Max Values:** Optional constraints on the component values

### 📊 Dimensions Tab
**Complete dimension management:**

#### Current Dimensions Section:
- **List of dimensions** currently assigned to the component
- Shows dimension name and size (e.g., "age_group (size: 5)")
- **➕ Add Dimension:** Create a new dimension for this component
- **✏️ Edit Dimension:** Open detailed dimension editor (same as before)
- **❌ Remove Dimension:** Remove dimension from component

#### Available Model Dimensions Section:
- **List of existing dimensions** in the model that aren't assigned to this component
- Shows dimension details (name, size, description)
- **⬇️ Add Selected to Component:** Assign existing dimension to this component

#### Management Options:
- **📐 Manage All Dimensions:** Open the comprehensive dimension manager

### 💾 Data Tab
**Data editing options:**
- **Information display** about current dimensions
- **📊 Edit Data:** Open spreadsheet-style data editor
- **Status updates** based on available dimensions

## 🎯 Complete Workflow Example

### Step 1: Create and Configure Stock Component

1. **Create Stock:**
   - Drag Stock from palette to canvas
   - Double-click the stock to open properties

2. **Set Basic Properties:**
   - Name: "Population"
   - Description: "Total population by age group"
   - Initial Value: 10000
   - Units: "people"

### Step 2: Add Age Dimension

1. **Go to Dimensions Tab**
2. **Click "➕ Add Dimension"**
3. **Enter Details:**
   - Name: `age_group`
   - Size: `5` (for 5 age groups)
4. **Click OK**

The dimension is now added to both the component and the model with default labels.

### Step 3: Edit Age Dimension Details

1. **In Dimensions Tab, select "age_group"**
2. **Click "✏️ Edit Dimension"**
3. **In the Dimension Details Editor:**
   - Go to **"⚡ Quick Actions"** tab
   - Click **"Add Child Ages (0-17)"** → Adds: 0-4, 5-9, 10-14, 15-17
   - Click **"Add Adult Ages (18-64)"** → Adds: 18-24, 25-34, 35-44, 45-54, 55-64
   - Click **"Add Senior Ages (65+)"** → Adds: 65-74, 75-84, 85+
4. **Click OK** to save changes

### Step 4: Add More Dimensions

1. **Add Zone Dimension:**
   - Click "➕ Add Dimension"
   - Name: `zone`, Size: `3`
   - Edit to add: Urban, Suburban, Rural

2. **Add Time Dimension:**
   - Click "➕ Add Dimension"
   - Name: `time_period`, Size: `10`
   - Edit with Quick Actions → Add Years 2020-2029

### Step 5: Edit Data

1. **Go to Data Tab**
2. **Click "📊 Edit Data"**
3. **Set initial population values** for each age group, zone, and time period
4. **Save changes**

## 🔍 Visual Indicators

### On Canvas:
- **Orange indicator** shows number of dimensions (e.g., "3" for 3 dimensions)
- **Dimension names** displayed below component (if ≤3 dimensions)
- **Enhanced tooltips** show dimension details

### In Dialog:
- **Real-time updates** of dimension information
- **Status messages** in Data tab
- **Validation feedback** for dimension operations

## 🎨 Features Matching Your Image

The dialog now includes all the options you showed in your image:

```
age_group (5): 0-4, 5-9, 10-14, 15-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75-84, 85+
zone (3): Urban, Suburban, Rural  
time_period (10): 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029
new_dimension (2): new_dimension_1, new_dimension_2

[📊 Edit Data] [📐 Manage Dimensions] [➕ Add Dimension] [✏️ Edit Dimension]
```

## 🚀 Advanced Features

### Batch Operations:
- **Apply button:** Save changes without closing dialog
- **Reset functionality:** Restore original values
- **Real-time validation:** Immediate feedback on changes

### Integration:
- **Seamless connection** with existing dimension editors
- **Automatic model updates** when dimensions change
- **Component modification signals** for canvas updates

### Error Handling:
- **Graceful fallbacks** if advanced features aren't available
- **Clear error messages** with helpful suggestions
- **Validation of dimension names** and properties

## 🧪 Testing

### Test the Complete Workflow:
1. **Main GUI:** `python main.py`
2. **Test Dialog:** `python test_component_dialog.py`
3. **Dimension Test:** `python test_dimension_gui.py`

### Verify Features:
- ✅ Double-click opens properties dialog
- ✅ Right-click context menu works
- ✅ All three tabs function correctly
- ✅ Dimension management integrated
- ✅ Data editing accessible
- ✅ Visual indicators on canvas
- ✅ Changes persist and update model

The Component Properties Dialog now provides a comprehensive, integrated solution for managing all aspects of system dynamics components, with special focus on dimension management as requested! 🎉
