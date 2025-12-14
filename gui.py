from kivy.config import Config

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '750')

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

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_bg, size=self.update_bg)
        with self.canvas.before:
            self.bg_color = Color(0.15, 0.2, 0.15, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[25])
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class BorderedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_border, size=self.update_border)
        with self.canvas.before:
            Color(0.35, 0.42, 0.32, 1)
            self.border = RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
    
    def update_border(self, *args):
        self.border.pos = self.pos
        self.border.size = self.size



class SmartTrendGUI(App):
    def __init__(self):
        super().__init__()
        self.extrapolator = SmartTrendExtrapolator()
        self.data_points = []
        self.current_method = 'Lagrange'

    def build(self):
        Window.resizable = False
        Window.size = (900, 750)
        Window.clearcolor = (0.12, 0.15, 0.12, 1)
        
        
        main = BoxLayout(orientation='vertical', spacing=10)
        
        # Title Card
        title_card = BoxLayout(orientation='vertical', padding=[10, 5, 10, 10], size_hint_y=None, height=100)
        with title_card.canvas.before:
            Color(0.08, 0.12, 0.08, 1)
            self.title_rect = RoundedRectangle(pos=title_card.pos, size=title_card.size, radius=[0])
        title_card.bind(pos=self.update_title_rect, size=self.update_title_rect)
        logo = Image(source='img/smarttrend_logo.png', size_hint=(None, None), size=(600, 90), pos_hint={'center_x': 0.5})
        title_card.add_widget(logo)
        main.add_widget(title_card)
        
        # Scrollable content
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(size_hint=(1, 1))
        
        # Content container with padding
        content = BoxLayout(orientation='vertical', padding=[10, 0, 10, 10], spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Cards row
        cards = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=250)
        
        
        
        # Data Point Card
        data_card = BoxLayout(orientation='vertical', padding=15, spacing=10)
        with data_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.data_shadow = RoundedRectangle(pos=(data_card.x, data_card.y - 3), size=data_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.data_rect = RoundedRectangle(pos=data_card.pos, size=data_card.size, radius=[15])
        data_card.bind(pos=self.update_rect, size=self.update_rect)
        
        data_card.add_widget(Label(text='Data Point', font_size=20, size_hint_y=None, height=30, bold=True))
        data_card.add_widget(Label(text='', size_hint_y=0.1))
        
        x_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        x_box.add_widget(Label(text='X:', size_hint_x=0.2, font_size=18))
        self.x_input = TextInput(multiline=False, size_hint_x=0.8)
        x_box.add_widget(self.x_input)
        data_card.add_widget(x_box)
        
        y_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        y_box.add_widget(Label(text='Y:', size_hint_x=0.2, font_size=18))
        self.y_input = TextInput(multiline=False, size_hint_x=0.8)
        y_box.add_widget(self.y_input)
        data_card.add_widget(y_box)
        
        self.x_input.bind(on_text_validate=lambda x: setattr(self.y_input, 'focus', True))
        self.x_input._next_widget = self.y_input
        self.x_input.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.x_input, w, k, t, m)
        self.y_input.bind(on_text_validate=self.add_point)
        self.y_input._next_widget = self.x_input
        self.y_input.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.y_input, w, k, t, m)
        
        data_card.add_widget(Label(text='', size_hint_y=1))
        add_btn = RoundedButton(text='Add Point', size_hint_y=None, height=50, on_press=self.add_point)
        data_card.add_widget(add_btn)
        
        cards.add_widget(data_card)
        
        # Axis Labels Card
        axis_card = BoxLayout(orientation='vertical', padding=15, spacing=10)
        with axis_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.axis_shadow = RoundedRectangle(pos=(axis_card.x, axis_card.y - 3), size=axis_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.axis_rect = RoundedRectangle(pos=axis_card.pos, size=axis_card.size, radius=[15])
        axis_card.bind(pos=self.update_rect2, size=self.update_rect2)
        
        axis_card.add_widget(Label(text='Axis Labels', font_size=20, size_hint_y=None, height=30, bold=True))
        axis_card.add_widget(Label(text='', size_hint_y=0.1))
        
        x_label_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        x_label_box.add_widget(Label(text='X:', size_hint_x=0.2, font_size=18))
        self.x_title = TextInput(text='Time', multiline=False, size_hint_x=0.8)
        x_label_box.add_widget(self.x_title)
        axis_card.add_widget(x_label_box)
        
        y_label_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        y_label_box.add_widget(Label(text='Y:', size_hint_x=0.2, font_size=18))
        self.y_title = TextInput(text='Value', multiline=False, size_hint_x=0.8)
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
        
        find_card.add_widget(Label(text='Find Point', font_size=20, size_hint_y=None, height=30, bold=True))
        find_card.add_widget(Label(text='', size_hint_y=0.1))
        
        find_x_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        find_x_box.add_widget(Label(text='Find X:', size_hint_x=0.3, font_size=16))
        self.predict_x = TextInput(multiline=False, size_hint_x=0.7)
        find_x_box.add_widget(self.predict_x)
        find_card.add_widget(find_x_box)
        
        num_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        num_box.add_widget(Label(text='Points:', size_hint_x=0.3, font_size=16))
        self.num_points = TextInput(text='5', multiline=False, size_hint_x=0.7)
        num_box.add_widget(self.num_points)
        find_card.add_widget(num_box)
        
        self.predict_x.bind(on_text_validate=lambda x: setattr(self.num_points, 'focus', True))
        self.predict_x._next_widget = self.num_points
        self.predict_x.keyboard_on_key_down = lambda w, k, t, m: self.handle_tab(self.predict_x, w, k, t, m)
        self.num_points.bind(on_text_validate=self.calculate)
        self.num_points._next_widget = self.predict_x
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
        
        method_card.add_widget(Label(text='Interpolation Method:', font_size=18, size_hint_x=0.3, bold=True))
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
        
        table_card.add_widget(Label(text='Data Points Table', font_size=18, size_hint_y=None, height=30, bold=True))
        
        # Table header
        header = GridLayout(cols=2, size_hint_y=None, height=30, spacing=2)
        self.x_header = BorderedLabel(text='X (Time)', font_size=14, bold=True)
        self.y_header = BorderedLabel(text='Y (Value)', font_size=14, bold=True)
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
        
        results_card.add_widget(Label(text='Results', font_size=18, size_hint_y=None, height=30, bold=True))
        results_card.add_widget(Label(text='', size_hint_y=1))
        self.result_x_label = BorderedLabel(text='X = ---', font_size=16, size_hint_y=None, height=50, color=(1, 1, 1, 1))
        self.result_y_label = BorderedLabel(text='Y = ---', font_size=16, size_hint_y=None, height=50, color=(1, 1, 1, 1))
        results_card.add_widget(self.result_x_label)
        results_card.add_widget(self.result_y_label)
        results_card.add_widget(Label(text='', size_hint_y=1))
        
        results_plot_row.add_widget(results_card)
        
        # Plot Card
        plot_card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_x=0.7)
        with plot_card.canvas.before:
            Color(0.1, 0.12, 0.1, 0.5)
            self.plot_shadow = RoundedRectangle(pos=(plot_card.x, plot_card.y - 3), size=plot_card.size, radius=[15])
            Color(0.25, 0.3, 0.22, 1)
            self.plot_rect = RoundedRectangle(pos=plot_card.pos, size=plot_card.size, radius=[15])
        plot_card.bind(pos=self.update_rect7, size=self.update_rect7)
        
        plot_card.add_widget(Label(text='Interpolation Plot', font_size=18, size_hint_y=None, height=30, bold=True))
        self.plot_image = Image(size_hint=(1, 1))
        plot_card.add_widget(self.plot_image)
        
        results_plot_row.add_widget(plot_card)
        
        content.add_widget(results_plot_row)
        
        # Status
        self.result_label = Label(text='Ready to calculate', size_hint_y=None, height=40, color=(0, 0, 0, 1))
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
            self.data_points.append((x, y))
            self.update_table()
            self.result_label.text = f'Added: ({x}, {y}) | Total Points: {len(self.data_points)}'
            self.x_input.text = ''
            self.y_input.text = ''
            self.x_input.focus = True
        except ValueError:
            self.result_label.text = 'Error: Invalid input values'
    
    def calculate(self, instance):
        try:
            if len(self.data_points) < 2:
                self.result_label.text = 'Error: Need at least 2 data points'
                return
            
            predict_x = float(self.predict_x.text)
            num_points = int(self.num_points.text)
            
            if num_points > len(self.data_points):
                self.result_label.text = f'Error: Requested {num_points} points but only {len(self.data_points)} available. Add more data points.'
                return
            
            self.extrapolator.collect_data_points(self.data_points)
            self.extrapolator.set_configuration(
                self.x_title.text, self.y_title.text, self.current_method, num_points, predict_x
            )
            self.extrapolator.select_extrapolation_subset()
            self.extrapolator.extrapolate_and_store()
            
            if self.extrapolator.predictions:
                pred = self.extrapolator.predictions[-1]
                self.result_x_label.text = f"{self.x_title.text} = {pred['x']:.4f}"
                self.result_y_label.text = f"{self.y_title.text} = {pred['y']:.4f}"
                self.result_label.text = f"Calculation complete using {pred['method']} method"
                
                # Plot the data with highlighted prediction point
                self.plot_data(predict_x, pred['y'])
        except Exception as e:
            self.result_label.text = f'Error: {str(e)}'
    
    def plot_data(self, predict_x, predict_y):
        fig = plt.figure(figsize=(8, 4))
        
        # Plot original data points
        x_vals = [p[0] for p in self.data_points]
        y_vals = [p[1] for p in self.data_points]
        plt.scatter(x_vals, y_vals, color='blue', s=100, label='Data Points', zorder=3)
        
        # Plot the interpolation curve
        import numpy as np
        x_range = np.linspace(min(x_vals), max(max(x_vals), predict_x), 100)
        y_range = []
        for x in x_range:
            self.extrapolator.collect_data_points(self.data_points)
            self.extrapolator.set_configuration(
                self.x_title.text, self.y_title.text, self.current_method, len(self.data_points), x
            )
            self.extrapolator.select_extrapolation_subset()
            self.extrapolator.extrapolate_and_store()
            if self.extrapolator.predictions:
                y_range.append(self.extrapolator.predictions[-1]['y'])
        
        plt.plot(x_range, y_range, 'g-', linewidth=2, label=f'{self.current_method} Curve')
        
        # Highlight the predicted point
        plt.scatter([predict_x], [predict_y], color='red', s=200, marker='*', 
                   label=f'Predicted Point ({predict_x:.2f}, {predict_y:.2f})', zorder=5)
        
        plt.xlabel(self.x_title.text, fontsize=12)
        plt.ylabel(self.y_title.text, fontsize=12)
        plt.title(f'{self.current_method} Interpolation', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert plot to image and display in Kivy
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        self.plot_image.texture = CoreImage(buf, ext='png').texture
        plt.close(fig)


if __name__ == '__main__':
    SmartTrendGUI().run()
