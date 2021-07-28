from fman import ApplicationCommand, DirectoryPaneListener, _get_app_ctxt
from fman import save_json, load_json
from pathlib import Path
from glob import glob
from tinycss.parsing import ParseError
from fman.impl.util.css import parse_css


delayed_init_started = False
plugin_path = Path(__file__).parent.parent
settings_file = 'alternative_colors.json'
current_theme = None


def load_qss(qss_filename):
    theme = _get_app_ctxt().theme

    # set qss rules without processing
    with open(qss_filename, 'rt') as f:
        f_contents = f.read()
    theme._extra_qss_from_css[qss_filename] = f_contents
    
    # set quicksearch rules into theme._quicksearch_item_css
    try:
        new_rules = parse_css(f_contents.encode())
        # only quicksearch rules uses class style, so filter them
        theme._css_rules[qss_filename] = [
            rule for rule in new_rules if rule.selectors[0].startswith('.')
        ]
        theme._quicksearch_item_css = theme._get_quicksearch_item_css()
    except (ValueError, ParseError) as e:
        print(repr(e))
        error_message = 'CSS error in %s: %s' % (qss_filename, e)
        raise ThemeError(error_message) from None

    # apply
    theme._update_app()


def unload_qss(qss_filename):
    theme = _get_app_ctxt().theme
    del theme._extra_qss_from_css[qss_filename]
    theme._quicksearch_item_css = theme._get_quicksearch_item_css()
    theme._update_app()


def activate_theme(name, save=True):
    global current_theme
    theme = _get_app_ctxt().theme
    theme._updates_enabled = False
    if current_theme:  # undo previous theme
        old_filename = Path(plugin_path) / '{}.qss'.format(current_theme)
        unload_qss(old_filename)
    filename = Path(plugin_path) / '{}.qss'.format(name)
    current_theme = name
    load_qss(filename)
    theme.enable_updates()
    if save:
        save_json(settings_file, {'name': name})


# add commands to change themes
for i, filename in enumerate(Path(plugin_path).glob('*.qss'), start=1):
    class_name = 'AlternativeColorTheme{}'.format(i)
    globals()[class_name] = type(
        class_name,
        (ApplicationCommand,),
        {
            'name': filename.stem,
            'aliases': ('Activate theme "{}"'.format(filename.stem),),
            '__call__': lambda self: activate_theme(self.name),
        },
    )


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
