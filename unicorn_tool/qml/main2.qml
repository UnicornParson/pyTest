import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


/*
component LabeledButton: Button {
    property string text  // Убрано 'required'
    implicitWidth: 140
    implicitHeight: 40
    background: Rectangle {
        color: "#eeeeee"
        radius: 5
    }
    contentItem: Text {
        text: parent.text  // parent.text -> обращение к свойству Button
        font.pointSize: 14
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}

component InfoBlock: Pane {
    property string title  // Убрано 'required'
    Layout.fillWidth: true
    implicitHeight: 80
    background: Rectangle {
        color: "#f8f8f8"
        border.width: 1
        border.color: "#dddddd"
    }
    contentItem: Text {
        text: title        // title -> свойство компонента InfoBlock
        font.pointSize: 14
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
*/
Window {
    id: window
    visible: true
    width: 800
    height: 600
    color: "#f5f5f5"
    title: "PyQt6 QML Application"

    // Удален PropertyAlias (несуществующий в Qt6)
    property int theme: 0

    Rectangle {
        id: background
        color: "#ffffff"
        border.width: 1
        border.color: "#cccccc"
        anchors.fill: parent
    }

    MenuBar {
        id: menuBar
        background: Rectangle {
            color: "#ffffff"
            border.width: 1
            border.color: "#cccccc"
        }

        Menu {
            title: "File"
            Action {
                text: "Open"
                onTriggered: window.show()
            }
            Action {
                text: "Save"
            }
            MenuSeparator {}
            Action {
                text: "Exit"
                onTriggered: window.close()
            }
        }
    }

    RowLayout {
        id: toolbar
        anchors.top: menuBar.bottom
        spacing: 10

        Button {
            text: "File"
            implicitWidth: 100
            implicitHeight: 50
            background: Rectangle {
                color: "#cccccc"
            }
        }

        Button {
            text: "Edit"
            implicitWidth: 200
            implicitHeight: 50
            background: Rectangle {
                color: "#cccccc"
            }
        }

        Button {
            text: "Help"
            implicitWidth: 100
            implicitHeight: 50
            background: Rectangle {
                color: "#cccccc"
            }
        }
    }

    ScrollView {
        id: editor
        width: 600
        height: 500
        anchors.top: toolbar.bottom

        TextArea {
            id: textEditor
            text: "Your code here"
            font.pointSize: 14
            background: Rectangle {
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"
            }
        }
    }

    ToolBar  {
        id: statusBar
        anchors.bottom: parent.bottom
        
        Label {
            text: "Status here"
            font.pointSize: 12
        }
    }

    // Оптимизированная структура сайдбаров
    GridLayout {
        columns: 3
        anchors.fill: parent
        anchors.margins: 5

        // Левый сайдбар
        Pane {
            id: leftSidebar
            Layout.preferredWidth: 150
            Layout.fillHeight: true
            background: Rectangle {
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"
            }

            ColumnLayout {
                spacing: 5
                anchors.fill: parent

                LabeledButton { text: "Project" }
                LabeledButton { text: "Variables" }
                LabeledButton { text: "Functions" }
            }
        }

        // Центральная область
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TextArea {
                text: "Main content area"
                wrapMode: Text.Wrap
            }
        }

        // Правый сайдбар
        Pane {
            id: rightSidebar
            Layout.preferredWidth: 200
            Layout.fillHeight: true
            background: Rectangle {
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"
            }

            ColumnLayout {
                spacing: 5
                anchors.fill: parent

                InfoBlock { title: "Info here" }
                InfoBlock { title: "Code here" }
                InfoBlock { title: "Other info" }
            }
        }
    }
}

