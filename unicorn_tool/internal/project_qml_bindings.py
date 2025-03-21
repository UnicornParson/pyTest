from PyQt6.QtCore import *
from .project import *

class ProjectSummaryModel(QAbstractListModel):
    KeyRole = Qt.ItemDataRole.UserRole + 1
    ValueRole = Qt.ItemDataRole.UserRole + 2


    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = []


    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        row = index.row()
        if 0 <= row < self.rowCount():
            if role == ProjectSummaryModel.KeyRole:
                return self._rows[row]["k"]
            if role == ProjectSummaryModel.ValueRole:
                getter = self._rows[row]["getter"]
                print(f"getter is {type(getter)}")
                return getter()
        return None
    

    def add_row(self, key, getter):
        self._rows.append({"k":key, "getter":getter})

    def rowCount(self, parent=None):
        return len(self._rows)

    def roleNames(self):
        return {
            ProjectSummaryModel.KeyRole: b'key',
            ProjectSummaryModel.ValueRole: b'value'
        }

    def set_enabled(self, id, new_val):
        for b in self._rows:
            if b[0] == id:
                b[3] = new_val
    def select(self, id):
        self._selected_tab = id




class ProjectQObject(QObject):
    projectChanged = pyqtSignal()
    summaryChanged = pyqtSignal(ProjectSummaryModel)

    def __init__(self, proj, parent = None):
            super().__init__(parent)
            self.project = proj
            self.project.set_listener(self.on_changed)
            self.s_model = ProjectSummaryModel(self)
            self.fill_model()

    def fill_model(self):
        self.s_model.add_row("Name", self.name_getter)
        self.s_model.add_row("Source", self.source_getter)
        self.s_model.add_row("Indexed", self.last_indexed_getter)

    def name_getter(self):
        return self.name()
    def source_getter(self):
        return self.source()
    def last_indexed_getter(self):
        return self.last_indexed()

    
    def on_changed(self):
        self.projectChanged.emit()
        self.summaryChanged.emit(self.s_model)

    @pyqtProperty(str, notify=projectChanged)
    def name(self) -> str:
        return self.project.name
    @pyqtProperty(str, notify=projectChanged)
    def source(self) -> str:
        return self.project.source
    @pyqtProperty(str, notify=projectChanged)
    def last_indexed(self) -> str:
        return self.project.last_indexed
    @pyqtProperty(ProjectSummaryModel, notify=projectChanged)
    def summary_model(self) -> ProjectSummaryModel:
        return self.s_model