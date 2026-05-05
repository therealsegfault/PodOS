import sys
import os
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

import sys
if sys.platform == 'darwin':
    os.environ['QT_SCALE_FACTOR'] = '1.5'

if sys.platform != 'linux':
    from src.system.mock import SystemBridge
else:
    from src.system.dbus import SystemBridge

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()

bridge = SystemBridge()
engine.rootContext().setContextProperty("System", bridge)

engine.load(QUrl.fromLocalFile(
    os.path.join(os.path.dirname(__file__), 'src/qml/Main.qml')
))

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())