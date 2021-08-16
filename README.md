## AlternativeColors

Plugin for [fman.io](https://fman.io) to switch themes.

Themes can set alternative background for even rows (`alternate-background-color` css property).

Theme now pure QSS, which allow any customisations without changing plugin code.  
CSS syntax with restricted properties remains only for `quicksearch` styles as they hardcoded at fman.

Plugin also pickup all `.qss` files from `User/Settings` directory.  
User ones has priority in case of name conflict with predefined themes.

Install with [fman's built-in command for installing plugins](https://fman.io/docs/installing-plugins).

### Usage

Some predefines themes in addon folder (you can suggest new ones via PR).

Use command palette to switch themes: `Activate theme ...`
