from aqt import mw, utils
from aqt.qt import *
from aqt.utils import tooltip, askUser
from anki.hooks import addHook
import re
from .eng_to_ipa import transcribe



LANG_EN = "English"
LANG_JP = "Japanese"
LANG_CN = "Chinese"

MODE_HINT_HEADING = "Only show first character"
MODE_HINT_ENDING = "Only show ending character"
MODE_HINT_VOWELS = "Hide vowels"
MODE_HINT_ALL = "Hide all characters"
MODE_RANDOM = "Random"


class EasyAnkiDialog(QDialog):
    """Main Options dialog"""

    def __init__(self, browser, nids) -> None:
        QDialog.__init__(self, parent=browser)
        self.browser = browser
        self.nids = nids
        self._setup_ui()

    def _setup_ui(self):
        """Set up widgets and layouts"""
        fields = self._get_fields()

        # IPA tab layout
        ipa_multi_label = QLabel("Multiple IPA")
        self.ipa_multi_cb = QCheckBox()
        self.ipa_multi_cb.setEnabled(False)
        
        ipa_lang_label = QLabel("Language")
        self.ipa_lang_selection = QComboBox()
        self.ipa_lang_selection.addItems([LANG_EN, 
                                          LANG_JP,
                                          LANG_CN])
        self.ipa_lang_selection.model().item(1).setEnabled(False)
        self.ipa_lang_selection.model().item(2).setEnabled(False)
        
        ipa_src_label = QLabel("Source Field")
        self.ipa_src_selection = QComboBox()
        self.ipa_src_selection.addItems(fields)
        
        ipa_dst_label = QLabel("Destination Field")
        self.ipa_dst_selection = QComboBox()
        self.ipa_dst_selection.addItems(fields)

        ipa_grid = QGridLayout()
        ipa_grid.setSpacing(10)
        ipa_grid.addWidget(ipa_multi_label, 1, 0, 1, 1)
        ipa_grid.addWidget(self.ipa_multi_cb, 1, 1, 1, 2)

        ipa_grid.addWidget(ipa_lang_label, 2, 0, 1, 1)
        ipa_grid.addWidget(self.ipa_lang_selection, 2, 1, 1, 2)

        ipa_grid.addWidget(ipa_src_label, 3, 0, 1, 1)
        ipa_grid.addWidget(self.ipa_src_selection, 3, 1, 1, 2)

        ipa_grid.addWidget(ipa_dst_label, 4, 0, 1, 1)
        ipa_grid.addWidget(self.ipa_dst_selection, 4, 1, 1, 2)

        tabIPA = QWidget()
        l_tabIPA = QVBoxLayout()
        l_tabIPA.addLayout(ipa_grid)
        tabIPA.setLayout(l_tabIPA)

        # Hint tab layout
        hint_mode_label = QLabel("Mode")
        self.hint_mode_selection = QComboBox()
        self.hint_mode_selection.addItems([MODE_HINT_HEADING, 
                                           MODE_HINT_ENDING, 
                                           MODE_HINT_VOWELS, 
                                           MODE_HINT_ALL, 
                                           MODE_RANDOM])

        hint_lang_label = QLabel("Language")
        self.hint_lang_selection = QComboBox()
        self.hint_lang_selection.addItems([LANG_EN,
                                           LANG_JP,
                                           LANG_CN])
        self.hint_lang_selection.model().item(1).setEnabled(False)
        self.hint_lang_selection.model().item(2).setEnabled(False)
        
        
        hint_src_label = QLabel("Source Field")
        self.hint_src_selection = QComboBox()
        self.hint_src_selection.addItems(fields)
        
        hint_dst_label = QLabel("Destination Field")
        self.hint_dst_selection = QComboBox() 
        self.hint_dst_selection.addItems(fields)

        hint_grid = QGridLayout()
        hint_grid.setSpacing(10)
        hint_grid.addWidget(hint_mode_label, 1, 0, 1, 1)
        hint_grid.addWidget(self.hint_mode_selection, 1, 1, 1, 2)

        hint_grid.addWidget(hint_lang_label, 2, 0, 1, 1)
        hint_grid.addWidget(self.hint_lang_selection, 2, 1, 1, 2)

        hint_grid.addWidget(hint_src_label, 3, 0, 1, 1)
        hint_grid.addWidget(self.hint_src_selection, 3, 1, 1, 2)

        hint_grid.addWidget(hint_dst_label, 4, 0, 1, 1)
        hint_grid.addWidget(self.hint_dst_selection, 4, 1, 1, 2) 

        tabHint = QWidget()
        l_tabHint = QVBoxLayout()
        l_tabHint.addLayout(hint_grid)
        tabHint.setLayout(l_tabHint)      


        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._on_accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_reject)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        save_btn.setEnabled(False)
        
        btn_box = QDialogButtonBox()
        btn_box.addButton(add_btn, QDialogButtonBox.AcceptRole)
        btn_box.addButton(cancel_btn, QDialogButtonBox.RejectRole)
        btn_box.addButton(save_btn, QDialogButtonBox.AcceptRole)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(tabIPA,"API")
        self.tabWidget.addTab(tabHint,"Hint")

        # Main layout
        l_main = QVBoxLayout()
        l_main.addWidget(self.tabWidget)
        l_main.addWidget(btn_box)
        self.setLayout(l_main)
        self.setMinimumWidth(360)
        self.setWindowTitle('EasyAnki')

    def _get_fields(self):
        nid = self.nids[0]
        mw = self.browser.mw
        model = mw.col.getNote(nid).model()
        fields = mw.col.models.fieldNames(model)
        return fields
    
    def _create_ipas(self):
        mw = self.browser.mw
        mw.progress.start()
        self.browser.model.beginReset()
        
        fld1 = self.ipa_src_selection.currentText()
        fld2 = self.ipa_dst_selection.currentText()

        cnt = 0

        for nid in self.nids:
            note = mw.col.getNote(nid)

            if (fld1 in note) and (fld2 in note):
                
                if self.ipa_multi_cb.isChecked():
                    note[fld2] = create_ipa(note[fld1], True)
                else:
                    note[fld2] = create_ipa(note[fld1], False)
                cnt += 1
                note.flush()

        self.browser.model.endReset()
        mw.requireReset()
        mw.progress.finish()
        mw.reset()
        tooltip("Processed {0} notes.".format(cnt), parent=self.browser)   

    def _create_hints(self):
        mw = self.browser.mw
        mw.progress.start()
        self.browser.model.beginReset()
        
        fld1 = self.hint_src_selection.currentText()
        fld2 = self.hint_dst_selection.currentText()
        mode = self.hint_mode_selection.currentText()

        cnt = 0

        for nid in self.nids:
            note = mw.col.getNote(nid)

            if (fld1 in note) and (fld2 in note):
                note[fld2] = create_hint(note[fld1], mode)
                cnt += 1
                note.flush()

        self.browser.model.endReset()
        mw.requireReset()
        mw.progress.finish()
        mw.reset()
        tooltip("Processed {0} notes.".format(cnt), parent=self.browser)              


    def _on_accept(self):
        current_tab_idx = self.tabWidget.currentIndex()
        if current_tab_idx == 0:
            self._create_ipas()
        elif current_tab_idx == 1:
            self._create_hints()
        else:
            pass
        self.close()

    def _on_reject(self):
        self.close()

    def _on_save(self):
        pass

def display_dialog(browser):
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    dialog = EasyAnkiDialog(browser, nids)
    dialog.exec_()

def setupMenu(browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('AnkiEasy')
    a.setShortcut(QKeySequence("Ctrl+Alt+E"))
    a.triggered.connect(lambda _, b=browser: display_dialog(b))

def create_ipa(text, is_multi=False):
    ipa = ""
    text = pre_process_text(text)
    if is_multi:
        pass
    else:
        ipa = transcribe.convert(text)
    return ipa

def create_hint(text, mode):
    hint = ""
    if mode == MODE_HINT_HEADING:
        hint = headinghint(text)
    elif mode == MODE_HINT_ENDING:
        hint = endinghint(text)
    elif mode == MODE_HINT_VOWELS:
        hint = vowelshint(text)
    elif mode == MODE_HINT_ALL:
        hint = allhint(text)
    else:
        pass
    
    return hint

def pre_process_text(text):
    text = striphtml(text)
    text = text.replace("(","")
    text = text.replace(")","")
    text = text.replace(r"/"," ")

    text = text.replace("sb", "somebody")
    text = text.replace("smt", "something")
    
    return text

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def headinghint(data):
    p = re.compile(r"\B\w")
    return p.sub('_', data)

def endinghint(data):
    p = re.compile(r"\w\B")
    return p.sub('_', data)

def vowelshint(data):
    p = re.compile(r"[aiueo]")
    return p.sub('_', data)

def allhint(data):
    p = re.compile(r"\w")
    return p.sub('_', data)

addHook("browser.setupMenus", setupMenu)

        
