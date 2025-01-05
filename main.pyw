from PyQt5.QtWidgets import QApplication
from gui.anasayfa import anamenu_ui
import sys

# Dark theme style definition
dark_style = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: 'Segoe UI', Arial;
    }
    
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QCalendarWidget QSpinBox {
        background-color: #3b3b3b;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px;
        color: #ffffff;
        selection-background-color: #4a4a4a;
    }
    
    QCalendarWidget QWidget {
        alternate-background-color: #2b2b2b;
    }
    
    QCalendarWidget QAbstractItemView:enabled {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QCalendarWidget QAbstractItemView:disabled {
        color: #666666;
    }
    
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background-color: #3b3b3b;
    }
    
    QCalendarWidget QToolButton {
        color: #ffffff;
        background-color: #3b3b3b;
        border: none;
        border-radius: 4px;
        padding: 4px;
    }
    
    QCalendarWidget QToolButton:hover {
        background-color: #4a4a4a;
    }
    
    QCalendarWidget QMenu {
        background-color: #2b2b2b;
        border: 1px solid #555555;
    }
    
    QCalendarWidget QMenu::item:selected {
        background-color: #3d5a80;
    }
    
    QCalendarWidget QToolButton::menu-indicator {
        image: none;
    }
    
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
        border: 1px solid #5c88c5;
    }
    
    QPushButton {
        background-color: #3d5a80;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #4a6b95;
    }
    
    QPushButton:pressed {
        background-color: #345070;
    }
    
    QTableWidget {
        background-color: #2b2b2b;
        alternate-background-color: #323232;
        border: 1px solid #3b3b3b;
        gridline-color: #3b3b3b;
        color: #ffffff;
        selection-background-color: #3d5a80;
    }
    
    QTableWidget::item {
        padding: 4px;
    }
    
    QHeaderView::section {
        background-color: #3b3b3b;
        color: #ffffff;
        padding: 6px;
        border: none;
        font-weight: bold;
    }
    
    QScrollBar:vertical {
        border: none;
        background-color: #2b2b2b;
        width: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #5c88c5;
        border-radius: 5px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #6b99d8;
    }
    
    QLabel {
        color: #ffffff;
    }
    
    QMessageBox {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QMessageBox QPushButton {
        min-width: 70px;
        min-height: 25px;
    }
    
    QDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QMenuBar::item:selected {
        background-color: #3d5a80;
    }
    
    QMenu {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #555555;
    }
    
    QMenu::item:selected {
        background-color: #3d5a80;
    }
"""

app = QApplication(sys.argv)
app.setStyleSheet(dark_style)  # Set the style globally
from gui.listele import liste_tablosu
pencere=liste_tablosu()
anamenu=anamenu_ui()
anamenu.show()
app.exec_()
