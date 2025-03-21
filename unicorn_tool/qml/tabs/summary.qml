import QtQuick 2.15
import QtQuick.Controls 2.15
import '../UnicornUI'

UTabContent {
    id: root
    anchors.fill: parent
    
    TableView {
        anchors.fill: parent
        height: root.height
        columnSpacing: 1
        rowSpacing: 1
        clip: true


        model: project.summary_model

        delegate: Rectangle {
            implicitHeight: 24
            implicitWidth: parent.width
            color: "transparent" 
            ULabel {
                
                id: name_label
                text: model.key
                textColor: skin.foregroundColor
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: parent.width / 4
                backgroundColor: "transparent"
            }
            ULabel {
                id: value_label
                text: model.value
                textColor: skin.foregroundColor
                anchors.left: name_label.right
                anchors.right: parent.right
                backgroundColor: "transparent"
                anchors.top: parent.top
                anchors.bottom: parent.bottom 
            }
        }
    }
}

