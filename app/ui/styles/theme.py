from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QColor, QPalette


_STYLE_DIR = Path(__file__).resolve().parent
_COMBO_ARROW_URL = (_STYLE_DIR / "assets" / "combo_arrow_down.svg").as_posix()


def build_light_palette() -> QPalette:
    palette = QPalette()

    palette.setColor(QPalette.Window, QColor("#f7f7f8"))
    palette.setColor(QPalette.WindowText, QColor("#1a1d21"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f3f4f6"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, QColor("#1a1d21"))
    palette.setColor(QPalette.Text, QColor("#1a1d21"))
    palette.setColor(QPalette.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ButtonText, QColor("#1a1d21"))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Highlight, QColor("#dce8ff"))
    palette.setColor(QPalette.HighlightedText, QColor("#1a1d21"))
    palette.setColor(QPalette.Link, QColor("#0d4d97"))
    palette.setColor(QPalette.PlaceholderText, QColor("#7d8693"))

    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#8d95a0"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#8d95a0"))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#8d95a0"))

    return palette


APP_STYLESHEET = """
QMainWindow {
    background-color: #f7f7f8;
}

QWidget {
    font-family: "Yu Gothic UI", "Meiryo", sans-serif;
    color: #1a1d21;
}

QFrame#sidebar {
    background-color: #f2f3f5;
}

QFrame#sectionCard {
    background-color: #ffffff;
    border-radius: 18px;
}

QFrame#primaryMetric,
QFrame#warningMetric,
QFrame#neutralMetric {
    background-color: #ffffff;
    border-radius: 18px;
    min-height: 116px;
}

QFrame#primaryMetric {
    border-left: 4px solid #0c58b4;
}

QFrame#warningMetric {
    border-left: 4px solid #8f3d0f;
}

QFrame#neutralMetric {
    border-left: 4px solid #0c58b4;
}

QFrame#emphasisCard {
    background-color: #0d4d97;
    border-radius: 18px;
}

QFrame#softInfoCard {
    background-color: #efefef;
    border-radius: 18px;
}

QLabel#pageTitle {
    font-size: 24px;
    font-weight: 800;
    color: #0d4d97;
}

QLabel#pageSubtitle {
    font-size: 15px;
    font-weight: 600;
    color: #4d5560;
}

QLabel#sidebarTitle {
    font-size: 24px;
    font-weight: 800;
    color: #0d4d97;
}

QLabel#sidebarSubtitle,
QLabel#sidebarFooter {
    font-size: 12px;
    color: #5d6672;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 800;
    color: #1a1d21;
}

QLabel#fieldLabel,
QLabel#metricLabel {
    font-size: 12px;
    font-weight: 700;
    color: #4c5562;
}

QLabel#metricValue {
    font-size: 34px;
    font-weight: 800;
    color: #0d4d97;
}

QLabel#metricInlineValue {
    font-size: 14px;
    font-weight: 700;
    color: #0d4d97;
    background-color: #eef3f8;
    border-radius: 12px;
    padding: 6px 10px;
}

QLabel#mutedText {
    font-size: 12px;
    color: #6e7782;
}

QLabel#noteText {
    font-size: 12px;
    color: #58708a;
    background-color: #f3f6fa;
    border-radius: 10px;
    padding: 10px 12px;
}

QLabel#detailText {
    font-size: 13px;
    color: #1a1d21;
}

QLabel#readoutValue {
    background-color: #e5e7ea;
    border-radius: 12px;
    padding: 12px 14px;
    font-size: 14px;
    font-weight: 700;
    color: #1a1d21;
}

QLabel#compactReadoutValue {
    background-color: #e5e7ea;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 700;
    color: #1a1d21;
}

QLabel#avatarCircle {
    background-color: #17354d;
    color: #ffffff;
    border-radius: 19px;
    font-size: 12px;
    font-weight: 700;
}

QLabel#emphasisTitle {
    font-size: 16px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#emphasisBody {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.90);
}

QPushButton {
    border: none;
    border-radius: 12px;
    padding: 10px 16px;
    min-width: 88px;
    background-color: #ffffff;
    color: #1a1d21;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #f1f3f6;
}

QPushButton#navButton {
    background-color: transparent;
    color: #304255;
    text-align: left;
    padding: 14px 14px 14px 16px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 700;
    border: none;
    outline: 0;
}

QPushButton#navGroupButton {
    background-color: transparent;
    color: #304255;
    text-align: left;
    padding: 12px 14px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 800;
    border: none;
    outline: 0;
}

QPushButton#navSubButton {
    background-color: transparent;
    color: #405164;
    text-align: left;
    padding: 10px 14px 10px 18px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    border: none;
    outline: 0;
}

QPushButton#navButton:hover {
    background-color: #e9edf2;
}

QPushButton#navGroupButton:hover,
QPushButton#navSubButton:hover {
    background-color: #e9edf2;
}

QPushButton#navButton:focus {
    border: none;
    outline: 0;
}

QPushButton#navGroupButton:focus,
QPushButton#navSubButton:focus {
    border: none;
    outline: 0;
}

QPushButton#navButton:checked {
    background-color: transparent;
    color: #0d4d97;
    font-weight: 800;
    border-left: 4px solid #0d4d97;
    padding-left: 12px;
}

QPushButton#navGroupButton:checked,
QPushButton#navSubButton:checked {
    background-color: transparent;
    color: #0d4d97;
    border-left: 4px solid #0d4d97;
}

QPushButton#navGroupButton:checked {
    padding-left: 10px;
}

QPushButton#navSubButton:checked {
    padding-left: 14px;
}

QPushButton#sidebarPrimaryButton {
    background-color: #0d5ab6;
    color: #ffffff;
    font-weight: 700;
    padding: 12px 16px;
}

QPushButton#sidebarPrimaryButton:hover {
    background-color: #0f66cc;
}

QPushButton#sidebarUtilityButton {
    background-color: transparent;
    color: #4b5664;
    text-align: left;
    padding: 10px 8px;
    border-radius: 10px;
}

QPushButton#sidebarUtilityButton:hover {
    background-color: #e9edf2;
}

QPushButton#headerCircleButton {
    border-radius: 19px;
    background-color: #ffffff;
    color: #405164;
    font-weight: 800;
    padding: 0;
}

QPushButton#ghostButton {
    background-color: #eceef1;
    color: #0d4d97;
    font-weight: 700;
    padding: 14px 20px;
}

QPushButton#ghostButton:hover {
    background-color: #e3e6ea;
}

QPushButton#primaryButton {
    color: #ffffff;
    border-radius: 12px;
    padding: 14px 20px;
    font-size: 14px;
    font-weight: 700;
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0c4f9d,
        stop: 1 #0e5db8
    );
}

QPushButton#primaryButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #125db6,
        stop: 1 #1670d5
    );
}

QPushButton#listPillButton,
QPushButton#listPillButtonActive {
    border-radius: 16px;
    padding: 8px 14px;
    min-width: 0;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#listPillButton {
    background-color: #eceef1;
    color: #4d5560;
}

QPushButton#listPillButtonActive {
    background-color: #0d4d97;
    color: #ffffff;
}

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #dde1e6;
    border: none;
    border-radius: 12px;
    padding: 12px 14px;
    min-height: 22px;
    font-size: 13px;
    color: #1a1d21;
    selection-background-color: #dce8ff;
    selection-color: #1a1d21;
}

QLineEdit#compactField,
QComboBox#compactField,
QSpinBox#compactField {
    border-radius: 10px;
    padding: 8px 12px;
    min-height: 18px;
    font-size: 12px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QLineEdit#topSearchInput:focus {
    border-bottom: 2px solid #0d4d97;
}

QFrame#dateFieldContainer {
    background-color: #dde1e6;
    border: none;
    border-radius: 12px;
    min-height: 46px;
}

QFrame#dateFieldContainer[compact="true"] {
    border-radius: 10px;
    min-height: 34px;
}

QLineEdit#dateFieldDisplay {
    background-color: transparent;
    border: none;
    border-radius: 12px;
    padding: 12px 14px;
    min-height: 22px;
    font-size: 13px;
    color: #122033;
}

QLineEdit#dateFieldDisplay[compact="true"] {
    border-radius: 10px;
    padding: 8px 12px;
    min-height: 16px;
    font-size: 12px;
}

QLineEdit#dateFieldDisplay:focus {
    border: none;
}

QLineEdit#compactInput {
    min-height: 18px;
    padding: 10px 12px;
}

QLineEdit#sizeInput {
    background-color: #ffffff;
    border: 1px solid #c7d0dc;
    border-radius: 10px;
    padding: 7px 12px;
    min-height: 18px;
    color: #17324d;
}

QLineEdit#sizeInput:focus {
    border: 2px solid #0d5ab6;
    background-color: #ffffff;
}

QLineEdit#sizeInput:hover {
    border: 1px solid #aebccd;
}

QLineEdit#topSearchInput {
    background-color: #ffffff;
    border-radius: 18px;
    padding: 10px 14px;
    min-height: 18px;
}

QPushButton#compactPrimaryButton,
QPushButton#compactSecondaryButton,
QPushButton#compactGhostButton {
    min-width: 84px;
    min-height: 20px;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
}

QPushButton#compactPrimaryButton {
    color: #ffffff;
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0c4f9d,
        stop: 1 #0e5db8
    );
}

QPushButton#compactPrimaryButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #125db6,
        stop: 1 #1670d5
    );
}

QPushButton#compactSecondaryButton {
    background-color: #eaf0f6;
    color: #0d4d97;
}

QPushButton#compactSecondaryButton:hover {
    background-color: #dde7f0;
}

QPushButton#compactGhostButton {
    background-color: #f3e7e8;
    color: #9b4d57;
}

QPushButton#compactGhostButton:hover {
    background-color: #eddcde;
}

QPushButton#filterToggleButton {
    background-color: #eceef1;
    color: #4d5560;
    border-radius: 14px;
    padding: 8px 14px;
    min-width: 0;
    font-size: 12px;
    font-weight: 700;
}

QPushButton#filterToggleButton:checked {
    background-color: #0d4d97;
    color: #ffffff;
}

QPushButton#filterToggleButton:hover {
    background-color: #dfe4ea;
}

QPushButton#filterToggleButton:checked:hover {
    background-color: #0d4d97;
}

QCheckBox#inlineCheck {
    color: #4d5560;
    font-size: 12px;
    font-weight: 700;
    spacing: 6px;
}

QCheckBox#inlineCheck::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    background-color: #dde1e6;
}

QCheckBox#inlineCheck::indicator:checked {
    background-color: #0d4d97;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 32px;
    border: none;
    background-color: rgba(0, 0, 0, 0.04);
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}

QComboBox::down-arrow {
    image: url("%s");
    width: 12px;
    height: 8px;
}

QComboBox QAbstractItemView,
QAbstractItemView {
    background-color: #ffffff;
    color: #1a1d21;
    selection-background-color: #dce8ff;
    selection-color: #1a1d21;
    alternate-background-color: #f3f4f6;
    border: none;
    outline: 0;
}

QSpinBox::up-button,
QSpinBox::down-button {
    width: 18px;
    border: none;
    background-color: rgba(0, 0, 0, 0.04);
}

QPushButton#dateFieldButton,
QPushButton#calendarNavButton,
QPushButton#calendarPillButton,
QPushButton#dialogPrimaryButton,
QPushButton#dialogSecondaryButton {
    min-width: 0;
    font-weight: 700;
}

QPushButton#dateFieldButton {
    background-color: rgba(255, 255, 255, 0.42);
    border: none;
    color: #0d4d97;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    min-width: 32px;
    padding: 12px 8px;
}

QPushButton#dateFieldButton[compact="true"] {
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    min-width: 28px;
    padding: 8px 6px;
}

QPushButton#dateFieldButton:hover {
    background-color: rgba(255, 255, 255, 0.58);
}

QPushButton#calendarNavButton,
QPushButton#calendarPillButton {
    background-color: #eef3f8;
    color: #2f4257;
    border-radius: 12px;
    padding: 9px 14px;
}

QPushButton#calendarNavButton:hover,
QPushButton#calendarPillButton:hover {
    background-color: #e2e9f2;
}

QPushButton#dialogPrimaryButton {
    color: #ffffff;
    border-radius: 14px;
    padding: 12px 18px;
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0c4f9d,
        stop: 1 #0e5db8
    );
}

QPushButton#dialogPrimaryButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #125db6,
        stop: 1 #1670d5
    );
}

QPushButton#dialogSecondaryButton {
    background-color: #eef2f7;
    color: #304255;
    border-radius: 14px;
    padding: 12px 18px;
}

QPushButton#dialogSecondaryButton:hover {
    background-color: #e3e9f0;
}

QDialog#modalDialog,
QDialog#calendarDialog {
    background: transparent;
}

QFrame#modalCard,
QFrame#calendarDialogCard {
    background-color: #ffffff;
    border: 1px solid rgba(13, 77, 151, 0.08);
    border-radius: 24px;
}

QLabel#modalBadge {
    border-radius: 16px;
    padding: 0 12px;
    font-size: 11px;
    font-weight: 800;
    min-width: 72px;
}

QLabel#modalTitle {
    font-size: 18px;
    font-weight: 800;
    color: #132033;
}

QLabel#modalMessage {
    font-size: 13px;
    line-height: 1.5;
    color: #516070;
}

QLabel#calendarMonthLabel {
    font-size: 18px;
    font-weight: 800;
    color: #132033;
}

QCalendarWidget#calendarWidget {
    background-color: #ffffff;
    border: none;
}

QCalendarWidget#calendarWidget QWidget {
    alternate-background-color: #ffffff;
}

QCalendarWidget#calendarWidget QAbstractItemView:enabled {
    background-color: #ffffff;
    color: #1a1d21;
    selection-background-color: #dce8ff;
    selection-color: #1a1d21;
    outline: 0;
}

QCalendarWidget#calendarWidget QTableView {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 8px;
}

QCalendarWidget#calendarWidget QTableView::item {
    border-radius: 12px;
    padding: 8px;
}

QCalendarWidget#calendarWidget QTableView::item:hover {
    background-color: #eef4fb;
}

QCalendarWidget#calendarWidget QTableView::item:selected {
    background-color: #0d5ab6;
    color: #ffffff;
}

QCalendarWidget#calendarWidget QWidget#qt_calendar_navigationbar {
    background: transparent;
}

QTableWidget#loanTable {
    background-color: #ffffff;
    alternate-background-color: #fbfbfc;
    border: none;
    border-radius: 12px;
    selection-background-color: #dce8ff;
    selection-color: #1a1d21;
}

QTableWidget#loanTable::item {
    padding: 8px;
    border-bottom: 1px solid #f1f2f4;
}

QHeaderView::section {
    background-color: #f3f4f6;
    color: #4c5562;
    border: none;
    padding: 12px 12px;
    font-size: 12px;
    font-weight: 700;
}
""" % _COMBO_ARROW_URL
