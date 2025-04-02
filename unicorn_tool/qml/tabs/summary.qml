import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import '../UnicornUI'

UTabContent {
    id: root
    anchors.fill: parent
    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth

        ColumnLayout {
            id: columnLayout
            anchors.fill: parent
            spacing: 10 // Optional: space between items

            ULabel {
                id: title
                text: "Summary"
                textColor: skin.foregroundColor
                backgroundColor: "transparent"
                Layout.minimumHeight: 24
                pointSize: 16
            }

            TableView {
                //nchors.fill: parent
                height: (24 + rowSpacing) * project.summary_row_count
                columnSpacing: 1
                rowSpacing: 1
                clip: true
                Layout.alignment: Qt.AlignCenter
                Layout.fillWidth: true

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

            UPanel {
                id: index_panel
                Layout.minimumHeight: 24
                Layout.fillWidth: true
                background.color: skin.secondBackgroundColor
                background.implicitWidth: width
                background.anchors.margins: 3
                border.width :1
                border.color : "#b1b1b1"

                Rectangle {
                    color: "#252526"
                    anchors.fill: parent
                    anchors.margins: 1
                }
                RowLayout {
                    id: indexLayout
                    anchors.fill: parent
                    spacing: 10

                    Text {
                        id: indexTitle

                        //width: background.width - (2 * margin)
                        text: "Index"
                        color: skin.foregroundColor
                        font.pointSize: 14
                        fontSizeMode: Text.Fit
                        Layout.preferredWidth: 60
                        width: 60
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        Component.onCompleted: {
                            console.log("index w ", width)
                        }
                    }

                    // UMarker {}
                    Button {
                        id: indexBtn
                        text: "Reindex"
                        Layout.minimumHeight: 20
                        Layout.preferredWidth: 64
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        palette.buttonText: skin.foregroundColor
                        background: Rectangle {
                            anchors.fill: indexBtn
                            color: indexBtn.pressed ? "#252526" : "#222229"
                            border.color: "#b1b1b1"
                            radius: 5
                        }

                        // Click handler
                        onClicked: {
                            project.runReindex()
                        }
                    }
                    ULed {
                        radius: 6
                        Layout.preferredWidth: radius * 2
                        Layout.minimumHeight: radius * 2
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        visible: false 
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        color: "transparent"
                        height: 20
                    }
                }

            }

        }
    }
}

