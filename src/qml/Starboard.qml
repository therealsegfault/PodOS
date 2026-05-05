import QtQuick

Item {
    id: starboard

    ListModel {
        id: appModel
        ListElement { appId: "music";    label: "Music";    sub: "MPD";    icon: "🎵"; color1: "#33ff2d55"; color2: "#1a0a2e" }
        ListElement { appId: "fetch";    label: "Fetch";    sub: "yt-dlp"; icon: "📡"; color1: "#33ff0000"; color2: "#0a1a0a" }
        ListElement { appId: "browser";  label: "Browser";  sub: "Dillo";  icon: "🌐"; color1: "#3300b4d8"; color2: "#0a1628" }
        ListElement { appId: "settings"; label: "Settings"; sub: "podOS";  icon: "⚙️"; color1: "#33636363"; color2: "#1a1a1a" }
        ListElement { appId: "photos";   label: "Photos";   sub: "Gallery";icon: "📷"; color1: "#336c5ce7"; color2: "#12081a" }
        ListElement { appId: "clock";    label: "Clock";    sub: "Time";   icon: "⏰"; color1: "#33fdcb6e"; color2: "#1a1000" }
    }

    PathView {
        id: flow
        anchors.centerIn: parent
        width: parent.width
        height: 400
        model: appModel
        pathItemCount: 5
        preferredHighlightBegin: 0.5
        preferredHighlightEnd: 0.5
        highlightRangeMode: PathView.StrictlyEnforceRange
        focus: true

        Keys.onRightPressed: incrementCurrentIndex()
        Keys.onLeftPressed: decrementCurrentIndex()

        path: Path {
            startX: -60; startY: 200

            PathAttribute { name: "itemScale";   value: 0.55 }
            PathAttribute { name: "itemAngle";   value: 65 }
            PathAttribute { name: "itemOpacity"; value: 0.45 }
            PathAttribute { name: "itemZ";       value: 0 }

            PathLine { x: 180; y: 200 }

            PathAttribute { name: "itemScale";   value: 0.75 }
            PathAttribute { name: "itemAngle";   value: 40 }
            PathAttribute { name: "itemOpacity"; value: 0.75 }
            PathAttribute { name: "itemZ";       value: 5 }

            PathLine { x: 300; y: 200 }

            PathAttribute { name: "itemScale";   value: 1.0 }
            PathAttribute { name: "itemAngle";   value: 0 }
            PathAttribute { name: "itemOpacity"; value: 1.0 }
            PathAttribute { name: "itemZ";       value: 10 }

            PathLine { x: 420; y: 200 }

            PathAttribute { name: "itemScale";   value: 0.75 }
            PathAttribute { name: "itemAngle";   value: -40 }
            PathAttribute { name: "itemOpacity"; value: 0.75 }
            PathAttribute { name: "itemZ";       value: 5 }

            PathLine { x: 660; y: 200 }

            PathAttribute { name: "itemScale";   value: 0.55 }
            PathAttribute { name: "itemAngle";   value: -65 }
            PathAttribute { name: "itemOpacity"; value: 0.45 }
            PathAttribute { name: "itemZ";       value: 0 }
        }

        delegate: Item {
            id: delegateRoot
            width: 260
            height: 320
            z: PathView.itemZ

            property real myAngle:   PathView.itemAngle
            property real myScale:   PathView.itemScale
            property real myOpacity: PathView.itemOpacity
            property bool isCenter:  PathView.isCurrentItem

            scale:   myScale
            opacity: myOpacity

            transform: Rotation {
                origin.x: 130
                origin.y: 130
                axis { x: 0; y: 1; z: 0 }
                angle: delegateRoot.myAngle
            }

            // card
            Rectangle {
                id: card
                width: 260
                height: 260
                radius: 16
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: color1 }
                    GradientStop { position: 1.0; color: color2 }
                }

                Text {
                    anchors.centerIn: parent
                    text: icon
                    font.pixelSize: 86
                }

                // gloss overlay
                Rectangle {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: parent.height * 0.45
                    radius: 16
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#22ffffff" }
                        GradientStop { position: 1.0; color: "#00ffffff" }
                    }
                }
            }

            // reflection
            ShaderEffectSource {
                id: reflectionSource
                sourceItem: card
                width: card.width
                height: card.height
                anchors.top: card.bottom
                anchors.topMargin: 2
                transform: Scale {
                    yScale: -1
                    origin.y: reflectionSource.height / 2
                }
                opacity: 0.0
                visible: false
            }

            Rectangle {
                id: reflectionFade
                anchors.top: card.bottom
                anchors.topMargin: 2
                width: card.width
                height: card.height

                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#00000000" }
                    GradientStop { position: 0.5; color: "#ff000000" }
                }
                z: 2
            }

            ShaderEffectSource {
                sourceItem: card
                width: card.width
                height: card.height
                anchors.top: card.bottom
                anchors.topMargin: 2
                transform: Scale {
                    yScale: -1
                    origin.y: height / 2
                }
                opacity: 0.4
                z: 1
            }

            MouseArea {
                anchors.fill: card
                onClicked: {
                    if (delegateRoot.isCenter) {
                        System.launchApp(appId)
                    } else {
                        flow.currentIndex = index
                    }
                }
            }
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 55
        spacing: 5

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: appModel.get(flow.currentIndex).label
            color: "#ffffff"
            font.pixelSize: 24
            font.weight: Font.Medium
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: appModel.get(flow.currentIndex).sub
            color: "#80ffffff"
            font.pixelSize: 15
        }
    }
}