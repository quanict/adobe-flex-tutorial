# 'setup.py'
setup(
    entry_points = {
        'sphinx.html_themes': [
            'name_of_theme = bootstrap-4.3.1',
        ]
    },
)

# 'your_package.py'
from os import path

def setup(app):
    app.add_html_theme('name_of_theme', path.abspath(path.dirname(__file__)))
    app.add_javascript("custom.js")
    app.add_stylesheet("custom.css")