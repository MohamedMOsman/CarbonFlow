"""
Climate Adaptation Specific Features for Spreadsheet Editor

This module provides specialized features for climate adaptation modeling
including pre-configured dimension combinations, time-series support,
validation rules, and quick templates.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit, QDialog, QDialogButtonBox, QMessageBox,
    QProgressBar, QTabWidget, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import json


class ClimateAdaptationTemplates:
    """
    Pre-configured templates for common climate adaptation scenarios.
    """
    
    @staticmethod
    def get_dimension_combinations():
        """Get common dimension combinations for climate adaptation."""
        return {
            'flood_protection': {
                'name': 'Flood Protection Measures',
                'dimensions': ['parcel', 'time'],
                'description': 'Flood protection measures by parcel over time',
                'variables': [
                    'basement_height_improvement_rate',
                    'offset_improvement_rate',
                    'structureBsmtHeight',
                    'structureOffsetFromGrnd'
                ]
            },
            'albedo_changes': {
                'name': 'Albedo Changes',
                'dimensions': ['parcel', 'time_10yr'],
                'description': 'Albedo modifications by parcel every 10 years',
                'variables': [
                    'albedoChange',
                    'albedoTempInt'
                ]
            },
            'building_cohorts': {
                'name': 'Building Cohorts',
                'dimensions': ['building_type', 'year_built_cohort'],
                'description': 'Building characteristics by type and construction era',
                'variables': [
                    'construction_quality',
                    'energy_efficiency',
                    'adaptation_potential'
                ]
            },
            'parcel_time_series': {
                'name': 'Parcel Time Series',
                'dimensions': ['parcel', 'year'],
                'description': 'Annual data by parcel',
                'variables': [
                    'population',
                    'housing_units',
                    'flood_risk',
                    'heat_exposure'
                ]
            }
        }
    
    @staticmethod
    def get_parcel_identifiers():
        """Get standard parcel identifiers for climate adaptation models."""
        return ['1001', '1002', '1003']
    
    @staticmethod
    def get_time_dimensions():
        """Get time dimension configurations."""
        return {
            'annual': {
                'name': 'Annual',
                'labels': [str(year) for year in range(2020, 2051)],
                'description': 'Annual time steps from 2020 to 2050'
            },
            'decadal': {
                'name': 'Decadal',
                'labels': [str(year) for year in range(2020, 2051, 10)],
                'description': 'Decadal time steps from 2020 to 2050'
            },
            'climate_periods': {
                'name': 'Climate Periods',
                'labels': ['2020-2030', '2030-2040', '2040-2050'],
                'description': 'Climate assessment periods'
            }
        }
    
    @staticmethod
    def get_building_types():
        """Get building type categories."""
        return [
            'single_family',
            'multi_family',
            'commercial',
            'industrial',
            'mixed_use'
        ]
    
    @staticmethod
    def get_cohort_periods():
        """Get year built cohort periods."""
        return [
            'pre_1950',
            '1950_1970',
            '1970_1990',
            '1990_2010',
            'post_2010'
        ]


class ClimateValidationRules:
    """
    Validation rules specific to climate adaptation parameters.
    """
    
    @staticmethod
    def validate_flood_protection(value, variable_name):
        """Validate flood protection measures."""
        try:
            num_value = float(value)
            
            if variable_name in ['basement_height_improvement_rate', 'offset_improvement_rate']:
                if num_value < 0:
                    return False, "Improvement rates must be non-negative"
                if num_value > 1:
                    return False, "Improvement rates should not exceed 100% (1.0)"
                    
            elif variable_name in ['structureBsmtHeight', 'structureOffsetFromGrnd']:
                if num_value < 0:
                    return False, "Structure measurements must be non-negative"
                if num_value > 10:  # Reasonable upper limit in meters
                    return False, "Structure measurements seem unreasonably high (>10m)"
                    
            return True, ""
            
        except ValueError:
            return False, "Value must be a number"
    
    @staticmethod
    def validate_albedo_changes(value, variable_name):
        """Validate albedo change parameters."""
        try:
            num_value = float(value)
            
            if variable_name == 'albedoChange':
                if num_value < -1 or num_value > 1:
                    return False, "Albedo changes must be between -1 and 1"
                    
            elif variable_name == 'albedoTempInt':
                if num_value < -10 or num_value > 10:
                    return False, "Temperature interaction values seem unreasonable"
                    
            return True, ""
            
        except ValueError:
            return False, "Value must be a number"
    
    @staticmethod
    def validate_population_data(value, variable_name):
        """Validate population-related data."""
        try:
            num_value = float(value)
            
            if variable_name == 'population':
                if num_value < 0:
                    return False, "Population must be non-negative"
                if num_value > 1000000:  # Reasonable upper limit
                    return False, "Population value seems unreasonably high"
                    
            elif variable_name == 'housing_units':
                if num_value < 0:
                    return False, "Housing units must be non-negative"
                if num_value > 100000:  # Reasonable upper limit
                    return False, "Housing units value seems unreasonably high"
                    
            return True, ""
            
        except ValueError:
            return False, "Value must be a number"


class DataPatternGenerator:
    """
    Generator for common data patterns in climate adaptation modeling.
    """
    
    @staticmethod
    def linear_growth(start_value, end_value, num_steps):
        """Generate linear growth pattern."""
        return np.linspace(start_value, end_value, num_steps)
    
    @staticmethod
    def exponential_growth(start_value, growth_rate, num_steps):
        """Generate exponential growth pattern."""
        return start_value * np.power(1 + growth_rate, np.arange(num_steps))
    
    @staticmethod
    def seasonal_variation(base_value, amplitude, num_steps, phase=0):
        """Generate seasonal variation pattern."""
        x = np.linspace(0, 2 * np.pi, num_steps)
        return base_value + amplitude * np.sin(x + phase)
    
    @staticmethod
    def step_function(values, step_points):
        """Generate step function pattern."""
        result = []
        current_value = values[0]
        value_index = 0
        
        for i in range(len(step_points)):
            if i in step_points and value_index < len(values) - 1:
                value_index += 1
                current_value = values[value_index]
            result.append(current_value)
            
        return result
    
    @staticmethod
    def climate_scenario_ramp(baseline, impact_factor, start_year, end_year, current_years):
        """Generate climate impact ramp-up pattern."""
        result = []
        
        for year in current_years:
            if year <= start_year:
                result.append(baseline)
            elif year >= end_year:
                result.append(baseline * (1 + impact_factor))
            else:
                # Linear ramp between start and end years
                progress = (year - start_year) / (end_year - start_year)
                value = baseline * (1 + impact_factor * progress)
                result.append(value)
                
        return result


class QuickTemplateDialog(QDialog):
    """
    Dialog for applying quick data templates to selected cells.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Apply Data Template")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the template dialog UI."""
        
        layout = QVBoxLayout(self)
        
        # Template selection
        template_group = QGroupBox("Template Type")
        template_layout = QFormLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Linear Growth",
            "Exponential Growth", 
            "Seasonal Variation",
            "Step Function",
            "Climate Scenario Ramp"
        ])
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_layout.addRow("Template:", self.template_combo)
        
        layout.addWidget(template_group)
        
        # Parameters
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QFormLayout(self.params_group)
        layout.addWidget(self.params_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        self.generate_preview_btn = QPushButton("Generate Preview")
        self.generate_preview_btn.clicked.connect(self.generate_preview)
        preview_layout.addWidget(self.generate_preview_btn)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize with first template
        self.on_template_changed()
        
    def on_template_changed(self):
        """Handle template selection changes."""
        
        # Clear existing parameters
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        template = self.template_combo.currentText()
        
        if template == "Linear Growth":
            self.start_spin = QDoubleSpinBox()
            self.start_spin.setRange(-999999, 999999)
            self.start_spin.setValue(0)
            self.params_layout.addRow("Start Value:", self.start_spin)
            
            self.end_spin = QDoubleSpinBox()
            self.end_spin.setRange(-999999, 999999)
            self.end_spin.setValue(100)
            self.params_layout.addRow("End Value:", self.end_spin)
            
            self.steps_spin = QSpinBox()
            self.steps_spin.setRange(2, 1000)
            self.steps_spin.setValue(10)
            self.params_layout.addRow("Number of Steps:", self.steps_spin)
            
        elif template == "Exponential Growth":
            self.start_spin = QDoubleSpinBox()
            self.start_spin.setRange(0.001, 999999)
            self.start_spin.setValue(1)
            self.params_layout.addRow("Start Value:", self.start_spin)
            
            self.rate_spin = QDoubleSpinBox()
            self.rate_spin.setRange(-0.99, 10)
            self.rate_spin.setValue(0.05)
            self.rate_spin.setSingleStep(0.01)
            self.params_layout.addRow("Growth Rate:", self.rate_spin)
            
            self.steps_spin = QSpinBox()
            self.steps_spin.setRange(2, 1000)
            self.steps_spin.setValue(10)
            self.params_layout.addRow("Number of Steps:", self.steps_spin)
            
        elif template == "Seasonal Variation":
            self.base_spin = QDoubleSpinBox()
            self.base_spin.setRange(-999999, 999999)
            self.base_spin.setValue(50)
            self.params_layout.addRow("Base Value:", self.base_spin)
            
            self.amplitude_spin = QDoubleSpinBox()
            self.amplitude_spin.setRange(0, 999999)
            self.amplitude_spin.setValue(10)
            self.params_layout.addRow("Amplitude:", self.amplitude_spin)
            
            self.steps_spin = QSpinBox()
            self.steps_spin.setRange(2, 1000)
            self.steps_spin.setValue(12)
            self.params_layout.addRow("Number of Steps:", self.steps_spin)
            
        elif template == "Climate Scenario Ramp":
            self.baseline_spin = QDoubleSpinBox()
            self.baseline_spin.setRange(-999999, 999999)
            self.baseline_spin.setValue(100)
            self.params_layout.addRow("Baseline Value:", self.baseline_spin)
            
            self.impact_spin = QDoubleSpinBox()
            self.impact_spin.setRange(-1, 10)
            self.impact_spin.setValue(0.2)
            self.impact_spin.setSingleStep(0.1)
            self.params_layout.addRow("Impact Factor:", self.impact_spin)
            
            self.start_year_spin = QSpinBox()
            self.start_year_spin.setRange(2020, 2100)
            self.start_year_spin.setValue(2030)
            self.params_layout.addRow("Start Year:", self.start_year_spin)
            
            self.end_year_spin = QSpinBox()
            self.end_year_spin.setRange(2020, 2100)
            self.end_year_spin.setValue(2050)
            self.params_layout.addRow("End Year:", self.end_year_spin)
            
    def generate_preview(self):
        """Generate and display preview of the template."""
        
        try:
            template = self.template_combo.currentText()
            
            if template == "Linear Growth":
                start = self.start_spin.value()
                end = self.end_spin.value()
                steps = self.steps_spin.value()
                values = DataPatternGenerator.linear_growth(start, end, steps)
                
            elif template == "Exponential Growth":
                start = self.start_spin.value()
                rate = self.rate_spin.value()
                steps = self.steps_spin.value()
                values = DataPatternGenerator.exponential_growth(start, rate, steps)
                
            elif template == "Seasonal Variation":
                base = self.base_spin.value()
                amplitude = self.amplitude_spin.value()
                steps = self.steps_spin.value()
                values = DataPatternGenerator.seasonal_variation(base, amplitude, steps)
                
            elif template == "Climate Scenario Ramp":
                baseline = self.baseline_spin.value()
                impact = self.impact_spin.value()
                start_year = self.start_year_spin.value()
                end_year = self.end_year_spin.value()
                
                # Generate sample years
                years = list(range(2020, 2051, 5))  # Every 5 years
                values = DataPatternGenerator.climate_scenario_ramp(
                    baseline, impact, start_year, end_year, years
                )
            else:
                values = []
                
            # Format preview
            preview_text = f"Generated {len(values)} values:\n"
            preview_text += ", ".join([f"{v:.2f}" for v in values[:10]])
            if len(values) > 10:
                preview_text += f", ... ({len(values)-10} more)"
                
            self.preview_text.setText(preview_text)
            
        except Exception as e:
            self.preview_text.setText(f"Error generating preview: {e}")
            
    def get_generated_values(self):
        """Get the generated values based on current parameters."""
        
        template = self.template_combo.currentText()
        
        if template == "Linear Growth":
            start = self.start_spin.value()
            end = self.end_spin.value()
            steps = self.steps_spin.value()
            return DataPatternGenerator.linear_growth(start, end, steps)
            
        elif template == "Exponential Growth":
            start = self.start_spin.value()
            rate = self.rate_spin.value()
            steps = self.steps_spin.value()
            return DataPatternGenerator.exponential_growth(start, rate, steps)
            
        elif template == "Seasonal Variation":
            base = self.base_spin.value()
            amplitude = self.amplitude_spin.value()
            steps = self.steps_spin.value()
            return DataPatternGenerator.seasonal_variation(base, amplitude, steps)
            
        elif template == "Climate Scenario Ramp":
            baseline = self.baseline_spin.value()
            impact = self.impact_spin.value()
            start_year = self.start_year_spin.value()
            end_year = self.end_year_spin.value()
            
            # Generate sample years
            years = list(range(2020, 2051, 5))  # Every 5 years
            return DataPatternGenerator.climate_scenario_ramp(
                baseline, impact, start_year, end_year, years
            )
            
        return []
