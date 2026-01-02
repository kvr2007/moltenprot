# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QGridLayout,
    QGroupBox, QLabel, QLayout, QLineEdit,
    QSizePolicy, QSpinBox, QTabWidget, QTextBrowser,
    QToolBox, QVBoxLayout, QWidget)

class Ui_moltenProtToolBoxDialog(object):
    def setupUi(self, moltenProtToolBoxDialog):
        if not moltenProtToolBoxDialog.objectName():
            moltenProtToolBoxDialog.setObjectName(u"moltenProtToolBoxDialog")
        moltenProtToolBoxDialog.setWindowModality(Qt.ApplicationModal)
        moltenProtToolBoxDialog.resize(693, 422)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(moltenProtToolBoxDialog.sizePolicy().hasHeightForWidth())
        moltenProtToolBoxDialog.setSizePolicy(sizePolicy)
        moltenProtToolBoxDialog.setModal(True)
        self.buttonBox = QDialogButtonBox(moltenProtToolBoxDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(330, 360, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok|QDialogButtonBox.RestoreDefaults)
        self.moltenprotToolBox = QToolBox(moltenProtToolBoxDialog)
        self.moltenprotToolBox.setObjectName(u"moltenprotToolBox")
        self.moltenprotToolBox.setGeometry(QRect(20, 20, 651, 331))
        self.importPage = QWidget()
        self.importPage.setObjectName(u"importPage")
        self.importPage.setGeometry(QRect(0, 0, 651, 183))
        self.importGroupBox = QGroupBox(self.importPage)
        self.importGroupBox.setObjectName(u"importGroupBox")
        self.importGroupBox.setGeometry(QRect(0, 0, 651, 231))
        self.importTabs = QTabWidget(self.importGroupBox)
        self.importTabs.setObjectName(u"importTabs")
        self.importTabs.setGeometry(QRect(10, 30, 651, 191))
        self.CSV = QWidget()
        self.CSV.setObjectName(u"CSV")
        self.gridLayoutWidget = QWidget(self.CSV)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 631, 111))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.separatorLabel = QLabel(self.gridLayoutWidget)
        self.separatorLabel.setObjectName(u"separatorLabel")

        self.gridLayout.addWidget(self.separatorLabel, 0, 0, 1, 1)

        self.denaturantLabel = QLabel(self.gridLayoutWidget)
        self.denaturantLabel.setObjectName(u"denaturantLabel")

        self.gridLayout.addWidget(self.denaturantLabel, 0, 2, 1, 1)

        self.scanRateLabel = QLabel(self.gridLayoutWidget)
        self.scanRateLabel.setObjectName(u"scanRateLabel")

        self.gridLayout.addWidget(self.scanRateLabel, 0, 3, 1, 1)

        self.separatorInput = QLineEdit(self.gridLayoutWidget)
        self.separatorInput.setObjectName(u"separatorInput")

        self.gridLayout.addWidget(self.separatorInput, 1, 0, 1, 1)

        self.denaturantComboBox = QComboBox(self.gridLayoutWidget)
        self.denaturantComboBox.addItem("")
        self.denaturantComboBox.addItem("")
        self.denaturantComboBox.setObjectName(u"denaturantComboBox")

        self.gridLayout.addWidget(self.denaturantComboBox, 1, 2, 1, 1)

        self.scanRateSpinBox = QDoubleSpinBox(self.gridLayoutWidget)
        self.scanRateSpinBox.setObjectName(u"scanRateSpinBox")
        self.scanRateSpinBox.setMinimum(0.100000000000000)
        self.scanRateSpinBox.setMaximum(100.000000000000000)
        self.scanRateSpinBox.setSingleStep(0.100000000000000)
        self.scanRateSpinBox.setValue(1.000000000000000)

        self.gridLayout.addWidget(self.scanRateSpinBox, 1, 3, 1, 1)

        self.decimalSeparatorInput = QLineEdit(self.gridLayoutWidget)
        self.decimalSeparatorInput.setObjectName(u"decimalSeparatorInput")
        self.decimalSeparatorInput.setMaxLength(1)

        self.gridLayout.addWidget(self.decimalSeparatorInput, 1, 1, 1, 1)

        self.decimalLabel = QLabel(self.gridLayoutWidget)
        self.decimalLabel.setObjectName(u"decimalLabel")

        self.gridLayout.addWidget(self.decimalLabel, 0, 1, 1, 1)

        self.spectrumCsvCheckBox = QCheckBox(self.gridLayoutWidget)
        self.spectrumCsvCheckBox.setObjectName(u"spectrumCsvCheckBox")

        self.gridLayout.addWidget(self.spectrumCsvCheckBox, 2, 0, 1, 1)

        self.importTabs.addTab(self.CSV, "")
        self.widget = QWidget()
        self.widget.setObjectName(u"widget")
        self.gridLayoutWidget_2 = QWidget(self.widget)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(100, 30, 172, 80))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.layoutWidget = QWidget(self.widget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 601, 101))
        self.gridLayout_3 = QGridLayout(self.layoutWidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.layoutWidget)
        self.textBrowser.setObjectName(u"textBrowser")

        self.gridLayout_3.addWidget(self.textBrowser, 0, 0, 3, 1)

        self.refoldingCheckBox = QCheckBox(self.layoutWidget)
        self.refoldingCheckBox.setObjectName(u"refoldingCheckBox")

        self.gridLayout_3.addWidget(self.refoldingCheckBox, 0, 1, 1, 1)

        self.rawCheckBox = QCheckBox(self.layoutWidget)
        self.rawCheckBox.setObjectName(u"rawCheckBox")

        self.gridLayout_3.addWidget(self.rawCheckBox, 1, 1, 1, 1)

        self.pantaCheckBox = QCheckBox(self.layoutWidget)
        self.pantaCheckBox.setObjectName(u"pantaCheckBox")

        self.gridLayout_3.addWidget(self.pantaCheckBox, 2, 1, 1, 1)

        self.importTabs.addTab(self.widget, "")
        self.moltenprotToolBox.addItem(self.importPage, u"Import")
        self.exportPage = QWidget()
        self.exportPage.setObjectName(u"exportPage")
        self.exportPage.setGeometry(QRect(0, 0, 651, 183))
        self.exportGroupBox = QGroupBox(self.exportPage)
        self.exportGroupBox.setObjectName(u"exportGroupBox")
        self.exportGroupBox.setGeometry(QRect(0, 0, 651, 181))
        self.verticalLayoutWidget = QWidget(self.exportGroupBox)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(9, 27, 311, 151))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.outputFormatLabel = QLabel(self.verticalLayoutWidget)
        self.outputFormatLabel.setObjectName(u"outputFormatLabel")

        self.verticalLayout.addWidget(self.outputFormatLabel)

        self.outputFormatComboBox = QComboBox(self.verticalLayoutWidget)
        self.outputFormatComboBox.addItem("")
        self.outputFormatComboBox.addItem("")
        self.outputFormatComboBox.addItem(u"XLSX")
        self.outputFormatComboBox.setObjectName(u"outputFormatComboBox")

        self.verticalLayout.addWidget(self.outputFormatComboBox)

        self.outputReportTypeLabel = QLabel(self.verticalLayoutWidget)
        self.outputReportTypeLabel.setObjectName(u"outputReportTypeLabel")

        self.verticalLayout.addWidget(self.outputReportTypeLabel)

        self.outputReportComboBox = QComboBox(self.verticalLayoutWidget)
        self.outputReportComboBox.addItem("")
        self.outputReportComboBox.addItem("")
        self.outputReportComboBox.addItem("")
        self.outputReportComboBox.addItem("")
        self.outputReportComboBox.setObjectName(u"outputReportComboBox")
        self.outputReportComboBox.setEnabled(True)

        self.verticalLayout.addWidget(self.outputReportComboBox)

        self.moltenprotToolBox.addItem(self.exportPage, u"Export")
        self.miscSettings = QWidget()
        self.miscSettings.setObjectName(u"miscSettings")
        self.miscSettings.setGeometry(QRect(0, 0, 651, 183))
        self.verticalLayoutWidget_2 = QWidget(self.miscSettings)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, -2, 180, 181))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.parallelSpinBoxLabel = QLabel(self.verticalLayoutWidget_2)
        self.parallelSpinBoxLabel.setObjectName(u"parallelSpinBoxLabel")

        self.verticalLayout_2.addWidget(self.parallelSpinBoxLabel)

        self.parallelSpinBox = QSpinBox(self.verticalLayoutWidget_2)
        self.parallelSpinBox.setObjectName(u"parallelSpinBox")
        self.parallelSpinBox.setEnabled(True)
        self.parallelSpinBox.setMinimum(1)

        self.verticalLayout_2.addWidget(self.parallelSpinBox)

        self.colormapForPlotLabel = QLabel(self.verticalLayoutWidget_2)
        self.colormapForPlotLabel.setObjectName(u"colormapForPlotLabel")

        self.verticalLayout_2.addWidget(self.colormapForPlotLabel)

        self.colormapForPlotComboBox = QComboBox(self.verticalLayoutWidget_2)
        self.colormapForPlotComboBox.setObjectName(u"colormapForPlotComboBox")

        self.verticalLayout_2.addWidget(self.colormapForPlotComboBox)

        self.moltenprotToolBox.addItem(self.miscSettings, u"Misc.")
        self.PlotSettings = QWidget()
        self.PlotSettings.setObjectName(u"PlotSettings")
        self.PlotSettings.setGeometry(QRect(0, 0, 651, 183))
        self.layoutWidget1 = QWidget(self.PlotSettings)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(0, 0, 621, 165))
        self.gridLayout_4 = QGridLayout(self.layoutWidget1)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.curveTypeLabel = QLabel(self.layoutWidget1)
        self.curveTypeLabel.setObjectName(u"curveTypeLabel")

        self.gridLayout_4.addWidget(self.curveTypeLabel, 0, 0, 1, 1)

        self.curveTypeLabel_2 = QLabel(self.layoutWidget1)
        self.curveTypeLabel_2.setObjectName(u"curveTypeLabel_2")

        self.gridLayout_4.addWidget(self.curveTypeLabel_2, 0, 1, 1, 1)

        self.curveTypeLabel_3 = QLabel(self.layoutWidget1)
        self.curveTypeLabel_3.setObjectName(u"curveTypeLabel_3")

        self.gridLayout_4.addWidget(self.curveTypeLabel_3, 0, 2, 1, 1)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.curveTypeComboBox = QComboBox(self.layoutWidget1)
        self.curveTypeComboBox.addItem("")
        self.curveTypeComboBox.addItem("")
        self.curveTypeComboBox.setObjectName(u"curveTypeComboBox")

        self.verticalLayout_5.addWidget(self.curveTypeComboBox)

        self.curveViewLabel = QLabel(self.layoutWidget1)
        self.curveViewLabel.setObjectName(u"curveViewLabel")

        self.verticalLayout_5.addWidget(self.curveViewLabel)

        self.curveViewComboBox = QComboBox(self.layoutWidget1)
        self.curveViewComboBox.addItem("")
        self.curveViewComboBox.addItem("")
        self.curveViewComboBox.addItem("")
        self.curveViewComboBox.setObjectName(u"curveViewComboBox")

        self.verticalLayout_5.addWidget(self.curveViewComboBox)

        self.curveHeatmapColorCheckBox = QCheckBox(self.layoutWidget1)
        self.curveHeatmapColorCheckBox.setObjectName(u"curveHeatmapColorCheckBox")

        self.verticalLayout_5.addWidget(self.curveHeatmapColorCheckBox)


        self.gridLayout_4.addLayout(self.verticalLayout_5, 1, 0, 1, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.curveBaselineCheckBox = QCheckBox(self.layoutWidget1)
        self.curveBaselineCheckBox.setObjectName(u"curveBaselineCheckBox")

        self.verticalLayout_3.addWidget(self.curveBaselineCheckBox)

        self.curveVlinesCheckBox = QCheckBox(self.layoutWidget1)
        self.curveVlinesCheckBox.setObjectName(u"curveVlinesCheckBox")

        self.verticalLayout_3.addWidget(self.curveVlinesCheckBox)

        self.curveMarkEverySpinBoxLabel = QLabel(self.layoutWidget1)
        self.curveMarkEverySpinBoxLabel.setObjectName(u"curveMarkEverySpinBoxLabel")

        self.verticalLayout_3.addWidget(self.curveMarkEverySpinBoxLabel)

        self.curveMarkEverySpinBox = QSpinBox(self.layoutWidget1)
        self.curveMarkEverySpinBox.setObjectName(u"curveMarkEverySpinBox")
        self.curveMarkEverySpinBox.setMinimum(1)

        self.verticalLayout_3.addWidget(self.curveMarkEverySpinBox)


        self.gridLayout_4.addLayout(self.verticalLayout_3, 1, 1, 1, 1)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.curveDerivativeCheckBox = QCheckBox(self.layoutWidget1)
        self.curveDerivativeCheckBox.setObjectName(u"curveDerivativeCheckBox")

        self.verticalLayout_4.addWidget(self.curveDerivativeCheckBox)

        self.label = QLabel(self.layoutWidget1)
        self.label.setObjectName(u"label")

        self.verticalLayout_4.addWidget(self.label)

        self.curveLegendComboBox = QComboBox(self.layoutWidget1)
        self.curveLegendComboBox.addItem("")
        self.curveLegendComboBox.addItem("")
        self.curveLegendComboBox.addItem("")
        self.curveLegendComboBox.setObjectName(u"curveLegendComboBox")

        self.verticalLayout_4.addWidget(self.curveLegendComboBox)


        self.gridLayout_4.addLayout(self.verticalLayout_4, 1, 2, 1, 1)

        self.moltenprotToolBox.addItem(self.PlotSettings, u"Plots")

        self.retranslateUi(moltenProtToolBoxDialog)
        self.buttonBox.accepted.connect(moltenProtToolBoxDialog.accept)
        self.buttonBox.rejected.connect(moltenProtToolBoxDialog.reject)
        self.buttonBox.clicked.connect(moltenProtToolBoxDialog.reject)

        self.moltenprotToolBox.setCurrentIndex(3)
        self.importTabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(moltenProtToolBoxDialog)
    # setupUi

    def retranslateUi(self, moltenProtToolBoxDialog):
        moltenProtToolBoxDialog.setWindowTitle(QCoreApplication.translate("moltenProtToolBoxDialog", u"MoltenProt settings", None))
#if QT_CONFIG(tooltip)
        moltenProtToolBoxDialog.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.importPage.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Set up how files are imported", None))
#endif // QT_CONFIG(tooltip)
        self.importGroupBox.setTitle(QCoreApplication.translate("moltenProtToolBoxDialog", u"Data import settings", None))
#if QT_CONFIG(tooltip)
        self.importTabs.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.separatorLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Separator:", None))
        self.denaturantLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Denaturation:", None))
        self.scanRateLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Scan rate:", None))
#if QT_CONFIG(tooltip)
        self.separatorInput.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Set *.csv file separator (default comma)", None))
#endif // QT_CONFIG(tooltip)
        self.separatorInput.setInputMask(QCoreApplication.translate("moltenProtToolBoxDialog", u"xx", None))
        self.separatorInput.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u",", None))
        self.denaturantComboBox.setItemText(0, QCoreApplication.translate("moltenProtToolBoxDialog", u"Temperature (C)", None))
        self.denaturantComboBox.setItemText(1, QCoreApplication.translate("moltenProtToolBoxDialog", u"Temperature (K)", None))

#if QT_CONFIG(tooltip)
        self.denaturantComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Set how protein was denatured (temperature in C or K)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.scanRateSpinBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Set scan rate in degrees per minute; this option is only relevant for kinetic models.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.decimalSeparatorInput.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Set *.csv file decimal separator (default dot)", None))
#endif // QT_CONFIG(tooltip)
        self.decimalSeparatorInput.setInputMask(QCoreApplication.translate("moltenProtToolBoxDialog", u"x", None))
        self.decimalSeparatorInput.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u".", None))
        self.decimalLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Decimal Separator:", None))
#if QT_CONFIG(tooltip)
        self.spectrumCsvCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"If checked, the columns in the input CSV will be treated as separate wavelengths of a spectrum", None))
#endif // QT_CONFIG(tooltip)
        self.spectrumCsvCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Spectrum (e.g. CD)", None))
        self.importTabs.setTabText(self.importTabs.indexOf(self.CSV), QCoreApplication.translate("moltenProtToolBoxDialog", u"CSV", None))
        self.textBrowser.setHtml(QCoreApplication.translate("moltenProtToolBoxDialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Noto Sans'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">How to obtain an input XLSX file:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">&gt; export &quot;processed&quot; data from the manufacturer's soft"
                        "ware</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">&gt; in the Overview sheet provide sample annotations (will be shown in the GUI)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">&gt; optionally, provide per-sample dCp values by creating an extra column with name &quot;dCp&quot;</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">Parsing of an XLSX file may take a lon"
                        "g time, consider saving a MoltenProt session to JSON right after import.</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.refoldingCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Indicate if refolding ramp was used", None))
#endif // QT_CONFIG(tooltip)
        self.refoldingCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Refolding data", None))
#if QT_CONFIG(tooltip)
        self.rawCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"<html><head/><body><p>Indicate if this is raw or processed data</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.rawCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Raw data", None))
#if QT_CONFIG(tooltip)
        self.pantaCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"<html><head/><body><p>Indicate if data was exported from the newer machine</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pantaCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Panta rhei (testing)", None))
        self.importTabs.setTabText(self.importTabs.indexOf(self.widget), QCoreApplication.translate("moltenProtToolBoxDialog", u"XLSX", None))
        self.moltenprotToolBox.setItemText(self.moltenprotToolBox.indexOf(self.importPage), QCoreApplication.translate("moltenProtToolBoxDialog", u"Import", None))
#if QT_CONFIG(tooltip)
        self.exportPage.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Set output options", None))
#endif // QT_CONFIG(tooltip)
        self.exportGroupBox.setTitle(QCoreApplication.translate("moltenProtToolBoxDialog", u"Data export settings", None))
        self.outputFormatLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Data format:", None))
        self.outputFormatComboBox.setItemText(0, QCoreApplication.translate("moltenProtToolBoxDialog", u"None", None))
        self.outputFormatComboBox.setItemText(1, QCoreApplication.translate("moltenProtToolBoxDialog", u"CSV", None))

#if QT_CONFIG(tooltip)
        self.outputFormatComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Select output format for raw and processed data as well as fit results", None))
#endif // QT_CONFIG(tooltip)
        self.outputReportTypeLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Report format:", None))
        self.outputReportComboBox.setItemText(0, QCoreApplication.translate("moltenProtToolBoxDialog", u"None", None))
        self.outputReportComboBox.setItemText(1, QCoreApplication.translate("moltenProtToolBoxDialog", u"PDF", None))
        self.outputReportComboBox.setItemText(2, QCoreApplication.translate("moltenProtToolBoxDialog", u"Summary (XLSX)", None))
        self.outputReportComboBox.setItemText(3, QCoreApplication.translate("moltenProtToolBoxDialog", u"Interactive (HTML)", None))

#if QT_CONFIG(tooltip)
        self.outputReportComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Summarize the results in a report", None))
#endif // QT_CONFIG(tooltip)
        self.moltenprotToolBox.setItemText(self.moltenprotToolBox.indexOf(self.exportPage), QCoreApplication.translate("moltenProtToolBoxDialog", u"Export", None))
        self.parallelSpinBoxLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Parallel processes:", None))
#if QT_CONFIG(tooltip)
        self.parallelSpinBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"If your computer has several cores, select number of cores used to process your data. ", None))
#endif // QT_CONFIG(tooltip)
        self.colormapForPlotLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Colormap for heatmap:", None))
#if QT_CONFIG(tooltip)
        self.colormapForPlotComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Matplotlib colormap to color buttons in the result heatmap", None))
#endif // QT_CONFIG(tooltip)
        self.moltenprotToolBox.setItemText(self.moltenprotToolBox.indexOf(self.miscSettings), QCoreApplication.translate("moltenProtToolBoxDialog", u"Misc.", None))
        self.curveTypeLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Display curve:", None))
        self.curveTypeLabel_2.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Additional elements:", None))
        self.curveTypeLabel_3.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Subplots:", None))
        self.curveTypeComboBox.setItemText(0, QCoreApplication.translate("moltenProtToolBoxDialog", u"Experimental signal", None))
        self.curveTypeComboBox.setItemText(1, QCoreApplication.translate("moltenProtToolBoxDialog", u"Baseline-corrected", None))

#if QT_CONFIG(tooltip)
        self.curveTypeComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Which data to plot", None))
#endif // QT_CONFIG(tooltip)
        self.curveViewLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Display as:", None))
        self.curveViewComboBox.setItemText(0, QCoreApplication.translate("moltenProtToolBoxDialog", u"Datapoints + Fit", None))
        self.curveViewComboBox.setItemText(1, QCoreApplication.translate("moltenProtToolBoxDialog", u"Datapoints", None))
        self.curveViewComboBox.setItemText(2, QCoreApplication.translate("moltenProtToolBoxDialog", u"Fit", None))

#if QT_CONFIG(tooltip)
        self.curveViewComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"How to plot data", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.curveHeatmapColorCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Color curves based on the heatmap button colors", None))
#endif // QT_CONFIG(tooltip)
        self.curveHeatmapColorCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Use heatmap color", None))
#if QT_CONFIG(tooltip)
        self.curveBaselineCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Show pre- and post-transition baselines", None))
#endif // QT_CONFIG(tooltip)
        self.curveBaselineCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Baselines", None))
#if QT_CONFIG(tooltip)
        self.curveVlinesCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Show fit parameters that are on X-axis (e.g. Tm)", None))
#endif // QT_CONFIG(tooltip)
        self.curveVlinesCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Vertical lines", None))
        self.curveMarkEverySpinBoxLabel.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Show every:", None))
#if QT_CONFIG(tooltip)
        self.curveMarkEverySpinBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Plot every n'th experimental datapoint", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.curveDerivativeCheckBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"Show smoothened experimental derivative in a separate plot", None))
#endif // QT_CONFIG(tooltip)
        self.curveDerivativeCheckBox.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Derivative plot", None))
        self.label.setText(QCoreApplication.translate("moltenProtToolBoxDialog", u"Legend:", None))
        self.curveLegendComboBox.setItemText(0, QCoreApplication.translate("moltenProtToolBoxDialog", u"None", None))
        self.curveLegendComboBox.setItemText(1, QCoreApplication.translate("moltenProtToolBoxDialog", u"ID", None))
        self.curveLegendComboBox.setItemText(2, QCoreApplication.translate("moltenProtToolBoxDialog", u"Annotation", None))

#if QT_CONFIG(tooltip)
        self.curveLegendComboBox.setToolTip(QCoreApplication.translate("moltenProtToolBoxDialog", u"How to display the legend", None))
#endif // QT_CONFIG(tooltip)
        self.moltenprotToolBox.setItemText(self.moltenprotToolBox.indexOf(self.PlotSettings), QCoreApplication.translate("moltenProtToolBoxDialog", u"Plots", None))
    # retranslateUi

