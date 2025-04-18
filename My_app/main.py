from kivy.app import App
from kivy.core.window import Window
from asteval import Interpreter  
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.properties import StringProperty
import os
from kivy.core.audio import SoundLoader
from kivy.animation import Animation


Window.size = (320, 500)
from kivy.properties import ListProperty
from kivy.uix.button import Button

class ToggleCalcButton(Button):
    background_color_normal = ListProperty([0.25, 0.25, 0.25, 1])
    background_color_down = ListProperty([0.35, 0.35, 0.35, 1])

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
class IconButton(ButtonBehavior, Image):
    background_color_normal = ListProperty([0.15, 0.15, 0.15, 1])
    background_color_down = ListProperty([0.5, 0.5, 0.5, 1])

class MyWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kv_path = os.path.join(os.path.dirname(__file__), 'calculator.kv')


        self.theme = App.get_running_app().theme

        
        # Make sure the KV file is only loaded once
        if not Builder.files:
            Builder.load_file(kv_path)
        
        self.aeval = Interpreter()
        self.just_calculated = False

        self.expression = self.ids.expression
        self.button_grid = self.ids.button_grid

        main_buttons = [
            'AC', 'del', '(', ')',
            '7', '8', '9', 'x',
            '4', '5', '6', '+',
            '3', '2', '1', '-',
            '.', '0', '/', '='
        ]
        
        # Clear any existing widgets in button_grid
        self.button_grid.clear_widgets()
        
        for b in main_buttons:
            if b in ['+', '-', 'x', 'AC', 'del', '(', ')']:
                btn = Factory.OperationButton(text=b)
            else:
                btn = Factory.ToggleCalcButton(text=b)

            if b == 'x':
                btn.bind(on_press=lambda instance, value='*': self.on_button_press_custom(value))
            elif b == 'AC':
                btn.bind(on_press=lambda instance: setattr(self.expression, 'text', ''))
            elif b == 'del':
                btn.bind(on_press=lambda instance: self.expression.do_backspace())
            elif b == '=':
                btn = Factory.EqualsButton(text=b)
                btn.bind(on_press=self.calcul)
            else:
                btn.bind(on_press=self.on_button_press)
            
            self.button_grid.add_widget(btn)

    def on_button_press_custom(self, value):
        if self.just_calculated:
            self.expression.text = ''
            self.just_calculated = False

        self.expression.text += value

    def on_button_press(self, instance):
        if self.just_calculated:
            self.expression.text = ''
            self.just_calculated = False
        current_text = self.expression.text
        new_text = current_text + instance.text
        self.expression.text = new_text

    def calcul(self, instance):
        try:
            expression = self.expression.text
            result = self.aeval(expression)
            if not isinstance(result, (int, float)):
                raise ValueError("Result is not a number")
            
            history_label = self.ids.his
            new_history = history_label.text + f"\n{expression}={result}" 
            history_label.text = new_history.strip()
            self.expression.text = str(result)
            self.just_calculated = True
        except Exception as e:
            self.expression.text = 'invalid input'
            self.just_calculated = True

    def Toggle_history(self):
        panel = self.ids.history_panel
        if panel.width == 0:
            anim = Animation(width=250, duration=0.3)
        else:
            anim = Animation(width=0, duration=0.3)
        anim.start(panel)


    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        sound = SoundLoader.load('toggle.wav')
        if sound:
            sound.play()

   

class CalculatorApp(App):
    theme = StringProperty('dark')

    def build(self):
        return MyWidget()

    def toggle_theme(self):
        root = self.root
        self.theme = 'light' if self.theme == 'dark' else 'dark'

        # Find the knob widget
        knob = root.ids.knob if hasattr(root, 'ids') and 'knob' in root.ids else None
        if knob:
            new_x = 30 if self.theme == 'light' else 5
            Animation(x=new_x, duration=0.2).start(knob)

        sound = SoundLoader.load('toggle.wav')
        if sound:
            sound.play()
            
    def on_theme_toggle_touch(self, widget, touch):
            if widget.collide_point(*touch.pos):
                self.toggle_theme()
                anim = Animation(x=widget.ids.knob.width if self.theme == 'dark' else 0, duration=0.2)
                anim.start(widget.ids.knob)
                print("Current theme:", self.theme)

        
if __name__ == '__main__':
    CalculatorApp().run()