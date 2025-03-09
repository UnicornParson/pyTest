import sys
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

class Backend(QObject):
    textChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._text = "Нажмите кнопку!"
        
    @pyqtProperty(str, notify=textChanged)
    def labelText(self):
        return self._text
        
    def updateText(self):
        self._text = "Кнопка была нажата!"
        self.textChanged.emit(self._text)

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    
    engine.load("qml/main2.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())