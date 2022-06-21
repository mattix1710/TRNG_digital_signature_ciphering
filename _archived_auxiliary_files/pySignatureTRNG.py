from Crypto.PublicKey import RSA
from Crypto.Hash import SHA3_256
from Crypto.Signature import pkcs1_15
import kivy
from sympy import public
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import pyperclip


class textTest(App):
    myNewKey = ''
    publicKey = ''
    key = ''
    mess = 'Witaj PPówko'
    signature = ''

    def build(self):
        self.generateRSA()
        self.window = self.layoutGUI() # GridLayout()

        return self.window

    def layoutGUI(self):
        box = BoxLayout(orientation = 'vertical')
        self.textInput = TextInput(size_hint=(1,0.8), text=self.publicKey)

        buttonBox = BoxLayout(size_hint=(1,0.2))
        saveButton = Button(text='Save')
        signatureButton = Button(text = 'Check signature')
        buttonBox.add_widget(signatureButton)
        buttonBox.add_widget(saveButton)

        saveButton.bind(on_press=self.saveText)
        signatureButton.bind(on_press=self.signatureCheck)

        box.add_widget(self.textInput)
        box.add_widget(buttonBox)
        return box

    def saveText(self, instance):
        print(type(self.publicKey))
        print(self.publicKey)
        myNewKey = bytes(self.textInput.text, 'utf-8')              #INFO: really IMPORTANT - key needs to be saved as bytes() instance
        print(type(myNewKey))
        print(myNewKey)

        self.publicKey = myNewKey

        # receivedKey = RSA.import_key(myNewKey)
        # hashReceivedMess = SHA3_256.new(bytes(self.mess, 'utf-8'))

        # try:
        #     pkcs1_15.new(receivedKey).verify(hashReceivedMess, self.signature)
        #     print("Same message!")
        # except(ValueError, TypeError):
        #     print("The signature is invalid!")
        
    def signatureCheck(self, instance):
        # print(self.publicKey)
        receivedKey = RSA.import_key(self.publicKey)
        

    def generateRSA(self):
        self.key = RSA.generate(1024)
        hashMess = SHA3_256.new(bytes(self.mess,'utf-8'))
        self.signature = pkcs1_15.new(self.key).sign(hashMess)
        print(self.signature)
        self.publicKey = self.key.public_key().export_key()


myApp = textTest()
myApp.run()

#after exiting from KIVY app



# mess = 'Witaj PPówko'
# hashMess = SHA3_256.new(bytes(mess,'utf-8'))
# signature = pkcs1_15.new(key).sign(hashMess)

# receivedKey = RSA.import_key(myNewKey)
# hashReceivedMess = SHA3_256.new(bytes(mess, 'utf-8'))

# try:
#     pkcs1_15.new(receivedKey).verify(hashReceivedMess, signature)
#     print("Same message!")
# except(ValueError, TypeError):
#     print("The signature is invalid!")