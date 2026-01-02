# -*- coding: utf-8 -*-
'Implments a graphical interface for MoltenProt'
# Copyright 2018-2021,2025 Vadim Kotov, Thomas C. Marlovits
#
#   This file is part of MoltenProt.
#
#    MoltenProt is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#    MoltenProt is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#    along with MoltenProt.  If not, see <https://www.gnu.org/licenses/>.

# handling exceptions
import sys
import os
# For printing line number and file name
from inspect import currentframe, getframeinfo
import traceback
# get the current date and time (GUI progressbar)
import time
# for passing clicked button ID's
from functools import partial

# For platform description
import platform

# Data processing modules
import pandas as pd
import numpy as np

# Graphics module.
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
# A cycler for color-safe 8-color palette from https://jfly.uni-koeln.de/color/
from cycler import cycler

# import GUI libraries
# try:
from PySide6.QtCore import (
    QThread,
    QThreadPool,
    QRunnable,
    QObject,
    Signal,
    Slot,
    QAbstractTableModel,
    Qt,
    QFile,
    # QTextStream,# for text logging, disabled
    QSettings,
    QEvent,
    QUrl,
    QFileInfo,
    QSize,
    QTranslator,
    QLocale,
)
from PySide6.QtGui import (
    QColor,
    QIcon,
    QKeySequence,
    #QPalette,
    QFont,
    QAction,
    QPixmap,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QDialog,
    QLabel,
    QComboBox,
    QToolBar,
    QWidget,
    QTableWidgetItem,
    QTextBrowser,
    QListView,
    QAbstractItemView,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QFileDialog,
    QFontDialog,
    QApplication,
    QSplashScreen,
    # QDesktopWidget, # removed in Qt6
    QProgressBar,
    QHeaderView,
    QItemDelegate,
)

# reading ui files
# https://doc.qt.io/qtforpython-6/tutorials/basictutorial/uifiles.html#option-b-loading-it-directly
from PySide6.QtUiTools import QUiLoader

# version of GUI library used
from PySide6.QtCore import __version__ as GUI_VERSION_STR

# core MoltenProt functions
from moltenprot import core

# widgets (also initializes QRC resources)
from moltenprot.ui.main import Ui_MainWindow
from moltenprot.ui.analysis import Ui_analysisDialog
from moltenprot.ui.settings import Ui_moltenProtToolBoxDialog
from moltenprot.ui.layout import Ui_layoutDialog

cf = currentframe()
cfFilename = getframeinfo(cf).filename

# check if core can do parallelization and set cpuCount
if core.parallelization:
    from multiprocessing import cpu_count
    cpuCount = cpu_count()
else:
    cpuCount = 1


showVersionInformation = False
if showVersionInformation:
    core.showVersionInformation()

# Color-safe 8-color palette from https://jfly.uni-koeln.de/color/
colorsafe_cycler = cycler(
    color=[
        "#0077B8",
        "#F4640D",
        "#FAA200",
        "#00B7EC",
        "#00A077",
        "#F4E635",
        "#E37DAC",
        "#242424",
    ]
)

# collect basic information to be presented in the About window
mp_version = str(core.__version__)
# check if running from PyInstaller bundle and add info to version
if core.from_pyinstaller:
    mp_version += " (PyInstaller bundle)"

ABOUT_HTML =f"""<b>MoltenProt</b> v. {mp_version}
        <p>Copyright &copy; 2018-2021,2025 Vadim Kotov, Thomas C. Marlovits
        <p>A robust toolkit for assessment and optimization of protein (thermo)stability.
        <p>Python {platform.python_version()} - PySide {GUI_VERSION_STR} - Matplotlib {matplotlib.__version__} on {platform.system()}"""

def load_uic(infile: str, parent):
    "Loads a UI file and attaches to the parent; for caveats between PyQt and PySide see https://www.pythonguis.com/faq/pyqt6-vs-pyside6/"
    uifile = QFile(infile)
    try:
        uifile.open(QFile.ReadOnly)
        return QUiLoader().load(uifile, parent)
    finally:
        uifile.close()


class ExportThread(QThread):
    'Customized threading'
    exportThreadSignal = Signal(str)

    def __init__(self, parent=None):
        'Initialize'
        QThread.__init__(self, parent)
        print(type(parent))

    def run(self):
        'example run function'
        for i in range(1, 21):
            self.sleep(3)
            self.exportThreadSignal.emit("i = %s" % i)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class ExportWorker(QRunnable):
    """
    Worker thread - runs data export in a separate thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, *args, **kwargs):
        'initializes the instance'
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            moltenProtFitMultiple = self.args[0]
            print("Running export thread", type(self.signals.progress))
            moltenProtFitMultiple.WriteOutputAll(**self.kwargs)
            self.signals.progress.emit(1)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done


class MoltenProtHelpDialog(QDialog):
    r"""
    ##  \brief This class implements Help Dialog of MoltenProt.
    #     \details Simpliest help system. Help information should be placed in subdirectory with name "help".

    """

    def __init__(self, parent=None):
        r"""
        ##  \brief MoltenProtHelpDialog constructor.
        #     \details MoltenProtHelpDialog is created programmaticaly, not from ui file. Create simple text browser with two navgation buttons - Home and Back.
        #                   Information about Html help files location should be placed in resources.qrc
        #   <qresource>
        #       <file alias="editmenu.html">help/editmenu.html</file>
        #       <file alias="filemenu.html">help/filemenu.html</file>
        #       <file alias="index.html">help/index.html</file>
        #   </qresource>
        #    \param page - Initial html page.
        """
        super().__init__(parent)
        self.setWindowTitle("MoltenProt Help")

        backAction = QAction(QIcon(":/back.svgz"), self.tr("&Back"), self)
        backAction.setShortcut(QKeySequence.Back)
        homeAction = QAction(QIcon(":/home.svgz"), self.tr("&Home"), self)
        homeAction.setShortcut(self.tr("Home"))
        self.pageLabel = QLabel()

        toolBar = QToolBar()
        toolBar.addAction(backAction)
        toolBar.addAction(homeAction)
        toolBar.addWidget(self.pageLabel)
        toolBar.setToolTip("toolBar.setToolTip")
        self.textBrowser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(toolBar)
        layout.addWidget(self.textBrowser, 1)
        self.setLayout(layout)

        # self.connect(backAction, SIGNAL("triggered()"), self.textBrowser, SLOT("backward()"))
        # QtCore.QObject.connect(backAction, SIGNAL("triggered()"), self.textBrowser, SLOT("backward()"))
        backAction.triggered.connect(self.textBrowser.backward)
        # backAction.triggered.connect()
        # self.connect(homeAction, SIGNAL("triggered()"), self.textBrowser, SLOT("home()"))
        homeAction.triggered.connect(self.textBrowser.home)
        # self.connect(self.textBrowser, SIGNAL("sourceChanged(QUrl)"), self.updatePageTitle)
        self.textBrowser.sourceChanged.connect(self.updatePageTitle)

        self.textBrowser.setSearchPaths([":/"])
        # explicitly searching in QRC https://forum.qt.io/topic/106828/
        self.textBrowser.setSource(QUrl("qrc:/index.html"))
        self.resize(400, 600)

    def updatePageTitle(self):
        r'##  \brief  Show page title according to selected help item.'
        self.pageLabel.setText(self.textBrowser.documentTitle())


class LayoutDialog(QDialog, Ui_layoutDialog):
    r"""
                ##  \brief This class implements Layout Dialog of MoltenProt.
    #     \details Dialog description is located in layout-designer.ui file. This file can be edited in Qt designer. The following command should be issued after editing layout-designer.ui file :
    #   - pyside-uic -o ui_layout.py      layout_designer.ui

    """

    def __init__(self):
        'create an instance'
        super().__init__()
        self.setupUi(self)
        # Method myAccept will be called when user pressed Ok button
        self.buttonBox.accepted.connect(self.myAccept)
        # Method myReject will be called when user pressed Cancel button
        self.buttonBox.rejected.connect(self.myReject)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        blankAction = QAction("Blank", self)
        blankAction.triggered.connect(self.on_blankAction)
        self.addAction(blankAction)

        # NOTE not implemented in main module, currently disabled
        #referenceAction = QAction("Reference", self)
        #referenceAction.triggered.connect(self.on_refAction)
        #self.addAction(referenceAction)

        ignoreAction = QAction("Ignore", self)
        ignoreAction.triggered.connect(self.on_ignoreAction)
        self.addAction(ignoreAction)

        clearSelectedAction = QAction("Clear selected cells", self)
        clearSelectedAction.triggered.connect(self.on_clearSelectedAction)
        self.addAction(clearSelectedAction)

    @Slot()
    def on_blankAction(self):
        'set text in selected cells to Blank'
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            currentQTableWidgetItem.setText("Blank")

    @Slot()
    def on_refAction(self):
        'set text in selected cells to Reference - TODO'
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            currentQTableWidgetItem.setText("Reference")

    @Slot()
    def on_ignoreAction(self):
        'set text in selected cells to Ignore'
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            currentQTableWidgetItem.setText("Ignore")
    
    @Slot()
    def on_clearSelectedAction(self):
        'clear text in selected cells'
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            currentQTableWidgetItem.setText("")

    @Slot()
    def myAccept(self):
        'when dialog accepted'
        if showVersionInformation:
            print("myAccept")
        # Hide dialog
        self.close()

    def myReject(self):
        'when dialog rejected'
        if showVersionInformation:
            print("myReject")
        # Hide dialog
        self.close()


class moltenProtToolBox(QDialog, Ui_moltenProtToolBoxDialog):
    r"##  \brief This class implements export/import and the other settings toolbox dialog of MoltenProt."

    def __init__(self, parent=None):
        'Initialize the object and connect callbacks'
        super().__init__(parent)
        if parent == None:
            print("parent == None", cfFilename, currentframe().f_lineno)
        self.parent = parent
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.myAccept)
        self.buttonBox.rejected.connect(self.myReject)
        self.buttonBox.clicked["QAbstractButton*"].connect(self.buttonClicked)
        self.parallelSpinBox.setMaximum(cpuCount - 1)
        self.settings = QSettings()
        self.restoreSettingsValues()

    # @Slot()
    def buttonClicked(self, button):
        'when a button was clicked'
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            self.resetToDefaults()

    @Slot()
    def myAccept(self):
        'when dialog accepted'
        self.settings.setValue(
            "toolbox/importSettingsPage/separatorInputText",
            self.separatorInput.text(),
        )
        self.settings.setValue(
            "toolbox/importSettingsPage/decimalSeparatorInputText",
            self.decimalSeparatorInput.text(),
        )
        self.settings.setValue(
            "toolbox/importSettingsPage/denaturantComboBoxIndex",
            self.denaturantComboBox.currentIndex(),
        )
        self.settings.setValue(
            "toolbox/importSettingsPage/scanRateSpinBoxValue",
            self.scanRateSpinBox.value(),
        )

        self.settings.setValue(
            "toolbox/importSettingsPage/spectrumCsvCheckBox",
            int(self.spectrumCsvCheckBox.isChecked()),
        )

        self.settings.setValue(
            "toolbox/importSettingsPage/refoldingCheckBox",
            int(self.refoldingCheckBox.isChecked()),
        )

        self.settings.setValue(
            "toolbox/importSettingsPage/rawCheckBox",
            int(self.rawCheckBox.isChecked()),
        )

        self.settings.setValue(
            "toolbox/importSettingsPage/pantaCheckBox",
            int(self.pantaCheckBox.isChecked()),
        )

        self.settings.setValue(
            "toolbox/exportSettingsPage/outputFormatComboBoxIndex",
            self.outputFormatComboBox.currentIndex(),
        )
        self.settings.setValue(
            "toolbox/exportSettingsPage/outputReportComboBoxIndex",
            self.outputReportComboBox.currentIndex(),
        )

        self.settings.setValue(
            "toolbox/miscSettingsPage/parallelSpinBox", self.parallelSpinBox.value()
        )
        self.settings.setValue(
            "toolbox/miscSettingsPage/colormapForPlotComboBoxIndex",
            self.colormapForPlotComboBox.currentIndex(),
        )

        self.settings.setValue(
            "toolbox/plotSettingsPage/curveVlinesCheckBox",
            int(self.curveVlinesCheckBox.isChecked()),
        )
        self.settings.setValue(
            "toolbox/plotSettingsPage/curveBaselineCheckBox",
            int(self.curveBaselineCheckBox.isChecked()),
        )
        self.settings.setValue(
            "toolbox/plotSettingsPage/curveDerivativeCheckBox",
            int(self.curveDerivativeCheckBox.isChecked()),
        )

        self.settings.setValue(
            "toolbox/plotSettingsPage/curveHeatmapColorCheckBox",
            int(self.curveHeatmapColorCheckBox.isChecked()),
        )

        self.settings.setValue(
            "toolbox/plotSettingsPage/curveLegendComboBox",
            self.curveLegendComboBox.currentIndex(),
        )
        self.settings.setValue(
            "toolbox/plotSettingsPage/curveMarkEverySpinBoxValue",
            self.curveMarkEverySpinBox.value(),
        )
        self.settings.setValue(
            "toolbox/plotSettingsPage/curveTypeComboboxIndex",
            self.curveTypeComboBox.currentIndex(),
        )
        self.settings.setValue(
            "toolbox/plotSettingsPage/curveViewComboboxIndex",
            self.curveViewComboBox.currentIndex(),
        )

        self.close()

    @Slot()
    def myReject(self):
        'when dialog rejected'
        self.restoreSettingsValues()
        self.close()

    def restoreSettingsValues(self):
        'restores values of settings'
        index = int(
            self.settings.value("toolbox/importSettingsPage/denaturantComboBoxIndex", 0)
        )
        self.denaturantComboBox.setCurrentIndex(index)
        text = self.settings.value("toolbox/importSettingsPage/separatorInputText", ",")
        self.separatorInput.setText(text)
        text = self.settings.value(
            "toolbox/importSettingsPage/decimalSeparatorInputText", "."
        )
        self.decimalSeparatorInput.setText(text)
        value = float(
            self.settings.value("toolbox/importSettingsPage/scanRateSpinBoxValue", 1.0)
        )
        self.scanRateSpinBox.setValue(value)
        isChecked = int(
            self.settings.value("toolbox/importSettingsPage/refoldingCheckBox", 0)
        )
        self.refoldingCheckBox.setChecked(isChecked)
        isChecked = int(
            self.settings.value("toolbox/importSettingsPage/rawCheckBox", 0)
        )
        self.rawCheckBox.setChecked(isChecked)

        isChecked = int(
            self.settings.value("toolbox/importSettingsPage/pantaCheckBox", 0)
        )
        self.pantaCheckBox.setChecked(isChecked)

        isChecked = int(
            self.settings.value("toolbox/importSettingsPage/spectrumCsvCheckBox", 0)
        )
        self.spectrumCsvCheckBox.setChecked(isChecked)

        value = int(self.settings.value("toolbox/miscSettingsPage/parallelSpinBox", 1))
        self.parallelSpinBox.setValue(value)
        index = int(
            self.settings.value(
                "toolbox/miscSettingsPage/colormapForPlotComboBoxIndex", 0
            )
        )
        self.colormapForPlotComboBox.setCurrentIndex(index)

        index = int(
            self.settings.value(
                "toolbox/exportSettingsPage/outputFormatComboBoxIndex", 0
            )
        )
        self.outputFormatComboBox.setCurrentIndex(index)
        index = int(
            self.settings.value(
                "toolbox/exportSettingsPage/outputReportComboBoxIndex", 0
            )
        )
        self.outputReportComboBox.setCurrentIndex(index)

        isChecked = int(
            self.settings.value("toolbox/plotSettingsPage/curveVlinesCheckBox", 0)
        )
        self.curveVlinesCheckBox.setChecked(isChecked)
        isChecked = int(
            self.settings.value("toolbox/plotSettingsPage/curveBaselineCheckBox", 0)
        )
        self.curveBaselineCheckBox.setChecked(isChecked)
        isChecked = int(
            self.settings.value("toolbox/plotSettingsPage/curveHeatmapColorCheckBox", 0)
        )
        self.curveHeatmapColorCheckBox.setChecked(isChecked)

        isChecked = int(
            self.settings.value("toolbox/plotSettingsPage/curveDerivativeCheckBox", 0)
        )
        self.curveDerivativeCheckBox.setChecked(isChecked)

        index = int(
            self.settings.value("toolbox/plotSettingsPage/curveLegendComboBox", 0)
        )
        self.curveLegendComboBox.setCurrentIndex(index)

        value = int(
            self.settings.value(
                "toolbox/plotSettingsPage/curveMarkEverySpinBoxValue", 0
            )
        )
        self.curveMarkEverySpinBox.setValue(value)

        index = int(
            self.settings.value("toolbox/exportSettingsPage/curveTypeComboboxIndex", 0)
        )
        self.curveTypeComboBox.setCurrentIndex(index)
        index = int(
            self.settings.value("toolbox/exportSettingsPage/curveViewComboboxIndex", 0)
        )
        self.curveViewComboBox.setCurrentIndex(index)

    def resetToDefaults(self):
        'resets values to defaults'
        index = 0  # int(self.settings.value('toolbox/importSettingsPage/denaturantComboBoxIndex',  0))
        self.denaturantComboBox.setCurrentIndex(index)

        text = core.defaults[
            "sep"
        ]  # self.settings.value('toolbox/importSettingsPage/separatorInputText',  ',')
        self.separatorInput.setText(text)

        text = core.defaults[
            "dec"
        ]  # self.settings.value('toolbox/importSettingsPage/decimalSeparatorInputText',  '.')
        self.decimalSeparatorInput.setText(text)

        value = 1.0  # float(self.settings.value('toolbox/importSettingsPage/scanRateSpinBoxValue',  1.0))
        self.scanRateSpinBox.setValue(value)

        isChecked = 0
        self.spectrumCsvCheckBox.setChecked(isChecked)

        isChecked = 0  # int(self.settings.value('toolbox/importSettingsPage/refoldingCheckBox',  0))
        self.refoldingCheckBox.setChecked(isChecked)

        isChecked = 0
        self.rawCheckBox.setChecked(isChecked)

        isChecked = 0
        self.pantaCheckBox.setChecked(isChecked)

        value = 1  # int(self.settings.value('toolbox/miscSettingsPage/parallelSpinBox',  1))
        self.parallelSpinBox.setValue(value)
        index = 0  # int(self.settings.value('toolbox/miscSettingsPage/colormapForPlotComboBoxIndex',  0))
        self.colormapForPlotComboBox.setCurrentIndex(index)

        index = 0  # int(self.settings.value('toolbox/exportSettingsPage/outputFormatComboBoxIndex',  0))
        self.outputFormatComboBox.setCurrentIndex(index)
        index = 0  # int(self.settings.value('toolbox/exportSettingsPage/outputReportComboBoxIndex',  0))
        self.outputReportComboBox.setCurrentIndex(index)
        # isChecked = 0  # int(self.settings.value('toolbox/exportSettingsPage/genpicsCheckBox',  0))
        # self.genpicsCheckBox.setChecked(isChecked)
        # isChecked = 0  # int(self.settings.value('toolbox/exportSettingsPage/heatmapCheckBox',  0))
        # self.heatmapCheckBox.setChecked(isChecked)

        isChecked = 0  # int(self.settings.value('toolbox/plotSettingsPage/curveVlinesCheckBox',  0))
        self.curveVlinesCheckBox.setChecked(isChecked)
        isChecked = 0  # int(self.settings.value('toolbox/plotSettingsPage/curveBaselineCheckBox',  0))
        self.curveBaselineCheckBox.setChecked(isChecked)
        isChecked = 0  # int(self.settings.value('toolbox/plotSettingsPage/curveDerivativeCheckBox',  0))
        self.curveDerivativeCheckBox.setChecked(isChecked)
        # isChecked = 0  # int(self.settings.value('toolbox/plotSettingsPage/curveLegendCheckBox',  0))
        # self.curveLegendCheckBox.setChecked(isChecked)
        isChecked = 0
        self.curveHeatmapColorCheckBox.setChecked(isChecked)

        index = 0
        self.curveLegendComboBox.setCurrentIndex(index)
        value = 0  # int(self.settings.value('toolbox/plotSettingsPage/curveMarkEverySpinBoxValue',  0))
        self.curveMarkEverySpinBox.setValue(value)
        if self.parent is not None:
            self.parent.getPlotSettings()
            self.parent.manageSubplots()

        index = 0  # int(self.settings.value('toolbox/exportSettingsPage/curveTypeComboboxIndex',  0))
        self.curveTypeComboBox.setCurrentIndex(index)
        index = 0  # int(self.settings.value('toolbox/exportSettingsPage/curveViewComboboxIndex',  0))
        self.curveViewComboBox.setCurrentIndex(index)


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        'creates an instance and assigns data'
        super().__init__()
        self._data = data

    def data(self, index, role):
        'fetches the data'
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        return None

    def rowCount(self, index):
        'retrieves the row count'
        return self._data.shape[0]

    def columnCount(self, index):
        'retrieves the column count'
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        'handles the header'
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None

    def flags(self, index):
        'returns an item flag based on index'
        if index.column() == 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled
        return Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.DisplayRole):
        'sets the data'
        self._data.iloc[index.row(), index.column()] = value


class ComboDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QComboBox in every
    cell of the column to which it's applied
    """

    def __init__(self, parent, items=None):
        'creates the object'
        super().__init__(parent)
        if items is None:
            items = []
        self.li = items

    def createEditor(self, parent, option, index):
        "creates a combobox"
        combo = QComboBox(parent)
        combo.addItems(self.li)
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index):
        "sets editor data"
        editor.blockSignals(True)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        "sets data in the model"
        model.setData(index, editor.currentText())

    def currentIndexChanged(self):
        "actions when index changes"
        self.commitData.emit(self.sender())


class AnalysisDialog(QDialog, Ui_analysisDialog):
    r"""
        ##  \brief This class implements AnalysisDialog of MoltenProt.
    #     \details

    """

    def __init__(self, parent=None):
        r"##  \brief AnalysisDialog constructor."
        super().__init__(parent)
        if parent is None:
            print("parent == None", cfFilename, currentframe().f_lineno)
        self.parent = parent
        # self = load_uic(":/analysis.ui", self)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.myAccept)
        self.buttonBox.rejected.connect(self.myReject)
        self.medianFilterCheckBox.clicked.connect(self.on_medianFilterCheckBoxChecked)
        self.shrinkCheckBox.clicked.connect(self.on_shrinkCheckBoxChecked)
        self.buttonBox.clicked["QAbstractButton*"].connect(self.buttonClicked)

        self.filterWindowSizeLabel.hide()
        self.shrinkNewdTValueLabel.hide()
        self.settings = QSettings()
        self.restoreSettingsValues()

        self.analysisTableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

    @Slot()
    def myAccept(self):
        "when dialog accepted"
        self.settings.setValue(
            "analysisSettings/dCpSpinBoxValue", self.dCpSpinBox.value()
        )
        self.settings.setValue(
            "analysisSettings/medianFilterCheckBox",
            int(self.medianFilterCheckBox.isChecked()),
        )
        self.settings.setValue(
            "analysisSettings/medianFilterSpinBox", self.medianFilterSpinBox.value()
        )
        self.settings.setValue(
            "analysisSettings/shrinkCheckBox", int(self.shrinkCheckBox.isChecked())
        )
        self.settings.setValue(
            "analysisSettings/shrinkDoubleSpinBox", self.shrinkDoubleSpinBox.value()
        )
        self.close()

    @Slot()
    def myReject(self):
        "when dialog rejected"
        self.restoreSettingsValues()
        self.close()

    def buttonClicked(self, button):
        "when button is clicked"
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ResetRole:
            self.resetToDefaults()

    def resetToDefaults(self):
        "Load default analysis settings"
        # default dCp value
        self.dCpSpinBox.setValue(core.analysis_defaults["dCp"])
        # median filter - disabled by default, but set the default value in the spinbox
        self.medianFilterCheckBox.setChecked(False)
        value = 5
        self.medianFilterSpinBox.setValue(value)
        self.on_medianFilterCheckBoxChecked()
        # shrinking - the same as with mfilt, good starting value is 1
        self.shrinkCheckBox.setChecked(False)
        value = 1.0
        self.shrinkDoubleSpinBox.setValue(value)
        self.on_shrinkCheckBoxChecked()
        # trimming - no trimming
        self.tempRangeMinSpinBox.setValue(core.prep_defaults["trim_min"])
        self.tempRangeMaxSpinBox.setValue(core.prep_defaults["trim_max"])
        # savgol, baselines, baseline bounds
        self.savgolSpinBox.setValue(core.analysis_defaults["savgol"])
        self.baselineFitSpinBox.setValue(core.analysis_defaults["baseline_fit"])
        self.baselineBoundsSpinbox.setValue(core.analysis_defaults["baseline_bounds"])
        # prepare the analysis table view
        if self.parent is not None:
            self.parent.prepareAnalysisTableView()

    def setCheckBox(self, checkBoxSettingValue, checkBox):
        "Handles values to be set for checkboxes"
        value = self.settings.value(checkBoxSettingValue)
        if value is None:
            value = False
        else:
            value = int(value)
        checkBox.setChecked(value == 1)

    def restoreSettingsValues(self):
        "restores values of settings"
        value = int(self.settings.value("analysisSettings/dCpSpinBoxValue", 0))
        self.dCpSpinBox.setValue(value)

        self.setCheckBox(
            "analysisSettings/medianFilterCheckBox", self.medianFilterCheckBox
        )
        value = self.settings.value("analysisSettings/medianFilterSpinBox", 5)
        value = int(value)
        self.medianFilterSpinBox.setValue(value)
        self.on_medianFilterCheckBoxChecked()

        self.setCheckBox("analysisSettings/shrinkCheckBox", self.shrinkCheckBox)
        value = self.settings.value("analysisSettings/shrinkDoubleSpinBox", 5)
        value = float(value)
        self.shrinkDoubleSpinBox.setValue(value)
        self.on_shrinkCheckBoxChecked()

    @Slot()
    def on_medianFilterCheckBoxChecked(self):
        r'##  \brief Show/hide medianFilterSpinBox,filterWindowSizeLabel  GUI elements according to medianFilterCheckBox state.'
        if self.medianFilterCheckBox.isChecked():
            self.medianFilterSpinBox.show()
            self.filterWindowSizeLabel.show()
        else:
            self.medianFilterSpinBox.hide()
            self.filterWindowSizeLabel.hide()

    @Slot()
    def on_snrCheckBoxChecked(self):
        r'##  \brief Show/hide snrDoubleSpinBox GUI element according to snrCheckBoxChecked state.'
        if self.snrCheckBox.isChecked():
            self.snrDoubleSpinBox.show()
        else:
            self.snrDoubleSpinBox.hide()

    @Slot()
    def on_shrinkCheckBoxChecked(self):
        r"    ##  \brief Show/hide shrinkDoubleSpinBox,shrinkNewdTValueLabel  GUI elements according to shrinkCheckBox state."
        if self.shrinkCheckBox.isChecked():
            self.shrinkDoubleSpinBox.show()
            self.shrinkNewdTValueLabel.show()
        else:
            self.shrinkDoubleSpinBox.hide()
            self.shrinkNewdTValueLabel.hide()


class MoltenProtMainWindow(QMainWindow, Ui_MainWindow):
    """
    Defines the main window of the GUI

    Notes
    -----
    * in the past a simpler UI loading approach could be used a provided by PyQt, with PySide one needs to convert the UIC files to PY and then use in multiple inheritance, see also: https://www.pythonguis.com/faq/pyqt6-vs-pyside6/

    """

    NextId = 1
    Instances = set()

    def __init__(self, filename=None, parent=None):
        r"""
        ##  \brief MoltenProtMainWindow constructor.
    #     \details
    #   - Set analysis defaults. \sa setAnalysisDefaults
    #   - Init class members.
    #   - Parse application arguments. \sa parseArgs
    #   - Read settings.
    #   - Create standard GUI elements of QMainWindow for MoltenProt application and set their visibility. \sa createMainWindow createStatusBar initDialogs.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MoltenProtMainWindow.Instances.add(self)
        ### initialize attributes related to plotting
        self.main_frame = None # keeps the matplolib widget
        self.layout = None
        self.canvas = None
        self.fig = None
        self.axes = None
        self.currentCurveColor = None
        self.legend = None
        
        ### initialize attributes related to widgets
        self.curveVlinesCheckBoxIsChecked = None
        self.curveHeatmapColorCheckBoxIsChecked = None
        self.curveBaselineCheckBoxIsChecked = None
        self.curveDerivativeCheckBoxIsChecked = None
        self.curveLegendComboboxCurrentText = None
        self.curveMarkEverySpinBoxValue = None
        self.curveTypeComboboxCurrentText = None
        self.curveViewComboboxCurrentText = None
        self.moltenProtToolBox = None
        self.colorMapComboBox = None
        self.datasetComboBox = None
        self.datasetComboBoxAction = None
        self.heatmapMultipleListView = None
        self.sortScoreComboBox = None
        self.dockButtonsFrame = None
        self.buttons = None
        self.scanRateValue = None
        self.font = None
        self.sepValue = None
        self.decValue = None
        self.analysisDialog = None
        self.allItemsInCurveTypeComboBox = None
        
        
        ## \brief  This attribute holds the filename of the data.
        self.filename = filename
        if self.filename is None:
            MoltenProtMainWindow.NextId += 1
        self.fileLoaded = False
        
        ### analysis-related attrs
        self.baseline_fit = None
        self.baseline_bounds = None
        self.mfilt = None
        self.shrink = None
        self.savgol = None
        self.trim_min = None
        self.trim_max = None
        self.dCp = None
        
        self.setAnalysisDefaults()
        ## \brief  This attribute holds the instance of MoltenProtFit object. \sa core.MoltenProtFit
        self.moltenProtFit = None
        ## \brief  This attribute holds the instance of MoltenProtFitMultiple object. \sa core.MoltenProtFitMultiple
        self.moltenProtFitMultiple = None
        # the initial state is that data is not processed
        self.dataProcessed = False
        ## \brief  This attribute holds the instance of AxesDerivative object.
        #   \details AxesDerivative object depicts derevative data plot under the main plot and is created in addDerivativeSublot method.
        #   \sa addDerivativeSublot
        self.axesDerivative = None
        self.axesLegend = None
        ## \brief  This attribute holds the instance of sortScoreCombBoxAction object.
        #    \details This attribute is created in populateAndShowSortScoreComboBox method. \sa populateAndShowSortScoreComboBox
        self.sortScoreCombBoxAction = None
        ## \brief This attribute holds user personal settings.
        #   \details At present moment this object holds last working directory. \sa lastDir
        self.settings = QSettings()
        ## \brief  This attribute holds last working directory.
        self.lastDir = self.settings.value("settings/lastDir", ".")
        # print type(self.lastDir), self.lastDir, cfFilename, currentframe().f_lineno
        ## \brief  This attribute holds the number of analysis runs.
        self.analysisRunsCounter = int(
            self.settings.value("settings/analysisRunsCounter", 0)
        )
        # set analysisRunsCounter threshold to display the survey request (the default starting value is 1000)
        self.analysisRunsThresh = int(
            self.settings.value("settings/analysisRunsThresh", 1000)
        )

        ## Plotting-related constants
        ## \brief  This attribute controls the legend placement on the main plot.
        self.legendLocation = (
            "best"  # legend is now in a separate axes, is this needed?
        )

        self.setWindowTitle("MoltenProt Main Window")

        # Set dimensions of experimental and layout data. Those dimensions are used in createButtonArray, editLayout methods.
        ## \brief  This attribute sets the row dimension of the experimental and the layout data. \sa createButtonArray editLayout
        self.rowsCount = 8
        ## \brief  This attribute sets the column dimension of the experimental and the layout data. \sa createButtonArray editLayout
        self.colsCount = 12
        # default button style
        self.buttonStyleString = "QPushButton {  border-width: 2px; border-color: black; background-color: gray } QPushButton:checked { border-color: green; border-style: inset;}"
        # default gray colour for buttons make part of HeatmapButton?
        self.buttonGray = QColor.fromRgbF(0.501961, 0.501961, 0.501961, 1.000000)

        ## \brief This attribute holds the name of edited layout file
        # self.layoutFileName = None
        ## \brief This attribute holds the instance of MoltenProtFit.hm_dic attribute. \sa core.MoltenProtFit.hm_dic
        self.hm_dic = core.MoltenProtFit.hm_dic

        # create cycler for colors and set the starting color
        self.resetColorCycler()

        ## \brief This attribute holds the name of default sort.
        # self.heatMapName = "Sort_score"
        ## \brief This attribute holds the export as spreadsheet flag.
        self.exportXlsx = False
        ## \brief This attribute holds the name of default analysis.
        self.analysisMode = "santoro1988"
        self.n_jobs = 1
        self.parseArgs()
        ## \brief This attribute holds the namelist of MoltenProt colormap names.
        self.colorMapNames = [
            "RdYlGn",
            "RdYlGn_r",
            "coolwarm",
            "coolwarm_r",
            "Greys",
            "Greys_r",
            "plasma",
            "plasma_r",
        ]
        ## \brief This attribute holds the current palette index.
        self.currentColorMapIndex = 0
        ## \brief This attribute holds the current palette.
        self.currentColorMap = self.colorMapNames[self.currentColorMapIndex]
        self.colorMapComboBoxAction = None
        self.createMainWindow()
        self.createStatusBar()

        self.initDialogs()
        # NOTE some dialogs must be visible only when a file is loaded
        self.actionsSetVisible(False)

        self.setRunAnalysisCounterLabel()

        self.exportThread = None
        self.threadpool = QThreadPool()
        print(
            "Multithreading with maximum %d threads" % self.threadpool.maxThreadCount()
        )
        self.threadIsWorking = False

        self.closeWithoutQuestion = False

        self.iconSize = 12
        self.readFontFromSettings()

    def createExportThread(self):
        'starts an export thread'
        self.exportThread = ExportThread(self)  # make a class instance
        self.exportThread.started.connect(self.on_started)
        self.exportThread.finished.connect(self.on_finished)
        self.exportThread.exportThreadSignal.connect(
            self.on_change, Qt.QueuedConnection
        )

    def resetColorCycler(self):
        """
        Creates a fresh iterator through colors and sets the initial color
        """
        self.curveColorCycler = colorsafe_cycler()
        self.currentCurveColor = next(self.curveColorCycler)["color"]

    def on_started(self):
        ' called when thread is started'
        if showVersionInformation:
            print("on_started")

    def on_finished(self):
        ' called when thread is finished'
        if showVersionInformation:
            print("on_finished")

    def on_change(self, s):
        'dummy method'
        if showVersionInformation:
            print("on_change", s)

    def threadComplete(self):
        self.threadIsWorking = False
        QMessageBox.information(
            self,
            "Info",
            "Export complete",
        )
        self.status_text.setText("Results exported!")

    def setAnalysisOptionsFromJSON(self):
        r"""    ## \brief  This method sets the analysis data, which has been loaded from json file, to analysis options data in the Analysis Dialog.
        """
        if self.moltenProtFit is None:
            print("self.moltenProtFit == None", cfFilename, currentframe().f_lineno)
        elif self.moltenProtFit.analysisHasBeenDone():
            # read the information from the MPFM instance
            (
                analysis_settings,
                model_settings,
            ) = self.moltenProtFitMultiple.GetAnalysisSettings()

            # set GUI elements
            self.setDoubleSpinBoxAccording2CheckBox(
                analysis_settings["shrink"],
                self.analysisDialog.shrinkCheckBox,
                self.analysisDialog.shrinkDoubleSpinBox,
            )
            self.setDoubleSpinBoxAccording2CheckBox(
                analysis_settings["mfilt"],
                self.analysisDialog.medianFilterCheckBox,
                self.analysisDialog.medianFilterSpinBox,
            )
            # NOTE trim settings are relative, but at the start of analysis the very original (plate_raw)
            # dataset is loaded, so extra chopping should not occur
            self.setAnalysisDialogTrimData()
            self.analysisDialog.dCpSpinBox.setValue(analysis_settings["dCp"])
            self.analysisDialog.baselineFitSpinBox.setValue(
                analysis_settings["baseline_fit"]
            )
            self.analysisDialog.baselineBoundsSpinbox.setValue(
                analysis_settings["baseline_bounds"]
            )
            if analysis_settings["savgol"] is not None:
                self.analysisDialog.savgolSpinBox.setValue(analysis_settings["savgol"])

            # update the dataset/model table
            self.prepareAnalysisTableView(data=model_settings)

    def setDoubleSpinBoxAccording2CheckBox(
        self, analysisParameter, checkBox, doubleSpinBox
    ):
        r"## \brief  This method is used to show/hide doubleSpinBox and set checkBox state according to analysisParameter."
        if analysisParameter is None:
            checkBox.setChecked(False)
            doubleSpinBox.hide()
        else:
            checkBox.setChecked(True)
            doubleSpinBox.setValue(analysisParameter)
            doubleSpinBox.show()

    def setAnalysisDialogTrimData(self):
        r"""     ## \brief  This method is used to show/hide tempRangeMaxSpinBox and set its range in the Analysis Dialog according to moltenProtFit.trim_min and moltenProtFit.trim_max values.

        """
        if self.moltenProtFit is None:
            print("self.moltenProtFit == None", cfFilename, currentframe().f_lineno)
        else:
            if self.moltenProtFit.trim_max is None:
                self.moltenProtFit.trim_max = 0
            self.analysisDialog.tempRangeMaxSpinBox.setValue(
                self.moltenProtFit.trim_max
            )
            if self.moltenProtFit.trim_min is None:
                self.moltenProtFit.trim_min = 0
            self.analysisDialog.tempRangeMinSpinBox.setValue(
                self.moltenProtFit.trim_min
            )
            self.analysisDialog.tempRangeMaxSpinBox.show()
            self.analysisDialog.tempRangeMinSpinBox.show()

    def setAnalysisDefaults(self):
        r"""
        ## \brief  This method set analysis defaults from core data.
        
        there are now 3 dicts with options in core:
            * analysis_defaults - options related to analysis
            * prep_defaults - options related to data preprocessing
            * defaults - uncategorized options
        """
        # TODO Is it necessary to copy all values here??
        self.model = core.analysis_defaults["model"]
        self.baseline_fit = core.analysis_defaults["baseline_fit"]
        self.baseline_bounds = core.analysis_defaults["baseline_bounds"]
        self.exclude = core.prep_defaults["exclude"]
        self.blanks = core.prep_defaults["blanks"]
        self.mfilt = core.prep_defaults["mfilt"]
        self.shrink = core.prep_defaults["shrink"]
        self.invert = core.prep_defaults["invert"]
        self.layout = core.defaults["layout"]
        self.savgol = core.analysis_defaults["savgol"]
        self.trim_min = core.prep_defaults["trim_min"]
        self.trim_max = core.prep_defaults["trim_max"]
        self.layout_input_type = "csv"
        self.dCp = core.analysis_defaults["dCp"]

    ## \brief  This method prints analysis settings for debug.
    def printAnalysisSettings(self):
        print("\033[91m" + "\nAnalysisSettings:")
        print(
            "model=",
            self.model,
            "exclude=",
            self.exclude,
            "blanks=",
            self.blanks,
            "mfilt=",
            self.mfilt,
        )
        print(
            "shrink=",
            self.shrink,
            type(self.shrink),
            "invert=",
            self.invert,
            "layout=",
            self.layout,
            "trim_min=",
            self.trim_min,
            "trim_max=",
            self.trim_max,
        )
        print(
            "savgol=", self.savgol, "baseline_fit", self.baseline_fit, "dCp=", self.dCp
        )
        print("\033[0m" + "\n")

    def setRunAnalysisCounterLabel(self):
        r"""
        ## \brief This method shows run analysis counter for paricular user.
            \details In Linux QSettings data (self.analysisRunsCounter is saved using QSettings object) are stored in $HOME/.config/MoltenProt/moltenprot.conf
                           In MS Windows this data is stored in MS Windows registry.

        """
        self.runAnalysisCounterLabel.setText(
            "Global curve counter: {}".format(self.analysisRunsCounter)
        )

    def acceptAnalysis(self):
        r"""
        ## \brief This method implements analysis according to parameters entered by user from the corresponding GUI elements.
        # \todo We have here debug print, which should be excluded from the production version.
    
        """
        # step 1: construct analysis_kwargs from GUI elements
        if self.analysisDialog.medianFilterCheckBox.isChecked():
            self.mfilt = self.analysisDialog.medianFilterSpinBox.value()
        else:
            self.mfilt = None

        if self.analysisDialog.shrinkCheckBox.isChecked():
            self.shrink = self.analysisDialog.shrinkDoubleSpinBox.value()
        else:
            self.shrink = None

        self.trim_min = self.analysisDialog.tempRangeMinSpinBox.value()
        self.trim_max = self.analysisDialog.tempRangeMaxSpinBox.value()

        self.dCp = self.analysisDialog.dCpSpinBox.value()
        self.baseline_fit = self.analysisDialog.baselineFitSpinBox.value()
        self.baseline_bounds = self.analysisDialog.baselineBoundsSpinbox.value()
        self.savgol = self.analysisDialog.savgolSpinBox.value()

        analysis_kwargs = dict(
            baseline_fit=self.baseline_fit,
            baseline_bounds=self.baseline_bounds,
            mfilt=self.mfilt,
            shrink=self.shrink,
            invert=self.invert,
            # layout=self.layout, # ever used in GUI?
            trim_min=self.trim_min,
            trim_max=self.trim_max,
            savgol=self.savgol,
            dCp=self.dCp,
        )

        analysis_kwargs = core.analysis_kwargs(analysis_kwargs)

        # step 2: cycle through datasets/models table and apply analysis options
        # read a pandas df representing the table of dataset/model (dm_table)
        dm_table = self.analysisDialog.analysisTableView.model()._data

        # cycle through available datasets and set analysis options as in analysis_kwargs
        for i in dm_table.index:
            # HACK change class type if lumry_eyring model was selected in at least one dataset
            if dm_table.Model[i] == "lumry_eyring":
                self.moltenProtFitMultiple.__class__ = core.MoltenProtFitMultipleLE

            analysis_kwargs["model"] = dm_table.Model[i]

            self.moltenProtFitMultiple.SetAnalysisOptions(
                which=dm_table.Dataset[i], **analysis_kwargs
            )

        # step 3: prepare the canvas
        self.axisClear()
        self.on_deselectAll()
        self.canvas.draw()

        # step 4: run analysis
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if showVersionInformation:
            self.printAnalysisSettings()

        # show error message if sth fails during analysis (only MoltenProt errors)
        try:
            self.runAnalysis()
            self.dataProcessed = True
        except (ValueError, TypeError) as e:
            QApplication.restoreOverrideCursor()
            print(e, cfFilename, currentframe().f_lineno)
            errMsg = (
                "Error occured during analysis: change analysis settings and try again."
            )
            QMessageBox.warning(self, "MoltenProt Error", str(e))
            self.status_text.setText(errMsg)
            self.dataProcessed = False

        # actions done regardless of analysis success/failure
        QApplication.restoreOverrideCursor()

        # actions done only if analysis was successful
        if self.dataProcessed:
            self.protocolPlainTextEdit.setPlainText(self.moltenProtFit.protocolString)
            self.populateAndShowSortScoreComboBox()
            self.setButtonsStyleAccordingToNormalizedData()

            self.settings.setValue(
                "settings/analysisRunsCounter", self.analysisRunsCounter
            )
            # check if analysisRunsCounter is above the threshold, show survey request and increase thershold
            if self.analysisRunsCounter > self.analysisRunsThresh:
                QMessageBox.information(
                    self,
                    "We need your feedback!",
                    """<p>You have processed {} curves with MoltenProt! Would you like to complete a survey?</p> 
            <p>Follow the link provided on the <a href="http://marlovitslab.org/lab/Download.html">download page</a> or click <a href="https://forms.gle/EacRgkQXfad4JnZx7">here</a>. </p>""".format(
                        self.analysisRunsCounter
                    ),
                    buttons=QMessageBox.Close,
                )
                self.analysisRunsThresh *= 10
                self.settings.setValue(
                    "settings/analysisRunsThresh", self.analysisRunsThresh
                )

            self.settings.sync()
            self.status_text.setText("Data analysis complete.")
            self.actionExport.setVisible(True)
            # adjust subplots
            self.manageSubplots()

    def runAnalysis(self):
        r"## \brief This method implements analysis according to parameters entered by user from the corresponding GUI elements."
        n_jobs = self.moltenProtToolBox.parallelSpinBox.value()

        self.moltenProtFitMultiple.PrepareAndAnalyseAll(n_jobs=n_jobs)

        # once the analysis is done, only show non-skipped datasets in the HeatmapMultipleComboBox
        available_datasets = self.moltenProtFitMultiple.GetDatasets(no_skip=True)
        # if the user decides to skip all datasets, then analysis is impossible
        if len(available_datasets) < 1:
            raise ValueError("No datasets selected for analysis")
        self.moltenProtFit = self.moltenProtFitMultiple.datasets[available_datasets[0]]
        self.populateDatasetComboBox(available_datasets)

        # count the total number of curves processed and add to the global counter
        for dataset in self.moltenProtFitMultiple.GetDatasets():
            if self.moltenProtFitMultiple.datasets[dataset].analysisHasBeenDone():
                self.analysisRunsCounter += len(
                    self.moltenProtFitMultiple.datasets[dataset].plate_results
                )

        self.setRunAnalysisCounterLabel()
        self.moltenProtToolBox.colormapForPlotComboBox.show()
        self.moltenProtToolBox.colormapForPlotLabel.show()

        self.showHideSelectDeselectAll(True)


    def connectPlotSettingsSignals(self):
        r"## \brief This method connects signals for Plot tab in Settings dialog data GUI elements."
        self.moltenProtToolBox.curveVlinesCheckBox.clicked.connect(self.getPlotSettings)
        self.moltenProtToolBox.curveBaselineCheckBox.clicked.connect(
            self.getPlotSettings
        )
        self.moltenProtToolBox.curveHeatmapColorCheckBox.clicked.connect(
            self.getPlotSettings
        )

        # legend and derivative subplots require dedicated methods
        self.moltenProtToolBox.curveLegendComboBox.currentIndexChanged.connect(
            self.manageSubplots
        )
        self.moltenProtToolBox.curveDerivativeCheckBox.clicked.connect(
            self.manageSubplots
        )

        # Get data from spinbox.
        self.moltenProtToolBox.curveMarkEverySpinBox.valueChanged[int].connect(
            self.on_curveMarkEverySpinBoxValueChanged
        )
        # Get data from comboboxes.
        self.moltenProtToolBox.curveTypeComboBox.currentIndexChanged.connect(
            self.on_curveTypeComboBoxCurrentIndexChanged
        )
        self.moltenProtToolBox.curveViewComboBox.currentIndexChanged.connect(
            self.on_curveViewComboBoxCurrentIndexChanged
        )

    @Slot()
    def on_curveTypeComboBoxCurrentIndexChanged(self):
        "when curve type widget is changed"
        self.curveTypeComboboxCurrentText = (
            self.moltenProtToolBox.curveTypeComboBox.currentText()
        )

    @Slot()
    def on_curveViewComboBoxCurrentIndexChanged(self):
        "when the curve viewing combobox is changed"
        self.curveViewComboboxCurrentText = (
            self.moltenProtToolBox.curveViewComboBox.currentText()
        )

    @Slot()
    def on_curveMarkEverySpinBoxValueChanged(self):
        "when a value changes in mark every spin box"
        self.curveMarkEverySpinBoxValue = (
            self.moltenProtToolBox.curveMarkEverySpinBox.value()
        )

    def getPlotSettings(self):
        r"## \brief This method gets Plot tab in Settings dialog data from its GUI elements."
        self.curveHeatmapColorCheckBoxIsChecked = (
            self.moltenProtToolBox.curveHeatmapColorCheckBox.isChecked()
        )
        self.curveVlinesCheckBoxIsChecked = (
            self.moltenProtToolBox.curveVlinesCheckBox.isChecked()
        )
        self.curveBaselineCheckBoxIsChecked = (
            self.moltenProtToolBox.curveBaselineCheckBox.isChecked()
        )
        self.curveDerivativeCheckBoxIsChecked = (
            self.moltenProtToolBox.curveDerivativeCheckBox.isChecked()
        )
        self.curveLegendComboboxCurrentText = (
            self.moltenProtToolBox.curveLegendComboBox.currentText()
        )
        self.curveMarkEverySpinBoxValue = (
            self.moltenProtToolBox.curveMarkEverySpinBox.value()
        )
        self.curveTypeComboboxCurrentText = (
            self.moltenProtToolBox.curveTypeComboBox.currentText()
        )
        self.curveViewComboboxCurrentText = (
            self.moltenProtToolBox.curveViewComboBox.currentText()
        )
        # clean up the axes after plot settings are changed
        self.axisClear()
        self.on_deselectAll()
        self.canvas.draw()

    def createToolBox(self):
        r"""
        ## \brief This method  creates toolbox dialog.
        #   \todo When toolbox appearence will be fixed, we should set fixed width and height for this dialog.
        """
        self.moltenProtToolBox = moltenProtToolBox(self)
        self.allItemsInCurveTypeComboBox = [
            self.moltenProtToolBox.curveTypeComboBox.itemText(i)
            for i in range(self.moltenProtToolBox.curveTypeComboBox.count())
        ]
        self.getPlotSettings()
        self.connectPlotSettingsSignals()

        width = self.moltenProtToolBox.width()
        height = self.moltenProtToolBox.height()

        screen_size = QApplication.instance().primaryScreen().availableSize()
        screenWidth = screen_size.width()
        screenHeight = screen_size.height()
        self.moltenProtToolBox.setGeometry(
            int((screenWidth / 2) - (width / 2)),
            int((screenHeight / 2) - (height / 2)),
            width,
            height,
        )

    def createAnalysisDialog(self):
        r"""    ## \brief This method  creates analysis dialog"""
        self.analysisDialog = AnalysisDialog(self)
        self.analysisDialog.buttonBox.accepted.connect(self.acceptAnalysis)

    def initDialogs(self):
        r"""    ## \brief This method creates the following dialogs: Preferences, Analysis and Layout.
      \sa AnalysisDialog, moltenProtToolBox, LayoutDialog and HelpDialog."""
        self.createToolBox()
        self.createColorMapComboBox()
        self.createAnalysisDialog()

        # Create layout dialog
        self.layoutDialog = LayoutDialog()
        self.connectButtonsFromLayoutDialog()
        # Create help dialog
        self.helpDialog = MoltenProtHelpDialog()

        # set tooltips for dialogs
        self.setTooltips()

    @Slot()
    def on_analysisPushButtonClicked(self):
        r"\brief This method shows the Analysis Dialog."
        self.analysisDialog.show()

    @Slot()
    def on_kelvinsCheckBoxChecked(self):
        "This method is dummy and should be implemented."
        if showVersionInformation:
            print("on_kelvinsCheckBoxChecked")

    def analysisModeBoxSelectionChange(self, i):
        "This method is not used."
        self.analysisMode = self.importDialog.analysisModeBox.currentText()

    def parseArgs(self):
        "dummy method for CLI parsing - to be implemented"
        self.sepValue = ","
        self.decValue = "."
        self.exclude = []
        self.blanks = []

    @Slot()
    def on_exportResults(self):
        """
        Actions performed when the export data button is clicked
        """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)
        filenames = None

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            filename = filenames[0]
            # get export settings from the ui elements and convert them into kwargs for MP.WriteOutput
            data_out = self.moltenProtToolBox.outputFormatComboBox.currentIndex()
            report_out = self.moltenProtToolBox.outputReportComboBox.currentIndex()

            out_kwargs = {}
            out_kwargs["outfolder"] = filename

            if data_out == 0:
                # 0 no data output
                # 1 CSV output
                # 2 XLSX output
                out_kwargs["no_data"] = True
            elif data_out == 1:
                out_kwargs["xlsx"] = False
            elif data_out == 2:
                out_kwargs["xlsx"] = True

            # NOTE matplotlib is not thread-safe, so threading is disabled for some options
            use_threads = True
            if report_out == 0:
                # 0 no report
                # 1 pdf
                # 2 XLSX summary
                # HTML
                out_kwargs["report_format"] = None
            elif report_out == 1:
                out_kwargs["report_format"] = "pdf"
                use_threads = False
            elif report_out == 2:
                out_kwargs["report_format"] = "xlsx"
            elif report_out == 3:
                out_kwargs["report_format"] = "html"
                use_threads = False

            out_kwargs["n_jobs"] = self.moltenProtToolBox.parallelSpinBox.value()

            QApplication.setOverrideCursor(Qt.WaitCursor)

            if use_threads:
                worker = ExportWorker(self.moltenProtFitMultiple, **out_kwargs)
                worker.signals.finished.connect(self.threadComplete)
                worker.signals.progress.connect(self.progressFn)
                self.threadIsWorking = True
                # Execute
                self.threadpool.start(worker)
            else:
                self.moltenProtFitMultiple.WriteOutputAll(**out_kwargs)

            QApplication.restoreOverrideCursor()
            self.status_text.setText("Results exported to folder {}".format(filename))

    def executeThisFn(self, progress_callback):
        "to show worker progress - not implemented"
        if showVersionInformation:
            print("executeThisFn")
        return "Done."

    def progressFn(self):
        "to show worker progress - not implemented"
        if showVersionInformation:
            print("progressFn")

    @Slot()
    def on_actionNewTriggered(self):
        r"## \brief This SLOT is called when user clicks <b>New</b> button and  runs another instance of MoltenProt GUI application."
        MoltenProtMainWindow().show()

    @Slot()
    def on_actionFontTriggered(self):
        'actions when fonts are changed'
        fontDialog = QFontDialog(self)
        fontDialog.setFont(self.font)
        ok, font = fontDialog.getFont()
        if ok:
            self.font = font
            self.settings.setValue("fontSettings/currentFont", self.font.toString())
            self.setNewFont(self.font)

    def setIconSize(self):
        "sets sizes of icons"
        self.iconSize = self.font.pointSize() * 3
        iconSize = QSize(self.iconSize, self.iconSize)
        self.fileToolBar.setIconSize(iconSize)
        self.actionToolBar.setIconSize(iconSize)
        self.miscToolBar.setIconSize(iconSize)

    def setNewFont(self, newFont):
        'sets a new font'
        self.font = newFont
        self.setApplicationMenuFont()
        self.setIconSize()

    def readFontFromSettings(self):
        "restore font settings"
        newFontString = self.settings.value("fontSettings/currentFont")
        newFont = QFont()
        ok = newFont.fromString(newFontString)
        if ok:
            self.setNewFont(newFont)
        else:
            print("Failed to set font", newFont, cfFilename, currentframe().f_lineno)

    def setApplicationMenuFont(self):
        "Updates fonts in widgets"
        QApplication.setFont(self.font, "QFileDialog")
        QApplication.setFont(self.font, "QPushButton")
        QApplication.setFont(self.font, "QAction")
        QApplication.setFont(self.font, "QFontDialog")
        QApplication.setFont(self.font, "QToolBar")
        QApplication.setFont(self.font, "QMainWindow")
        QApplication.setFont(self.font, "QWidget")
        QApplication.setFont(self.font, "QTextEdit")
        QApplication.setFont(self.font, "QDialogButtonBox")
        if self.canvas is not None:
            self.canvas.setFont(self.font)

    @Slot()
    def on_actionAbout(self):
        r"    ## \brief This SLOT is called when user clicks <b>About</b> button and shows some information about used python modules and Qt version."
        QMessageBox.about(
            self,
            "About MoltenProt",
            ABOUT_HTML
        )

    @Slot()
    def on_actionCite_MoltenProt(self):
        r"## \brief This SLOT is called when user clicks <b>Cite</b> menu item."
        QMessageBox.about(
            self,
            "Cite MoltenProt",
            core.citation["html"],
        )

    @Slot()
    def on_actionHelp(self):
        r"## \brief This SLOT is called when user clicks <b>Help</b> menu item and shows the MoltenProt help system main window."
        self.helpDialog.show()

    @Slot()
    def on_actionLoad_sample_data(self):
        r"""
        ## \brief This SLOT is called when user clicks File>Load sample data
             opens the folder where demo data is stored
        """
        self.on_loadFile(directory=os.path.join(core.__location__, "demo_data"))

    @Slot()
    def on_actionSave_as_JSONTriggered(self):
        """## \brief Save the current session as JSON."""
        filename = QFileDialog.getSaveFileName(
            self,
            caption=self.tr(
                "Save MoltenProt session in *.json format"
            ),  # the title of the dialog window
            dir=self.lastDir,  # the starting directory, use "." for cwd
            filter="JSON Files (*.json)",  # file type filter
        )

        if filename[0] != "":
            # convert returned filname value to string and add .json if necessary
            filename = str(filename[0])
            if filename[-5:] != ".json":
                filename += ".json"
            core.mp_to_json(self.moltenProtFitMultiple, filename)

    def prepareAnalysisTableView(self, data:pd.DataFrame=None):
        """if data is None generate the table freshly
        otherwise populate using the values from supplied dataframe"""

        analysisModeComboBoxItemsList = list(core.avail_models.keys())

        if data is None:
            defaultModel = analysisModeComboBoxItemsList[0]

            currentDataSetsList = list(self.moltenProtFitMultiple.GetDatasets())
            data = pd.DataFrame(columns=("Dataset", "Model"))
            for i in range(len(currentDataSetsList)):
                data.loc[i] = [currentDataSetsList[i], defaultModel]

        tableModel = TableModel(data)
        self.analysisDialog.analysisTableView.setModel(tableModel)
        comboDelegate = ComboDelegate(self, analysisModeComboBoxItemsList)
        self.analysisDialog.analysisTableView.setItemDelegateForColumn(1, comboDelegate)

    def showHideSelectDeselectAll(self, show):
        "Toggle visiblity of the select/deselect buttons"
        self.actionSelectAll.setVisible(show)
        self.actionDeselectAll.setVisible(show)

    @Slot()
    def on_loadFile(self, directory=None):
        r"""
        \brief Load the input data in xlsx, JSON or csv format for analysis.
        
        Parameters
        ----------
        directory
            a folder where to open the file dialog
        """
        if directory is None:
            directory = self.lastDir
        # HACK prevent directory from being a boolean
        if isinstance(directory, bool):
            directory = None

        self.on_deselectAll()

        filename = QFileDialog.getOpenFileName(
            self,
            caption=self.tr("Open JSON session or import data"),
            dir=directory,
            filter=self.tr(
                "XLSX Files (*.xlsx);;JSON Files (*.json);;CSV files (*.csv)"
            ),
        )
        # returns a tuple with file path, and the mode of QFileDialog used (XLSX Files, JSON Files, etc)
        filename = filename[0]
        fileInfo = QFileInfo(filename)
        if fileInfo.isReadable():
            self.lastDir = fileInfo.canonicalPath()
            self.settings.setValue("settings/lastDir", self.lastDir)
            self.settings.sync()
            self.resetButtons()
            if self.sortScoreCombBoxAction is not None:  # TODO is this really needed here?
                self.sortScoreCombBoxAction.setVisible(False)
            self.dataProcessed = False
            if self.fileLoaded:
                self.on_deselectAll()
                self.axisClear()
                self.actionExport.setVisible(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                if filename.endswith(".csv"):
                    self.processCsv(filename)
                elif filename.endswith(".json"):
                    self.processJSON(filename)
                elif filename.endswith(".xlsx"):
                    self.processXLSX(filename)
                self.status_text.setText("Loaded " + filename)
                self.fileLoaded = True
            except (
                ValueError,
                KeyError,
            ) as e:  # KeyError is raised when a regular XLSX file is opened with panta_rhei settings
                # TODO currently the previous data/layout is left around even though the file could not open
                # TODO if loading a spectrum CSV with regular CSV settings no error is shown (but the UI is empty)
                QMessageBox.warning(
                    self,
                    "MoltenProt Open File Error",
                    f"The input file cannot be opened due to error:\n {e}\n check if the correct file is selected and if import settings are appropriate",
                )
                self.status_text.setText("Requested file could not be opened.")
                # reset the GUI
                self.resetGUI()
                self.fileLoaded = False

            # done regarless of file loading success
            QApplication.restoreOverrideCursor()
            # done only when opening succeeded
            if self.fileLoaded:
                self.actionsSetVisible(True)

                self.setAllButtons("enable", True)
                self.showOnlyValidButtons()
                self.prepareAnalysisTableView()

                # Overwrite default analysis settings if input file was JSON and was processed
                # for any other file type reset to defaults
                if filename.endswith(".json"):
                    self.setAnalysisOptionsFromJSON()
                else:
                    ###TODO restore default analysis settings
                    pass

                # actions in case the data was processed (JSON only)
                if self.dataProcessed:
                    if showVersionInformation:
                        print(
                            "Analysis has been done",
                            cfFilename,
                            currentframe().f_lineno,
                        )
                    # self.showHideSelectDeselectAll(True)
                    self.moltenProtToolBox.colormapForPlotComboBox.show()
                    self.moltenProtToolBox.colormapForPlotLabel.show()
                    self.populateAndShowSortScoreComboBox()
                    self.setButtonsStyleAccordingToNormalizedData()
                    self.sortScoreComboBox.clear()
                    self.sortScoreComboBox.insertItems(
                        1, self.moltenProtFit.getResultsColumns()
                    )
                else:
                    self.moltenProtToolBox.colormapForPlotComboBox.hide()
                    self.moltenProtToolBox.colormapForPlotLabel.hide()
        elif filename != "":
            # empty string is returned when Cancel is pressed in QFileDialog
            QMessageBox.warning(
                self, "MoltenProt Open File Error", "Input file not readable"
            )
            self.resetGUI()

    def populateDatasetComboBox(self, available_datasets):
        """ Adds datasets from the list to the respective combobox
         if there is one or no datasets, the combobox is hidden"""
        self.datasetComboBox.clear()
        if len(available_datasets) <= 1:
            self.datasetComboBoxAction.setVisible(False)
        else:
            self.datasetComboBox.insertItems(1, available_datasets)
            width = self.datasetComboBox.minimumSizeHint().width()
            self.datasetComboBox.setMinimumWidth(width)
            self.datasetComboBoxAction.setVisible(True)

    def processCsv(self, filename):
        r"""
        # \brief This method is used to process CSV file named filename
       \param filename - CSV file to process.
       \todo Debug print is used here.
        """
        if showVersionInformation:
            print("processCsv", filename, cfFilename, currentframe().f_lineno)
        self.sepValue = self.moltenProtToolBox.separatorInput.text()
        self.decValue = self.moltenProtToolBox.decimalSeparatorInput.text()
        self.scanRateValue = self.moltenProtToolBox.scanRateSpinBox.value()

        if self.moltenProtToolBox.spectrumCsvCheckBox.isChecked():
            self.moltenProtFitMultiple = core.parse_spectrum_csv(
                filename,
                sep=self.sepValue,
                dec=self.decValue,
                scan_rate=self.scanRateValue,
            )
        else:
            self.moltenProtFitMultiple = core.parse_plain_csv(
                filename,
                sep=self.sepValue,
                dec=self.decValue,
                scan_rate=self.scanRateValue,
            )
        available_datasets = self.moltenProtFitMultiple.GetDatasets()
        self.moltenProtFit = self.moltenProtFitMultiple.datasets[available_datasets[0]]
        self.populateDatasetComboBox(available_datasets)

    def processJSON(self, filename):
        r"""
        ## \brief This method is used to process JSON file named filename
        \param filename - JSON file to process.
        \todo Debug print is used here.    
        """
        jsonData = core.mp_from_json(filename)
        if isinstance(jsonData, core.MoltenProtFitMultiple):
            self.moltenProtFitMultiple = jsonData

            # do not show datasets that were marked as skipped in the combobox
            available_datasets = self.moltenProtFitMultiple.GetDatasets(no_skip=True)
            self.moltenProtFit = self.moltenProtFitMultiple.datasets[
                available_datasets[0]
            ]

            # MPF2 dynamically populate heatmap combobox
            self.populateDatasetComboBox(available_datasets)

            # TODO currently this only checks analysis completion only in one of MoltenProtFit instances
            if self.moltenProtFit.analysisHasBeenDone():
                self.dataProcessed = True
                # make the export button visible
                self.actionExport.setVisible(True)
                # update plot view
                self.manageSubplots()
            else:
                if showVersionInformation:
                    print(
                        "Analysis has not been done",
                        cfFilename,
                        currentframe().f_lineno,
                    )
        else:
            if showVersionInformation:
                print(
                    "Unknown object has been created from json file",
                    filename,
                    cfFilename,
                    currentframe().f_lineno,
                )

    def processXLSX(self, filename):
        r"""
        \brief This method is used to process XLSX file named filename.
       \param filename - XLSX file to process.
       \todo Debug print is used here.
        """
        refolding = self.moltenProtToolBox.refoldingCheckBox.isChecked()
        is_raw = self.moltenProtToolBox.rawCheckBox.isChecked()
        is_panta = self.moltenProtToolBox.pantaCheckBox.isChecked()
        self.moltenProtFitMultiple = core.parse_prom_xlsx(
            filename,
            raw=is_raw,
            refold=refolding,
            panta_rhei=is_panta,
        )
        available_datasets = self.moltenProtFitMultiple.GetDatasets()
        self.moltenProtFit = self.moltenProtFitMultiple.datasets[available_datasets[0]]
        self.populateDatasetComboBox(available_datasets)
        # NOTE XLSX is always unprocessed, however, dataProcessed attribute
        # and the view of the plots must be reset from the previous run
        self.dataProcessed = False
        self.manageSubplots()

    def setTooltips(self):
        r"""
        \brief This method set tooltips for GUI elements using core.MoltenProtFit.defaults dictionary.
        \sa core.defaults dicts
        """
        # data prep defaults
        self.analysisDialog.shrinkCheckBox.setToolTip(core.prep_defaults["shrink_h"])
        self.analysisDialog.shrinkDoubleSpinBox.setToolTip(
            core.prep_defaults["shrink_h"]
        )
        self.analysisDialog.medianFilterCheckBox.setToolTip(
            core.prep_defaults["mfilt_h"]
        )
        self.analysisDialog.medianFilterSpinBox.setToolTip(
            core.prep_defaults["mfilt_h"]
        )
        self.analysisDialog.tempRangeMaxSpinBox.setToolTip(
            core.prep_defaults["trim_max_h"]
        )
        self.analysisDialog.tempRangeMinSpinBox.setToolTip(
            core.prep_defaults["trim_min_h"]
        )
        # analysis defaults
        self.analysisDialog.dCpSpinBox.setToolTip(core.analysis_defaults["dCp_h"])
        self.analysisDialog.baselineFitSpinBox.setToolTip(
            core.analysis_defaults["baseline_fit_h"]
        )
        self.analysisDialog.baselineBoundsSpinbox.setToolTip(
            core.analysis_defaults["baseline_bounds_h"]
        )
        self.analysisDialog.savgolSpinBox.setToolTip(core.analysis_defaults["savgol_h"])

    @Slot()
    def on_showmoltenProtToolBox(self):
        r"""
        \brief This method shows the Preferences Dialog.
       \sa moltenProtToolBox

        """
        self.moltenProtToolBox.show()

    def showMessage(self, message, messageKind):
        r" \brief creates QMessageBox with messageKind icon and shows message."
        msg = QMessageBox()
        msg.setIcon(messageKind)
        msg.setText(message)
        msg.exec_()

    def __layout2widget(self, input_series):
        """
        Helper function to convert a single row of layout DataFrame into
        a QTableWidget entry
        NOTE to avoid Overflow errors, the respective DataFrame must have np.nan etc changed to 'None' string
        """
        # Convert alphanumeric index to numeric indices:
        # A1 -> (0, 0)
        # H12 -> (7, 11)
        row = "ABCDEFGH".index(input_series.name[0])
        column = int(input_series.name[1:]) - 1

        if input_series["Condition"] != "None":
            item_value = input_series["Condition"]
        else:
            # default value for layout is ""
            item_value = ""
        self.layoutDialog.tableWidget.setItem(
            row, column, QTableWidgetItem(str(item_value))
        )

    def editLayout(self):
        r"""
        \brief This method shows the layout from MoltenProtFitMultiple.layout in QTableWidget in LayoutDialog.
       \sa LayoutDialog

        """
        layout = self.moltenProtFitMultiple.layout.fillna("None")
        layout.apply(self.__layout2widget, axis=1)
        self.layoutDialog.tableWidget.resizeColumnsToContents()
        self.layoutDialog.tableWidget.alternatingRowColors()
        self.layoutDialog.show()

    def openLayout(self):
        """
        Load a layout from a specially formatted CSV file to QTableWidget
        """
        layoutFileName = QFileDialog.getOpenFileName(
            self,
            caption=self.tr("Open layout from CSV file"),
            dir=self.lastDir,
            filter="CSV files (*.csv)",
        )
        layoutFileName = layoutFileName[0]
        if layoutFileName != "":
            fileInfo = QFileInfo(layoutFileName)
            if showVersionInformation:
                print(fileInfo.fileName(), currentframe().f_lineno, cfFilename)
            if fileInfo.isReadable():
                layout = pd.read_csv(
                    layoutFileName, index_col="ID", encoding="utf_8"
                ).fillna("None")
                layout.apply(self.__layout2widget, axis=1)
                self.layoutDialog.tableWidget.resizeColumnsToContents()
                self.layoutDialog.tableWidget.alternatingRowColors()
                self.layoutDialog.show()
            else:
                print(
                    layoutFileName + " can not be processed. Check your permissions!",
                    currentframe().f_lineno,
                    cfFilename,
                )

    def updateLayout(self):
        "edit the layout of MPFM instance"
        # TODO use tableWidget.rowCount()/columnCount()
        for column in range(0, 12):
            for row in range(0, 8):
                item = self.layoutDialog.tableWidget.item(row, column)
                alphanumeric_index = "ABCDEFGH"[row] + str(column + 1)

                # NOTE the layout is always 12x8, however, the data may have less samples
                # do not assign layout to the data that is not present in plate_raw
                if self.moltenProtFit.testWellID(
                    alphanumeric_index, ignore_results=True
                ):
                    if item.text() != "":
                        self.moltenProtFitMultiple.layout.loc[
                            alphanumeric_index, "Condition"
                        ] = item.text()
                    else:
                        self.moltenProtFitMultiple.layout.loc[
                            alphanumeric_index, "Condition"
                        ] = None
        # apply edited layout to all datasets inside MPFM
        self.moltenProtFitMultiple.UpdateLayout()

    def resetLayout(self):
        """
        Action to be performed when reset button in Layout dialog is pressed.
        Restore the original layout from layout_raw if this is available
        """
        self.moltenProtFitMultiple.ResetLayout()
        self.layoutDialog.close()

    ## \brief This SLOT (in Qt terms) is called when user changes heatmap table name.
    #   \sa createComboBoxesForActionToolBar
    @Slot()
    def on_changeInputTable(self):
        "When the source table is changed"
        if self.moltenProtFit is not None:
            self.on_deselectAll()
            inputTableName = self.datasetComboBox.currentText()
            if inputTableName in self.moltenProtFitMultiple.GetDatasets():
                inputTableNameIsValid = True
                self.moltenProtFit = self.moltenProtFitMultiple.datasets[inputTableName]
                newProtocolString = self.moltenProtFitMultiple.datasets[
                    inputTableName
                ].protocolString
                self.protocolPlainTextEdit.setPlainText(newProtocolString)
            else:
                print(
                    "Unknown table name",
                    inputTableName,
                    currentframe().f_lineno,
                    cfFilename,
                )
                inputTableNameIsValid = False
            if inputTableNameIsValid:
                if self.dataProcessed:
                    # NOTE before this is done, we must ensure that the combobox contains valid items
                    self.populateAndShowSortScoreComboBox()
                    self.setButtonsStyleAccordingToNormalizedData()
                else:
                    self.resetButtons()
        else:
            if showVersionInformation:
                print("self.moltenProtFit == None", currentframe().f_lineno, cfFilename)

    def __genTooltip(self, input_series, heatMapName):
        """
        Helper function that converts a single row of MPF.plate_results to a tooltip string
        """

        output = "{} {} {} = {}".format(
            input_series.name,
            input_series.Condition,
            heatMapName,
            round(
                input_series[heatMapName],
                2,
            ),
        )
        return output

    def setButtonsStyleAccordingToNormalizedData(self):
        "Colorizes the buttons"
        if self.moltenProtFit is not None:
            heatMapName = self.sortScoreComboBox.currentText()
            # NOTE during startup the values of the drop-down list
            # can be empty which would result in a crash
            if heatMapName in self.moltenProtFit.getResultsColumns():
                # normalize the data in selected column and create colors (rgba tuples) with the current colormap
                cmap = cm.get_cmap(self.currentColorMap)
                button_colors = core.normalize(
                    self.moltenProtFit.plate_results[heatMapName]
                ).apply(cmap)
                # update the Color column in the Buttons df with existing colors
                # NOTE buttons without a color will have None
                button_colors.name = "Color"
                self.buttons.Color = None  # resets all colors to None
                self.buttons.update(button_colors)

                # generate tooltips
                self.buttons.Tooltip = None  # reset all tooltips
                tooltips = self.moltenProtFit.plate_results.apply(
                    self.__genTooltip, heatMapName=heatMapName, axis=1
                )
                tooltips.name = "Tooltip"
                self.buttons.update(tooltips)

                # apply changes to the buttons
                self.buttons.apply(self.__setOneButtonStyle, axis=1)
        else:
            print("self.moltenProtFit == None", currentframe().f_lineno, cfFilename)

    def setAllButtons(self, action, flag):
        """
        Applies a certain boolean action to all buttons in self.buttons

        Possible actions:
        check - whether the button was clicked or not
        enable - whether the button is enabled

        flag (bool) - true or false for action

        """
        for button_id in core.alphanumeric_index:
            if action == "check":
                # TODO add skipping of gray buttons
                self.buttons.at[button_id, "Button"].setChecked(flag)
            elif action == "enable":
                self.buttons.at[button_id, "Button"].setEnabled(flag)
            else:
                raise ValueError("Unknown action: {}".format(action))

    def resetButtons(self):
        "resets the button style"
        for button_id in core.alphanumeric_index:
            self.buttons.at[button_id, "Button"].setStyleSheet(self.buttonStyleString)

    @Slot()
    def on_selectAll(self):
        """
        Cycles through all buttons, checks valid buttons and updates plots and table
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for button_id in self.buttons.index:
            if self.moltenProtFit.testWellID(button_id):
                self.buttons.at[button_id, "Button"].setChecked(True)
                self.updateTable(button_id)
                self.plotFigAny(button_id)
                self.currentCurveColor = next(self.curveColorCycler)["color"]
        # re-initialize colors
        self.resetColorCycler()
        self.canvas.draw()
        QApplication.restoreOverrideCursor()

    @Slot()
    def on_deselectAll(self):
        "When all samples are deselected"
        # clear axes
        self.axisClear()
        self.setAllButtons("check", False)
        self.resetTable()
        for button_id in core.alphanumeric_index:
            # NOTE draw_canvas=False makes the removal faster
            self.removeButtonLine2D(button_id, draw_canvas=False)
        # re-initialize colors
        self.resetColorCycler()
        self.canvas.draw()

    @Slot()
    def on_show(self, button_id):
        """
        The main action on button click
        This method is also called:
        1) when GUI is initialized
        2) when all buttons are selected/deselected

        checks for the validity of the button id are in respective methods (plotfig and updateTable)

        if button clicked
            upd table
            plot the curve
        else -> button unclicked
            remove plotted curve
            remove table entry

        Parameters
        ----------
        button_id
            alphanumeric code (e.g. A1) of the button that was clicked

        Known issues
        ------------
        * if a button that was already clicked is unclicked, the color cycle doesn't go back. This means that upon unclicking the color used in the line of the unclicked button will not become the current color. Visually, it is somewhat inconsistent, however, one would need to somehow track the previous color and check if the button was previously clicked or not. For instance, one can keep two copies of curve cyclers, where one is one step ahead of the other
        """
        btn = self.buttons.at[button_id, "Button"]
        if btn.isChecked():
            self.updateTable(button_id)
            # line has already been already plotted by the hover function, but need to change the color for plotting
            self.currentCurveColor = next(self.curveColorCycler)["color"]
        else:
            self.removeButtonLine2D(button_id)
            # remove respective entry from the table - scan all rows of the first column to find the button_id
            for row in range(self.tableWidget.rowCount()):
                # id in the table
                item = self.tableWidget.item(row, 0)
                if item is not None:
                    table_id = self.tableWidget.item(row, 0).text()
                    if table_id == button_id:
                        self.tableWidget.removeRow(row)
                        # only one table_id should exist, stop the cycle when found
                        break
        self.canvas.draw()

    def removeButtonLine2D(self, button_id, draw_canvas=True):
        """
        Removes lines associated with a button
        """
        lines = self.buttons.at[button_id, "Line2D"]
        if lines is not np.nan:
            for line in lines:
                try:
                    line.remove()
                except NotImplementedError:
                    # appeared in matplotlib 3.10, not sure why this happens
                    continue
            self.buttons.at[button_id, "Line2D"] = np.nan  # deregisters the line list
        if draw_canvas:
            # NOTE this updates the plot and may be a slow step
            # if this step is omitted then the changes to the plot will not be updated on the screen
            self.canvas.draw()

    def resetTable(self):
        """
        Cleans, but does not hide the table widget
        """
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

    def updateTable(self, button_id):
        """
        Reads information from self.moltenProtFit and creates a table under the heatmap

        Notes
        -----
        * Table widget will be made visible when the method is called for the first time
        """

        if self.dataProcessed:
            plateResults = self.moltenProtFit.plate_results
            # create a dictionary to map column ID's in GUI to column names from getResultsColumns
            column_labels = ["ID", "Condition"] + self.moltenProtFit.getResultsColumns()
            column_dict = {}
            for i in range(len(column_labels)):
                column_dict[i] = column_labels[i]
            # set the number of columns in the table
            self.tableWidget.setColumnCount(len(column_dict))

            if not self.tableWidget.isVisible():
                self.tableWidget.show()
                self.tableDockWidget.show()

            # temporarily disable sorting to allow proper insertion of new rows (see QTableWidget docs)
            self.tableWidget.setSortingEnabled(False)

            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            for column_pos, column_name in column_dict.items():
                if column_name == "ID":
                    table_string = button_id
                elif column_name == "Condition":
                    table_string = plateResults.loc[button_id, column_name]
                    if table_string is np.nan:
                        # NOTE prevents QTableWidgetItem Overflow error
                        table_string = "n/a"
                    else:
                        table_string = str(table_string)
                elif column_name == "S":
                    # NOTE for S formatting to two last decimals is not always working
                    table_string = str(plateResults.loc[button_id, column_name])
                else:
                    table_string = "{:10.2f}".format(
                        plateResults.loc[button_id, column_name]
                    )
                item = QTableWidgetItem(table_string)
                item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(rowPosition, column_pos, item)
            # set table widget titles accordingly
            self.tableWidget.setHorizontalHeaderLabels(column_labels)
            # restore sorting functionality
            self.tableWidget.setSortingEnabled(True)
        else:
            # TODO can use this section to show sample information before analysis
            # print("Warning: cannot create table because data is not processed")
            pass

    def axisClear(self, draw_canvas=True):
        """
        Clears all available axes.

        Parameters
        ----------
        draw_canvas: bool
            force redraw of the plot window

        Notes
        -----
        This is not equivalent to self.fig.clear, which would remove everything from the plot window
        """
        # NOTE the very last ax is reserved for legend and nothing should be cleared here
        self.axes.clear()
        self.axes.grid(True)
        if self.axesDerivative != None:
            self.axesDerivative.clear()
            self.axesDerivative.grid(True)
        if draw_canvas:
            self.canvas.draw()

    def __setOneButtonStyle(self, input_series):
        """
        Helper function that applies a color and state to one button
        To be used in setButtonsStyle/setButtonsStyleAccordingToNormalizedData
        """
        button = input_series["Button"]
        color = input_series["Color"]
        tooltip = input_series["Tooltip"]
        if color is not None:
            styleString = (
                "QPushButton {  border-width: 2px; border-color: white; background-color: "
                + matplotlib.colors.to_hex(color, keep_alpha=False)
                + "} QPushButton:checked { border-color:  black; border-style: inset;}"
            )
            enabled = True
        else:
            styleString = "QPushButton {  border-width: 2px; border-color: white; background-color: gray } QPushButton:checked { border-color:  black; border-style: inset;}"
            enabled = False
        button.setEnabled(enabled)
        button.setStyleSheet(styleString)
        if tooltip is not None:
            button.setToolTip(tooltip)

    def createButtonArray(self, hbox):
        r"""## \brief self.buttons attribute contains all information related to samples selected in the GUI heatmap and their plots
        index is alphanumeric ID's (similar to mp.MoltenProtFit.plate_results), but columns contain the info on the state of the GUI:
        * Visible (bool) - whether the button should be displayed at all - can be fetched from the button object
        * Selected (bool) - whether the user clicked on the button - can be fetched from the button object
        * Color (str) - matplotlib-compatible color for the curve
        * Button - reference to the respective GUI button
        * Tooltip - information displayed when mouse is over a button
        * Line2D - reference to the matplotlib object of the experimental line; if None, then the curve was not plotted!
        * LineColor - the color used for the line (e.g. from colorsafe list, or the same color as the button)"""
        self.buttons = pd.DataFrame(
            index=core.alphanumeric_index,
            columns=(
                "Button",
                "Color",
                "Tooltip",
                "Line2D",
                "LineColor",
            ),
        )
        self.buttons.index.name = "ID"

        # constants for the button generation
        buttonSize = 40
        letters = ["A", "B", "C", "D", "E", "F", "G", "H"]

        # populate the buttons DataFrame with actual buttons
        for j in range(self.colsCount):
            right_vbox = QVBoxLayout()
            for i in range(self.rowsCount):
                button_name = letters[i] + str(j + 1)
                button = QPushButton(button_name)
                button.setObjectName(button_name)
                button.setCheckable(True)
                button.setChecked(False)
                button.setEnabled(False)
                button.setFixedWidth(buttonSize)
                button.setFixedHeight(buttonSize)
                button.setStyleSheet(self.buttonStyleString)
                button.installEventFilter(self)
                # pass the button name to the slot:
                # borrowed [here](https://eli.thegreenplace.net/2011/04/25/passing-extra-arguments-to-pyqt-slot)
                button.clicked.connect(partial(self.on_show, button_name))
                right_vbox.addWidget(button)
                # add button to buttons df
                self.buttons.at[button_name, "Button"] = button
            right_vbox.addStretch(1)
            hbox.addLayout(right_vbox)
        hbox.addStretch(1)

    def showOnlyValidButtons(self):
        "shows a button only if it is found in the raw data"
        for button_id in core.alphanumeric_index:
            if self.moltenProtFit.testWellID(button_id, ignore_results=True):
                self.buttons.at[button_id, "Button"].show()
            else:
                self.buttons.at[button_id, "Button"].hide()

    def actionsSetVisible(self, show):
        "show/hide buttons that require a dataset to be loaded"
        self.showHideSelectDeselectAll(show)
        self.actionAnalysis.setVisible(show)
        self.actionEdit_layout.setVisible(show)
        self.actionSave_as_JSON.setVisible(show)
        self.actionToolBar.setVisible(show)
        self.actionToolBar.setEnabled(show)
        self.actionShowHideProtocol.setVisible(show)

    def resetGUI(self):
        """ Make the GUI look like it was just opened:
        * analysis options, layout etc are hidden, all buttons are not clickable
        * This method is used when a file could not be opened"""
        self.actionsSetVisible(False)
        self.resetButtons()
        self.setAllButtons("enable", False)
        self.populateDatasetComboBox(
            []
        )  # with an empty list as argument the combobox will be hidden

    def eventFilter(self, calling_object, event):
        """
        Event filter to handle additional button events (clicks are handled via method on_show)
        """
        button_id = calling_object.objectName()  # get button ID
        if event.type() == QEvent.HoverMove or event.type() == QEvent.Enter:
            # NOTE handling non-existing/gray samples is in method plotFigAny
            if self.fileLoaded:
                # plot new lines only if not registered
                if self.buttons.at[button_id, "Line2D"] is np.nan:
                    self.plotFigAny(button_id)
                    self.canvas.draw()
            # TODO highlight the curve if it has already been selected
            if calling_object.isChecked():
                pass

        if event.type() == QEvent.HoverLeave or event.type() == QEvent.Leave:
            if not calling_object.isChecked():
                if self.buttons.at[button_id, "Line2D"] is not np.nan:
                    # NOTE when draw_canvas is false, then the curve will be only removed when a new one is plotted, this makes hovering more smooth, however, creates "undeletable" plots
                    self.removeButtonLine2D(button_id)

        return False

    ## \brief This method plots a curve from a single well on the axes using the curve* set of settings and the processing status (raw or after analysis)
    def plotFigAny(self, wellID):
        """
        Plot a curve from a single well on the axes
        using the curve* set of settings and the processing status (raw or after analysis)

        Parameters
        ----------
        wellID
            a string with the alphanumeric well id; non-existent ID's are also handled
        """
        # some starting settings
        # NOTE MoltenProt internally uses K, but in future chemical denaturants can be here, too
        xlabel = "Temperature, K"
        ylabel = self.moltenProtFit.readout_type
        # variable to have only one legend entry for exp/fit plots
        sample_label = False

        # set the color of all curves to be plotted
        if self.curveHeatmapColorCheckBoxIsChecked:
            current_color = self.buttons.at[wellID, "Color"]
        else:
            current_color = self.currentCurveColor

        # a list of all plotted lines
        lines = []

        # check if the well exists anywhere in the data
        if self.moltenProtFit.testWellID(wellID, ignore_results=True):
            # a flag to request raw data plotting
            # will only be false when processed data is available and plotted
            plot_raw = True

            # the well is definitely recorded, but the fit might have failed or not even performed
            if self.dataProcessed:
                # main plotting part
                if self.moltenProtFit.testWellID(wellID, ignore_results=False):
                    # sample was successfully fit
                    # the displayable elements primarily depend on curve type
                    # applicable to all types:
                    # curveLegendComboboxCurrentText - either show ID in legend or annotation, or no legend at all
                    # curveMarkEverySpinBoxValue - density of datapoints
                    # curveViewComboboxCurrentText - Datapoints, Fit, Datapoints + Fit - also for van 't Hoff?
                    # applicable to exp and funf
                    # applicable to exp only
                    # curveDerivativeCheckBoxIsChecked - yes/no derivative plot
                    # curveBaselineCheckBoxIsChecked - yes/no baselines

                    # sample label is taken from the layout or well ID
                    label = wellID
                    if self.curveLegendComboboxCurrentText == "Annotation":
                        label = self.moltenProtFit.plate_results.at[wellID, "Condition"]

                    if self.curveTypeComboboxCurrentText == "Experimental signal":
                        if self.curveViewComboboxCurrentText in ("Datapoints", "Datapoints + Fit"):
                            lines += self.axes.plot(
                                self.moltenProtFit.plate[wellID].index.values,
                                self.moltenProtFit.plate[wellID],
                                lw=0,
                                marker=".",
                                markevery=self.curveMarkEverySpinBoxValue,
                                label=label,
                                color=current_color,
                            )
                            sample_label = True
                        if self.curveViewComboboxCurrentText in ("Fit","Datapoints + Fit"):
                            # if exp signal was plotted, do not add label to fit
                            if sample_label:
                                lines += self.axes.plot(
                                    self.moltenProtFit.plate_fit[wellID].index.values,
                                    self.moltenProtFit.plate_fit[wellID],
                                    color=current_color,
                                )
                            else:
                                lines += self.axes.plot(
                                    self.moltenProtFit.plate_fit[wellID].index.values,
                                    self.moltenProtFit.plate_fit[wellID],
                                    color=current_color,
                                    label=label,
                                )

                        # draw Tm/Tagg or Tons
                        lines += self.plotVlines(wellID, current_color)

                        if self.curveBaselineCheckBoxIsChecked:
                            # draw baselines
                            # calculate polynomials
                            poly_pre = np.poly1d(
                                *self.moltenProtFit.plate_results.loc[
                                    [wellID], ["kN_fit", "bN_fit"]
                                ].values
                            )
                            poly_post = np.poly1d(
                                *self.moltenProtFit.plate_results.loc[
                                    [wellID], ["kU_fit", "bU_fit"]
                                ].values
                            )
                            xmin_xmax = (
                                self.moltenProtFit.plate[wellID].index.min(),
                                self.moltenProtFit.plate[wellID].index.max(),
                            )
                            lines += self.axes.plot(
                                xmin_xmax,
                                poly_pre(xmin_xmax),
                                linestyle="--",
                                color=current_color,
                            )
                            lines += self.axes.plot(
                                xmin_xmax,
                                poly_post(xmin_xmax),
                                linestyle="--",
                                color=current_color,
                            )
                    elif self.curveTypeComboboxCurrentText == "Baseline-corrected":
                        if self.moltenProtFit.plate_raw_corr is not None:
                            # NOTE In this plotting mode no fit data exists
                            if self.curveViewComboboxCurrentText in ("Datapoints", "Datapoints + Fit"):
                                lines += self.axes.plot(
                                    self.moltenProtFit.plate_raw_corr[
                                        wellID
                                    ].index.values,
                                    self.moltenProtFit.plate_raw_corr[wellID],
                                    lw=0,
                                    # linestyle=":",
                                    marker=".",
                                    markevery=self.curveMarkEverySpinBoxValue,
                                    label=label,
                                    color=current_color,
                                )
                                self.axes.set_ylim([-0.2, 1.2])
                                # current_color = self.axes.get_lines()[-1].get_color()
                                # draw Tm/Tagg or Tons
                                lines += self.plotVlines(wellID, current_color)

                            if self.curveViewComboboxCurrentText in ("Fit", "Datapoints + Fit"):
                                # show warning in the status bar that the fit is not available here
                                self.status_text.setText(
                                    "Fit data are not available in this plotting mode"
                                )
                                # show the derivative on the extra plot
                    if (
                        self.curveDerivativeCheckBoxIsChecked
                        and self.axesDerivative is not None
                    ):
                        if self.curveTypeComboboxCurrentText == "Experimental signal":
                            lines += self.axesDerivative.plot(
                                self.moltenProtFit.plate_derivative[
                                    wellID
                                ].index.values,
                                self.moltenProtFit.plate_derivative[wellID],
                                color=current_color,
                            )
                        else:
                            # derivative only available for exp signal
                            lines.append(
                                self.axesDerivative.text(
                                    0.5,
                                    0.5,
                                    "n/a",
                                    horizontalalignment="center",
                                    verticalalignment="center",
                                    transform=self.axesDerivative.transAxes,
                                )
                            )
                        self.axesDerivative.set_xlabel("Temperature")
                        self.axesDerivative.set_ylabel("1st Deriv.")
                        # rescale axes
                        self.axesDerivative.relim()
                        self.axesDerivative.autoscale_view()
                    # skip raw data plotting
                    plot_raw = False

            if plot_raw:
                # this is run in two cases: when then there are gray wells after analysis, or when no processing done yet
                # NOTE this mode ignores the curveLegendComboBox and curveHeatmapColorCheckBox
                sourcedf = self.moltenProtFit.plate_raw
                lines += self.axes.plot(
                    sourcedf[wellID].index.values,
                    sourcedf[wellID],
                    label=wellID,
                    color=self.currentCurveColor,
                )
        else:
            print("Debug: non-existent well ID called: {}".format(wellID))

        # set labels for axes
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        # set xlim for axes based on the respective MoltenProt instance
        self.axes.set(xlim=self.moltenProtFit.xlim)
        # rescale axes
        self.axes.relim()
        self.axes.autoscale_view()

        # create legend (if respective axes already exists)
        if (
            self.curveLegendComboboxCurrentText != "None"
            and self.axesLegend is not None
        ):
            ncol = 1
            # select column number based on the legend display mode
            if self.curveLegendComboboxCurrentText == "ID":
                ncol = 8
            if self.curveLegendComboboxCurrentText == "Annotation":
                ncol = 2

            self.legend = self.axes.legend(
                bbox_to_anchor=(0.0, 0.8, 1.0, 0.0),
                bbox_transform=self.axesLegend.transAxes,
                ncol=ncol,
                mode="expand",
            )
        # if plotting was successful, record the line color and line list for future reference
        self.buttons.at[wellID, "LineColor"] = current_color
        self.buttons.at[wellID, "Line2D"] = lines

    def plotVlines(self, wellID, current_color):
        """
        Adds a Tm/Tagg or Tonset vertical line for wellID with color current_color based on the settings

        Arguments
        ---------
        wellID
            ID of the sample to plot
        current_color
            which color to use

        Returns
        -------
        A list of plotted Line2D objects

        Notes
        -----
        Lines may have different names from different models; just use the contents of MPFit.plotlines
        """
        out = []
        if self.curveVlinesCheckBoxIsChecked:
            for parameter_name in self.moltenProtFit.plotlines:
                # NOTE lines are not labeled so that they are not listed in the legend
                out.append(
                    self.axes.axvline(
                        self.moltenProtFit.plate_results[parameter_name][wellID],
                        ls="dotted",
                        c=current_color,
                        lw=3,
                    )
                )
                # add text with the parameter used to generate the line
                out.append(
                    self.axes.text(
                        self.moltenProtFit.plate_results[parameter_name][wellID],
                        self.axes.get_ylim()[0]
                        + 0.05 * (self.axes.get_ylim()[1] - self.axes.get_ylim()[0]),
                        " " + parameter_name,
                    )
                )
        return out

    def manageSubplots(self):
        r"    ## \brief this method creates subplots for derivative and/or legend"
        if self.dataProcessed:
            self.getPlotSettings()
            self.fig.clear()
            if (
                self.curveDerivativeCheckBoxIsChecked
                and self.curveLegendComboboxCurrentText != "None"
            ):
                self.axes = self.fig.add_subplot(3, 1, 1)
                # TODO hide ticks for main plot when deriv plot is on
                self.axesDerivative = self.fig.add_subplot(3, 1, 2, sharex=self.axes)
                self.axesLegend = self.fig.add_subplot(3, 1, 3)
            elif self.curveDerivativeCheckBoxIsChecked:
                self.axes = self.fig.add_subplot(2, 1, 1)
                self.axesDerivative = self.fig.add_subplot(2, 1, 2, sharex=self.axes)
                self.axesLegend = None
            elif self.curveLegendComboboxCurrentText != "None":
                self.axes = self.fig.add_subplot(2, 1, 1)
                self.axesDerivative = None
                self.axesLegend = self.fig.add_subplot(2, 1, 2)
            else:
                # nothing checked - just keep the main plot
                self.axes = self.fig.add_subplot(1, 1, 1)
                self.axesDerivative = None
                self.axesLegend = None
            # remove spines from legend subplot
            if self.axesLegend is not None:
                self.axesLegend.axis("off")
            # set axes grids
            self.axes.grid(True)
            if self.axesDerivative is not None:
                self.axesDerivative.grid(True)
        else:
            # without complete analysis most visualizations are not possible
            self.status_text.setText(
                "Run analysis to enable additional plotting options"
            )

    @Slot()
    def on_legendChecked(self):
        r" \brief This method shows or hides the legend."
        self.getPlotSettings()
        self.fig.clear()
        if self.curveLegendComboboxCurrentText != "None":
            # create a dedicated subplot for holding the legend
            if self.axesDerivative is not None:
                self.axes = self.fig.add_subplot(3, 1, 1)
                self.axesDerivative = self.fig.add_subplot(3, 1, 2)
                self.axesLegend = self.fig.add_subplot(3, 1, 3)
            else:
                self.axes = self.fig.add_subplot(2, 1, 1)
                # self.axesDerivative = self.fig.add_subplot(2,1,2)
                self.axesLegend = self.fig.add_subplot(2, 1, 2)
        else:
            # remove existing legend
            if self.axesLegend is not None:
                if self.axesDerivative is not None:
                    self.axes = self.fig.add_subplot(2, 1, 1)
                    self.axesDerivative = self.fig.add_subplot(2, 1, 2)
                else:
                    self.axes = self.fig.add_subplot(1, 1, 1)

    @Slot()
    def on_curveBaselineCheckBoxChecked(self):
        "Prints status of curve baseline checkbox"
        if showVersionInformation:
            print(
                "on_curveBaselineCheckBoxChecked",
                self.moltenProtToolBox.curveBaselineCheckBox.isChecked(),
                cfFilename,
                currentframe().f_lineno,
            )

    def createMatplotlibStuff(self):
        "Embeds matplotlib elements in the GUI"
        self.main_frame = QWidget()
        self.fig = Figure()
        self.axes = self.fig.add_subplot()
        self.axes.grid(True)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        self.main_frame.setLayout(left_vbox)

    def addDerivativeSublot(self):
        "Add a subplot to show the derivative"
        self.axesDerivative = self.fig.add_subplot(2, 1, 2)

    def createMatplotlibContextMenu(self):
        "show context menu of matplolib window, show/hide legend, show/hide derivative plot - currently not used"
        self.main_frame.setContextMenuPolicy(Qt.ActionsContextMenu)
        # show/hide legend
        # self.showLegendAction = QAction("Show legend",  self.main_frame)
        # self.showLegendAction.setCheckable(True)
        # Show or hide the legend.
        # self.showLegendAction.triggered.connect(self.on_legendChecked)
        # Create matplotlib - show/hide the derivative.
        # self.showDerivativeSubplotAction = QAction("Show derivative subplot",  self.main_frame)
        # self.showDerivativeSubplotAction.setCheckable(True)
        # Hide the derivative window.
        # self.showDerivativeSubplotAction.setVisible(False)
        # actions after using the checkbox
        # add matplolib actions to Qt context menu
        # self.main_frame.addAction(self.showLegendAction)
        # self.main_frame.addAction(self.showDerivativeSubplotAction)

    def createHeatmapDockWidget(self):
        r"## \brief This method assignes to  the stackable window heatmap."
        heatmapDockWidget = self.heatmapDockWidget
        return heatmapDockWidget

    def createHeatmapButtons(self):
        "Create buttons in the dockable heatmap widget"
        self.dockButtonsFrame = QWidget(self.heatmapDockWidgetContents)
        hbox = QHBoxLayout()
        self.createButtonArray(hbox)
        self.dockButtonsFrame.setLayout(hbox)

    
    def createComboBoxesForActionToolBar(self):
        r'## \brief This method creates sortScoreComboBox and datasetComboBox, sets tooltips for them'
        ## \brief  This attribute holds the sortScoreComboBox.
        self.sortScoreComboBox = QComboBox()
        self.sortScoreComboBox.setToolTip("Select sort score")
        self.sortScoreComboBox.currentIndexChanged.connect(
            self.setButtonsStyleAccordingToNormalizedData
        )
        ## \brief  This attribute holds the datasetComboBox.
        self.datasetComboBox = QComboBox()
        self.datasetComboBox.setToolTip("Select a dataset for viewing")
        self.datasetComboBox.currentIndexChanged.connect(self.on_changeInputTable)
        self.heatmapMultipleListView = QListView(self.datasetComboBox)
        self.datasetComboBox.setView(self.heatmapMultipleListView)
        self.datasetComboBoxAction = self.actionToolBar.addWidget(self.datasetComboBox)

    def createColorMapComboBox(self):
        "Initializes colormap combobox widget"
        self.colorMapComboBox = self.moltenProtToolBox.colormapForPlotComboBox
        self.moltenProtToolBox.colormapForPlotLabel.hide()
        self.colorMapComboBox.hide()
        self.colorMapComboBox.insertItems(1, self.colorMapNames)
        index = int(
            self.settings.value(
                "toolbox/miscSettingsPage/colormapForPlotComboBoxIndex", 0
            )
        )
        self.colorMapComboBox.currentIndexChanged.connect(self.on_changeColorMap)
        self.moltenProtToolBox.colormapForPlotComboBox.setCurrentIndex(index)

    @Slot()
    def on_changeColorMap(self):
        "Actions when color map is changed"
        self.currentColorMapIndex = self.colorMapComboBox.currentIndex()
        self.currentColorMap = self.colorMapNames[self.currentColorMapIndex]
        self.on_deselectAll()  # TODO can this be avoided?
        if self.moltenProtFit is not None:
            self.setButtonsStyleAccordingToNormalizedData()

    def populateAndShowSortScoreComboBox(self):
        r"""
             \brief This method adds  self.sortScoreComboBox to self.actionToolBar if it was not already added. Then clears items in it, populates self.sortScoreComboBox by self.moltenProtFit.getResultsColumns() method and shows it. \sa core.MoltenProtFit.getResultsColumns() \sa sortScoreComboBox

        """
        if self.sortScoreCombBoxAction is None:
            self.sortScoreCombBoxAction = self.actionToolBar.addWidget(
                self.sortScoreComboBox
            )
        self.sortScoreComboBox.clear()
        self.sortScoreComboBox.insertItems(1, self.moltenProtFit.getResultsColumns())
        width = self.sortScoreComboBox.minimumSizeHint().width()
        self.sortScoreComboBox.setMinimumWidth(width)
        self.sortScoreCombBoxAction.setVisible(True)

    def createMainWindow(self):
        r"""
            # \brief This method creates MoltenProt GUI application main window.
      \details
      This method:
      - Creates Matplotlib GUI elements.
      - Creates MoltenProt MainWindow and set Matplotlib main_frame as CentralWidget.
      - Creates ComboBoxes for ActionToolBar via createComboBoxesForActionToolBar method. \sa createComboBoxesForActionToolBar

        """
        self.fileLoaded = False
        self.dataProcessed = False
        self.createMatplotlibStuff()
        # self = load_uic(":/main.ui", self)         # no effect in PySide6
        self.setCentralWidget(self.main_frame)
        self.createComboBoxesForActionToolBar()
        self.actionToolBar.setVisible(False)
        self.actionToolBar.setEnabled(False)

        self.heatmapDockWidgetContents = QWidget(self.heatmapDockWidget)
        self.heatmapDockWidgetContents.setObjectName("heatmapDockWidgetContents")
        self.heatmapDockWidget.setWidget(self.heatmapDockWidgetContents)

        self.tableDockWidget.hide()
        self.tableDockWidget = self.tableDockWidget
        tableWidget = self.tableWidget
        tableWidget.setColumnCount(5)  # ATTENTION has to be set dynamically
        header = tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        tableWidget.setSortingEnabled(True)
        tableWidget.setAlternatingRowColors(True)
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tableWidget.hide()
        self.tableWidget = tableWidget
        self.heatmapDockWidget.setMinimumWidth(560)
        # Hide the Protocol DockWidget
        self.protocolDockWidget.setVisible(False)

        # self.createColormap()
        self.createHeatmapButtons()
        self.connectSignals2Actions()
        self.actionSave_as_JSON.setVisible(False)

        self.font = QFont("Arial", 10)

    def connectSignals2Actions(self):
        "Connects callback methods to Qt actions"
        self.actionNew.triggered.connect(self.on_actionNewTriggered)
        self.actionLoad.triggered.connect(self.on_loadFile)
        self.actionLoad_sample_data.triggered.connect(self.on_actionLoad_sample_data)
        self.actionSave_as_JSON.triggered.connect(self.on_actionSave_as_JSONTriggered)
        self.actionQuit.triggered.connect(self.on_closeMoltenProtMainWindow)
        self.actionAbout.triggered.connect(self.on_actionAbout)
        self.actionCite_MoltenProt.triggered.connect(self.on_actionCite_MoltenProt)
        self.actionHelp.triggered.connect(self.on_actionHelp)
        self.actionAnalysis.triggered.connect(self.on_analysisPushButtonClicked)
        self.actionActions.triggered.connect(self.on_showmoltenProtToolBox)
        self.actionExport.triggered.connect(self.on_exportResults)
        self.actionDeselectAll.triggered.connect(self.on_deselectAll)
        self.actionSelectAll.triggered.connect(self.on_selectAll)
        self.actionEdit_layout.triggered.connect(self.editLayout)
        self.actionPrtSc.triggered.connect(self.on_saveMainWindowAsPng)
        self.actionShowHideProtocol.triggered.connect(self.on_actionShowHideProtocol)
        self.actionFont.triggered.connect(self.on_actionFontTriggered)

    @Slot()
    def on_closeMoltenProtMainWindow(self):
        "Callback for closing the main window; will check if any export threads are still running"
        msg = QMessageBox(self)
        msg.setFont(self.font)
        msg.setWindowTitle("MoltenProt")
        if self.threadIsWorking:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Some thread is still running. Please try later.")
            msg.setStandardButtons(QMessageBox.Ok)
        else:
            msg.setIcon(QMessageBox.Question)
            msg.setText("Are you sure that you want to close MoltenProt?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
            if retval == QMessageBox.Ok:
                self.closeWithoutQuestion = True
                self.close()

    def closeEvent(self, event):
        "Handling threading events"
        msg = QMessageBox()
        msg.setFont(self.font)
        msg.setWindowTitle("MoltenProt")
        if self.threadIsWorking:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Some thread is still running. Please try later.")
            msg.setStandardButtons(QMessageBox.Ok)
            event.ignore()
        else:
            if self.closeWithoutQuestion:
                event.accept()
            else:
                msg.setIcon(QMessageBox.Question)
                msg.setText("Are you sure that you want to close MoltenProt?")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                retval = msg.exec_()
                if retval == QMessageBox.Ok:
                    event.accept()
                else:
                    event.ignore()

    @Slot()
    def on_actionShowHideProtocol(self):
        "Callback for hide/show protocol window"
        self.protocolDockWidget.setVisible(self.actionShowHideProtocol.isChecked())
        # read protocol from the currently viewed MoltenProtFit instance
        if self.moltenProtFit is not None:
            self.protocolPlainTextEdit.setPlainText(self.moltenProtFit.protocolString)

    def connectButtonsFromLayoutDialog(self):
        "Sets up callbacks for layout dialog buttons"
        # if OK clicked - update layout as it is
        self.layoutDialog.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(
            self.updateLayout
        )
        # NOTE Save button is redundant
        # self.layoutDialog.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.saveLayout)
        # Open button allow loading an external layout file and applying it to the MPFM instance
        self.layoutDialog.buttonBox.button(QDialogButtonBox.Open).clicked.connect(
            self.openLayout
        )
        # a button to restore original layout
        self.layoutDialog.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(
            self.resetLayout
        )

    def layoutTableCellClicked(self, row, column):
        "Prints row and columns clicked in the layout table"
        if showVersionInformation:
            print(row, column, currentframe().f_lineno, cfFilename)

    def createStatusBar(self):
        "initializes the status bar"
        self.status_text = QLabel("Please load a data file")
        self.statusBar().addWidget(self.status_text, 1)
    
    @Slot()
    def on_saveMainWindowAsPng(self):
        "Callback when saving the window screenshot"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            caption=self.tr("Enter png file name "),
            dir=self.lastDir,
            filter="png Files (*.png)",
        ) # the 2nd return value is the selected filter
        # NOTE file name has zero length only when user pressed Cancel
        if len(filename) > 0:
            #pixMap = QApplication.primaryScreen().grabWindow(self.winId())
            pixMap = self.grab() # this method will also work with wayland
            if pixMap.isNull():
                QMessageBox.warning(self, "MoltenProt Error", "Could not generate app screenshot")
            else:
                # add PNG suffix if needed
                if filename[-4:] != ".png":
                    filename += ".png"
                pixMap.save(filename, format=None)

    def setExpertMode(self):
        "Callback for setting the expert mode - currently not implemented"
        if showVersionInformation:
            print("setExpertMode")


def LaunchMoltenprotGUI(localizationStuffFlag=False):
    r"""
    Below is doxygen documentation code.
    \brief Start up the GUI of MoltenProt
        \details
    - Create Qt GUI application.
    - Create and show splashscreen.
    - Create MoltenProtMainWindow class instance and set it size and placement.
    - Run GUI MoltenProt application.
    \sa moltenprotgui.MoltenProtMainWindow
        \param localizationStuffFlag - If True use Qt internationalization facilities.
        \todo TODO list for MoltenprotGUI.

    Some tricks for the GUI to supprot Hi-DPI displays, see below for more info:
    https://stackoverflow.com/questions/41331201/pyqt-5-and-4k-screen
    https://doc.qt.io/qt-5/highdpi.html
    """
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    splashPixmap = QPixmap(":/splash.png")
    splash = QSplashScreen(splashPixmap)
    splash.setEnabled(False)
    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, splashPixmap.height() - 50, splashPixmap.width(), 20)
    splash.show()
    for i in range(1, 11):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
            app.processEvents()

    if localizationStuffFlag:
        # Localization stuff
        locale = QLocale.system().name()
        print(locale)
        qtTranslator = QTranslator()
        # if qtTranslator.load("qt_" + locale, ":/"):
        if qtTranslator.load("qt_ru", ":/"):
            app.installTranslator(qtTranslator)
        else:
            print("Failed to load locale")
        appTranslator = QTranslator()
        if appTranslator.load("moltenprot_ru", ":/"):
            app.installTranslator(appTranslator)
        else:
            print("Failed to load application locale.")
    else:
        pass  # Localization not implemented
    app.setOrganizationName("MoltenProt")
    app.setApplicationName("moltenprot")
    app.setWindowIcon(QIcon(":/MP_icon.png"))
    # print app.arguments()
    moltenProtMainWindow = MoltenProtMainWindow()

    width = int(moltenProtMainWindow.width())
    height = int(moltenProtMainWindow.height())
    screen_size = app.primaryScreen().availableSize()
    screenWidth = int(screen_size.width())
    screenHeight = int(screen_size.height())
    moltenProtMainWindow.setGeometry(
        int((screenWidth / 2) - (width / 2)),
        int((screenHeight / 2) - (height / 2)),
        width,
        height,
    )

    # forces main window decorator on Windows
    moltenProtMainWindow.setWindowFlags(Qt.Window)
    moltenProtMainWindow.show()
    # Hide splashscreen
    splash.finish(moltenProtMainWindow)
    app.exec_()
