// LabeledButton.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    Theme {
        id: theme
    }

    width: 100
    height: 40
    text: "TEXT"
/*
    transitions: [
        Transition {
            fromState: "!hovered"
            toState: "hovered"
            animations: [
                ColorAnimation {
                    target: background
                    property: "color"
                    from: theme.backgroundColor
                    to: theme.selectedItemBackgroundColor
                    duration: 200
                    easing.type: Easing.OutQuad
                },
                ColorAnimation {
                    target: contentItem.children[0]
                    property: "color"
                    from: theme.foregroundColor
                    to: theme.selectedItemForegroundColor
                    duration: 200
                    easing.type: Easing.OutQuad
                }
            ]
        },
        Transition {
            fromState: "hovered"
            toState: "!hovered"
            animations: [
                ColorAnimation {
                    target: background
                    property: "color"
                    from: theme.selectedItemBackgroundColor
                    to: theme.backgroundColor
                    duration: 200
                    easing.type: Easing.OutQuad
                },
                ColorAnimation {
                    target: contentItem.children[0]
                    property: "color"
                    from: theme.selectedItemForegroundColor
                    to: theme.foregroundColor
                    duration: 200
                    easing.type: Easing.OutQuad
                }
            ]
        }
    ]
*/
    background: Rectangle {
        implicitWidth: 100
        implicitHeight: 40
        color: parent.hovered ? theme.selectedItemBackgroundColor : theme.backgroundColor
        border.color: theme.borderColor
        border.width: 1
        radius: 5 
    }

    contentItem: Row {
        spacing: 8
        anchors.centerIn: parent
        Text {
            text: "TEXT" //parent.text
            font.pointSize: 14
            
            color: parent.hovered ? theme.selectedItemForegroundColor : theme.foregroundColor
            verticalAlignment: Text.AlignVCenter
        }
    }
}
