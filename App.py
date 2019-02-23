# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.core.window import Window, WindowBase
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty, BooleanProperty, \
    OptionProperty
from jnius import autoclass
from jnius import cast

WallpaperManager = autoclass('android.app.WallpaperManager')
Uri = autoclass('android.net.Uri')
PythonActivity = autoclass('org.renpy.android.PythonActivity')

import requests

from kivymd.theming import ThemeManager
from kivymd.grid import SmartTileWithLabel
from kivy.uix.boxlayout import BoxLayout
from kivymd.navigationdrawer import NavigationDrawerIconButton
from kivymd.textfields import TextInput
from kivymd.button import BaseRoundButtongit



main_widget_kv = '''
#:import Toolbar kivymd.toolbar.Toolbar
#:import ThemeManager kivymd.theming.ThemeManager
#:import MDNavigationDrawer kivymd.navigationdrawer.MDNavigationDrawer
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import NavigationDrawerDivider kivymd.navigationdrawer.NavigationDrawerDivider
#:import NavigationDrawerToolbar kivymd.navigationdrawer.NavigationDrawerToolbar
#:import NavigationDrawerSubheader kivymd.navigationdrawer.NavigationDrawerSubheader
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
#:import MDSwitch kivymd.selectioncontrols.MDSwitch
#:import MDList kivymd.list.MDList
#:import OneLineListItem kivymd.list.OneLineListItem
#:import TwoLineListItem kivymd.list.TwoLineListItem
#:import ThreeLineListItem kivymd.list.ThreeLineListItem
#:import OneLineAvatarListItem kivymd.list.OneLineAvatarListItem
#:import OneLineIconListItem kivymd.list.OneLineIconListItem
#:import OneLineAvatarIconListItem kivymd.list.OneLineAvatarIconListItem
#:import MDTextField kivymd.textfields.MDTextField
#:import MDSpinner kivymd.spinner.MDSpinner
#:import MDCard kivymd.card.MDCard
#:import MDSeparator kivymd.card.MDSeparator
#:import MDDropdownMenu kivymd.menu.MDDropdownMenu
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import colors kivymd.color_definitions.colors
#:import SmartTile kivymd.grid.SmartTile
#:import MDSlider kivymd.slider.MDSlider
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
#:import MDProgressBar kivymd.progressbar.MDProgressBar
#:import MDAccordion kivymd.accordion.MDAccordion
#:import MDAccordionItem kivymd.accordion.MDAccordionItem
#:import MDAccordionSubItem kivymd.accordion.MDAccordionSubItem
#:import MDThemePicker kivymd.theme_picker.MDThemePicker
#:import MDBottomNavigation kivymd.tabs.MDBottomNavigation
#:import MDBottomNavigationItem kivymd.tabs.MDBottomNavigationItem
#:import AsyncImage kivy.uix.image
#:import MDFlatButton kivymd.button 
#:import FloatLayout kivy.uix.floatlayout 

NavigationLayout:
    id: nav_layout
    MDNavigationDrawer:
        id: nav_drawer
        NavigationDrawerToolbar:
            title: "Categories"
    ScreenManager:
        id: scr_mngr
        Screen: 
            name: 'grid_image_box'
            BoxLayout:
                orientation: 'vertical'
                Toolbar:
                    id: toolbar
                    title: 'Wallpapers for smart-phone'
                    md_bg_color: app.theme_cls.primary_color
                    background_palette: 'Primary'
                    background_hue: '500'
                    left_action_items: [['menu', lambda x: app.root.toggle_nav_drawer()]]
                    right_action_items: [['dots-vertical', lambda x: app.root.toggle_nav_drawer()]]
                ScrollView:
                    id: scroll_view
                    do_scroll_x: False
                    scroll_y: 1.0
                    GridLayout:
                        id: main_grid
                        cols: 3
                        row_default_height: (Window.width - self.cols*self.spacing[0])/self.cols*(Window.height/Window.width)
                        row_force_default: True
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(2), dp(2)
                        spacing: dp(2)
        Screen: 
            name: 'image_box'
            BoxLayout:
                orientation: 'vertical' 
                Toolbar:
                    id: toolbar
                    title: 'Wallpapers for smart-phone'
                    md_bg_color: app.theme_cls.primary_color
                    background_palette: 'Primary'
                    background_hue: '500'
                    left_action_items: [['arrow-left', lambda x: app.viewMainScreen()]]
                    right_action_items: [['download', lambda x: app.setWallpaper()]]
                AsyncImage:
                    id: image              
'''

class WallpaperForPhone(App):
    theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    title = "Wallpapers for phone"
    page = 1
    results_on_page = 21
    token = '11217207-c3d2074d9eadf911755cc6505'
    category = NavigationDrawerIconButton()
    categories = ({'title': 'Abstraction', 'icon': 'image'},
                  {'title': 'Architecture', 'icon': 'city'},
                  {'title': 'Animals', 'icon': 'bug'},
                  {'title': 'Business', 'icon': 'coins'},
                  {'title': 'Computers', 'icon': 'laptop'},
                  {'title': 'Food', 'icon': 'pizza'},
                  {'title': 'Love', 'icon': 'heart'},
                  {'title': 'Music', 'icon': 'music-box'},
                  {'title': 'Nature', 'icon': 'nature'},
                  {'title': 'Religion', 'icon': 'crosshairs'},
                  {'title': 'Sport', 'icon': 'bike'},
                  {'title': 'Transport', 'icon': 'car'},
                  {'title': 'Travel', 'icon': 'airplane'})

    images = list()

    def build(self):
        self.main_widget = Builder.load_string(main_widget_kv)
        self.theme_cls.theme_style = 'Light'
        i = 0
        for value in self.categories:
            menu_button = NavigationDrawerIconButton(text=value['title'])
            menu_button.icon = value['icon']
            menu_button.bind(on_release=self.viewImagesCategory)
            self.main_widget.ids.nav_drawer.add_widget(menu_button)
            if i == 0:
                self.category = menu_button
            i += 1

        self.viewMainScreen()

        self.main_widget.ids.scroll_view.bind(on_scroll_stop=self.getNextPage)

        return self.main_widget

    def viewMainScreen(self):
        self.main_widget.ids.scr_mngr.current = "grid_image_box"

    def viewImagesCategory(self, category):
        self.images = list()
        self.viewMainScreen()
        self.main_widget.ids.main_grid.clear_widgets()
        self.category = category
        self.page = 1
        self.main_widget.ids.scroll_view.scroll_y = 1.0
        self.getImage()
        self.viewImages()

    def viewImages(self):
        for image_source in self.images:
            image_widget = SmartTileWithLabel(mipmap=True, source=image_source['webformatURL'], text=image_source['tags'])
            image_widget.large_image = image_source['largeImageURL']
            image_widget.bind(on_release=self.image_on_press)
            self.main_widget.ids.main_grid.add_widget(image_widget)

    def image_on_press(self, intance):
        self.root.ids.image.source = intance.large_image
        self.root.ids.image.reload()
        self.root.ids.scr_mngr.current = 'image_box'

    def getNextPage(self, intance, *args):
        if intance.scroll_y < 0.0:
            self.page += 1
            if self.getImage():
                self.viewImages()
                intance.scroll_y = 1 - (((self.page * self.results_on_page) - self.results_on_page) / (
                            self.page * self.results_on_page))

    def getImage(self):

        self.images = list()
        orient = 'vertical'
        if Window.width > Window.height:
            orient = 'horizontal'
        url = 'https://pixabay.com/api/?key=' + self.token + '&q=' + self.category.text.replace('/', ' ') \
              + '&image_type=photo&orientation='+orient+'&page=' + str(self.page) \
              + '&per_page=' + str(self.results_on_page)\
              + '&min_width=' + str(Window.width)\
              + '&min_height=' + str(Window.height)\
              + '$editors_choice=true'

        _respons = requests.get(url)
        if _respons.ok:
            respons_data = _respons.json()
            hits = respons_data['hits']
            for hit in hits:
                self.images.append(hit)
        return len(self.images) > 0

    def viewImagesForSearch(self, intance):
        pass

    def setWallpaper(self):
        wallpaperManager = WallpaperManager()
        wallpaperManager.setAction(wallpaperManager.ACTION_CROP_AND_SET_WALLPAPER)
        wallpaperManager.getCropAndSetWallpaperIntent(Uri.parse('http://kivy.org'))
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        currentActivity.startActivity(wallpaperManager)

    def on_start(self):
        self.viewImagesCategory(self.category)


if __name__ == '__main__':
    WallpaperForPhone().run()
