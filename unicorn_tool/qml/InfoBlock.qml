// InfoBlock.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Pane {
    property string title
    Layout.fillWidth: true
    implicitHeight: 80

    background: Rectangle {
        color: "#f8f8f8"
        border.width: 1
        border.color: "#dddddd"
    }

    contentItem: Text {
        text: parent.title
        font.pointSize: 14
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
