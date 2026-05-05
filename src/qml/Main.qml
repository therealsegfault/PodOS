import QtQuick
import QtQuick.Window

Window {
    id: root
    width: 600
    height: 800
    visible: true
    title: "podOS"

    Rectangle {
        anchors.fill: parent
        color: "#000000"

        Item {
            id: statusBar
            width: parent.width
            height: 28
            z: 100

            Text {
                id: clock
                anchors.centerIn: parent
                text: Qt.formatTime(new Date(), "hh:mm")
                color: "#ffffff"
                font.pixelSize: 13
                font.weight: Font.Medium

                Timer {
                    interval: 10000
                    running: true
                    repeat: true
                    onTriggered: clock.text = Qt.formatTime(new Date(), "hh:mm")
                }
            }

            Text {
                anchors.right: parent.right
                anchors.rightMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                text: System.battery + "%"
                color: "#b3ffffff"
                font.pixelSize: 11
            }

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                text: System.wifi
                color: "#b3ffffff"
                font.pixelSize: 11
            }
        }

        Starboard {
            anchors.fill: parent
        }
    }
}