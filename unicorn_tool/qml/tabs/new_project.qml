import QtQuick 2.15
import QtQuick.Controls 2.15
import '../UnicornUI'

UTabContent {
    id: root
    anchors.fill: parent
    Text {
        text: "new project tab"
        font.pixelSize: 24
        anchors.centerIn: parent
        color: skin.foregroundColor
    }

}