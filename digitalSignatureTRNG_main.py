# all the important imports:
#----------------------------
# my local classes and files
from TRNgenClass import TRNG
import Constants
# modules
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA3_256
from Crypto.Signature import pkcs1_15
import pyperclip
#
#============================

# all the kivy imports
#----------------------------
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
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ButtonBehavior
#
#============================

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
        self.ifNotGenerated = True
        self.origTextBeforeChange = ''
        self.ifHashedOriginal = False
        self.signature = ''

    def build(self):
        #returns a window object with all it's widgets
        self.icon = r'images/appIco.png'
        Window.clearcolor = Constants.MAIN_BACKGROUND
        self.window = self.layoutGUI() # GridLayout()
        Clock.schedule_interval(self.launchGenerator, 1/30)
        Clock.schedule_interval(self.checkOriginalInputMessage, 1/30)
        Clock.schedule_interval(self.checkWindowSize, 1/30)

        return self.window

    def layoutGUI(self):
        TEXT_PADDING = 5
        buttonFontSize = '16sp'
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
            font_name = Constants.MAIN_FONT_BOLD_LOCATION,
            font_size = '20sp',
            bold = True,
            background_normal = '',                                     #get rid of color tint of gray after implementing "background_color"
            background_color = Constants.INITIAL_GEN_BUTTON_COLOR,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        self.generatorButton.bind(on_press=self.generateRSAkeys)

        genOptionsBoxSection = BoxLayout(orientation='vertical')
        genOptionsBoxSection.add_widget(self.generatorButton)
        
        

        genOptionsLabel = Label(
            text = 'Key length:',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '15sp',
            color = Constants.MESSAGE_KEY_LENGTH_TEXT,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        genOptionsLabelBoxSection = BoxLayout(size_hint=(0.3,1))
        genOptionsLabelBoxSection.add_widget(genOptionsLabel)

        #============================
        # TOGGLE BUTTON section

        keySizeVals = [1024, 2048, 4096]
        keyOption1 = ToggleButton(
            text=str(keySizeVals[0]), 
            group='keySize', 
            state='down', 
            font_size=buttonFontSize, 
            font_name = Constants.MAIN_FONT_LOCATION,
            background_color = Constants.TOGGLE_BUTTON_COLOR_BCKGRD,
            bold = True)
        keyOption1.bind(on_press=self.setKeySize)
        keyOption2 = ToggleButton(
            text=str(keySizeVals[1]), 
            group='keySize', 
            font_size=buttonFontSize, 
            font_name = Constants.MAIN_FONT_LOCATION,
            background_color = Constants.TOGGLE_BUTTON_COLOR_BCKGRD,
            bold = True)
        keyOption2.bind(on_press=self.setKeySize)
        keyOption3 = ToggleButton(
            text=str(keySizeVals[2]), 
            group='keySize', 
            font_size=buttonFontSize, 
            font_name = Constants.MAIN_FONT_LOCATION,
            background_color = Constants.TOGGLE_BUTTON_COLOR_BCKGRD,
            bold = True)
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
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = buttonFontSize,
            bold = True,
            background_color = Constants.REGULAR_BUTTON_BCKGRD,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        copyPublicButton = Button(
            text = 'Copy PUBLIC key',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = buttonFontSize,
            bold = True,
            background_color = Constants.REGULAR_BUTTON_BCKGRD,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        editPublicButton = Button(
            text = 'Edit PUBLIC key',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = buttonFontSize,
            bold = True,
            background_color = Constants.EDIT_PUBLIC_BUTTON_BCKGRD,
            color = Constants.EDIT_PUBLIC_BUTTON_TEXT,
            outline_color = Constants.OUTLINE_COLOR_EDIT_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        resetPublicButton = Button(
            text = 'Reset PUBLIC key',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = buttonFontSize,
            bold = True,
            background_color = Constants.REGULAR_BUTTON_BCKGRD,
            color = Constants.RESET_PUBLIC_BUTTON_TEXT,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
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
            font_size = '18sp',
            padding_y = (TEXT_PADDING, TEXT_PADDING),
            padding_x = (TEXT_PADDING, TEXT_PADDING),
            hint_text = 'Write your message')

        originalLabel = Label(
            text = 'Original message',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '20sp',
            color = Constants.MESSAGE_INFO_TEXT,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
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
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '18sp',
            bold = True,
            background_color = Constants.REGULAR_BUTTON_BCKGRD,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        self.cypherButtonOrig.bind(on_press=self.hashOriginal)

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
            source = r'images/copy_green_dimmed.png',
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
            font_size = '18sp',
            padding_y = (TEXT_PADDING, TEXT_PADDING),
            padding_x = (TEXT_PADDING, TEXT_PADDING),
            #size_hint= (1, 0.5),
            hint_text = 'Write your message')

        receivedLabel = Label(
            text = 'Received message',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '20sp',
            color = Constants.MESSAGE_INFO_TEXT,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
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
            halign = 'center',
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '18sp',
            bold = True,
            background_color = Constants.REGULAR_BUTTON_BCKGRD,
            outline_color = Constants.OUTLINE_COLOR_TUPLE,
            outline_width = Constants.OUTLINE_WIDTH
        )
        self.hashDecypherButton.bind(on_press = self.hashReceived)

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

        #TODO: uncomment after debugging
        self.disableButtons()

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
        self.editText = TextInput(
            hint_text = 'Here should be your RSA public key',
            text = self.currentPublicKey,
            size_hint=(1, 0.8))

        layoutPopUpButtonsBox = BoxLayout(size_hint=(1,0.2))
        saveAndExit = Button(
            text='Save and exit', 
            font_name = Constants.MAIN_FONT_LOCATION,
            background_color='#00F0FF')
        saveAndExit.bind(on_press=self.savePublicKey)
        exitWithoutSaving = Button(
            text ='Exit without saving',
            font_name = Constants.MAIN_FONT_LOCATION,
            background_color = '#00F0FF')
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
            background_color = [0, 0, 0, 0.9],
            auto_dismiss=False,
        )

        self.editKeyPopUp.open()

    def savePublicKey(self, instance):
        self.currentPublicKey = bytes(self.editText.text, 'utf-8')      #INFO: really IMPORTANT - key needs to be saved as bytes() instance
        print("INFO: edited PUBLIC key")
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
        #proceed with generation random string of numbers

        #display PopUp
        #TODO: change GENERATING RSA popup colours!
        infoPopUpBox = BoxLayout(orientation='vertical')
        generateLabel = Label(
            text = "RSA keys are generated. Please wait...",
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '30sp',
            color = Constants.LABEL_POPUP_GREYISH,
            size_hint=(1, 0.9)
        )
        disclaimerLabel = Label(
            text = "Don't react for a possible info that the program doesn't answer",
            font_name = Constants.MAIN_FONT_LOCATION,
            font_size = '15sp',
            color = '#FF0000',
            size_hint=(1, 0.1)
        )

        infoPopUpBox.add_widget(generateLabel)
        infoPopUpBox.add_widget(disclaimerLabel)

        self.generatePopup = Popup(
            title = 'Generating RSA keys',
            content = infoPopUpBox,
            size_hint=(0.9,0.9),
            background_color = [0,0,0,0.9],
            auto_dismiss=False
        )
        self.generatePopup.open()
        #set flag - generating RSA
        self.generatingRSA = True
        self.disableButtons()
        self.generatorButton.background_color = Constants.GENERATOR_BUTTON_BCKGRD
    
    def launchGenerator(self, instance):
        if(self.generatingRSA == True):
            #generate random string of numbers
            print("===================================================")
            print("INFO: RSA GENERATOR STARTED")
            print("INFO: started generating random string of numbers")
            self.gen.setRandom()
            #using that string - generate RSA keys
            print("INFO: started generating RSA keys")
            self.keyRSA = RSA.generate(self.keySize, self.gen.getRandom)
            #save public key to string variable for editing purposes
            self.currentPublicKey = self.keyRSA.public_key().export_key()
            self.origPublicKey = self.keyRSA.public_key().export_key()
            print("INFO: done generating RSA keys")
            print("===================================================")

            #exit from this function and dismiss INFO popup
            self.ifNotGenerated = False
            self.generatingRSA = False
            self.enableAllWidgets()
            self.generatePopup.dismiss()

    def disableButtons(self):
        self.cypherButtonOrig.disabled = True
        self.hashDecypherButton.disabled = True
        self.buttonGridSection.disabled = True

    def enableAllWidgets(self):
        self.cypherButtonOrig.disabled = False
        self.hashDecypherButton.disabled = False
        self.buttonGridSection.disabled = False

    def hashOriginal(self, instance):
        hashMess = SHA3_256.new(bytes(self.originalInput.text, 'utf-8'))        # needs to be casted to bytes(), otherwise throws an Error (string cannot be passed in C)
        self.signature = pkcs1_15.new(self.keyRSA).sign(hashMess)

        #print DEBUG info, set "ifHashedOriginal" flag and disable button
        print("INFO: original message hashed")
        self.cypherButtonOrig.disabled = True
        self.ifHashedOriginal = True

    def checkOriginalInputMessage(self, instance):
        if(self.origTextBeforeChange != self.originalInput.text):
            print("INFO: original message changed")
            self.origTextBeforeChange = self.originalInput.text
            if(self.ifNotGenerated == False):
                self.cypherButtonOrig.disabled = False
            self.ifHashedOriginal = False

    def hashReceived(self, instance):
        if(self.ifHashedOriginal == False):                                     # if the user would like to HASH received message and check result 
            print("ERROR: original message not hashed!")                        # before HASHing the original message
            errorHashingMessage = Label(
                size_hint = (1, 0.9),
                text = 'First hash the original message\n(step 4)',
                halign = 'center',
                font_name = Constants.MAIN_FONT_LOCATION,
                font_size = '30sp'
            )
            errorHashingButton = Button(
                size_hint = (1, 0.1),
                text = 'CLOSE',
                font_size = '20sp',
                font_name = Constants.MAIN_FONT_LOCATION,
                background_color = Constants.REGULAR_BUTTON_BCKGRD
            )
            
            errorHashingBox = BoxLayout(orientation = 'vertical')
            errorHashingBox.add_widget(errorHashingMessage)
            errorHashingBox.add_widget(errorHashingButton)

            errorHashingPopUp = Popup(
                title = 'ERROR: original message not hashed!',
                content = errorHashingBox,
                size_hint=(0.8,0.8),
                background_color = [0,0,0,0.9],
                auto_dismiss=False
            )
            errorHashingPopUp.open()
            errorHashingButton.bind(on_press = errorHashingPopUp.dismiss)
        else:
            hashReceivedMess = SHA3_256.new(bytes(self.receivedInput.text, 'utf-8'))

            digitalSignatureBox = BoxLayout(orientation = 'vertical')
            digitalSignatureInfoBox = BoxLayout(size_hint=(1, 0.6))
            digitalSignatureInfoAnchor = AnchorLayout(size_hint=(1,0.9), anchor_y='center')
            digitalSignatureButton = Button(
                size_hint = (1, 0.1),
                text = 'CLOSE',
                font_name = Constants.MAIN_FONT_LOCATION,
                font_size = '20sp',
                background_color = Constants.REGULAR_BUTTON_BCKGRD
            )

            try:
                receivedKey = RSA.import_key(self.currentPublicKey)
                pkcs1_15.new(receivedKey).verify(hashReceivedMess, self.signature)
                print("INFO: same message was received!")

                #if there was a positive feedback
                #display "correct signature" popup
                digitalSignatureImg = Image(
                    source = r'images/success_green.png'
                )
                digitalSignatureMess = Label(
                    text = 'Original message\nis the same as\nthe received message!',
                    halign = 'center',
                    font_name = Constants.MAIN_FONT_LOCATION,
                    font_size = '22sp',
                    color = Constants.LABEL_POPUP_GREYISH,
                )
            except(ValueError, TypeError):
                print("ERROR: The signature is invalid!")

                #if there was a negative feedback
                #display "invalid signature" popup
                digitalSignatureImg = Image(
                    source = r'images/error_red.png'
                )
                digitalSignatureMess = Label(
                    text = Constants.RECEIVED_MESSAGE_ERROR,
                    font_name = Constants.MAIN_FONT_LOCATION,
                    halign = 'center',
                    font_size = '22sp',
                    color = Constants.LABEL_POPUP_GREYISH
                )

            

            digitalSignatureInfoBox.add_widget(digitalSignatureImg)
            digitalSignatureInfoBox.add_widget(digitalSignatureMess)



            digitalSignatureInfoAnchor.add_widget(digitalSignatureInfoBox)
            digitalSignatureBox.add_widget(digitalSignatureInfoAnchor)
            digitalSignatureBox.add_widget(digitalSignatureButton)

            #print DEBUG info and display Popup with a result
            print("INFO: received message hashed and compared to original")
            digitalSignaturePopUp = Popup(
                title = 'Digital signature confirmation',
                content = digitalSignatureBox,
                size_hint=(0.8,0.8),
                background_color = [0,0,0,0.9],
                auto_dismiss=False
            )
            digitalSignaturePopUp.open()
            digitalSignatureButton.bind(on_press=digitalSignaturePopUp.dismiss)

            #INFO: there is no need for disabling this button as compared to "hashOriginal"

    def checkWindowSize(self, instance):
        if(Window.size == Constants.DEFAULT_WINDOW_SIZE):
            Constants.RECEIVED_MESSAGE_ERROR = "Received message\ndoesn't match\nor\npublic key is invalid!"
        else:
            Constants.RECEIVED_MESSAGE_ERROR = "Received message doesn't match\nor\npublic key is invalid!"

        


if __name__ == '__main__':
    #print(kivy.__version__)
    DigitalSignatureTRNGApp().run()