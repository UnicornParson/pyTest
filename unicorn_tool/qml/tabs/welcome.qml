import QtQuick 2.15
import QtQuick.Controls 2.15
import '../UnicornUI'

UTabContent {
    id: root
    anchors.fill: parent
    Column {
        anchors.centerIn: parent
        spacing: 20

        Image {
            id: logo
            source: "../img/UnicornUILogo.png"
            width: root.width / 3
            height: root.height / 3
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: "UNICORN PROJECT TOOL"
            font.pixelSize: 24
            anchors.horizontalCenter: parent.horizontalCenter
            color: skin.foregroundColor
        }
    }
}
