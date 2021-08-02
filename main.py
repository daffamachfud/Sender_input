from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivymd.uix.textfield import MDTextField
import time,os,tqdm

from kivy.clock import Clock
import time, pickle, socket
from scipy.io import wavfile
from kivy.core.audio import SoundLoader

from jnius import autoclass


class screen_connect(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget((Image(source= 'logo/logo2.png', 
            size= (75, 150), 
            pos_hint= {"center_x": 0.5, "center_y": 0.8},
            size_hint_y= None, 
            allow_stretch= True)))

        self.title = MDLabel(
            text= 'SELAMAT DATANG (Sender)',
            halign= 'center',
            pos_hint= {"center_x": 0.5, "center_y": 0.7}
        )
        self.add_widget(self.title)
        
        self.input = MDTextField(
        	text='',
        	pos_hint= {"center_x": 0.5, "center_y": 0.55},
        	required = True,
        	size_hint = (None, 1),
        	width ='160dp'
        	)
        self.input.hint_text ="IP Address"
        self.add_widget(self.input)
        
        self.connect_btn = MDRectangleFlatButton(
            text= 'Sambungkan ke Server',
            pos_hint= {"center_x": 0.5, "center_y": 0.4}
        )
        self.connect_btn.bind(on_press = self.connect_GUI)
        self.add_widget(self.connect_btn)

        self.lanjut_btn = MDRectangleFlatButton(
            text= 'Mulai Rekam',
            pos_hint= {"center_x": 0.5, "center_y": 0.25},
            opacity = 0,
            disabled = True
        )
        self.lanjut_btn.bind(on_press = self.lanjut_gui)
        self.add_widget(self.lanjut_btn)

    def connect_GUI(self,_):
        self.connect_btn.opacity = 0
        self.connect_btn.disabled = True
        
        self.title = MDLabel(
            text= 'Menyambungkan ke Server',
            halign= 'center',
            pos_hint= {"center_x": 0.5, "center_y":  0.35}
        )
        self.add_widget(self.title)
        Clock.schedule_once(self.connect_to_server, 1)


    def connect_to_server(self,_):
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host= self.input.text
        s.connect((host, 5000))
        msg = s.recv(64)
        if msg:
            data = msg.decode()
            print(data)
            self.title.text = data
        self.lanjut_btn.opacity = 1
        self.lanjut_btn.disabled = False

    def lanjut_gui(self,_):
        app.rekam()
        app.screen_manager.current = 'rekam'

class screen_rekam(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.HEADERSIZE = 10

        self.add_widget((Image(source= 'logo/logo2.png', 
            size= (75, 150), 
            pos_hint= {"center_x": 0.5, "center_y": 0.8},
            size_hint_y= None, 
            allow_stretch= True)))
        self.output_label = MDLabel(
            opacity= 0,
            text = '',
            halign= "center",
            pos_hint= {"center_x": 0.5, "center_y": 0.6}
        )

        self.add_widget(self.output_label)

        self.rekam_btn = MDRectangleFlatButton(
            text = 'Rekam',
            pos_hint= {"center_x": 0.5, "center_y": 0.5}
        )

        self.rekam_btn.bind(on_press = self.record_text)
        self.add_widget(self.rekam_btn)
        self.ket_text = MDLabel(
            text = 'Berikan Perintah!',
            halign = "center",
            pos_hint= {"center_x": 0.5, "center_y": 0.25}
        )
        self.add_widget(self.ket_text)
        self.received = MDLabel(
            text = '',
            halign = "center",
            pos_hint= {"center_x": 0.5, "center_y": 0.3}
        )
        self.add_widget(self.received)
        self.play_btn = MDRectangleFlatButton(
            text = 'Dengar',
            pos_hint= {"center_x": 0.5, "center_y": 0.15},
            opacity = 0,
            disabled = True
        )
        self.play_btn.bind(on_press = self.play)
        self.add_widget(self.play_btn)
        print("* ready for record")

    def print(self,*arg):
        pc = print_class()
        pc.printing(self)

    def record_text(self,*arg):
        self.received.text = ''
        self.output_label.text = 'Sedang Merekam Perintah!'
        self.output_label.opacity = 1
        Clock.schedule_once(self.record,0.5)
        
    def record(self,_):
        rc = record_class()
        rc.recording(self)
        self.sending(self)
        Clock.schedule_once(self.print,0.5)
        
    def sending(self,*arg):
        SEPARATOR = "<SEPARATOR>"
        BUFFER_SIZE = 4096
        # the name of file we want to send, make sure it exists
        filename = "temp/send.mp3"
        # get the file size
        filesize = os.path.getsize(filename)
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                s.sendall(bytes_read)
                

        print("* Sending")    
        recv = s.recv(64).decode()
        if (recv == 'Got It The File'):
            self.received.text = 'Sudah Diterima oleh Server'
            print("* Received by Server") 

    def play(self, *arg):
        psc = playsound_class()
        psc.play_sound(self)
        

class record_class():
    
    
    def recording(self,source):
        self.WAVE_OUTPUT_FILENAME = "temp/output.wav"
        print('*recording')

        # get the default audio input (mic on most cases)
        MediaRecorder = autoclass('android.media.MediaRecorder')
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
        #AudioFormat = autoclass('android.media.AudioFormat')
		
        # create out recorder
        mRecorder = MediaRecorder()
        mRecorder.setAudioSource(AudioSource.DEFAULT)
        mRecorder.setOutputFormat(OutputFormat.THREE_GPP)
        mRecorder.setOutputFile('temp/send.mp3')
        mRecorder.setAudioEncoder(AudioEncoder.AAC)
        mRecorder.setAudioChannels(2)
        mRecorder.setAudioEncodingBitRate(128000)
        mRecorder.setAudioSamplingRate(44100)
        mRecorder.prepare()

        # record 5 seconds
        mRecorder.start()
        time.sleep(5)
        mRecorder.stop()
        mRecorder.release()
        
        return


class playsound_class():
    def play_sound(self,source):
        print("* playing recording")
        # get the MediaPlayer java class
        MediaPlayer = autoclass('android.media.MediaPlayer')

        # create our player
        mPlayer = MediaPlayer()
        mPlayer.setDataSource('temp/send.mp3')
        mPlayer.prepare()

        # play
        print('duration:', mPlayer.getDuration())
        mPlayer.start()
        time.sleep(5)
        # then after the play:
        mPlayer.release()
        return

class print_class():
    def printing(self,source):
        source.ket_text.text = 'Dengarkan Kembali Perintah?'
        source.output_label.text = 'Sudah Memberikan Perintah!'
        source.output_label.opacity = 1
        source.play_btn.disabled = False
        source.play_btn.opacity = 1

class Sender(MDApp):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_connect = screen_connect()
        screen = Screen(name = 'connect')
        screen.add_widget(self.screen_connect)
        self.screen_manager.add_widget(screen)
        return self.screen_manager

    def rekam(self):
        self.screen_rekam = screen_rekam()
        screen = Screen(name = 'rekam')
        screen.add_widget(self.screen_rekam)
        self.screen_manager.add_widget(screen)
        return

if __name__ == '__main__':
    app = Sender()
    app.run()