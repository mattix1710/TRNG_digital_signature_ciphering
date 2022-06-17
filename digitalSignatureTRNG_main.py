# all the important imports:
#----------------------------
from email import message
from msilib import schema

from matplotlib.pyplot import text
from TRNgenClass import TRNG

import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window

class MyMainApp(App):
    def build(self):
        #returns a window object with all it's widgets
        self.icon = r'images/appIco.png'
        self.window = self.getGridLayout(Window.size) # GridLayout()
        # self.window.cols = 1
        # self.window.size_hint = (0.6, 0.7)
        # self.window.pos_hint = {"center_x": 0.5, "center_y":0.5}

        # # label widget
        # self.title = 'Digital Signature demonstration'


        # self.titleName = Label(
        #                 text= "Digital Signature demonstration",
        #                 font_size= 18,
        #                 color= '#00FFCE'
        #                 )
        # self.window.add_widget(self.titleName)

        # self.inputDisplay = Label(text = "", font_size = 10, color='#10FFCE')

        # self.window.add_widget(self.inputDisplay)

        # #TEXT INPUT window
        # self.input = TextInput(
        #     padding_y= (10,10),
        #     padding_x= (10,10),
        #     size_hint= (1, 0.5)
        # )


        # self.window.add_widget(self.input)

        # # button widget
        # self.button = Button(
        #               text= "GREET",
        #               size_hint= (1,0.5),
        #               bold= True,
        #               background_color ='#00FFCE',
        #               #remove darker overlay of background colour
        #               # background_normal = ""
        #               )
        # self.button.bind(on_press=self.callback)
        # self.window.add_widget(self.button)

        return self.window

    def callback(self, instance):
        # change label text to "Hello + user name!"
        self.message.text = str(Window.size)


    def getGridLayout(self, windowSize):
        mainLayout = GridLayout(cols = 1)
        upperRowGrid = GridLayout(cols = 2)

        # all the necessary labels to display
        RSAGen = Label(
            text='GENERUJ RSA', 
            font_size=18, 
            color='#00FFCE'
            )
        klucze = Label(text='KLUCZE', font_size=18, color='#00FFCE')
        schemat = Button(
                      text= "Klik",
                      #size_hint= (1,0.5),
                      size_hint=(None, None),
                      height=0.1*Window.size[0],
                      width=0.8*Window.size[1],
                      bold= True,
                      background_color ='#00FFCE',
                      #remove darker overlay of background colour
                      # background_normal = ""
                      )

        schemat.bind(on_press=self.callback)

        self.message = TextInput(
            padding_y= (10,10),
            padding_x= (10,10),
            size_hint= (1, 0.5),
            text=str(Window.size)
        )

        upperRowGrid.add_widget(RSAGen)
        upperRowGrid.add_widget(klucze)

        mainLayout.add_widget(upperRowGrid)
        mainLayout.add_widget(schemat)
        mainLayout.add_widget(self.message)

        return mainLayout

if __name__ == '__main__':
    print("Hello!")
    #print(kivy.__version__)
    MyMainApp().run()