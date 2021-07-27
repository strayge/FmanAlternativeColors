from fman import ApplicationCommand, DirectoryPaneListener, _get_app_ctxt
from fman import save_json, load_json
from pathlib import Path
from glob import glob


delayed_init_started = False
plugin_path = Path(__file__).parent.parent
settings_file = 'alternative_colors.json'
current_theme = None


def activate_theme(name, save=True):
    global current_theme
    context = _get_app_ctxt()
    theme = context.theme
    theme._updates_enabled = False
    if current_theme:
        # undo previous theme
        old_filename = Path(plugin_path) / '{}.css'.format(current_theme)
        theme.unload(old_filename)
    filename = Path(plugin_path) / '{}.css'.format(name)
    current_theme = name
    theme.load(filename)
    theme.enable_updates()
    if save:
        save_json(settings_file, {'name': name})


# add commands to change themes
for i, filename in enumerate(Path(plugin_path).glob('*.css'), start=1):
    class_name = 'Theme{}'.format(i)
    globals()[class_name] = type(
        class_name,
        (ApplicationCommand,),
        {
            'name': filename.stem,
            'aliases': ('Activate theme "{}"'.format(filename.stem),),
            '__call__': lambda self: activate_theme(self.name),
        },
    )

def extend_css_to_qss():
    theme = _get_app_ctxt().theme
    theme._CSS_TO_QSS.update({
        'QTableView': 'QTableView',
        'QMessageBox': 'QMessageBox',
        'QDialog': 'QDialog',
        'QListView': 'QListView',
        'QHeaderView': 'QHeaderView',
        'QHeaderView-section': 'QHeaderView::section',
        'QTableView-section':  'QHeaderView::section',
        'QTableView-item':  'QTableView::item',
        'QTableView-item:first': 'QTableView::item:has-children',
        'QTableView-item:last': 'QTableView::item:open',
        'QTableView-item:selected': 'QTableView::item:selected',
        'QTableView-item:focus': 'QTableView::item:focus',
        'QLabel': 'QLabel',
        'QRadioButton': 'QRadioButton',
        'QRadioButton-checked': 'QRadioButton::checked',
        'QCheckBox': 'QCheckBox',
        'QLineEdit': 'QLineEdit',
        'QLineEdit:read-only': 'QLineEdit:read-only',
        'QStatusBar': 'QStatusBar',
        'QStatusBar-label': 'QStatusBar QLabel',
        'QScrollBar': 'QScrollBar',
        'QScrollBar::handle': 'QScrollBar::handle',
        'QScrollBar::add-line': 'QScrollBar::add-line',
        'QScrollBar::sub-line': 'QScrollBar::sub-line',
        'QInputDialog': 'QInputDialog',
        'QInputDialog-edit': 'QInputDialog QLineEdit',
        'QPushButton': 'QPushButton',
        'QMenu': 'QMenu',
        'QMenu-item': 'QMenu::item',
        'QMenu-item:selected': 'QMenu::item:selected',
        'QMenu-separator': 'QMenu::separator',
        '.prompt-edit': 'Prompt QLineEdit',
        '.quicksearch': 'Quicksearch',
        '.quicksearch-query': 'Quicksearch #query-container',
        '.quicksearch-query-div': 'Quicksearch #query-container > Div',
        '.quicksearch-edit': 'Quicksearch QLineEdit',
        '.quicksearch-view': 'Quicksearch QListView',
        '.quicksearch-view:selected': 'Quicksearch QListView::item:selected',
        '.quicksearch-items': 'Quicksearch #items-container',
        '.splashscreen-button': 'SplashScreen QPushButton',
        '.overlay': 'Overlay',
        '.filterbar': 'FilterBar',
        '.filterbar-edit': 'FilterBar QLineEdit',
        '.nonexistentshortcutdialog-button': 'NonexistentShortcutDialog QPushButton',
        '.nonexistentshortcutdialog-edit': 'NonexistentShortcutDialog QLineEdit',
    })


def load_theme_on_startup():
    theme_name = load_json(settings_file, default={'name': 'Default'}).get('name')
    activate_theme(theme_name, save=False)

def delayed_init():
    """Activate scheme on startup.
    
    Without delay `load_json` did not pickup up user profile location.
    """
    global delayed_init_started
    if delayed_init_started:
        # start only once (there is 2 panes)
        return
    delayed_init_started = True

    extend_css_to_qss()
    load_theme_on_startup()


class AlternateColorPane(DirectoryPaneListener):
    """Activate alternative colors for panes."""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.pane._widget._file_view.setAlternatingRowColors(True)


class AlternateColorDelayedInit(DirectoryPaneListener):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        try:
            delayed_init()
        except Exception:
            import traceback
            traceback.print_exc()
