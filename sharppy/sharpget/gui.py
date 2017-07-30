from PySide.QtCore import *
from PySide.QtGui import *
import os
import os.path
from profileList import ProfileList, createList
from sharppy.io.decoder import getDecoders
from bz2 import compress
from json import dumps

class DownloadThread(QThread):
    status_update = Signal(str)
    def __init__(self, profile_list, archive_path):
        super(DownloadThread, self).__init__()
        self.profile_list = profile_list
        self.archive_path = archive_path    
    def __del__(self):
        self.wait()
    def run(self):
        download_count = 0
        for x in range(len(self.profile_list)):
            if self.profile_list[x].enabled:
                self.status_update.emit(self.profile_list[x].url)
                for decname, deccls in getDecoders().iteritems():
                    try:
                        dec = deccls(self.profile_list[x].url)
                        break
                    except:
                        dec = None
                        continue
                if dec is not None:
                    self.status_update.emit(' - Downloaded')
                    try:
                        profs = dec.getProfiles(indexes=None)
                        file_name = os.path.join(self.archive_path, self.profile_list[x].get_archive_file(profs.getCurrentDate()))
                        with open(file_name, 'wb') as out_file:
                            out_file.write(compress(dumps(profs.serialize(stringify_date=True))))
                        self.status_update.emit(', Archived\n')
                        download_count += 1
                    except:
                        self.status_update.emit(', Archive Failed\n')
                else:
                    self.status_update.emit(' - Download Failed\n')
        self.status_update.emit('\nDone.\nSaved {0:d} profile{1:s} successfully'.format(download_count, '' if download_count == 1 else 's'))
        
class AddEditDialog(QDialog):
    def __init__(self, title, model=None, loc=None, url=None, enabled=None, parent=None):
        super(AddEditDialog, self).__init__(parent)
        self.remove_profile = False
        self.setWindowTitle(title)
        self.resize(570, 160)
        layout = QVBoxLayout(self)
        form = QWidget()
        form_layout = QHBoxLayout()
        form_layout.setContentsMargins(0,0,0,0)
        form.setLayout(form_layout)
        form_left = QWidget()
        form_left_layout = QVBoxLayout()
        form_left_layout.setContentsMargins(0,0,0,0)
        form_left.setLayout(form_left_layout)
        form_right = QWidget()
        form_right_layout = QVBoxLayout()
        form_right_layout.setContentsMargins(0,0,0,0)
        form_right.setLayout(form_right_layout)
        form_layout.addWidget(form_left)
        form_layout.addWidget(form_right)
        form_left_layout.addWidget(QLabel('Model'))
        self.model = QLineEdit()
        if model is not None:
            self.model.setText(model)
        form_right_layout.addWidget(self.model)
        form_left_layout.addWidget(QLabel('Location'))
        self.loc = QLineEdit()
        if loc is not None:
            self.loc.setText(loc)
        form_right_layout.addWidget(self.loc)
        form_left_layout.addWidget(QLabel('URL'))
        self.url = QLineEdit()
        if url is not None:
            self.url.setText(url)
        form_right_layout.addWidget(self.url)
        form_left_layout.addWidget(QLabel('Enabled'))
        self.enabled = QCheckBox()
        if enabled is not None:
            self.enabled.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
        else:
            self.enabled.setCheckState(Qt.CheckState.Checked)
        form_right_layout.addWidget(self.enabled)
        layout.addWidget(form)
        layout.addStretch(1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Close | QDialogButtonBox.Save,
            Qt.Horizontal, self)
        if loc is not None and model is not None and url is not None and enabled is not None:
            remove_button = buttons.addButton('Remove', QDialogButtonBox.DestructiveRole)
            remove_button.clicked.connect(self.remove)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def remove(self):
        self.remove_profile = True
        self.reject()
    def getModel(self):
        return self.model.text()
    def getLoc(self):
        return self.loc.text()
    def getURL(self):
        return self.url.text()
    def getEnabled(self):
        return self.enabled.isChecked()
    @staticmethod
    def getNewProfile(title, parent=None):
        dialog = AddEditDialog(title, parent=parent)
        result = dialog.exec_()
        return ((dialog.getModel(), dialog.getLoc(), dialog.getURL(), dialog.getEnabled()), result == QDialog.Accepted)
    @staticmethod
    def getUpdatedProfile(title, model, loc, url, enabled, parent=None):
        dialog = AddEditDialog(title, model=model, loc=loc, url=url, enabled=enabled, parent=parent)
        result = dialog.exec_()
        return ((dialog.getModel(), dialog.getLoc(), dialog.getURL(), dialog.getEnabled()), result == QDialog.Accepted, dialog.remove_profile)

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(LogHighlighter, self).__init__(parent)
        self.formats = []
        success_format = QTextCharFormat()
        success_format.setForeground(QColor(0,204,0))
        self.formats.append((success_format, QRegExp("\\b(?:Downloaded)|(?:Archived)\\b")))
        fail_format = QTextCharFormat()
        fail_format.setForeground(QColor(204,0,0))
        self.formats.append((fail_format, QRegExp("\\b(?:Download Failed)|(?:Archive Failed)\\b")))
    def highlightBlock(self, text):
        for text_format, expression in self.formats:
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, text_format)
                index = expression.indexIn(text, index + length)

class SHARPGetGUI(QWidget):
    def __init__(self, config, **kwargs):
        super(SHARPGetGUI, self).__init__(**kwargs)
        self.__lists__ = []
        self.config = config
        # Setup directories
        if not self.config.has_section('paths'):
            self.config.add_section('paths')
        if not self.config.has_option('paths', 'sharpget_lists'):
            self.config.set('paths', 'sharpget_lists', os.path.abspath(os.path.join(os.getcwd(), 'lists')))
            if not os.path.exists(self.config.get('paths', 'sharpget_lists')):
                os.makedirs(self.config.get('paths', 'sharpget_lists'))
        if not self.config.has_option('paths', 'archive_path'):
            self.config.set('paths', 'archive_path', os.path.abspath(os.path.join(os.getcwd(), 'archive')))
            if not os.path.exists(self.config.get('paths', 'archive_path')):
                os.makedirs(self.config.get('paths', 'archive_path'))
        self.list_combobox = None
        self.__initUI()
    def __initUI(self):
        self.control_widget = QVBoxLayout()
        self.setLayout(self.control_widget)
        self.list_controls = QWidget()
        self.list_controls_layout = QHBoxLayout()
        self.list_controls_layout.setContentsMargins(0,0,0,0)
        self.list_controls.setLayout(self.list_controls_layout)
        list_label = QLabel('Select List')
        list_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.list_controls_layout.addWidget(list_label)
        self.list_combobox = self.dropdown_menu([])
        self.list_combobox.activated.connect(self.update_list_profiles)
        self.list_controls_layout.addWidget(self.list_combobox)
        self.add_list = QPushButton('New List')
        self.add_list.clicked.connect(self.add_new_list)
        self.add_list.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.add_profile = QPushButton('Add Profile')
        self.add_profile.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_profile.clicked.connect(self.add_new_profile)
        self.default_list = QPushButton('Set Default List')
        self.default_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.default_list.clicked.connect(self.update_default_list)
        self.list_controls_layout.addWidget(self.add_list)
        self.list_controls_layout.addWidget(self.add_profile)
        self.list_controls_layout.addWidget(self.default_list)
        self.control_widget.addWidget(self.list_controls)
        self.list_profiles = QListWidget()
        self.list_profiles.doubleClicked.connect(self.edit_profile)
        self.control_widget.addWidget(self.list_profiles)
        self.download = QPushButton('Download')
        self.download.clicked.connect(self.download_clicked)
        self.control_widget.addWidget(self.download)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.control_widget.addWidget(self.log_view)
        self.log_highlight = LogHighlighter(self.log_view.document())
        self.update_available_lists()
    def add_new_list(self):
        text, ok = QInputDialog.getText(self, 'New List', 'List Name')
        if ok:
            createList(text, os.path.join(self.config.get('paths', 'sharpget_lists'), text.replace(' ', '_') + '.xml'))
            self.update_available_lists(selected_list=text)
    def add_new_profile(self):
        profile, ok = AddEditDialog.getNewProfile("Add Profile")
        if ok:
            current_list = self.list_combobox.currentIndex()
            self.__lists__[current_list].add_profile(*profile)
            self.__lists__[current_list].save()
            self.update_list_profiles(current_list)
    def edit_profile(self, index):
        current_profile = self.__lists__[self.list_combobox.currentIndex()][index.row()]
        profile, ok, remove = AddEditDialog.getUpdatedProfile('Edit Profile', current_profile.model, current_profile.loc, current_profile.url, current_profile.enabled)
        if ok:
            current_list = self.list_combobox.currentIndex()
            self.__lists__[current_list].update_profile(index.row(), *profile)
            self.__lists__[current_list].save()
            self.update_list_profiles(current_list)
        elif remove:
            current_list = self.list_combobox.currentIndex()
            self.__lists__[current_list].remove_profile(index.row())
            self.__lists__[current_list].save()
            self.update_list_profiles(current_list)
    def update_list_profiles(self, index):
        self.list_profiles.clear()
        for x in self.__lists__[index]:
            self.list_profiles.addItem('{0:s} - {1:s} {2:s}'.format(x.model, x.loc, '(Disabled)' if not x.enabled else ''))
    def update_default_list(self):
        current_list = self.list_combobox.currentText()
        if not self.config.has_section('sharpget'):
            self.config.add_section('sharpget')
        self.config.set('sharpget', 'default_list', current_list)
    def update_available_lists(self, selected_list=None):
        list_dir = self.config.get('paths', 'sharpget_lists')
        if self.list_combobox is not None:
            self.__lists__ = []
            __lists__ = []
            for x in os.listdir(list_dir):
                if os.path.splitext(x)[1] == '.xml':
                    __lists__.append(ProfileList(os.path.join(list_dir, x)))
            if len(__lists__) > 0:
                name_index = dict([(__lists__[i].name, i) for i in range(len(__lists__))])
                names = name_index.keys()
                names.sort()
                for x in names:
                    self.__lists__.append(__lists__[name_index[x]])
                if selected_list is None:
                    if self.list_combobox.currentText() == '':
                        if self.config.has_option('sharpget', 'default_list'):
                            selected_list = self.config.get('sharpget', 'default_list')
                    else:
                        selected_list = self.list_combobox.currentText()
                    selected_index = 0
                self.list_combobox.clear()
                for x in range(len(names)):
                    self.list_combobox.addItem(names[x])
                    if selected_list == names[x]:
                        selected_index = x
                self.list_combobox.setCurrentIndex(selected_index)
                self.update_list_profiles(selected_index)
    def update_log(self, text):
        self.log_view.setPlainText(self.log_view.toPlainText() + text)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())
    def download_clicked(self):
        self.log_view.setPlainText('')
        self.download_worker = DownloadThread(self.__lists__[self.list_combobox.currentIndex()], self.config.get('paths', 'archive_path'))
        self.download_worker.status_update.connect(self.update_log)
        self.download_worker.start()
    def dropdown_menu(self, item_list):
        """
        Create and return a dropdown menu containing items in item_list.

        Params
        ------
        item_list : a list of strings for the contents of the dropdown menu

        Returns
        -------
        dropdown : a QtGui.QComboBox object
        """
        ## create the dropdown menu
        dropdown = QComboBox()
        ## set the text as editable so that it can have centered text
        dropdown.setEditable(True)
        dropdown.lineEdit().setReadOnly(True)
        dropdown.lineEdit().setAlignment(Qt.AlignCenter)

        ## add each item in the list to the dropdown
        for item in item_list:
            dropdown.addItem(item)

        return dropdown
