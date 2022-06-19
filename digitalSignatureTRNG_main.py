# all the important imports:
#----------------------------
from cgitb import reset
from TRNgenClass import TRNG
from Crypto.PublicKey import RSA
import time
import pyperclip

import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
import Constants

BUTTON_COLOR = '#00FFC0'
INITIAL_GEN_BUTTON_COLOR = '#00FF00'

class ImageButton(ButtonBehavior, Image):               #INFO: IDEA from https://stackoverflow.com/questions/48509828/kivy-image-button-stretching
    pass

class DigitalSignatureTRNGApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.iterator = 0
        self.ifClicked = False
        self.returned = False
        self.keySize = 1024
        self.originalInput = TextInput()
        self.receivedInput = TextInput()
        self.origPublicKey = ""
        self.currentPublicKey = ""
        self.gen = TRNG()
        self.keyRSA = ""
        self.generatingRSA = False

    def build(self):
        #returns a window object with all it's widgets
        self.icon = r'images/appIco.png'
        self.window = self.layoutGUI() # GridLayout()
        Clock.schedule_interval(self.launchGenerator, 1/30)

        return self.window

    def layoutGUI(self):
        TEXT_PADDING = 5
        self.mainLayout = BoxLayout(orientation='vertical', padding=50)

        """
            layout RSA-generator section
        """
        self.RSAsection = BoxLayout(orientation='horizontal', size_hint=(1,0.3))

        #############################
        # button RSA GENERATOR section
        #
        step1 = Image(source=r'images/circle1_white.png')
        stepGenBoxSection = BoxLayout(size_hint=(0.15,1))
        stepGenBoxSection.add_widget(step1)

        self.generatorButton = Button(
            text = 'Generate RSA keys',
            font_size = '20sp',
            bold = True,
            background_color = INITIAL_GEN_BUTTON_COLOR
        )
        self.generatorButton.bind(on_press=self.generateRSAkeys)

        genOptionsBoxSection = BoxLayout(orientation='vertical')
        genOptionsBoxSection.add_widget(self.generatorButton)
        
        

        genOptionsLabel = Label(
            text = 'Key length (bits):',
            font_size = '15sp',
            color = '#b3b356'
        )
        genOptionsLabelBoxSection = BoxLayout(size_hint=(0.3,1))
        genOptionsLabelBoxSection.add_widget(genOptionsLabel)

        #============================
        # TOGGLE BUTTON section
        buttonFontSize = '14sp'

        keySizeVals = [1024, 2048, 4096]
        keyOption1 = ToggleButton(text=str(keySizeVals[0]), group='keySize', state='down', font_size=buttonFontSize, background_color = Constants.TOGGLE_BUTTON_COLOR_BCKGRD)
        keyOption1.bind(on_press=self.setKeySize)
        keyOption2 = ToggleButton(text=str(keySizeVals[1]), group='keySize', font_size=buttonFontSize, background_color = Constants.TOGGLE_BUTTON_COLOR_BCKGRD)
        keyOption2.bind(on_press=self.setKeySize)
        keyOption3 = ToggleButton(text=str(keySizeVals[2]), group='keySize', font_size=buttonFontSize, background_color = Constants.TOGGLE_BUTTON_COLOR_BCKGRD)
        keyOption3.bind(on_press=self.setKeySize)

        genOptionsButtonsBoxSection = BoxLayout(size_hint=(0.7,1), padding = '15dp')
        genOptionsButtonsBoxSection.add_widget(keyOption1)
        genOptionsButtonsBoxSection.add_widget(keyOption2)
        genOptionsButtonsBoxSection.add_widget(keyOption3)
        #============================


        optionsBoxSection = BoxLayout()
        optionsBoxSection.add_widget(genOptionsLabelBoxSection)
        optionsBoxSection.add_widget(genOptionsButtonsBoxSection)

        genOptionsBoxSection.add_widget(optionsBoxSection)


        genButtonBoxSection = BoxLayout(size_hint=(0.85,1))
        genButtonBoxSection.add_widget(genOptionsBoxSection)


        generatorBoxSection = BoxLayout()
        generatorBoxSection.add_widget(stepGenBoxSection)
        generatorBoxSection.add_widget(genButtonBoxSection)
        #
        #############################

        #############################
        # option BUTTONS section
        #
        copyPrivateButton = Button(
            text = 'Copy PRIVATE key',
            font_size = buttonFontSize,
            bold = True,
            background_color = '#90EE90'
        )
        copyPublicButton = Button(
            text = 'Copy PUBLIC key',
            font_size = buttonFontSize,
            bold = True,
            background_color = '#90EE90'
        )
        editPublicButton = Button(
            text = 'Edit PUBLIC key',
            font_size = buttonFontSize,
            bold = True,
            background_color = Constants.EDIT_PUBLIC_BUTTON_BCKGRD,
            color = Constants.EDIT_PUBLIC_BUTTON_TEXT
        )
        resetPublicButton = Button(
            text = 'Reset PUBLIC key',
            font_size = buttonFontSize,
            bold = True,
            background_color = '#00FFCE',
            color = '#22FF22'
        )

        editPublicButton.bind(on_press=self.editKey)
        resetPublicButton.bind(on_press=self.resetPublicKey)
        copyPublicButton.bind(on_press=self.copyPublic)
        copyPrivateButton.bind(on_press=self.copyPrivate)

        buttonPadding = 5

        firstButtonBoxSection = BoxLayout(padding = buttonPadding)
        firstButtonBoxSection.add_widget(copyPrivateButton)

        secondButtonBoxSection = BoxLayout(padding = buttonPadding)
        secondButtonBoxSection.add_widget(editPublicButton)

        thirdButtonBoxSection = BoxLayout(padding = buttonPadding)
        thirdButtonBoxSection.add_widget(copyPublicButton)

        fourthButtonBoxSection = BoxLayout(padding = buttonPadding)
        fourthButtonBoxSection.add_widget(resetPublicButton)

        self.buttonGridSection = GridLayout(cols = 2)
        self.buttonGridSection.add_widget(firstButtonBoxSection)
        self.buttonGridSection.add_widget(secondButtonBoxSection)
        self.buttonGridSection.add_widget(thirdButtonBoxSection)
        self.buttonGridSection.add_widget(fourthButtonBoxSection)

        #
        #############################

        self.RSAsection.add_widget(generatorBoxSection)
        #self.RSAsection.add_widget(progressBarBoxSection)
        self.RSAsection.add_widget(self.buttonGridSection)

        """
            layout MESSAGE section
        """
        self.messageSection = BoxLayout(orientation='vertical')

        #============================
        # ORIGINAL MESSAGE section
        self.originalMessSection = BoxLayout(orientation='horizontal')
        originalMessageInputSection = BoxLayout(orientation='horizontal', size_hint=(0.5,1))

        step2 = Image(source=r'images/circle2_white.png')
        self.originalInput = TextInput(
            font_size = '20sp',
            padding_y = (TEXT_PADDING, TEXT_PADDING),
            padding_x = (TEXT_PADDING, TEXT_PADDING),
            hint_text = 'Write your message')

        originalLabel = Label(
            text = 'Original message',
            font_size = '20sp',
            color = '#00FF23'
        )

        origMessStepBox = BoxLayout(size_hint=(0.15,1))
        origMessStepBox.add_widget(step2)

        origMessInputBox = BoxLayout(orientation='vertical', size_hint=(0.85,1))
        origMessInputLabelBoxSection = BoxLayout(size_hint=(1,0.2))
        origMessInputTextBoxSection = BoxLayout(size_hint=(1,0.8))
        #origMessInputBox.add_widget(self.originalInput)

        origMessInputLabelBoxSection.add_widget(originalLabel)
        origMessInputTextBoxSection.add_widget(self.originalInput)
        origMessInputBox.add_widget(origMessInputLabelBoxSection)
        origMessInputBox.add_widget(origMessInputTextBoxSection)


        originalMessageInputSection.add_widget(origMessStepBox)
        originalMessageInputSection.add_widget(origMessInputBox)
        #-------------------------------
        cypherOrigMessageSection = BoxLayout(orientation='horizontal', size_hint=(0.5,1))

        arrowImg = Image(source=r'images/arrow.png')
        arrowImgBoxSection = BoxLayout(size_hint=(0.5,0.5))
        arrowImgBoxSection.add_widget(arrowImg)
        arrowImgSection = AnchorLayout(anchor_x='center', anchor_y='center')
        arrowImgSection.add_widget(arrowImgBoxSection)
        arrowOutlineSection = BoxLayout(size_hint=(0.3,1))
        arrowOutlineSection.add_widget(arrowImgSection)

        step4Section = AnchorLayout(anchor_x='right', anchor_y='center')
        step4 = Image(source=r'images/circle4_white.png')
        step4Section.add_widget(step4)
        step4BoxSection = BoxLayout(size_hint=(0.3,1))
        step4BoxSection.add_widget(step4Section)

        cypherButtonOrigSection = AnchorLayout(anchor_x='left', anchor_y='center')
        self.cypherButtonOrig = Button(
            text = 'Hash & Cypher',
            font_size = '18sp',
            bold = True,
            background_color = '#00FFCE'
        )
        cypherButtonOrigSection.add_widget(self.cypherButtonOrig)
        cypherButtonOrigBoxSection = BoxLayout(size_hint=(0.7,1))
        cypherButtonOrigBoxSection.add_widget(cypherButtonOrigSection)

        cypherButtonBoxSection = BoxLayout(size_hint=(1,1))
        cypherButtonBoxSection.add_widget(step4BoxSection)
        cypherButtonBoxSection.add_widget(cypherButtonOrigBoxSection)

        cypherButtonAnchorSection = AnchorLayout(anchor_x='center', anchor_y='center')
        cypherButtonAnchorSection.add_widget(cypherButtonBoxSection)
        cypherOutlineSection = BoxLayout(size_hint=(0.7,1))
        cypherOutlineSection.add_widget(cypherButtonAnchorSection)

        cypherOrigMessageSection.add_widget(arrowOutlineSection)
        cypherOrigMessageSection.add_widget(cypherOutlineSection)

        self.originalMessSection.add_widget(originalMessageInputSection)
        self.originalMessSection.add_widget(cypherOrigMessageSection)
        ############################

        #============================
        # COPY MESSAGE section
        self.copyMessageSection = BoxLayout(orientation='horizontal')
        copyMessageImageSection = AnchorLayout(anchor_x='center', anchor_y='center')
        copyMessageImageBoxSection = BoxLayout(size_hint=(0.4,0.8))
        copyMessageStepAnchor = AnchorLayout(anchor_x='right', anchor_y='center')
        copyMessageImageButtonAnchor = AnchorLayout(anchor_x='left', anchor_y='center')
        step3 = Image(source=r'images/circle3_white.png')
        copyMessageStepAnchor.add_widget(step3)
        copyMessageImageBoxSection.add_widget(copyMessageStepAnchor)

        # copyImgButton = Button(
        #     text = "",
        #     background_normal = r'images/copy_normal.png',
        #     background_down = r'images/copy_down.png',
        #     allow_stretch = True
        # )

        copyImg = ImageButton(
            source = r'images/copy_normal.png',
            size_hint = (0.8,0.8),
        )

        #copyImgButton.add_widget(copyImg)

        #self.add_widget(ImageButton(source=('Image.png'),size=(200,200), size_hint=(None,None),pos_hint={"x":0.3, "top":0.7}))


        copyImg.bind(on_press=self.copyContent)

        #copyImg = Image(source=r'images/copy.png')
        copyMessageImageButtonAnchor.add_widget(copyImg)
        copyMessageImageBoxSection.add_widget(copyMessageImageButtonAnchor)

        copyMessageImageSection.add_widget(copyMessageImageBoxSection)

        self.copyMessageSection.add_widget(copyMessageImageSection)
        self.copyMessageSection.add_widget(Label())
        ############################

        #============================
        # RECEIVED MESSAGE section
        self.receivedMessSection = BoxLayout(orientation='horizontal')
        receivedMessageInputSection = BoxLayout(orientation='horizontal', size_hint=(0.5,1))

        step3Mess = Image(source=r'images/circle3_white.png')
        self.receivedInput = TextInput(
            font_size = '20sp',
            padding_y = (TEXT_PADDING, TEXT_PADDING),
            padding_x = (TEXT_PADDING, TEXT_PADDING),
            #size_hint= (1, 0.5),
            hint_text = 'Write your message')

        receivedLabel = Label(
            text = 'Received message',
            font_size = '20sp',
            color = '#00FF23'
        )

        receivedMessStepBox = BoxLayout(size_hint=(0.15,1))
        receivedMessStepBox.add_widget(step3Mess)

        receivedMessInputBox = BoxLayout(orientation='vertical', size_hint=(0.85,1))
        receivedMessInputLabelBoxSection = BoxLayout(size_hint=(1,0.2))
        receivedMessInputTextBoxSection = BoxLayout(size_hint=(1,0.8))
        #receivedMessInputBox.add_widget(self.receivedInput)

        receivedMessInputLabelBoxSection.add_widget(receivedLabel)
        receivedMessInputTextBoxSection.add_widget(self.receivedInput)
        receivedMessInputBox.add_widget(receivedMessInputLabelBoxSection)
        receivedMessInputBox.add_widget(receivedMessInputTextBoxSection)


        receivedMessageInputSection.add_widget(receivedMessStepBox)
        receivedMessageInputSection.add_widget(receivedMessInputBox)
        #-------------------------------
        hashDecypherMessageSection = BoxLayout(orientation='horizontal', size_hint=(0.5,1))

        arrowImgDe = Image(source=r'images/arrow.png')
        arrowImgDeBoxSection = BoxLayout(size_hint=(0.5,0.5))
        arrowImgDeBoxSection.add_widget(arrowImgDe)
        arrowImgDeSection = AnchorLayout(anchor_x='center', anchor_y='center')
        arrowImgDeSection.add_widget(arrowImgDeBoxSection)
        arrowDeOutlineSection = BoxLayout(size_hint=(0.3,1))
        arrowDeOutlineSection.add_widget(arrowImgDeSection)
        
        step5Section = AnchorLayout(anchor_x='right', anchor_y='center')
        step5 = Image(source=r'images/circle5_white.png')
        step5Section.add_widget(step5)
        step5BoxSection = BoxLayout(size_hint=(0.3,1))
        step5BoxSection.add_widget(step5Section)

        hashDecypherButtonSection = AnchorLayout(anchor_x='left', anchor_y='center')
        self.hashDecypherButton = Button(
            text = 'Hash, Decypher\n& CHECK',
            font_size = '18sp',
            bold = True,
            background_color = '#00FFCE'
        )
        hashDecypherButtonSection.add_widget(self.hashDecypherButton)
        hashDecypherButtonBoxSection = BoxLayout(size_hint=(0.7,1))
        hashDecypherButtonBoxSection.add_widget(hashDecypherButtonSection)

        hashDecypherBoxSection = BoxLayout(size_hint=(1,1))
        hashDecypherBoxSection.add_widget(step5BoxSection)
        hashDecypherBoxSection.add_widget(hashDecypherButtonBoxSection)

        hashDecypherButtonAnchorSection = AnchorLayout(anchor_x='center', anchor_y='center')
        hashDecypherButtonAnchorSection.add_widget(hashDecypherBoxSection)
        hashDecypherOutlineSection = BoxLayout(size_hint=(0.7,1))
        hashDecypherOutlineSection.add_widget(hashDecypherButtonAnchorSection)

        hashDecypherMessageSection.add_widget(arrowDeOutlineSection)
        hashDecypherMessageSection.add_widget(hashDecypherOutlineSection)

        self.receivedMessSection.add_widget(receivedMessageInputSection)
        self.receivedMessSection.add_widget(hashDecypherMessageSection)
        ############################

        #ADD message section layouts to main MESSAGE SECTION
        self.messageSection.add_widget(self.originalMessSection)
        self.messageSection.add_widget(self.copyMessageSection)
        self.messageSection.add_widget(self.receivedMessSection)

        """
            ADD all layouts to MAIN layout
        """
        self.mainLayout.add_widget(self.RSAsection)
        self.mainLayout.add_widget(self.messageSection)

        #self.mainBorderLayout = AnchorLayout(anchor_x='center', anchor_y='center')
        #self.mainBorderLayout.add_widget(self.mainLayout)

        #TODO: uncomment after debugging
        #self.disableButtons()

        return self.mainLayout

    def setKeySize(self, instance):
        self.keySize = int(instance.text)
        print("KEYSIZE set to: {}".format(self.keySize))

    def editKey(self, instance):
        #create a popUp window and show it

        relative = RelativeLayout()

        #create inside BoxLayout
        layoutPopUp = BoxLayout(orientation = 'vertical')
        #create TextInput and Button for saving
        self.editText = TextInput(hint_text = 'Here should be your RSA public key', text = self.currentPublicKey, size_hint=(1, 0.8))

        layoutPopUpButtonsBox = BoxLayout(size_hint=(1,0.2))
        saveAndExit = Button(text='Save and exit', background_color='#00F0FF')
        saveAndExit.bind(on_press=self.savePublicKey)
        exitWithoutSaving = Button(text ='Exit without saving', background_color = '#00F0FF')
        exitWithoutSaving.bind(on_press=self.discardEditingPublicKey)

        layoutPopUpButtonsBox.add_widget(saveAndExit)
        layoutPopUpButtonsBox.add_widget(exitWithoutSaving)
        
        layoutPopUp.add_widget(self.editText)
        layoutPopUp.add_widget(layoutPopUpButtonsBox)

        relative.add_widget(layoutPopUp)

        self.editKeyPopUp = Popup(
            title = 'Edit RSA public key',
            content = relative,
            size_hint=(0.8,0.8),
            auto_dismiss=False,
        )

        self.editKeyPopUp.open()

    def savePublicKey(self, instance):
        self.currentPublicKey = bytes(self.editText.text, 'utf-8')      #INFO: really IMPORTANT - key needs to be saved as bytes() instance
        print("EDITED PUBLIC KEY")
        self.editKeyPopUp.dismiss()

    def discardEditingPublicKey(self, instance):
        print("INFO: left EDITING PUBLIC KEY WINDOW without saving")
        self.editKeyPopUp.dismiss()
    
    def resetPublicKey(self, instance):
        self.currentPublicKey = self.origPublicKey

    def copyPublic(self, instance):
        pyperclip.copy(str(self.currentPublicKey))

    def copyPrivate(self, instance):
        privateKey = self.keyRSA.export_key(pkcs=1)
        pyperclip.copy(str(privateKey))

    def copyContent(self, instance):
        self.receivedInput.text = self.originalInput.text

    def generateRSAkeys(self, instance):        #INFO: changing Label doesn't work immediately!!
        #process with generation random string of numbers
        # self.gen.setRandom()

        # self.keyRSA = RSA.generate(self.keySize, self.gen.getRandom)

        #display PopUp
        infoPopUpBox = BoxLayout(orientation='vertical')
        generateLabel = Label(
            text = "RSA keys are generated. Please wait...",
            font_size = '30sp',
            color = '#BB00BB',
            size_hint=(1, 0.9)
        )
        disclaimerLabel = Label(
            text = "Don't react for a possible info that the program doesn't answer",
            font_size = '15sp',
            color = '#FF0000',
            size_hint=(1, 0.1)
        )

        infoPopUpBox.add_widget(generateLabel)
        infoPopUpBox.add_widget(disclaimerLabel)

        self.generatePopup = Popup(
            title = 'Generating RSA keys',
            content = infoPopUpBox,
            size_hint=(0.8,0.8),
            background_color = [0,0,0,0.9],
            auto_dismiss=False
        )
        self.generatePopup.open()
        #set flag - generating RSA
        self.generatingRSA = True
        self.disableButtons()
        self.generatorButton.background_color = BUTTON_COLOR
    
    def launchGenerator(self, instance):
        if(self.generatingRSA == True):
            #generate random string of numbers
            self.gen.setRandom()
            #using that string - generate RSA keys
            self.keyRSA = RSA.generate(self.keySize, self.gen.getRandom)
            #save public key to string variable for editing purposes
            self.currentPublicKey = self.keyRSA.public_key().export_key()
            self.origPublicKey = self.keyRSA.public_key().export_key()

            #exit from this function and dismiss INFO popup
            self.generatingRSA = False
            self.enableAllWidgets()
            self.generatePopup.dismiss()

    #TODO: disableAllWidgets function
    def disableButtons(self):
        self.cypherButtonOrig.disabled = True
        self.hashDecypherButton.disabled = True
        self.buttonGridSection.disabled = True

    #TODO: enableAllWidgets function
    def enableAllWidgets(self):
        self.cypherButtonOrig.disabled = False
        self.hashDecypherButton.disabled = False
        self.buttonGridSection.disabled = False


if __name__ == '__main__':
    #print(kivy.__version__)
    DigitalSignatureTRNGApp().run()