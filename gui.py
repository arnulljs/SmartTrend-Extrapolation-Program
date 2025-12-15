from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '850')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from kivy.core.image import Image as CoreImage
import io
from home import SmartTrendExtrapolator
import os
import json
import csv
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.font_name = 'Roboto'
        self.font_size = '16sp'
        self.bind(pos=self.update_bg, size=self.update_bg)
        with self.canvas.before:
            self.bg_color = Color(0.18, 0.55, 0.3, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class BorderedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Roboto'
        self.bind(pos=self.update_border, size=self.update_border)
        with self.canvas.before:
            Color(0.32, 0.45, 0.32, 1)
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
    
    def update_border(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size



class SmartTrendGUI(App):
    def __init__(self):
        super().__init__()
        self.extrapolator = SmartTrendExtrapolator()
        self.data_points = []
        self.current_method = 'Lagrange'
        self.last_pred = None
        self.last_interpretation = None
        self.sm = ScreenManager()

    def build(self):
        self.title = "SmartTrend: Koi DO Predictor"
        Window.resizable = False
        Window.size = (1000, 850)
        Window.clearcolor = (0.09, 0.11, 0.1, 1)

        splash = Screen(name='splash')
        splash_container = AnchorLayout(anchor_x='center', anchor_y='center')
        splash_layout = BoxLayout(
            orientation='vertical',
            padding=[40, 50, 40, 50],
            spacing=30,
            size_hint=(None, None),
            width=600
        )
        splash_layout.bind(minimum_height=lambda inst, val: setattr(inst, 'height', val))
        splash_layout.add_widget(Label(text='SmartTrend: Koi DO Predictor', font_size='28sp', bold=True,
                                       color=(0.9, 1, 0.9, 1), font_name='Roboto', size_hint_y=None, height=50))
        splash_layout.add_widget(Label(text='Predict and interpret Koi pond DO trends', font_size='16sp',
                                       color=(0.8, 0.95, 0.8, 1), font_name='Roboto', size_hint_y=None, height=30))
        start_btn = RoundedButton(text='Start', size_hint=(None, None), size=(200, 60), pos_hint={'center_x': 0.5})
        start_btn.bind(on_press=lambda *a: setattr(self.sm, 'current', 'main'))
        splash_layout.add_widget(start_btn)
        splash_container.add_widget(splash_layout)
        splash.add_widget(splash_container)

        main_screen = Screen(name='main')
        main_screen.add_widget(self.build_main_ui())

        self.sm.add_widget(splash)
        self.sm.add_widget(main_screen)
        return self.sm

    def build_main_ui(self):
        main = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # Title Card
        title_card = BoxLayout(orientation='vertical', padding=[15, 10, 15, 15], size_hint_y=None, height=90)
        with title_card.canvas.before:
            Color(0.07, 0.09, 0.08, 1)
            self.title_rect = RoundedRectangle(pos=title_card.pos, size=title_card.size, radius=[12])
        title_card.bind(pos=self.update_title_rect, size=self.update_title_rect)
        title_label = Label(text='SmartTrend: Koi DO Predictor', font_size='24sp', bold=True,
                            color=(0.9, 1, 0.9, 1), size_hint_y=None, height=60, font_name='Roboto')
        title_card.add_widget(title_label)
        main.add_widget(title_card)
        
        # Scrollable content
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True, bar_width=12)
        
        # Content container with padding
        content = BoxLayout(orientation='vertical', padding=[10, 0, 10, 10], spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Cards row
        cards = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=250)
        
        # Data Point Card
        data_card = BoxLayout(orientation='vertical', padding=15, spacing=12)
        with data_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.data_shadow = RoundedRectangle(pos=(data_card.x, data_card.y - 3), size=data_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.data_rect = RoundedRectangle(pos=data_card.pos, size=data_card.size, radius=[15])
        data_card.bind(pos=self.update_rect, size=self.update_rect)
        
        header = Label(text='Data Points', font_size='16sp', bold=True, color=(0.9, 1, 0.9, 1), font_name='Roboto', size_hint_y=None, height=30)
        data_card.add_widget(header)
        data_card.add_widget(Label(text='', size_hint_y=0.1))
        
        x_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        x_box.add_widget(Label(text='X:', size_hint_x=0.2, font_size='14sp', font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.x_input = TextInput(multiline=False, size_hint_x=0.8, font_size='14sp', font_name='Roboto')
        x_box.add_widget(self.x_input)
        data_card.add_widget(x_box)
        
        y_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        y_box.add_widget(Label(text='Y:', size_hint_x=0.2, font_size='14sp', font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.y_input = TextInput(multiline=False, size_hint_x=0.8, font_size='14sp', font_name='Roboto')
        y_box.add_widget(self.y_input)
        data_card.add_widget(y_box)
        
        self.x_input.bind(on_text_validate=lambda x: setattr(self.y_input, 'focus', True))
        self.x_input._next_widget = self.y_input
        self.x_input.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.x_input, w, k, t, m)
        self.y_input.bind(on_text_validate=self.add_point)
        self.y_input._next_widget = self.x_input
        self.y_input.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.y_input, w, k, t, m)
        
        data_card.add_widget(Label(text='', size_hint_y=1))
        btn_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        add_btn = RoundedButton(text='Add Point', size_hint_y=1, height=40, on_press=self.add_point)
        del_btn = RoundedButton(text='Delete Point', size_hint_y=1, height=40, on_press=self.delete_point)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(del_btn)
        data_card.add_widget(btn_row)
        
        cards.add_widget(data_card)
        
        # Axis Labels Card
        axis_card = BoxLayout(orientation='vertical', padding=15, spacing=10)
        with axis_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.axis_shadow = RoundedRectangle(pos=(axis_card.x, axis_card.y - 3), size=axis_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.axis_rect = RoundedRectangle(pos=axis_card.pos, size=axis_card.size, radius=[15])
        axis_card.bind(pos=self.update_rect2, size=self.update_rect2)
        
        axis_card.add_widget(Label(text='Axis Labels', font_size='16sp', size_hint_y=None, height=30, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        axis_card.add_widget(Label(text='', size_hint_y=0.1))
        
        x_label_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        x_label_box.add_widget(Label(text='X:', size_hint_x=0.2, font_size='14sp', font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.x_title = TextInput(text='Time (Hours)', multiline=False, size_hint_x=0.8, font_size='14sp', font_name='Roboto')
        x_label_box.add_widget(self.x_title)
        axis_card.add_widget(x_label_box)
        
        y_label_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        y_label_box.add_widget(Label(text='Y:', size_hint_x=0.2, font_size='14sp', font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.y_title = TextInput(text='DO Level (mg/L)', multiline=False, size_hint_x=0.8, font_size='14sp', font_name='Roboto')
        y_label_box.add_widget(self.y_title)
        axis_card.add_widget(y_label_box)
        
        self.x_title.bind(on_text_validate=lambda x: setattr(self.y_title, 'focus', True))
        self.x_title._next_widget = self.y_title
        self.x_title.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.x_title, w, k, t, m)
        self.y_title.bind(on_text_validate=self.set_labels)
        self.y_title._next_widget = self.x_title
        self.y_title.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.y_title, w, k, t, m)
        
        axis_card.add_widget(Label(text='', size_hint_y=1))
        set_labels_btn = RoundedButton(text='Set Labels', size_hint_y=None, height=50, on_press=self.set_labels)
        axis_card.add_widget(set_labels_btn)
        
        cards.add_widget(axis_card)
        
        # Find Point Card
        find_card = BoxLayout(orientation='vertical', padding=15, spacing=10)
        with find_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.find_shadow = RoundedRectangle(pos=(find_card.x, find_card.y - 3), size=find_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.find_rect = RoundedRectangle(pos=find_card.pos, size=find_card.size, radius=[15])
        find_card.bind(pos=self.update_rect3, size=self.update_rect3)
        
        find_card.add_widget(Label(text='Find Point', font_size='16sp', size_hint_y=None, height=30, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        find_card.add_widget(Label(text='', size_hint_y=0.1))
        
        find_x_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        find_x_box.add_widget(Label(text='Horizon:', size_hint_x=0.3, font_size='14sp', font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.horizon_input = TextInput(multiline=False, size_hint_x=0.7, font_size='14sp', font_name='Roboto')
        find_x_box.add_widget(self.horizon_input)
        find_card.add_widget(find_x_box)
        
        num_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        num_box.add_widget(Label(text='Points:', size_hint_x=0.3, font_size='14sp', font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.num_points = TextInput(text='5', multiline=False, size_hint_x=0.7, font_size='14sp', font_name='Roboto')
        num_box.add_widget(self.num_points)
        find_card.add_widget(num_box)
        
        self.horizon_input.bind(on_text_validate=lambda x: setattr(self.num_points, 'focus', True))
        self.horizon_input._next_widget = self.num_points
        self.horizon_input.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.horizon_input, w, k, t, m)
        self.num_points.bind(on_text_validate=self.calculate)
        self.num_points._next_widget = self.horizon_input
        self.num_points.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.num_points, w, k, t, m)
        
        find_card.add_widget(Label(text='', size_hint_y=1))
        calc_btn = RoundedButton(text='Calculate', size_hint_y=None, height=50, on_press=self.calculate)
        find_card.add_widget(calc_btn)
        
        cards.add_widget(find_card)
        
        content.add_widget(cards)
        
        # Method Card
        method_card = BoxLayout(orientation='horizontal', padding=15, spacing=15, size_hint_y=None, height=70)
        with method_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.method_shadow = RoundedRectangle(pos=(method_card.x, method_card.y - 3), size=method_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.method_rect = RoundedRectangle(pos=method_card.pos, size=method_card.size, radius=[15])
        method_card.bind(pos=self.update_rect5, size=self.update_rect5)
        
        method_card.add_widget(Label(text='Extrapolation Method:', font_size='14sp', size_hint_x=0.3, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.method_btn = RoundedButton(text='Lagrange', size_hint_x=0.7, on_press=self.toggle_method)
        method_card.add_widget(self.method_btn)
        
        content.add_widget(method_card)
        
        # Data Table Card
        table_card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None, height=300)
        with table_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.table_shadow = RoundedRectangle(pos=(table_card.x, table_card.y - 3), size=table_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.table_rect = RoundedRectangle(pos=table_card.pos, size=table_card.size, radius=[15])
        table_card.bind(pos=self.update_rect4, size=self.update_rect4)
        
        table_card.add_widget(Label(text='Data Points Table', font_size='16sp', size_hint_y=None, height=30, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        
        # Table header
        header = GridLayout(cols=2, size_hint_y=None, height=30, spacing=2)
        self.x_header = BorderedLabel(text='X (Time)', font_size='14sp', bold=True)
        self.y_header = BorderedLabel(text='Y (Value)', font_size='14sp', bold=True)
        header.add_widget(self.x_header)
        header.add_widget(self.y_header)
        table_card.add_widget(header)
        
        # Scrollable table content
        table_scroll = ScrollView(size_hint=(1, 1))
        self.table_grid = GridLayout(cols=2, spacing=2, size_hint_y=None)
        self.table_grid.bind(minimum_height=self.table_grid.setter('height'))
        table_scroll.add_widget(self.table_grid)
        table_card.add_widget(table_scroll)
        
        content.add_widget(table_card)
        
        # Results and Plot Row
        results_plot_row = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=350)
        
        # Results Card
        results_card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_x=0.3)
        with results_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.results_shadow = RoundedRectangle(pos=(results_card.x, results_card.y - 3), size=results_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.results_rect = RoundedRectangle(pos=results_card.pos, size=results_card.size, radius=[15])
        results_card.bind(pos=self.update_rect6, size=self.update_rect6)
        
        results_card.add_widget(Label(text='Results', font_size='16sp', size_hint_y=None, height=30, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        results_card.add_widget(Label(text='', size_hint_y=1))
        self.result_x_label = BorderedLabel(text='X = ---', font_size='14sp', size_hint_y=None, height=50, color=(0.9, 1, 0.9, 1))
        self.result_y_label = BorderedLabel(text='Y = ---', font_size='14sp', size_hint_y=None, height=50, color=(0.9, 1, 0.9, 1))
        self.risk_label = BorderedLabel(
            text='Risk: ---',
            font_size='13sp',
            size_hint_y=None,
            height=90,
            color=(0.9, 1, 0.9, 1),
            halign='left',
            valign='middle'
        )
        self.risk_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - 12, None)))
        results_card.add_widget(self.result_x_label)
        results_card.add_widget(self.result_y_label)
        results_card.add_widget(self.risk_label)
        results_card.add_widget(Label(text='', size_hint_y=1))
        
        results_plot_row.add_widget(results_card)
        
        # Plot + Interpretation Group
        right_group = BoxLayout(orientation='horizontal', padding=0, spacing=10, size_hint_x=0.7)
        
        # Plot Card
        plot_card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_x=0.7)
        with plot_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.plot_shadow = RoundedRectangle(pos=(plot_card.x, plot_card.y - 3), size=plot_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.plot_rect = RoundedRectangle(pos=plot_card.pos, size=plot_card.size, radius=[15])
        plot_card.bind(pos=self.update_rect7, size=self.update_rect7)
        
        plot_card.add_widget(Label(text='Extrapolation Plot', font_size='16sp', size_hint_y=None, height=30, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.plot_image = Image(size_hint=(1, 1))
        plot_card.add_widget(self.plot_image)
        
        # Interpretation Card (separate square to the right)
        interp_card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_x=0.3)
        with interp_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.interp_shadow = RoundedRectangle(pos=(interp_card.x, interp_card.y - 3), size=interp_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.interp_rect = RoundedRectangle(pos=interp_card.pos, size=interp_card.size, radius=[15])
        interp_card.bind(pos=lambda inst, val: setattr(self.interp_shadow, 'pos', (inst.x, inst.y - 3)))
        interp_card.bind(size=lambda inst, val: setattr(self.interp_shadow, 'size', inst.size))
        interp_card.bind(pos=lambda inst, val: setattr(self.interp_rect, 'pos', inst.pos))
        interp_card.bind(size=lambda inst, val: setattr(self.interp_rect, 'size', inst.size))
        
        interp_card.add_widget(Label(text='Interpretation', font_size='16sp', size_hint_y=None, height=30, bold=True, font_name='Roboto', color=(0.9, 1, 0.9, 1)))
        self.interpretation_label = BorderedLabel(
            text='Interpretation: ---',
            font_size='13sp',
            size_hint_y=1,
            color=(0.9, 1, 0.9, 1),
            halign='left',
            valign='top'
        )
        self.interpretation_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - 12, None)))
        interp_card.add_widget(self.interpretation_label)
        
        right_group.add_widget(plot_card)
        right_group.add_widget(interp_card)
        results_plot_row.add_widget(right_group)
        
        content.add_widget(results_plot_row)
        
        export_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=[0, 0, 0, 0], spacing=10)
        export_btn = RoundedButton(text='Export Results', on_press=self.export_all)
        export_row.add_widget(export_btn)
        content.add_widget(export_row)
        
        # Status
        self.result_label = Label(text='Ready to calculate', size_hint_y=None, height=40,
                                  color=(0.9, 1, 0.9, 1), font_name='Roboto', font_size='14sp')
        content.add_widget(self.result_label)
        
        scroll.add_widget(content)
        main.add_widget(scroll)
        
        return main
    
    def handle_tab(self, widget, window, keycode, text, modifiers):
        if keycode == 9:  # Tab key
            widget._next_widget.focus = True
            return True
        return TextInput.keyboard_on_key_down(widget, window, keycode, text, modifiers)
    
    def update_title_rect(self, instance, value):
        self.title_rect.pos = instance.pos
        self.title_rect.size = instance.size
    
    def update_rect(self, instance, value):
        self.data_shadow.pos = (instance.x, instance.y - 3)
        self.data_shadow.size = instance.size
        self.data_rect.pos = instance.pos
        self.data_rect.size = instance.size
    
    def update_rect2(self, instance, value):
        self.axis_shadow.pos = (instance.x, instance.y - 3)
        self.axis_shadow.size = instance.size
        self.axis_rect.pos = instance.pos
        self.axis_rect.size = instance.size
    
    def update_rect3(self, instance, value):
        self.find_shadow.pos = (instance.x, instance.y - 3)
        self.find_shadow.size = instance.size
        self.find_rect.pos = instance.pos
        self.find_rect.size = instance.size
    
    def update_rect4(self, instance, value):
        self.table_shadow.pos = (instance.x, instance.y - 3)
        self.table_shadow.size = instance.size
        self.table_rect.pos = instance.pos
        self.table_rect.size = instance.size
    
    def update_rect5(self, instance, value):
        self.method_shadow.pos = (instance.x, instance.y - 3)
        self.method_shadow.size = instance.size
        self.method_rect.pos = instance.pos
        self.method_rect.size = instance.size
    
    def update_rect6(self, instance, value):
        self.results_shadow.pos = (instance.x, instance.y - 3)
        self.results_shadow.size = instance.size
        self.results_rect.pos = instance.pos
        self.results_rect.size = instance.size
    
    def update_rect7(self, instance, value):
        self.plot_shadow.pos = (instance.x, instance.y - 3)
        self.plot_shadow.size = instance.size
        self.plot_rect.pos = instance.pos
        self.plot_rect.size = instance.size
    
    def set_labels(self, instance):
        self.update_table()
        self.result_label.text = f'Labels set: X = {self.x_title.text}, Y = {self.y_title.text}'
    
    def update_table(self):
        self.table_grid.clear_widgets()
        for x, y in self.data_points:
            self.table_grid.add_widget(BorderedLabel(text=f'{x:.2f}', size_hint_y=None, height=25, color=(1, 1, 1, 1)))
            self.table_grid.add_widget(BorderedLabel(text=f'{y:.2f}', size_hint_y=None, height=25, color=(1, 1, 1, 1)))
        
        # Update headers with axis labels
        self.x_header.text = f'X ({self.x_title.text})'
        self.y_header.text = f'Y ({self.y_title.text})'
    
    def toggle_method(self, instance):
        if self.current_method == 'Lagrange':
            self.current_method = 'Divided Difference'
            self.method_btn.text = 'Divided Difference'
        else:
            self.current_method = 'Lagrange'
            self.method_btn.text = 'Lagrange'
    
    def add_point(self, instance):
        try:
            x = float(self.x_input.text)
            y = float(self.y_input.text)
            if not (0.0 <= y <= 20.0):
                self.result_label.text = 'Error: DO must be between 0-20 mg/L'
                return
            self.data_points.append((x, y))
            self.update_table()
            self.result_label.text = f'Added: ({x}, {y}) | Total Points: {len(self.data_points)}'
            self.x_input.text = ''
            self.y_input.text = ''
            self.x_input.focus = True
        except ValueError:
            self.result_label.text = 'Error: Invalid input values'
    
    def delete_point(self, instance):
        try:
            x = float(self.x_input.text)
            y = float(self.y_input.text)
            if (x, y) in self.data_points:
                self.data_points.remove((x, y))
                self.update_table()
                self.result_label.text = f'Deleted: ({x}, {y}) | Total Points: {len(self.data_points)}'
            else:
                self.result_label.text = f'Point ({x}, {y}) not found'
        except ValueError:
            self.result_label.text = 'Error: Invalid input values for deletion'
    
    def calculate(self, instance):
        try:
            if len(self.data_points) < 2:
                self.result_label.text = 'Error: Need at least 2 data points'
                return
            
            horizon = float(self.horizon_input.text)
            num_points = int(self.num_points.text)
            
            if num_points > len(self.data_points):
                self.result_label.text = f'Error: Requested {num_points} points but only {len(self.data_points)} available. Add more data points.'
                return
            
            self.extrapolator.collect_data_points(self.data_points)
            target_x = self.extrapolator.set_prediction_horizon(horizon)
            self.extrapolator.set_configuration(
                self.x_title.text, self.y_title.text, self.current_method, num_points, target_x
            )
            self.extrapolator.select_extrapolation_subset()
            self.extrapolator.extrapolate_and_store()
            
            if self.extrapolator.predictions:
                pred = self.extrapolator.predictions[-1]
                self.last_pred = pred
                self.result_x_label.text = f"{self.x_title.text} = {pred['x']:.4f}"
                self.result_y_label.text = f"{self.y_title.text} = {pred['y']:.4f}"
                self.result_label.text = f"Calculation complete using {pred['method']} method"
                risk = pred.get('risk', {})
                hex_color = risk.get('color', '#FFFFFF')
                to_rgba = lambda h: tuple(int(h[i:i+2], 16) / 255 for i in (1, 3, 5)) + (1,)
                self.risk_label.color = to_rgba(hex_color)
                self.risk_label.text = (
                    f"Risk: {risk.get('status', 'N/A')}\n"
                    f"{risk.get('message', '')}\n"
                    f"Action: {risk.get('action', '')}"
                )
                # Interpretation
                latest_x = max(self.data_points, key=lambda p: p[0])[0]
                latest_y = [p[1] for p in self.data_points if p[0] == latest_x][0]
                interp = self.extrapolator.generate_interpretation(latest_x, latest_y, pred['x'], pred['y'])
                self.last_interpretation = interp
                self.interpretation_label.text = interp
                # Plot the data with highlighted prediction point
                self.plot_data(target_x, pred['y'])
        except Exception as e:
            self.result_label.text = f'Error: {str(e)}'

    def export_all(self, instance):
        if not self.last_pred or not self.last_interpretation:
            self.result_label.text = 'Error: No prediction to export. Run Calculate first.'
            return
        export_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        # TXT summary
        txt_path = os.path.join(export_dir, 'prediction.txt')
        r = self.last_pred.get('risk', {})
        solution = self.last_pred.get('solution', 'No solution available.')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("SmartTrend: Koi DO Predictor - Export Results\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Method: {self.last_pred['method']}\n")
            f.write(f"Subset Size: {self.last_pred['subset_size']}\n")
            f.write(f"X ({self.x_title.text}): {self.last_pred['x']:.4f}\n")
            f.write(f"Y ({self.y_title.text}): {self.last_pred['y']:.4f}\n")
            f.write(f"Risk: {r.get('status', '')} | {r.get('message', '')} | Action: {r.get('action', '')}\n\n")
            f.write("INTERPRETATION:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{self.last_interpretation}\n\n")
            f.write("STEP-BY-STEP SOLUTION:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{solution}\n")
        # Graph (PNG/PDF)
        png_path = os.path.join(export_dir, 'extrapolation_plot.png')
        pdf_path = os.path.join(export_dir, 'extrapolation_plot.pdf')
        self.plot_data(self.last_pred['x'], self.last_pred['y'], export_paths={'png': png_path, 'pdf': pdf_path})
        self.result_label.text = f'Exported to {export_dir}'

    def plot_data(self, target_x, target_y, export_paths=None):
        fig = plt.figure(figsize=(8, 4))
        
        num_points = int(self.num_points.text)
        
        # Get the subset of points used for extrapolation (closest to target_x)
        sorted_points = sorted(self.data_points, key=lambda p: abs(p[0] - target_x))
        subset_points = sorted_points[:num_points]
        
        # Plot only the subset points used for extrapolation
        x_vals = [p[0] for p in subset_points]
        y_vals = [p[1] for p in subset_points]
        max_x = max(x_vals)
        min_x = min(x_vals)
        horizon_value = target_x - max_x
        
        plt.scatter(x_vals, y_vals, color='blue', s=100, label=f'Data Points ({num_points} used)', zorder=3)
        plt.axhline(y=6.0, color='#00FF00', linestyle='--', label='Optimal (6.0)', zorder=1)
        plt.axhline(y=4.0, color='#FFA500', linestyle='--', label='Caution (4.0)', zorder=1)
        plt.axhline(y=3.0, color='#FF0000', linestyle='-', label='Critical (3.0)', zorder=1)
        
        # Plot the extrapolation curve using only the subset
        import numpy as np
        x_range = np.linspace(min_x, max_x + horizon_value, 100)
        y_range = []
        for x in x_range:
            self.extrapolator.collect_data_points(subset_points)
            self.extrapolator.set_configuration(
                self.x_title.text, self.y_title.text, self.current_method, num_points, x
            )
            self.extrapolator.select_extrapolation_subset()
            self.extrapolator.extrapolate_and_store()
            if self.extrapolator.predictions:
                y_range.append(self.extrapolator.predictions[-1]['y'])
        
        plt.plot(x_range, y_range, 'g-', linewidth=2, label='Extrapolation Trend')
        plt.axvline(x=max_x, color='gray', linestyle='--', label='Current Time', zorder=2)
        
        # Highlight the predicted point
        plt.scatter([target_x], [target_y], color='red', s=200, marker='*', 
                   label=f'Predicted Point ({target_x:.2f}, {target_y:.2f})', zorder=5)
        
        plt.xlabel(self.x_title.text, fontsize=12)
        plt.ylabel(self.y_title.text, fontsize=12)
        plt.title(f'{self.current_method} Extrapolation', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if export_paths:
            plt.savefig(export_paths.get('png'), format='png', dpi=120)
            plt.savefig(export_paths.get('pdf'), format='pdf', dpi=120)
        else:
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            self.plot_image.texture = CoreImage(buf, ext='png').texture
        plt.close(fig)


if __name__ == '__main__':
    SmartTrendGUI().run()
