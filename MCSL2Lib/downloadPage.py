#     Copyright 2023, MCSL Team, mailto:lxhtt@mcsl.com.cn
#
#     Part of "MCSL2", a simple and multifunctional Minecraft server launcher.
#
#     Licensed under the GNU General Public License, Version 3.0, with our
#     additional agreements. (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        https://github.com/MCSLTeam/MCSL2/raw/master/LICENSE
#
################################################################################
"""
Download page with FastMirror and MCSLAPI.
"""
from os import path

from PyQt5.QtCore import Qt, QSize, QRect, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QSizePolicy,
    QWidget,
    QFrame,
    QGridLayout,
    QVBoxLayout,
    QSpacerItem,
    QStackedWidget,
)
from qfluentwidgets import (
    SmoothScrollArea,
    StrongBodyLabel,
    SubtitleLabel,
    TitleLabel,
    Pivot,
    ToolButton,
    FluentIcon as FIF,
    MessageBox,
    InfoBarPosition,
    InfoBar,
)

from MCSL2Lib.DownloadProgressWidget import DownloadMessageBox
from MCSL2Lib.interfaceController import ChildStackedWidget
from MCSL2Lib.MCSLAPI import FetchMCSLAPIDownloadURLThreadFactory
from MCSL2Lib.FastMirrorAPI import (
    FetchFastMirrorAPIThreadFactory,
    FetchFastMirrorAPICoreVersionThreadFactory,
    FetchFastMirrorAPICoreDownloadThreadFactory,
)
from MCSL2Lib.aria2ClientController import Aria2Controller
from MCSL2Lib.loadingTipWidget import MCSLAPILoadingErrorWidget, MCSLAPILoadingWidget
from MCSL2Lib.singleMCSLAPIDownloadWidget import singleMCSLAPIDownloadWidget
from MCSL2Lib.singleton import Singleton
from MCSL2Lib.variables import (
    GlobalMCSL2Variables,
    DownloadVariables,
    SettingsVariables,
)
from MCSL2Lib.settingsController import SettingsController

settingsController = SettingsController()
downloadVariables = DownloadVariables()
settingsVariables = SettingsVariables()


@Singleton
class DownloadPage(QWidget):
    """下载页"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.fetchMCSLAPIDownloadURLThreadFactory = (
            FetchMCSLAPIDownloadURLThreadFactory()
        )
        self.fetchFastMirrorAPIThreadFactory = FetchFastMirrorAPIThreadFactory()
        self.fetchFastMirrorAPICoreVersionThreadFactory = (
            FetchFastMirrorAPICoreVersionThreadFactory()
        )
        self.fetchFastMirrorAPICoreDownloadThreadFactory = (
            FetchFastMirrorAPICoreDownloadThreadFactory()
        )
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        spacerItem = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.titleLimitWidget = QWidget(self)
        self.titleLimitWidget.setObjectName("titleLimitWidget")

        self.verticalLayout = QVBoxLayout(self.titleLimitWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.titleLabel = TitleLabel(self.titleLimitWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setObjectName("titleLabel")

        self.verticalLayout.addWidget(self.titleLabel)
        self.subTitleLabel = StrongBodyLabel(self.titleLimitWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.subTitleLabel.sizePolicy().hasHeightForWidth()
        )
        self.subTitleLabel.setSizePolicy(sizePolicy)
        self.subTitleLabel.setTextFormat(Qt.MarkdownText)
        self.subTitleLabel.setObjectName("subTitleLabel")

        self.verticalLayout.addWidget(self.subTitleLabel)
        self.gridLayout.addWidget(self.titleLimitWidget, 1, 2, 2, 2)
        spacerItem1 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.downloadStackedWidget = QStackedWidget(self)
        self.downloadStackedWidget.setObjectName("downloadStackedWidget")

        self.downloadWithFastMirror = QWidget()
        self.downloadWithFastMirror.setObjectName("downloadWithFastMirror")

        self.gridLayout_2 = QGridLayout(self.downloadWithFastMirror)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.versionSubtitleLabel = SubtitleLabel(self.downloadWithFastMirror)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.versionSubtitleLabel.sizePolicy().hasHeightForWidth()
        )
        self.versionSubtitleLabel.setSizePolicy(sizePolicy)
        self.versionSubtitleLabel.setObjectName("versionSubtitleLabel")

        self.gridLayout_2.addWidget(self.versionSubtitleLabel, 0, 1, 1, 1)
        self.coreListSmoothScrollArea = SmoothScrollArea(self.downloadWithFastMirror)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.coreListSmoothScrollArea.sizePolicy().hasHeightForWidth()
        )
        self.coreListSmoothScrollArea.setSizePolicy(sizePolicy)
        self.coreListSmoothScrollArea.setMinimumSize(QSize(200, 0))
        self.coreListSmoothScrollArea.setMaximumSize(QSize(200, 16777215))
        self.coreListSmoothScrollArea.setFrameShape(QFrame.NoFrame)
        self.coreListSmoothScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.coreListSmoothScrollArea.setWidgetResizable(True)
        self.coreListSmoothScrollArea.setObjectName("coreListSmoothScrollArea")

        self.coreListScrollAreaWidgetContents = QWidget()
        self.coreListScrollAreaWidgetContents.setGeometry(QRect(0, 0, 200, 349))
        self.coreListScrollAreaWidgetContents.setObjectName(
            "coreListScrollAreaWidgetContents"
        )

        self.verticalLayout_14 = QVBoxLayout(self.coreListScrollAreaWidgetContents)
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_14.setObjectName("verticalLayout_14")

        self.coreListLayout = QVBoxLayout()
        self.coreListLayout.setObjectName("coreListLayout")

        self.verticalLayout_14.addLayout(self.coreListLayout)
        self.coreListSmoothScrollArea.setWidget(self.coreListScrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.coreListSmoothScrollArea, 1, 0, 1, 1)
        self.buildSubtitleLabel = SubtitleLabel(self.downloadWithFastMirror)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.buildSubtitleLabel.sizePolicy().hasHeightForWidth()
        )
        self.buildSubtitleLabel.setSizePolicy(sizePolicy)
        self.buildSubtitleLabel.setObjectName("buildSubtitleLabel")
        self.gridLayout_2.addWidget(self.buildSubtitleLabel, 0, 2, 1, 1)
        self.coreListSubtitleLabel = SubtitleLabel(self.downloadWithFastMirror)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.coreListSubtitleLabel.sizePolicy().hasHeightForWidth()
        )
        self.coreListSubtitleLabel.setSizePolicy(sizePolicy)
        self.coreListSubtitleLabel.setObjectName("coreListSubtitleLabel")
        self.gridLayout_2.addWidget(self.coreListSubtitleLabel, 0, 0, 1, 1)
        self.versionSmoothScrollArea = SmoothScrollArea(self.downloadWithFastMirror)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.versionSmoothScrollArea.sizePolicy().hasHeightForWidth()
        )
        self.versionSmoothScrollArea.setSizePolicy(sizePolicy)
        self.versionSmoothScrollArea.setMinimumSize(QSize(160, 0))
        self.versionSmoothScrollArea.setMaximumSize(QSize(160, 16777215))
        self.versionSmoothScrollArea.setFrameShape(QFrame.NoFrame)
        self.versionSmoothScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.versionSmoothScrollArea.setWidgetResizable(True)
        self.versionSmoothScrollArea.setObjectName("versionSmoothScrollArea")

        self.versionScrollAreaWidgetContents = QWidget()
        self.versionScrollAreaWidgetContents.setGeometry(QRect(0, 0, 160, 349))
        self.versionScrollAreaWidgetContents.setObjectName(
            "versionScrollAreaWidgetContents"
        )

        self.verticalLayout_13 = QVBoxLayout(self.versionScrollAreaWidgetContents)
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_13.setObjectName("verticalLayout_13")

        self.versionLayout = QVBoxLayout()
        self.versionLayout.setObjectName("versionLayout")

        self.verticalLayout_13.addLayout(self.versionLayout)
        self.versionSmoothScrollArea.setWidget(self.versionScrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.versionSmoothScrollArea, 1, 1, 1, 1)
        self.refreshFastMirrorAPIBtn = ToolButton(self.downloadWithFastMirror)
        self.refreshFastMirrorAPIBtn.setObjectName("refreshFastMirrorAPIBtn")

        self.gridLayout_2.addWidget(self.refreshFastMirrorAPIBtn, 0, 3, 1, 1)
        self.buildScrollArea = SmoothScrollArea(self.downloadWithFastMirror)
        self.buildScrollArea.setMinimumSize(QSize(304, 0))
        self.buildScrollArea.setFrameShape(QFrame.NoFrame)
        self.buildScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.buildScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.buildScrollArea.setWidgetResizable(True)
        self.buildScrollArea.setObjectName("buildScrollArea")

        self.buildScrollAreaWidgetContents = QWidget()
        self.buildScrollAreaWidgetContents.setGeometry(QRect(0, 0, 346, 349))
        self.buildScrollAreaWidgetContents.setObjectName(
            "buildScrollAreaWidgetContents"
        )

        self.verticalLayout_2 = QVBoxLayout(self.buildScrollAreaWidgetContents)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.buildLayout = QVBoxLayout()
        self.buildLayout.setObjectName("buildLayout")

        self.verticalLayout_2.addLayout(self.buildLayout)
        self.buildScrollArea.setWidget(self.buildScrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.buildScrollArea, 1, 2, 1, 2)
        self.downloadStackedWidget.addWidget(self.downloadWithFastMirror)
        self.downloadWithMCSLAPI = QWidget()
        self.downloadWithMCSLAPI.setObjectName("downloadWithMCSLAPI")

        self.gridLayout_3 = QGridLayout(self.downloadWithMCSLAPI)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.MCSLAPIPivot = Pivot(self.downloadWithMCSLAPI)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MCSLAPIPivot.sizePolicy().hasHeightForWidth())
        self.MCSLAPIPivot.setSizePolicy(sizePolicy)
        self.MCSLAPIPivot.setFixedSize(QSize(210, 45))
        self.MCSLAPIPivot.setObjectName("MCSLAPIPivot")

        self.gridLayout_3.addWidget(self.MCSLAPIPivot, 0, 0, 1, 1)
        spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem2, 0, 1, 1, 1)
        self.MCSLAPIStackedWidget = ChildStackedWidget(self.downloadWithMCSLAPI)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIStackedWidget.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIStackedWidget.setSizePolicy(sizePolicy)
        self.MCSLAPIStackedWidget.setMinimumSize(QSize(676, 336))
        self.MCSLAPIStackedWidget.setMaximumSize(QSize(16777215, 16777215))
        self.MCSLAPIStackedWidget.setObjectName("MCSLAPIStackedWidget")

        self.MCSLAPIJava = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MCSLAPIJava.sizePolicy().hasHeightForWidth())
        self.MCSLAPIJava.setSizePolicy(sizePolicy)
        self.MCSLAPIJava.setObjectName("MCSLAPIJava")

        self.verticalLayout_3 = QVBoxLayout(self.MCSLAPIJava)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.MCSLAPIJavaScrollArea = SmoothScrollArea(self.MCSLAPIJava)
        self.MCSLAPIJavaScrollArea.setWidgetResizable(True)
        self.MCSLAPIJavaScrollArea.setObjectName("MCSLAPIJavaScrollArea")

        self.MCSLAPIJavaScrollAreaWidgetContents = QWidget()
        self.MCSLAPIJavaScrollAreaWidgetContents.setGeometry(QRect(0, 0, 698, 348))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIJavaScrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIJavaScrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.MCSLAPIJavaScrollAreaWidgetContents.setObjectName(
            "MCSLAPIJavaScrollAreaWidgetContents"
        )

        self.verticalLayout_8 = QVBoxLayout(self.MCSLAPIJavaScrollAreaWidgetContents)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")

        self.MCSLAPIJavaScrollAreaLayout = QVBoxLayout()
        self.MCSLAPIJavaScrollAreaLayout.setObjectName("MCSLAPIJavaScrollAreaLayout")

        self.verticalLayout_8.addLayout(self.MCSLAPIJavaScrollAreaLayout)
        self.MCSLAPIJavaScrollArea.setWidget(self.MCSLAPIJavaScrollAreaWidgetContents)
        self.verticalLayout_3.addWidget(self.MCSLAPIJavaScrollArea)
        self.MCSLAPIStackedWidget.addWidget(self.MCSLAPIJava)
        self.MCSLAPISpigot = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPISpigot.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPISpigot.setSizePolicy(sizePolicy)
        self.MCSLAPISpigot.setObjectName("MCSLAPISpigot")

        self.verticalLayout_4 = QVBoxLayout(self.MCSLAPISpigot)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.MCSLAPISpigotScrollArea = SmoothScrollArea(self.MCSLAPISpigot)
        self.MCSLAPISpigotScrollArea.setWidgetResizable(True)
        self.MCSLAPISpigotScrollArea.setObjectName("MCSLAPISpigotScrollArea")

        self.MCSLAPISpigotScrollAreaWidgetContents = QWidget()
        self.MCSLAPISpigotScrollAreaWidgetContents.setGeometry(QRect(0, 0, 698, 348))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPISpigotScrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPISpigotScrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.MCSLAPISpigotScrollAreaWidgetContents.setObjectName(
            "MCSLAPISpigotScrollAreaWidgetContents"
        )

        self.verticalLayout_9 = QVBoxLayout(self.MCSLAPISpigotScrollAreaWidgetContents)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")

        self.MCSLAPISpigotScrollAreaLayout = QVBoxLayout()
        self.MCSLAPISpigotScrollAreaLayout.setObjectName(
            "MCSLAPISpigotScrollAreaLayout"
        )

        self.verticalLayout_9.addLayout(self.MCSLAPISpigotScrollAreaLayout)
        self.MCSLAPISpigotScrollArea.setWidget(
            self.MCSLAPISpigotScrollAreaWidgetContents
        )
        self.verticalLayout_4.addWidget(self.MCSLAPISpigotScrollArea)
        self.MCSLAPIStackedWidget.addWidget(self.MCSLAPISpigot)
        self.MCSLAPIPaper = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MCSLAPIPaper.sizePolicy().hasHeightForWidth())
        self.MCSLAPIPaper.setSizePolicy(sizePolicy)
        self.MCSLAPIPaper.setObjectName("MCSLAPIPaper")

        self.verticalLayout_5 = QVBoxLayout(self.MCSLAPIPaper)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.MCSLAPIPaperScrollArea = SmoothScrollArea(self.MCSLAPIPaper)
        self.MCSLAPIPaperScrollArea.setWidgetResizable(True)
        self.MCSLAPIPaperScrollArea.setObjectName("MCSLAPIPaperScrollArea")

        self.MCSLAPIPaperScrollAreaWidgetContents = QWidget()
        self.MCSLAPIPaperScrollAreaWidgetContents.setGeometry(QRect(0, 0, 698, 348))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIPaperScrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIPaperScrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.MCSLAPIPaperScrollAreaWidgetContents.setObjectName(
            "MCSLAPIPaperScrollAreaWidgetContents"
        )

        self.verticalLayout_10 = QVBoxLayout(self.MCSLAPIPaperScrollAreaWidgetContents)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.MCSLAPIPaperScrollAreaLayout = QVBoxLayout()
        self.MCSLAPIPaperScrollAreaLayout.setObjectName("MCSLAPIPaperScrollAreaLayout")

        self.verticalLayout_10.addLayout(self.MCSLAPIPaperScrollAreaLayout)
        self.MCSLAPIPaperScrollArea.setWidget(self.MCSLAPIPaperScrollAreaWidgetContents)
        self.verticalLayout_5.addWidget(self.MCSLAPIPaperScrollArea)
        self.MCSLAPIStackedWidget.addWidget(self.MCSLAPIPaper)
        self.MCSLAPIBungeeCord = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIBungeeCord.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIBungeeCord.setSizePolicy(sizePolicy)
        self.MCSLAPIBungeeCord.setObjectName("MCSLAPIBungeeCord")

        self.verticalLayout_6 = QVBoxLayout(self.MCSLAPIBungeeCord)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.MCSLAPIBungeeCordScrollArea = SmoothScrollArea(self.MCSLAPIBungeeCord)
        self.MCSLAPIBungeeCordScrollArea.setWidgetResizable(True)
        self.MCSLAPIBungeeCordScrollArea.setObjectName("MCSLAPIBungeeCordScrollArea")

        self.MCSLAPIBungeeCordScrollAreaWidgetContents = QWidget()
        self.MCSLAPIBungeeCordScrollAreaWidgetContents.setGeometry(
            QRect(0, 0, 698, 348)
        )
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIBungeeCordScrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIBungeeCordScrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.MCSLAPIBungeeCordScrollAreaWidgetContents.setObjectName(
            "MCSLAPIBungeeCordScrollAreaWidgetContents"
        )

        self.verticalLayout_11 = QVBoxLayout(
            self.MCSLAPIBungeeCordScrollAreaWidgetContents
        )
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")

        self.MCSLAPIBungeeCordScrollAreaLayout = QVBoxLayout()
        self.MCSLAPIBungeeCordScrollAreaLayout.setObjectName(
            "MCSLAPIBungeeCordScrollAreaLayout"
        )

        self.verticalLayout_11.addLayout(self.MCSLAPIBungeeCordScrollAreaLayout)
        self.MCSLAPIBungeeCordScrollArea.setWidget(
            self.MCSLAPIBungeeCordScrollAreaWidgetContents
        )
        self.verticalLayout_6.addWidget(self.MCSLAPIBungeeCordScrollArea)
        self.MCSLAPIStackedWidget.addWidget(self.MCSLAPIBungeeCord)
        self.MCSLAPIOfficialCore = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIOfficialCore.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIOfficialCore.setSizePolicy(sizePolicy)
        self.MCSLAPIOfficialCore.setObjectName("MCSLAPIOfficialCore")

        self.verticalLayout_7 = QVBoxLayout(self.MCSLAPIOfficialCore)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")

        self.MCSLAPIOfficialCoreScrollArea = SmoothScrollArea(self.MCSLAPIOfficialCore)
        self.MCSLAPIOfficialCoreScrollArea.setWidgetResizable(True)
        self.MCSLAPIOfficialCoreScrollArea.setObjectName(
            "MCSLAPIOfficialCoreScrollArea"
        )
        self.MCSLAPIOfficialCoreScrollAreaWidgetContents = QWidget()
        self.MCSLAPIOfficialCoreScrollAreaWidgetContents.setGeometry(
            QRect(0, 0, 98, 28)
        )
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.MCSLAPIOfficialCoreScrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.MCSLAPIOfficialCoreScrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.MCSLAPIOfficialCoreScrollAreaWidgetContents.setObjectName(
            "MCSLAPIOfficialCoreScrollAreaWidgetContents"
        )

        self.verticalLayout_12 = QVBoxLayout(
            self.MCSLAPIOfficialCoreScrollAreaWidgetContents
        )
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")

        self.MCSLAPIOfficialCoreScrollAreaLayout = QVBoxLayout()
        self.MCSLAPIOfficialCoreScrollAreaLayout.setObjectName(
            "MCSLAPIOfficialCoreScrollAreaLayout"
        )

        self.verticalLayout_12.addLayout(self.MCSLAPIOfficialCoreScrollAreaLayout)
        self.MCSLAPIOfficialCoreScrollArea.setWidget(
            self.MCSLAPIOfficialCoreScrollAreaWidgetContents
        )
        self.verticalLayout_7.addWidget(self.MCSLAPIOfficialCoreScrollArea)
        self.MCSLAPIStackedWidget.addWidget(self.MCSLAPIOfficialCore)
        self.gridLayout_3.addWidget(self.MCSLAPIStackedWidget, 1, 0, 1, 3)
        self.refreshMCSLAPIBtn = ToolButton(FIF.UPDATE, self.downloadWithMCSLAPI)
        self.refreshMCSLAPIBtn.setObjectName("refreshMCSLAPIBtn")

        self.gridLayout_3.addWidget(self.refreshMCSLAPIBtn, 0, 2, 1, 1)
        self.downloadStackedWidget.addWidget(self.downloadWithMCSLAPI)
        self.gridLayout.addWidget(self.downloadStackedWidget, 3, 2, 1, 1)
        dsList = [self.downloadWithFastMirror, self.downloadWithMCSLAPI]
        self.downloadStackedWidget.setCurrentWidget(
            dsList[
                settingsVariables.downloadSourceList.index(
                    settingsController.fileSettings["downloadSource"]
                )
            ]
        )

        self.setObjectName("DownloadInterface")

        self.titleLabel.setText("下载")
        self.subTitleLabel.setText("Aria2引擎高速驱动！")
        self.coreListSubtitleLabel.setText("核心列表")
        self.versionSubtitleLabel.setText("游戏版本")
        self.buildSubtitleLabel.setText("构建列表")

        self.coreListSmoothScrollArea.setAttribute(Qt.WA_StyledBackground)
        self.MCSLAPIPivot.addItem(
            routeKey="MCSLAPIJava",
            text="Java环境",
            onClick=lambda: self.MCSLAPIStackedWidget.setCurrentWidget(
                self.MCSLAPIJava
            ),
        )
        self.MCSLAPIPivot.addItem(
            routeKey="MCSLAPISpigot",
            text="Spigot核心",
            onClick=lambda: self.MCSLAPIStackedWidget.setCurrentWidget(
                self.MCSLAPISpigot
            ),
        )
        self.MCSLAPIPivot.addItem(
            routeKey="MCSLAPIPaper",
            text="Paper核心",
            onClick=lambda: self.MCSLAPIStackedWidget.setCurrentWidget(
                self.MCSLAPIPaper
            ),
        )
        self.MCSLAPIPivot.addItem(
            routeKey="MCSLAPIBungeeCord",
            text="BungeeCord代理",
            onClick=lambda: self.MCSLAPIStackedWidget.setCurrentWidget(
                self.MCSLAPIBungeeCord
            ),
        )
        self.MCSLAPIPivot.addItem(
            routeKey="MCSLAPIOfficialCore",
            text="Vanilla核心",
            onClick=lambda: self.MCSLAPIStackedWidget.setCurrentWidget(
                self.MCSLAPIOfficialCore
            ),
        )
        self.MCSLAPILayoutList = [
            self.MCSLAPIJavaScrollAreaLayout,
            self.MCSLAPISpigotScrollAreaLayout,
            self.MCSLAPIPaperScrollAreaLayout,
            self.MCSLAPIBungeeCordScrollAreaLayout,
            self.MCSLAPIOfficialCoreScrollAreaLayout,
        ]
        self.MCSLAPIJavaScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.MCSLAPISpigotScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.MCSLAPIPaperScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.MCSLAPIBungeeCordScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.MCSLAPIOfficialCoreScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.coreListSmoothScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.versionSmoothScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.buildScrollArea.viewport().setStyleSheet(
            GlobalMCSL2Variables.scrollAreaViewportQss
        )
        self.MCSLAPIPivot.setCurrentItem("MCSLAPIJava")
        self.MCSLAPIStackedWidget.currentChanged.connect(self.refreshDownloads)
        self.refreshMCSLAPIBtn.clicked.connect(self.getMCSLAPI)
        self.refreshMCSLAPIBtn.setEnabled(False)

    @pyqtSlot(int)
    def onPageChangedRefresh(self, currentChanged):
        """刷新下载列表触发"""
        if currentChanged == 3:
            self.refreshDownloads()
        else:
            pass

    def refreshDownloads(self):
        """刷新下载页面主逻辑"""
        # FastMirror
        if self.downloadStackedWidget.currentIndex() == 0:
            if downloadVariables.FastMirrorAPIDict:
                # init
                pass
            else:
                self.getFastMirrorAPI()
        # MCSLAPI
        elif self.downloadStackedWidget.currentIndex() == 1:
            # 如果存在列表且不为空,则不再重新获取
            if downloadVariables.MCSLAPIDownloadUrlDict:
                idx = self.MCSLAPIStackedWidget.currentIndex()
                if (
                    str(
                        downloadVariables.MCSLAPIDownloadUrlDict[idx][
                            "downloadFileTitles"
                        ]
                    )
                    != "-2"
                    or str(
                        downloadVariables.MCSLAPIDownloadUrlDict[idx][
                            "downloadFileTitles"
                        ]
                    )
                    != "-1"
                ):
                    self.initMCSLAPIDownloadWidget(n=idx)
                else:
                    self.showMCSLAPIFailedWidget()
            else:
                self.getMCSLAPI()
                self.refreshMCSLAPIBtn.setEnabled(False)

    def getMCSLAPI(self):
        """请求MCSLAPI"""
        workThread = self.fetchMCSLAPIDownloadURLThreadFactory.create(
            _singleton=True, finishSlot=self.updateMCSLAPIDownloadUrlDict
        )
        if workThread.isRunning():
            self.refreshMCSLAPIBtn.setEnabled(False)
            return
        else:
            for layout in self.MCSLAPILayoutList:
                for i in reversed(range(layout.count())):
                    layout.itemAt(i).widget().setParent(None)
                layout.addWidget(MCSLAPILoadingWidget())
            workThread.start()
            self.refreshMCSLAPIBtn.setEnabled(False)

    @pyqtSlot(dict)
    def updateMCSLAPIDownloadUrlDict(self, _downloadUrlDict: dict):
        """更新获取MCSLAPI结果"""
        downloadVariables.MCSLAPIDownloadUrlDict.update(_downloadUrlDict)
        idx = self.MCSLAPIStackedWidget.currentIndex()
        if (
            str(downloadVariables.MCSLAPIDownloadUrlDict[idx]["downloadFileTitles"])
            != "-2"
            or str(downloadVariables.MCSLAPIDownloadUrlDict[idx]["downloadFileTitles"])
            != "-1"
        ):
            self.initMCSLAPIDownloadWidget(n=idx)
        else:
            self.showMCSLAPIFailedWidget()

    def showMCSLAPIFailedWidget(self):
        layout = self.MCSLAPILayoutList[self.MCSLAPIStackedWidget.currentIndex()]
        for i2 in reversed(range(layout.count())):
            layout.itemAt(i2).widget().setParent(None)
        layout.addWidget(MCSLAPILoadingErrorWidget())
        self.refreshMCSLAPIBtn.setEnabled(True)

    def getFastMirrorAPI(self):
        """请求FastMirror API"""
        workThread = self.fetchFastMirrorAPIThreadFactory.create(
            _singleton=True, finishSlot=self.updateFastMirrorAPIDict
        )
        if workThread.isRunning():
            self.refreshFastMirrorAPIBtn.setEnabled(False)
            return
        else:
            # for layout in self.MCSLAPILayoutList:
            #     for i in reversed(range(layout.count())):
            #         layout.itemAt(i).widget().setParent(None)
            #     layout.addWidget(MCSLAPILoadingWidget())
            workThread.start()
            self.refreshFastMirrorAPIBtn.setEnabled(False)

    def getFastMirrorAPICoreVersion(self, name, mcVersion):
        """请求FastMirror API 核心的版本"""
        workThread = self.fetchFastMirrorAPICoreVersionThreadFactory.create(
            name=name,
            mcVersion=mcVersion,
            _singleton=True,
            finishSlot=self.updateFFastMirrorAPICoreVersionDict,
        )
        if workThread.isRunning():
            self.refreshFastMirrorAPIBtn.setEnabled(False)
            return
        else:
            # for layout in self.MCSLAPILayoutList:
            #     for i in reversed(range(layout.count())):
            #         layout.itemAt(i).widget().setParent(None)
            #     layout.addWidget(MCSLAPILoadingWidget())
            workThread.start()
            self.refreshFastMirrorAPIBtn.setEnabled(False)

    def getFastMirrorAPIRealCoreDownloadURL(self, name, mcVersion, coreVersion):
        """请求FastMirror API 下载链接"""
        workThread = self.fetchFastMirrorAPICoreDownloadThreadFactory.create(
            name=name,
            mcVersion=mcVersion,
            coreVersion=coreVersion,
            _singleton=True,
            finishSlot=self.updateFastMirrorAPIRealCoreDownloadURL,
        )
        if workThread.isRunning():
            self.refreshFastMirrorAPIBtn.setEnabled(False)
            return
        else:
            # for layout in self.MCSLAPILayoutList:
            #     for i in reversed(range(layout.count())):
            #         layout.itemAt(i).widget().setParent(None)
            #     layout.addWidget(MCSLAPILoadingWidget())
            workThread.start()
            self.refreshFastMirrorAPIBtn.setEnabled(False)

    @pyqtSlot(dict)
    def updateFastMirrorAPIDict(self, _APIDict: dict):
        """更新获取FastMirrorAPI结果"""
        downloadVariables.FastMirrorAPIDict.update(_APIDict)

    @pyqtSlot(dict)
    def updateFFastMirrorAPICoreVersionDict(self, _APICoreVersionDict: dict):
        """更新获取FastMirrorAPI结果"""
        downloadVariables.FastMirrorAPICoreVersionDict.update(_APICoreVersionDict)

    @pyqtSlot(str)
    def updateFastMirrorAPIRealCoreDownloadURL(self, _realCoreDownloadURL: str):
        """更新获取FastMirrorAPI结果"""
        downloadVariables.FastMirrorAPIRealCoreDownloadURL = _realCoreDownloadURL

    def showFastMirrorFailedTip(self):
        InfoBar.error(
            title="错误",
            content="获取FastMirror API失败！\n尝试检查一下网络？",
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2222,
            parent=self,
        )

    @staticmethod
    def getMCSLAPIDownloadIcon(downloadType):
        """设置MCSLAPI源图标"""
        if downloadType == 0:
            return QPixmap(":/built-InIcons/Java.svg")
        elif downloadType == 1:
            return QPixmap(":/built-InIcons/Spigot.svg")
        elif downloadType == 2:
            return QPixmap(":/built-InIcons/Paper.png")
        elif downloadType == 3:
            return QPixmap(":/built-InIcons/Spigot.svg")
        elif downloadType == 4:
            return QPixmap(":/built-InIcons/Grass.png")
        else:
            return QPixmap(":/built-InIcons/MCSL2.png")

    def initMCSLAPIDownloadWidget(self, n: int):
        """
        初始化MCSLAPI模式下的UI\n
        n 代表第几种类型\n
        下方循环的 i 代表次数
        """
        # 先把旧的清空，但是必须先删除Spacer
        for layout in self.MCSLAPILayoutList:
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

        self.refreshMCSLAPIBtn.setEnabled(True)
        try:
            if (
                type(downloadVariables.MCSLAPIDownloadUrlDict[n]["downloadFileTitles"])
                == list
            ):
                for i in range(
                    len(
                        downloadVariables.MCSLAPIDownloadUrlDict[n][
                            "downloadFileTitles"
                        ]
                    )
                ):
                    self.tmpSingleMCSLAPIDownloadWidget = singleMCSLAPIDownloadWidget()
                    self.tmpSingleMCSLAPIDownloadWidget.MCSLAPIPixmapLabel.setPixmap(
                        self.getMCSLAPIDownloadIcon(downloadType=n)
                    )
                    self.tmpSingleMCSLAPIDownloadWidget.MCSLAPIPixmapLabel.setFixedSize(
                        QSize(60, 60)
                    )
                    self.tmpSingleMCSLAPIDownloadWidget.fileTitle.setText(
                        downloadVariables.MCSLAPIDownloadUrlDict[n][
                            "downloadFileTitles"
                        ][i]
                    )
                    self.tmpSingleMCSLAPIDownloadWidget.fileName.setText(
                        f"{downloadVariables.MCSLAPIDownloadUrlDict[n]['downloadFileNames'][i]}.{downloadVariables.MCSLAPIDownloadUrlDict[n]['downloadFileFormats'][i]}"
                    )
                    self.tmpSingleMCSLAPIDownloadWidget.setObjectName(
                        f"DownloadWidget{i}..{n}"
                    )
                    self.tmpSingleMCSLAPIDownloadWidget.MCSLAPIDownloadBtn.setObjectName(
                        f"DownloadBtn{i}..{n}"
                    )
                    self.tmpSingleMCSLAPIDownloadWidget.MCSLAPIDownloadBtn.clicked.connect(
                        self.downloadMCSLAPIFile
                    )
                    self.MCSLAPILayoutList[n].addWidget(
                        self.tmpSingleMCSLAPIDownloadWidget
                    )
            else:
                self.showMCSLAPIFailedWidget()
        except TypeError:
            self.showMCSLAPIFailedWidget()

    def downloadMCSLAPIFile(self):
        """下载MCSLAPI文件"""
        sender = self.sender()
        idx = int(sender.objectName().split("..")[-1])
        idx2 = int(sender.objectName().split("..")[0].split("n")[-1])
        url = downloadVariables.MCSLAPIDownloadUrlDict[idx]["downloadFileURLs"][idx2]
        name = downloadVariables.MCSLAPIDownloadUrlDict[idx]["downloadFileNames"][idx2]
        format = downloadVariables.MCSLAPIDownloadUrlDict[idx]["downloadFileFormats"][
            idx2
        ]
        titles = downloadVariables.MCSLAPIDownloadUrlDict[idx]["downloadFileTitles"][
            idx2
        ]

        if not Aria2Controller.testAria2Service():
            if not Aria2Controller.startAria2():
                box = MessageBox(title="无法下载", content="Aria2可能未安装或启动失败", parent=self)
                box.exec()
                return
        box = DownloadMessageBox(f"{name}.{format}", parent=self)
        box.DownloadWidget().closeBoxBtnFinished.clicked.connect(box.close)
        box.DownloadWidget().closeBoxBtnFailed.clicked.connect(box.close)

        # 判断文件是否存在
        if path.exists(
            path.join("MCSL2", "Downloads", f"{name}.{format}")
        ) and not path.exists(
            path.join("MCSL2", "Downloads", f"{name}.{format}.aria2")
        ):
            print("文件已存在")
            box.show()
            box.onDownloadExist()
        else:
            gid = Aria2Controller.download(
                uri=url,
                watch=True,
                info_get=box.onInfoGet,
                stopped=box.onDownloadFinished,
                interval=0.2,
            )
            box.canceled.connect(lambda: Aria2Controller.cancelDownloadTask(gid))
            box.paused.connect(
                lambda x: Aria2Controller.pauseDownloadTask(gid)
                if x
                else Aria2Controller.resumeDownloadTask(gid)
            )
            box.show()
