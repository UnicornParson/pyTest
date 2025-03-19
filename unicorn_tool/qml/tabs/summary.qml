import QtQuick 2.15
import QtQuick.Controls 2.15
import '../UnicornUI'

UTabContent {
    id: root
    anchors.fill: parent
    ListModel {
        id: tableModel
        ListElement { name: "Name"; value: "" }
        ListElement { name: "Src"; age: "25"; city: "London"; role: "Designer" }
        ListElement { name: "Bob"; age: "35"; city: "Paris"; role: "Manager" }
        ListElement { name: "Eve"; age: "28"; city: "Berlin"; role: "Analyst" }
    }

    TableView {
        anchors.fill: parent
        columnSpacing: 1
        rowSpacing: 1
        clip: true

        // Модель колонок
        model: TableModel {
            TableModelColumn { display: "name" }
            TableModelColumn { display: "category" }
            TableModelColumn { display: "price" }
            TableModelColumn { display: "stock" }

            rows: tableModel.rows
        }
}
