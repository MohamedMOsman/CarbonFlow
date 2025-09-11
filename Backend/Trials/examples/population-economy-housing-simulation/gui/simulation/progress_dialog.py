"""
Progress Dialog for Simulation Monitoring

This module provides a progress dialog for monitoring simulation execution
with detailed status updates and cancellation support.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from typing import Optional
import time


class SimulationProgressDialog(QDialog):
    """
    Enhanced progress dialog for simulation monitoring.
    
    Provides:
    - Progress bar with percentage
    - Detailed status messages
    - Elapsed time display
    - Cancel/pause functionality
    - Log of simulation steps
    """
    
    # Signals
    cancelled = pyqtSignal()
    paused = pyqtSignal()
    resumed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Simulation Progress")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.setMaximumSize(600, 500)
        
        # State
        self.start_time = None
        self.is_paused = False
        self.is_cancelled = False
        
        # Setup UI
        self.setup_ui()
        
        # Timer for elapsed time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        
    def setup_ui(self):
        """Set up the progress dialog UI."""
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title and status
        title_label = QLabel("Running Simulation")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Current status
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("QLabel { color: #666; padding: 5px; }")
        layout.addWidget(self.status_label)
        
        # Progress bar
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress info
        progress_info_layout = QHBoxLayout()
        
        self.elapsed_label = QLabel("Elapsed: 00:00")
        self.elapsed_label.setFont(QFont("Arial", 9))
        progress_info_layout.addWidget(self.elapsed_label)
        
        progress_info_layout.addStretch()
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        progress_info_layout.addWidget(self.percentage_label)
        
        progress_layout.addLayout(progress_info_layout)
        layout.addWidget(progress_group)
        
        # Log area
        log_group = QGroupBox("Simulation Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)  # Enable when simulation starts
        button_layout.addWidget(self.pause_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_simulation)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def start_simulation(self):
        """Start simulation monitoring."""
        
        self.start_time = time.time()
        self.is_paused = False
        self.is_cancelled = False
        
        # Enable pause button
        self.pause_btn.setEnabled(True)
        
        # Start timer
        self.timer.start(1000)  # Update every second
        
        # Add initial log entry
        self.add_log_entry("Simulation started")
        
    def update_progress(self, percentage: int):
        """Update progress bar."""
        
        if self.is_cancelled:
            return
            
        self.progress_bar.setValue(percentage)
        self.percentage_label.setText(f"{percentage}%")
        
        # Update progress bar color based on percentage
        if percentage < 30:
            color = "#ff6b6b"  # Red
        elif percentage < 70:
            color = "#ffa726"  # Orange
        else:
            color = "#66bb6a"  # Green
            
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
    def update_status(self, status: str):
        """Update status message."""
        
        if self.is_cancelled:
            return
            
        self.status_label.setText(status)
        self.add_log_entry(status)
        
    def add_log_entry(self, message: str):
        """Add entry to simulation log."""
        
        if self.is_cancelled:
            return
            
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.append(log_entry)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_elapsed_time(self):
        """Update elapsed time display."""
        
        if not self.start_time or self.is_paused:
            return
            
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        self.elapsed_label.setText(f"Elapsed: {minutes:02d}:{seconds:02d}")
        
    def toggle_pause(self):
        """Toggle pause/resume simulation."""
        
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.pause_btn.setText("Pause")
            self.timer.start(1000)
            self.add_log_entry("Simulation resumed")
            self.resumed.emit()
        else:
            # Pause
            self.is_paused = True
            self.pause_btn.setText("Resume")
            self.timer.stop()
            self.add_log_entry("Simulation paused")
            self.paused.emit()
            
    def cancel_simulation(self):
        """Cancel simulation."""
        
        self.is_cancelled = True
        self.timer.stop()
        
        # Update UI
        self.status_label.setText("Cancelling simulation...")
        self.pause_btn.setEnabled(False)
        self.cancel_btn.setText("Cancelling...")
        self.cancel_btn.setEnabled(False)
        
        self.add_log_entry("Simulation cancelled by user")
        
        # Emit signal
        self.cancelled.emit()
        
    def simulation_finished(self, success: bool = True):
        """Handle simulation completion."""
        
        self.timer.stop()
        
        if success and not self.is_cancelled:
            self.status_label.setText("Simulation completed successfully!")
            self.progress_bar.setValue(100)
            self.percentage_label.setText("100%")
            self.add_log_entry("Simulation completed successfully")
            
            # Change cancel button to close
            self.cancel_btn.setText("Close")
            self.cancel_btn.setEnabled(True)
            self.cancel_btn.clicked.disconnect()
            self.cancel_btn.clicked.connect(self.accept)
            
        elif not success:
            self.status_label.setText("Simulation failed!")
            self.add_log_entry("Simulation failed with errors")
            
            # Change cancel button to close
            self.cancel_btn.setText("Close")
            self.cancel_btn.setEnabled(True)
            self.cancel_btn.clicked.disconnect()
            self.cancel_btn.clicked.connect(self.reject)
            
        # Disable pause button
        self.pause_btn.setEnabled(False)
        
    def simulation_error(self, error_message: str):
        """Handle simulation error."""
        
        self.simulation_finished(success=False)
        self.add_log_entry(f"ERROR: {error_message}")
        
    def closeEvent(self, event):
        """Handle dialog close event."""
        
        if not self.is_cancelled and self.timer.isActive():
            # Simulation is still running - ask for confirmation
            from PyQt6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "Cancel Simulation",
                "Simulation is still running. Do you want to cancel it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.cancel_simulation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
    def get_log_text(self) -> str:
        """Get the complete log text."""
        return self.log_text.toPlainText()
        
    def save_log(self, file_path: str):
        """Save simulation log to file."""
        
        with open(file_path, 'w') as f:
            f.write(f"Simulation Log\n")
            f.write(f"==============\n\n")
            f.write(self.get_log_text())


class SimpleProgressDialog(QDialog):
    """Simplified progress dialog for quick operations."""
    
    cancelled = pyqtSignal()
    
    def __init__(self, title: str = "Progress", message: str = "Processing...", parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 120)
        
        layout = QVBoxLayout(self)
        
        # Message
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def cancel(self):
        """Cancel operation."""
        self.cancelled.emit()
        self.reject()
        
    def set_message(self, message: str):
        """Update message."""
        # Find the message label and update it
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setText(message)
                break
