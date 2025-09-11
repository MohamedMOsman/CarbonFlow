# Dimension Editing Workflow Guide

This guide walks you through the complete workflow for creating and modifying dimensions in stock components within the System Dynamics GUI.

## 🎯 Complete Workflow: Create Stock → Add Dimension → Edit Dimension

### Step 1: Create a Stock Component

1. **Start the GUI:**
   ```bash
   python main.py
   ```

2. **Create a New Project:**
   - Click "New Project" in the project tree
   - Enter project name (e.g., "Population Study")
   - The system automatically creates a "Main System" and makes it active

3. **Add a Stock Component:**
   - Drag a **Stock** from the component palette to the canvas
   - The stock will be created with default properties

4. **Select the Stock:**
   - Click on the stock component on the canvas
   - The Component Inspector (right panel) will show the component details

### Step 2: Add an "Age" Dimension

1. **Go to Data Tab:**
   - In the Component Inspector, click the **"Data"** tab
   - You'll see four buttons for dimension management

2. **Add Dimension (Method 1 - Quick Add):**
   - Click **"➕ Add Dimension"**
   - Enter dimension name: `age`
   - Set size: `3` (for 3 age groups)
   - Click OK

3. **Verify Dimension Added:**
   - The Data tab should now show: "Dimensions: age"
   - The dimension is automatically added to both component and model
   - Default labels are created: `age_1`, `age_2`, `age_3`

### Step 3: Edit the Age Dimension Details

1. **Open Dimension Editor:**
   - Click **"✏️ Edit Dimension"** button
   - If you have multiple dimensions, select "age" from the dropdown
   - The **Dimension Details Editor** opens

2. **Edit Labels (Method 1 - Manual):**
   - Go to **"📝 Labels"** tab
   - Double-click on labels to edit them directly:
     - Change `age_1` to `0-17`
     - Change `age_2` to `18-64`
     - Change `age_3` to `65+`

3. **Add More Age Groups (Method 2 - Quick Actions):**
   - Go to **"⚡ Quick Actions"** tab
   - Click **"Add Child Ages (0-17)"** to add: `0-4`, `5-9`, `10-14`, `15-17`
   - Click **"Add Adult Ages (18-64)"** to add: `18-24`, `25-34`, `35-44`, `45-54`, `55-64`
   - Click **"Add Senior Ages (65+)"** to add: `65-74`, `75-84`, `85+`

4. **Custom Age Range:**
   - In Quick Actions tab, use "Custom Age Range"
   - Set Start: `0`, End: `100`, Step: `10`
   - Click "Add Age Range" to add: `0-9`, `10-19`, `20-29`, etc.

5. **Set Properties:**
   - Go to **"⚙️ Properties"** tab
   - Set Type: `categorical`
   - Add Description: `Age groups for population analysis`
   - Set Units: `years` (optional)

6. **Save Changes:**
   - Click **"OK"** to save all changes
   - The dimension is updated in the model

### Step 4: Verify and Use the Updated Dimension

1. **Check Updated Dimension:**
   - Back in the Data tab, you should see the updated dimension info
   - The size should reflect the new number of age groups

2. **Edit Data Values:**
   - Click **"📊 Edit Data"** to open the spreadsheet editor
   - You can now set initial population values for each age group
   - The column headers will show your custom age group labels

3. **View Data Table:**
   - The Data tab will show a table with your age groups as columns
   - Initial values can be displayed in the table format

## 🔧 Alternative Methods

### Method A: Use Manage Dimensions Dialog

1. Click **"📐 Manage Dimensions"**
2. Select dimension from list
3. Click **"Edit Selected"**
4. This opens the same Dimension Details Editor

### Method B: Add Dimension via Manage Dimensions

1. Click **"📐 Manage Dimensions"**
2. Click **"Add Dimension"**
3. Fill in dimension details in the Add Dimension Dialog
4. The dimension is added to the model and can be assigned to components

## 📊 Quick Actions Reference

### Time Series Actions:
- **Add Years:** Specify range (2020-2030) to add all years
- **Add Months:** Add Jan, Feb, Mar, ..., Dec

### Age Groups Actions:
- **Child Ages:** 0-4, 5-9, 10-14, 15-17
- **Adult Ages:** 18-24, 25-34, 35-44, 45-54, 55-64
- **Senior Ages:** 65-74, 75-84, 85+
- **Custom Range:** Specify start, end, step

### Categories Actions:
- **Income Levels:** Low, Lower Middle, Upper Middle, High
- **Education Levels:** No Formal, Primary, Secondary, Higher
- **Geographic Regions:** Urban, Suburban, Rural, Remote

## 🐛 Troubleshooting

### Button Not Enabled?
- **"✏️ Edit Dimension"** requires:
  - Component selected
  - Component has dimensions
  - Model has dimension definitions
- Use **"➕ Add Dimension"** first if no dimensions exist

### Dimension Not Found?
- Use **"📐 Manage Dimensions"** to see all available dimensions
- Add dimension to model first, then assign to component

### Changes Not Saved?
- Make sure to click **"OK"** in the Dimension Details Editor
- Check that the Data tab shows updated dimension info
- Use **"Show Results"** in test GUI to verify changes

## 🧪 Test the Workflow

Run the test GUI to verify everything works:

```bash
python test_dimension_gui.py
```

This opens a simplified interface that walks you through the complete workflow step by step.

## ✅ Success Indicators

You know the workflow is working when:
1. ✅ Stock component is created and selected
2. ✅ Dimension is added (Data tab shows "Dimensions: age")
3. ✅ Edit Dimension button is enabled and clickable
4. ✅ Dimension Details Editor opens successfully
5. ✅ You can add/edit/remove labels in the editor
6. ✅ Quick Actions work (adding age groups, years, etc.)
7. ✅ Changes are saved and reflected in the Data tab
8. ✅ Edit Data button works with updated dimension structure

The system now provides professional-grade dimension management for system dynamics modeling! 🚀
