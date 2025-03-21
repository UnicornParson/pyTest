from PyQt6.QtCore import *

class ButtonModel(QAbstractListModel):
    TextRole = Qt.ItemDataRole.UserRole + 1
    IndexRole = Qt.ItemDataRole.UserRole + 2
    TabSrcRole = Qt.ItemDataRole.UserRole + 3 
    TabSelected = Qt.ItemDataRole.UserRole + 4
    TabEnabled = Qt.ItemDataRole.UserRole + 5
    IdRole = Qt.ItemDataRole.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = []
        self._selected_tab = None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        row = index.row()
        if 0 <= row < self.rowCount():
            if role == ButtonModel.TextRole:
                return self._buttons[row]["text"]
            if role == ButtonModel.IndexRole:
                return row
            if role == ButtonModel.TabSrcRole:
                return self._buttons[row]["src"]   
            if role == ButtonModel.TabEnabled:
                return self._buttons[row]["enabled"]   
            if role == ButtonModel.TabSelected:
                return self._buttons[row]["id"] == self._selected_tab
            if role == ButtonModel.IdRole:
                return self._buttons[row]["id"]
        return None

    def rowCount(self, parent=None):
        return len(self._buttons)

    def roleNames(self):
        return {
            ButtonModel.TextRole: b'buttonText',
            ButtonModel.IndexRole: b'buttonIndex',
            ButtonModel.TabSrcRole: b'tabSource',
            ButtonModel.TabSelected: b'tabSelected',
            ButtonModel.TabEnabled: b'tabEnabled',
            ButtonModel.IdRole: b'tabId',

        }

    def set_enabled(self, id, new_val):
        for b in self._buttons:
            if b[0] == id:
                b[3] = new_val
    def select(self, id):
        self._selected_tab = id

    def add_button(self, id, text, src, enabled):
        self.beginInsertRows(self.index(0,0), self.rowCount(), self.rowCount())
        self._buttons.append({"id":id,"text": text , "src" : src, "enabled": enabled} )
        self.endInsertRows()

class Tab:
    def __init__(self, tab_id=None , tab_name = None, tab_src = None):
        self.tab_id = tab_id
        self.tab_name = tab_name
        self.tab_src = tab_src
        self.enabled = True

    def add_to_model(self, model:ButtonModel):
        model.add_button(self.tab_id, self.tab_name, self.tab_src, self.enabled)
    def select_it(self, model:ButtonModel):
        model.select(self.tab_id)

class TabController(QObject):
    currentSrcChanged = pyqtSignal(str)
    buttonModelChanged = pyqtSignal(ButtonModel)

    class TabIds:
        Welcome = 1
        NewProject = 2
        Summary = 3

    def __init__(self, parent = None) -> QObject:
        super().__init__(parent)
        self._tabs: list[Tab] = [] 
        self._current_tab: Tab = None 
        self.model = ButtonModel(self)
        self.make_tabs()
        self.selectTab(TabController.TabIds.Welcome)
        self.buttonModelChanged.emit(self.model)

    def make_tabs(self):
        self._tabs = [
            Tab(TabController.TabIds.Welcome, "Welcome", "tabs/welcome.qml"), 
            Tab(TabController.TabIds.NewProject, "NewProject", "tabs/new_project.qml"),
            Tab(TabController.TabIds.Summary, "Project", "tabs/summary.qml"),
        ]
        for tab in self._tabs:
            tab.add_to_model(self.model)

    def selectTab(self, id):
        for tab in self._tabs:
            if tab.tab_id == id:
                
                self._current_tab = tab
                tab.select_it(self.model)
                self.currentSrcChanged.emit(tab.tab_src)
                return
        print(f"Tab with id {id} not found")

    @pyqtProperty(str, notify=currentSrcChanged)
    def currentSrc(self) -> str:
        return self._current_tab.tab_src if self._current_tab else "tabs/notab.qml"
    
    @pyqtProperty(ButtonModel, notify=buttonModelChanged)
    def buttonModel(self) -> ButtonModel:
        return self.model
    
    @pyqtSlot(int, int)
    def nav_press(self, id, row_index):
        print(f"Navigating to tab with ID {id} at index {row_index})" )
        self.selectTab(id)






