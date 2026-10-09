"""
Provides a space to change the UI theme 
TODO custom theme support via json
"""
import tkinter as tk
import sys

bgColor = '#232528'
toolbarColor = '#2F3237'
buttonHoverColor = '#383C42'
sectionColor = '#383C42'
normalTextColor = '#EEEEEE'
# macOS draws native button backgrounds independently of Tk's background color.
buttonTextColor = '#111111' if sys.platform == 'darwin' else normalTextColor
buttonDisabledTextColor = '#666666' if sys.platform == 'darwin' else '#A0A0A0'
sectionBorderColor = '#3DAFE0'
consoleColor = '#2F3237'
consoleError = 'red'
consoleWarning = 'yellow'
consoleNormal = 'lime'
debug = '#39FF14'