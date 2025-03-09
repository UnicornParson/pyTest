// LabeledButton.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property string text
    width: 140
    height: 40

    Button {
        anchors.fill: parent
        background: Rectangle {
            color: "#eeeeee"
            radius: 5
        }
    }

    Text {
        text: parent.text
        anchors.centerIn: parent
        font.pointSize: 14
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}