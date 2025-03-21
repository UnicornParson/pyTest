import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import './UnicornUI'

UWindow
{
    id: root
    backgroundElement.color: skin.backgroundColor

    UConsole {
        id: consoleViewer
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        height:parent.height * 0.25
    }

    UPanel {
        id: navPanel
        width: parent.width * 0.25
        background.color: skin.secondBackgroundColor
        background.implicitWidth: width
        anchors {
            left: parent.left
            top: parent.top
            bottom: consoleViewer.top
        }
        Rectangle {
            color: "#252526"
            anchors.fill: parent
        }
        ListView {
            id: listView
            Layout.fillWidth: true
            clip: true
            spacing: 0
            model: tab_controller.buttonModel
            anchors.fill: parent

            delegate: UTextButton {
                id: delegateButton
                height: 24
                font.pointSize: 14
                text: buttonText
                width: ListView.view.width
                backgroundColor: "#3c3c3c"
                borderSize : 0
                borderRadius : 6
                margin: 3
                onClicked: tab_controller.nav_press(tabId, buttonIndex)

                Behavior on opacity {NumberAnimation { duration: 200 }}
                Behavior on height {NumberAnimation { duration: 300 }}
            }


            add: Transition {
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: 300
                }
            }

            remove: Transition {
                NumberAnimation {
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: 300
                }
            }

            ScrollBar.vertical: ScrollBar {
                // policy: ScrollBar.AsNeeded
                policy: ScrollBar.AlwaysOff
                width: 8

                background: Rectangle {
                    color: "#1E1E1E"
                    radius: 2
                }

                contentItem: Rectangle {
                    color: "#A9A9A9"
                    radius: 2
                }
            }
        }
    }
    UPanel
    {
        id: contetnPanel
        background.color : skin.backgroundColor
        anchors {
            left: navPanel.right
            top: parent.top
            bottom: consoleViewer.top
            right: parent.right
        }
        Loader {
            id: contentLoader
            anchors.fill: parent
            source: tab_controller.currentSrc
            onLoaded: console.log("tab changed to " + source)
        }
    }


Component.onCompleted: {
    if(!globals)
    {
        console.error("no globals")
        return
    }
}

}