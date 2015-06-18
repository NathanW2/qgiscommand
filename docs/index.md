# QGIS Command Bar

[![Buy Nathan a drink because he makes cool stuff. )](https://img.shields.io/badge/Paypal-Buy%20a%20Drink-blue.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=F8FQJT9PBF5VE&lc=AU&item_name=Buy%20Nathan%20a%20drink%20because%20he%20makes%20cool%20stuff%2e%20%28%20You%20know%20you%20love%20it%29&currency_code=AUD&bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHosted)

Are you pining for the good old MicroStation command line? Love the AutoCAD style data entry? Or really who needs a mouse anyway.
The QGIS Command Bar plugin has your back.

## What the heck is this?

A simple to use interactive command bar for QGIS. A bit like Emcas command line, or the AutoCAD one, or whatever it
evolves into. 

Because Python is so bloody great new commands can be defined in Python with normal functions.
All functions are interactive and if not all arguments are given will prompt for each one as required.

Pro Tip: Type `define-package yourpackagename` to open a new package in your text editor. `reload-packages` to load it


![Demo](images/commandbar.gif)

Download the plugin from the QGIS plugin repo or from [http://plugins.qgis.org/plugins/qgiscommand/](here)

Inspiration for the command bar was drawn from AutoCAD and Emacs, so you might
find things that feel the same - or at least an attempt to.

## Usage

The command bar is designed to be a simple interactive command window, using
`CTRL ,` will open the command bar at the bottom of you QGIS map canvas ready to
type. The first auto complete will show all the functions that have been defined
and typing will filter the list.

**Tip**: The auto complete is fuzzy matched so you can type any letters in order
and it will filter based on each leter not the exact pattern.  Try it.

## Init file

The `init.qgsc` file is loaded from `qgis2\python\commandbar` when QGIS is fully
loaded, after all plugins have been loaded.

Commands in the init file need to be wrapped in `()` in order to be considered
commands.  Here is an example of defining aliases for commands you might use all
the time.

```lisp
(alias pt point-at)
(alias lp load-project)
(alias move feature-move)
```

You can also define a single command over many lines like so:

```lisp
(define-project-paths '/home/user/gisdata'
                      '/home/user/projects')
```

## API

Follow the API guide in order to create you own commands.  Commands can also be
defined in plugins to add plugin functions to the command bar.

User commands can be created in `.qgis\python\commandbar` by following Adding
User commands guide
