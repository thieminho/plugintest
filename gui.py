import os, sys, inspect
'''current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)'''
#from application import mainWindow
import glob
import importlib
import importlib.util
from pathlib import PureWindowsPath, PurePosixPath, PurePath
import pandas as pd
import shutil
from distutils.dir_util import copy_tree
from PyQt5.QtCore import pyqtSlot, QMutex, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QFileDialog, QGridLayout, \
    QMessageBox, QVBoxLayout, QColorDialog, QListWidget, QListWidgetItem, QMainWindow, QLineEdit, QApplication
from visualizer.visualizer import Visualizer


class App(QWidget):
    def __init__(self):
        super().__init__()
        #self.mutex = QMutex()
        self.setStyleSheet("background-color: #E7ECFA;")
        #generating list of available plugins
        self.list_of_files = glob.glob("plugins\*.py")
        self.list_of_files = [x.split('.')[0] for x in self.list_of_files]
        self.list_of_files = [x.split('\\')[-1] for x in self.list_of_files]
        self.PLUGIN_NAME = "plugins."
        self.filename = None
        self.last_filename_from_filedialog = None
        self.result_file = ""
        #set size and title of main window
        self.title = 'Visualizer'
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 400
        #self.setAcceptDrops(True)
        self.init_ui()


    def init_ui(self):
        #main window
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.parameters = None
        self.grid = QGridLayout(self)
        # self.grid.addLayout(self.parameters, 0, 2, 4, 1)

        #button to load xes/csv file
        self.button_load = QPushButton('Dodaj plik', self)
        self.button_load.setStyleSheet("background-color: #8FAAF7;")
        self.grid.addWidget(self.button_load, 0, 0)
        self.button_load.clicked.connect(self.on_click)
        self.label_file = QLabel(self)
        self.grid.addWidget(self.label_file, 2, 0)
        self.label_file.setText("Dodaj/upuść plik")
        self.label_file.adjustSize()

        '''self.listbox_file = ListBoxWidget(self)
        self.grid.addWidget(self.listbox_file, 0, 2)

        self.btn = QPushButton('Get Value', self)
        self.grid.addWidget(self.btn, 1, 2)
        self.btn.clicked.connect(lambda: print(self.getSelectedItem()))
        self.edit1 = ListBoxWidget(self)
        self.grid.addWidget(self.edit1, 1, 2)
        self.btn = QPushButton('Get Value', self)
        self.grid.addWidget(self.btn, 1, 3)
        self.btn.clicked.connect(lambda: print(self.getSelectedItem()))'''
        #self.button = Button('&Button', self)
        #self.grid.addWidget(self.button, 1, 3)

        self.listbox_view = ListBoxWidget(self)
        self.listbox_view.setStyleSheet("background-color: #BBCCFB;")
        self.grid.addWidget(self.listbox_view, 1, 0)
        self.btn = QPushButton('Usuń plik', self)
        self.grid.addWidget(self.btn, 8, 0)
        self.btn.clicked.connect(self.remove_file_from_list)


        #combobox to choose plugin
        self.combo = QComboBox(self)
        self.combo.setStyleSheet("background-color: #8FAAF7;")
        self.combo.addItem(" ")
        self.combo.addItems(self.list_of_files)
        self.grid.addWidget(self.combo, 4, 0)
        self.qlabel = QLabel(self)
        self.grid.addWidget(self.qlabel, 5, 0)
        self.qlabel.setText("Nie wybrano modułu")
        self.qlabel.adjustSize()
        #run on_changed function after click on name of plugin
        self.combo.activated[str].connect(self.on_changed)

        #create object of visualizer and add it to window
        self.visualizer = Visualizer()
        self.visualizer.setStyleSheet("background-color: #8FAAF7;")
        self.grid.addWidget(self.visualizer, 0, 1, -1, -1)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 4)
        self.setLayout(self.grid)

        #button to start processing
        self.button_start = QPushButton("Uruchom", self)
        self.button_start.setStyleSheet("background-color: #8FAAF7;")
        self.button_start.resize(30, 10)
        self.grid.addWidget(self.button_start, 6, 0)
        #run analyze_data after click on button
        self.button_start.clicked.connect(self.analyze_data)
        self.label = QLabel(self)
        #self.label.setFixedSize(100, 50)
        self.grid.addWidget(self.label)

        self.button_new_plugin = QPushButton("Dodaj nowy moduł", self)
        self.button_new_plugin.setStyleSheet("background-color: #8FAAF7;")
        self.button_new_plugin.resize(30, 10)
        self.grid.addWidget(self.button_new_plugin, 7, 0)
        self.button_new_plugin.clicked.connect(self.add_plugin)

        self.show()


    def add_plugin(self):
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.new_plugin_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik modułu", "",
                                                       "All Files (*);;Python Files (*.py)", options=self.options)
        #albo my_dir = QtGui.QFileDialog.getExistingDirectory jak chcemy foldery
        if self.new_plugin_path:
            self.temp_path = os.path.dirname(os.path.abspath(__file__))
            self.temp_path = PurePath(self.temp_path).parts[0:-1]
            self.to_directory = os.path.join(*self.temp_path, "gui/plugins")
            print(self.to_directory)
            print(self.new_plugin_path)
            shutil.copy(self.new_plugin_path, self.to_directory)
            self.list_of_files = glob.glob("plugins\*.py")
            self.list_of_files = [x.split('.')[0] for x in self.list_of_files]
            self.list_of_files = [x.split('\\')[-1] for x in self.list_of_files]
            self.combo.clear()
            self.combo.addItem(" ")
            self.combo.addItems(self.list_of_files)

    def remove_file_from_list(self):
        self.listbox_view.takeItem(self.listbox_view.currentIndex())

    @pyqtSlot()
    def on_click(self):
        #select file for processing and assign name to self.filename
        self.options = QFileDialog.Options()
        self.options |= QFileDialog.DontUseNativeDialog
        self.filename, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "",
                                                       "All Files (*);;Python Files (*.py)", options=self.options)
        self.listbox_view.addItem(self.filename)
        self.last_filename_from_filedialog = self.filename
        '''if self.filename:
            print(self.filename)
            with open(self.filename) as file:
                self.loaded_file = pd.read_csv(self.filename)'''
        #print(self.loaded_file)
        '''self.label_file.setText("Wybrany plik: " + self.filename)
        self.label_file.adjustSize()'''

    def on_changed(self, text):
        #select plugin from combobox
        self.qlabel.setText("Wybrany moduł: " + text)
        self.qlabel.adjustSize()

        #print(self.filename)
        self.PLUGIN_NAME = "plugins."
        self.PLUGIN_NAME += text
        self.plugin_module = importlib.import_module(self.PLUGIN_NAME, ".")
        plugin = self.plugin_module.Plugin()
        #print(self.grid.columnCount())
        #load parameters from plugin using fill_my_parameters() class function
        if self.parameters == None:
            print('Adding parameters to window')
            self.parameters = QVBoxLayout()
            self.grid.addLayout(self.parameters, 0, 2, 4, 1)
            self.fill_base_parameters()
            #add fill_specific_parameters()
            plugin.fill_my_parameters(self.parameters)
        else:
            self.grid.addLayout(self.parameters, 0, 2, 4, 1)
            self.clearLayout(self.parameters)
            plugin.fill_my_parameters(self.parameters)
            self.fill_base_parameters()
        print("end")


    @pyqtSlot()
    def analyze_data(self):
        #checking if plugin and file have been selected
        print(self.listbox_view.currentItem())
        if self.listbox_view.currentItem():
            self.filename = self.listbox_view.currentItem().text()
        else:
            self.filename = self.last_filename_from_filedialog

        self.label_file.setText("Wybrany plik: " + self.filename)
        self.label_file.adjustSize()
        if self.PLUGIN_NAME == "plugins." and self.filename is None:
            msg_plugin_file = QMessageBox()
            msg_plugin_file.setIcon(QMessageBox.Critical)
            msg_plugin_file.setText("Błąd")
            msg_plugin_file.setInformativeText('Nie wybrano modułu i nie wczytano pliku')
            msg_plugin_file.setWindowTitle("Błąd")
            msg_plugin_file.exec_()
        elif self.filename is None and self.PLUGIN_NAME != "plugins.":
            print("wczytaj plik")
            msg_file = QMessageBox()
            msg_file.setIcon(QMessageBox.Critical)
            msg_file.setText("Błąd")
            msg_file.setInformativeText('Nie wczytano pliku do analizy')
            msg_file.setWindowTitle("Błąd")
            msg_file.exec_()
        elif self.PLUGIN_NAME == "plugins." and self.filename is not None:
            msg_plugin = QMessageBox()
            msg_plugin.setIcon(QMessageBox.Critical)
            msg_plugin.setText("Błąd")
            msg_plugin.setInformativeText('Nie wybrano modułu')
            msg_plugin.setWindowTitle("Błąd")
            msg_plugin.exec_()
        else:
            print("hej")
            #print(self.plugin, self.filename)
            self.plugin = self.plugin_module.Plugin()
            execution = self.plugin.execute(self.filename)
            self.result_file = execution[1]
            if execution[0] == "success":
                self.label.setText("Success, file saved in {}".format(execution[1]))
                self.label.adjustSize()
            else:
                self.label.setText("Error")
                self.label.adjustSize()
        if self.visualizer.used is True:
            del self.visualizer
            self.visualizer = Visualizer()
            self.grid.addWidget(self.visualizer, 0, 1, 4, 1)
            self.visualizer.base_color = self.node_color_choice.currentText()
            self.visualizer.base_edge_color = self.edge_color_choice.currentText()
            self.visualizer.set_graph_to_network(filename=self.result_file)
            self.visualizer.show()
            self.clearLayout(self.parameters)
            self.grid.removeItem(self.parameters)
        else:
            #self.visualizer = Visualizer()
            # self.visualizer.set_graph_to_network()
            '''grid.addWidget(self.visualizer, 0, 1, 4, 1)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 4)
            self.setLayout(grid)'''
            self.visualizer.base_color = self.node_color_choice.currentText()
            self.visualizer.base_edge_color = self.edge_color_choice.currentText()
            self.visualizer.set_graph_to_network(filename=self.result_file)
            self.visualizer.show()
            self.clearLayout(self.parameters)
            self.grid.removeItem(self.parameters)

    def fill_base_parameters(self):
        # TODO: Change it to colorPicker
        self.edge_color_choice = QComboBox(self)
        self.node_color_choice = QComboBox(self)
        node_color_label = QLabel('Choose Node Color:')
        colors = ['red', 'green', 'blue', 'purple', 'black', 'white']
        edge_color_label = QLabel('Choose Edge Color:')
        self.parameters.addWidget(node_color_label)
        self.node_color_choice.addItems(colors)
        self.parameters.addWidget(self.node_color_choice)

        # add edge color choice.
        self.parameters.addWidget(edge_color_label)
        self.edge_color_choice.addItems(colors)
        self.parameters.addWidget(self.edge_color_choice)

    def clearLayout(self, lay):
        while lay.count():
            child = lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class ListBoxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.resize(100, 50)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                # https://doc.qt.io/qt-5/qurl.html
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                    #mainWindow.label_file.setText("Wybrany no: ")
                    #mainWindow.filename = url.toLocalFile()
                else:
                    links.append(str(url.toString()))
            self.addItems(links)
        else:
            event.ignore()



'''
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                print(url)
                # https://doc.qt.io/qt-5/qurl.html
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))
            self.addItems(links)
        else:
            event.ignore()
print('drop event')
        #self.setText(event.mimeData().text())
        #for url in event.mimeData().urls():
        path = event.mimeData().urls()[0].toLocalFile()
        print(path)
        #mainWindow.filename = path
        #mainWindow.left = 20
        print(mainWindow.left)
        #print(mainWindow.filename)
        event.accept()
            #mainWindow.label_file.setText("Wybrany plik: " + mainWindow.filename)
            #mainWindow.label_file.adjustSize()
            #print(App.filename)'''

mainWindow = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = App()
    mainWindow.show()
    sys.exit(app.exec_())