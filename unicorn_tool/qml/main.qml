import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import QtQuick.Graphics 2.0

Window {
    id: window
    visible: true
    width: 800
    height: 600
    color: "#f5f5f5"

    // Режим окна
    PropertyAlias { windowState: "WindowState" }

    // Тема окна
    property int theme: 0

    // Фон и шрифт
    Rectangle {
        id: background
        color: "#ffffff"
        border.width: 1
        border.color: "#cccccc"
        anchors.fill: parent
    }

    // Menu
    MenuBar {
        id: menuBar
        backgroundColor: "#ffffff"
        border.width: 1
        border.color: "#cccccc"

        MenuItem {
            text: "Open"
            onActivated: {
                window.show()
            }
        }

        MenuItem {
            text: "Save"
            onActivated: {
                // Code for saving
            }
        }

        MenuItem {
            text: "Exit"
            onActivated: {
                window.close()
            }
        }
    }

    // Toolbar
    RowLayout {
        anchors.top: menuBar.bottom

        Item {
            width: 100
            height: 50
            color: "#cccccc"

            Text {
                font.pointSize: 14
                text: "File"
                anchors.centerIn: parent
            }
        }

        Item {
            width: 200
            height: 50
            color: "#cccccc"

            Text {
                font.pointSize: 14
                text: "Edit"
                anchors.centerIn: parent
            }
        }

        Item {
            width: 100
            height: 50
            color: "#cccccc"

            Text {
                font.pointSize: 14
                text: "Help"
                anchors.centerIn: parent
            }
        }
    }

    // Editor
    Rectangle {
        id: editor
        width: 600
        height: 500
        color: "#ffffff"
        border.width: 1
        border.color: "#cccccc"

        TextEdit {
            anchors.fill: parent
            font.pointSize: 14
            text: "Your code here"
        }
    }

    // Status bar
    Rectangle {
        id: statusBar
        width: parent.width
        height: 30
        color: "#ffffff"
        border.width: 1
        border.color: "#cccccc"

        Text {
            anchors.centerIn: parent
            font.pointSize: 12
            text: "Status here"
        }
    }

    // Sidebar
    Rectangle {
        id: sidebar
        width: 150
        height: parent.height - 30
        color: "#ffffff"
        border.width: 1
        border.color: "#cccccc"

        ColumnLayout {
            anchors.centerIn: parent

            Item {
                width: 100
                height: 50
                color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Project"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: 100
                height: 50
                color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Variables"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: 100
                height: 50
                color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Functions"
                    anchors.centerIn: parent
                }
            }
        }
    }

    // Сторона справки
    Rectangle {
        id: infoSidebar
        width: parent.width - sidebar.width
        height: parent.height - 30

        ColumnLayout {
            anchors.centerIn: parent

            Item {
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Info here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Code here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Other info here"
                    anchors.centerIn: parent
                }
            }
        }
    }

    // Сторона окна
    Rectangle {
        id: leftSidebar
        width: sidebar.width
        height: parent.height - 30

        ColumnLayout {
            anchors.top: parent.top

            Item {
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Left side here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "More left side here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: parent.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Even more left side here"
                    anchors.centerIn: parent
                }
            }
        }

        // Сторона сidebar
        RowLayout {
            anchors.bottom: parent.bottom

            Item {
                width: sidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Sidebar here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: sidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "More sidebar here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: sidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Even more sidebar here"
                    anchors.centerIn: parent
                }
            }
        }
    }

    // Сторона справки
    Rectangle {
        id: rightSidebar
        width: infoSidebar.width - sidebar.width
        height: parent.height - 30

        ColumnLayout {
            anchors.bottom: parent.bottom

            Item {
                width: infoSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Info here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: infoSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Code here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: infoSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Other info here"
                    anchors.centerIn: parent
                }
            }
        }
    }

    // Сторона сidebar и справки
    Rectangle {
        id: bottomSidebar
        width: leftSidebar.width + sidebar.width
        height: infoSidebar.height

        ColumnLayout {
            anchors.top: parent.top

            Item {
                width: leftSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Left side here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: leftSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "More left side here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: leftSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Even more left side here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: sidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Sidebar here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: sidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "More sidebar here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: sidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Even more sidebar here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: infoSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Info here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: infoSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Code here"
                    anchors.centerIn: parent
                }
            }

            Item {
                width: infoSidebar.width
                height: 50
                color: "#ffffff"
                border.width: 1
                border.color: "#cccccc"

                Text {
                    font.pointSize: 14
                    text: "Other info here"
                    anchors.centerIn: parent
                }
            }
        }

        // Сторона справки и сidebar
        Rectangle {
            id: bottomSidebarInfo
            width: leftSidebar.width + sidebar.width
            height: infoSidebar.height

            ColumnLayout {
                anchors.bottom: parent.bottom

                Item {
                    width: leftSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Left side here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: leftSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "More left side here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: leftSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Even more left side here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: sidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Sidebar here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: sidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "More sidebar here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: sidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Even more sidebar here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: infoSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Info here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: infoSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Code here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: infoSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Other info here"
                        anchors.centerIn: parent
                    }
                }
            }
        }

        // Сторона справки, сidebar и справка
        Rectangle {
            id: bottomSidebarInfoSidebar
            width: leftSidebar.width + sidebar.width
            height: infoSidebar.height

            ColumnLayout {
                anchors.bottom: parent.bottom

                Item {
                    width: leftSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Left side here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: leftSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "More left side here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: leftSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Even more left side here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: sidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Sidebar here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: sidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "More sidebar here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: sidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Even more sidebar here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: infoSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Info here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: infoSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Code here"
                        anchors.centerIn: parent
                    }
                }

                Item {
                    width: infoSidebar.width
                    height: 50
                    color: "#ffffff"
                    border.width: 1
                    border.color: "#cccccc"

                    Text {
                        font.pointSize: 14
                        text: "Other info here"
                        anchors.centerIn: parent
                    }
                }
            }

            // Сторона справки, сidebar и справка
            Rectangle {
                id: bottomSidebarInfoSidebarInfo
                width: leftSidebar.width + sidebar.width
                height: infoSidebar.height

                ColumnLayout {
                    anchors.bottom: parent.bottom

                    Item {
                        width: leftSidebar.width
                        height: 50
                        color: "#ffffff"
                        border.width: 1
                        border.color: "#cccccc"

                        Text {
                            font.pointSize: 14
                            text: "Left side here"
                            anchors.centerIn: parent
                        }
                    }

                    Item {
                        width: leftSidebar.width
                        height: 50
                        color: "#ffffff"
                        border.width: 1
                        border.color: "#cccccc"

                        Text {
                            font.pointSize: 14
                            text: "More left side here"
                            anchors.centerIn: parent
                        }
                    }

                    Item {
                        width: leftSidebar.width
                        height: 50
                        color: "#ffffff"
                        border.width: 1
                        border.color: "#cccccc"

                        Text {
                            font.pointSize: 14
                            text: "Even more left side here"
                            anchors.centerIn: parent
                        }
                    }

                    Item {
                        width: sidebar.width
                        height: 50
                        color: "#ffffff"
                        border.width: 1
                        border.color: "#cccccc"

                        Text {
                            font.pointSize: 14
                            text: "Sidebar here"
                            anchors.centerIn: parent
                        }
                    }

                    Item {
                        width: sidebar.width
                        height: 50
                        color: "#ffffff"
                        border.width: 1
                        border.color: "#cccccc"
                    }
                }
            }
        }
    }
}