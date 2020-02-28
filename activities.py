# coding: utf-8
'''
Created on 8 sep. 2019

@author: Facundo
'''

from time import sleep
from time import perf_counter as time

from threading import Thread
from threading import Event

from array import array

import wave
import pyo
import pyaudio # need binarie package or Microsoft Visual 14


class Metronome(Thread):
    def __init__(self, ppm):
        Thread.__init__(self)
        self.next_beat = None
        self.stop_event = Event()
        self.ppm_interval = 60 / ppm
    
    def ppm(self, ppm=False):
        if ppm:
            self.ppm_interval = 60 / ppm
        else:
            ppm = 60 / self.ppm_interval
            return ppm
    
    def nextBeat(self):
        return self.next_beat
    
    def stop(self):
        self.stop_event.set()
    
    def run(self):
        CHUNK = 1024
        
        self.next_beat = time() + self.ppm_interval
        py_audio = pyaudio.PyAudio()
        wave_file = wave.open("metronom.wav", 'rb')
        
        stream = py_audio.open(format=py_audio.get_format_from_width(wave_file.getsampwidth()),
                                    channels=wave_file.getnchannels(),
                                    rate=wave_file.getframerate(),
                                    output=True)
        
        while not self.stop_event.is_set():
            wave_file.rewind()
            data = wave_file.readframes(CHUNK)
            
            while data != b'':
                stream.write(data)
                data = wave_file.readframes(CHUNK)
            
            sleep_time = self.next_beat-time()
            sleep(sleep_time if sleep_time >= 0 else 0)
            self.next_beat += self.ppm_interval
        
        self.next_beat = None
        stream.stop_stream()
        stream.close()
        wave_file.close()
        
        py_audio.terminate()

class BaseLesson():
    def __init__(self, vocal_range):
        self.vocal_range = vocal_range
        self.database = "database.txt"
        self.wave = "output.wav"
        
        try:
            self.lesson_level, self.lesson_parameters = self.read()
        except:
            self.lesson_level, self.lesson_parameters = self.generateLessonsParameters()
        
        self.ppm = 60
        self.level_size = 3
        
        self.stop_lesson = False
        self.current_lesson_parameters = 0
        
        self.updateCurrentLessonParameters()
    
    def read(self):
        lesson_level = 0
        lesson_parameters = ([], [], [], [], [])
        
        with open(self.database) as database:
            line = database.readline()
            
            while line:
                exec(line.strip())
                line = database.readline()
        
        return lesson_level, lesson_parameters
    
    def save(self):
        text_format = """lesson_parameters={}
lesson_level={}"""
        
        #with open(self.database, 'w') as database:
            #database.write(text_format.format(self.lesson_parameters, self.lesson_level))
    
    def updateCurrentLessonParameters(self):
        ppm = self.ppm
        progress = self.level_size * 2
        start = self.lesson_level * progress
        end = start + progress
        
        durations, notes_sequences, amplitudes, wave_forms, amp_wave_forms = self.lesson_parameters
        self.current_lesson_parameters = self.processLessonParameters(ppm, 
                                                                                                                durations[start:end], 
                                                                                                                notes_sequences[start:end], 
                                                                                                                amplitudes[start:end], 
                                                                                                                wave_forms[start:end], 
                                                                                                                amp_wave_forms[start:end])
    
    def generateLessonParameters(self):
        def angloToNum(semitone):
            octave = int(semitone[-1])
            anglo_semitone = semitone[:-1]
            
            semitone_index = anglo_notation.index(anglo_semitone)
            numerate_semitone = (octave*12+semitone_index)
            
            return numerate_semitone
        
        def numToAnglo(semitone):
            octave = semitone // 12
            numerate_semitone = semitone % 12
            
            anglo_semitone = anglo_notation[numerate_semitone] + str(octave)
            
            return anglo_semitone
        
        def lectionInfoText():
            notes = [numToAnglo(x) for x in range(middle_note-pair_amplitude, middle_note+pair_amplitude+1) if x <= max_note]
            list_notes = notes[0]
            for x in notes[1:]:
                list_notes = list_notes + ", " + x
            
            lesson_string = "Notas {}".format(list_notes)
        
        min_anglo_note, max_anglo_note = self.vocal_range
        
        anglo_notation = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        notes_sequence, wave_forms, amplitudes, amp_wave_forms, durations = [], [], [], [], []
        
        min_note = angloToNum(min_anglo_note)
        max_note = angloToNum(max_anglo_note)
        middle_note = int((max_note + min_note) / 2 + .5)
        amplitude_levels = int((max_note - min_note) / 2 + 1.5)
        
        for amplitude_level in range(1, amplitude_levels):
            left_limit = middle_note-amplitude_level
            right_limit = middle_note+amplitude_level if middle_note+amplitude_level <= max_note else max_note
            total_items = right_limit-left_limit+1
            
            for pair_amplitude in range(2, total_items):            
                for index in range(total_items-pair_amplitude):
                    notes_sequence.extend([left_limit+index]*2 + [left_limit+index+pair_amplitude]*2)
                    wave_forms.extend(["flat"]*4)
                    amplitudes.extend([0, 1]*2)
                    amp_wave_forms.extend(["flat"]*4)
                    durations.extend([1]*4)
                
                for index in range(total_items-pair_amplitude):
                    notes_sequence.extend([right_limit-index]*2 + [right_limit-index-pair_amplitude]*2)
                    wave_forms.extend(["flat"]*4)
                    amplitudes.extend([0, 1]*2)
                    amp_wave_forms.extend(["flat"]*4)
                    durations.extend([1]*4)
        
        lesson_level = 0
        lesson_parameters = (durations, notes_sequence, amplitudes, wave_forms, amp_wave_forms)
        
        return lesson_level, lesson_parameters
    
    def generateLessonsParameters(self):
        return self.generateLessonParameters()
    
    def processLessonParameters(self, ppm, durations, notes, amplitudes, note_wave_forms, amplitude_wave_forms):   
        def drawWaveStep(wave_form, fraction):
            if wave_form == "flat":
                return 1
            
            if wave_form == "linear":
                return fraction
            
            if wave_form == "log":
                return fraction**3
            
            if wave_form == "antilog":
                return fraction
            
            if wave_form == "log-antilog":
                return fraction
            
            if wave_form == "antilog-log":
                return fraction
        
        def processPair(start_time, end_time, start_note, end_note, start_amplitude_level, end_amplitude_level, note_wave_form, amplitude_wave_form, resolution=100):        
            if note_wave_form == "flat" and amplitude_wave_form == "flat":
                time_variations.append(end_time)
                note_variations.append(end_note)
                amplitude_variations.append(end_amplitude_level)
            
            else:
                time_steps = int((end_time - start_time) / (1/resolution))+1
                time_range = end_time - start_time
                note_range = end_note - start_note
                amplitude_range = end_amplitude_level - start_amplitude_level
                
                for time_step in range(1, time_steps+1):
                    fraction = 1 / time_steps * time_step
                    end_time = start_time + time_range * fraction
                    end_note = start_note + note_range * drawWaveStep(note_wave_form, fraction)
                    end_amplitude_level = start_amplitude_level + amplitude_range * drawWaveStep(amplitude_wave_form, fraction)
                    
                    time_variations.append(end_time)
                    note_variations.append(end_note)
                    amplitude_variations.append(end_amplitude_level)
        
        time_variations, note_variations, amplitude_variations = [], [], []
        total_time = 0
        
        for index, duration, note_wave_form, amplitude_wave_form  in zip(range(len(notes)-1), durations, note_wave_forms, amplitude_wave_forms):
            start_time = total_time
            time_duration = 60 / ppm * duration
            end_time = total_time = total_time + time_duration
            
            start_note, end_note = notes[index], notes[index+1]
            start_amplitude_level, end_amplitude_level = amplitudes[index], amplitudes[index+1]
            
            processPair(start_time, end_time, start_note, end_note, start_amplitude_level, end_amplitude_level, note_wave_form, amplitude_wave_form)
        
        return (time_variations, note_variations, amplitude_variations)
    
    def playAnswer(self):
        CHUNK = 1024
        
        wave_file = wave.open(self.wave, 'rb')
        py_audio = pyaudio.PyAudio()
        
        stream = py_audio.open(format=py_audio.get_format_from_width(wave_file.getsampwidth()),
                            channels=wave_file.getnchannels(),
                            rate=wave_file.getframerate(),
                            output=True)
        
        data = wave_file.readframes(CHUNK)
        while data != b'':
            stream.write(data)
            data = wave_file.readframes(CHUNK)
        
        stream.stop_stream()
        stream.close()
        wave_file.close()
        py_audio.terminate()
    
    def record(self, duration=5, output_filename="output.wav", channels=1, chunk=1024, rate=44100, format=pyaudio.paInt16):
        THRESHOLD = 1000
        
        frames = []
        py_audio = pyaudio.PyAudio()
        
        try:
            stream = py_audio.open(format=format,
                                                    channels=channels,
                                                    rate=rate,
                                                    input=True,
                                                    frames_per_buffer=chunk)
        
        except Exception as exception:
            if type(exception).__name__ == "OSError":
                raise Exception("No hay micrófono conectado")
                exit()
        
        data = array('h', stream.read(chunk))
        
        while max(data) < THRESHOLD:
            data = array('h', stream.read(chunk))
        
        for _ in range(0, int(rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        py_audio.terminate()
        
        wave_file = wave.open(output_filename, 'wb')
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(py_audio.get_sample_size(format))
        wave_file.setframerate(rate)
        wave_file.writeframes(b''.join(frames))
        
    def play(self, time_variations, note_variations, amplitude_variations, metronome):
        def playFragment(end_time, note, amplitude):
            base = 1.059463
            C0_frequency = 16.351593
            harmonic_octaves_limit = 12
            
            fundamental_frequency = C0_frequency * base**note
            harmonic_frequences = [fundamental_frequency * i for i in range(1, harmonic_octaves_limit)]
            multipliers = [1./pow(i, 2)+AMPLITUDE_FIX for i in range(1, harmonic_octaves_limit)]        
            
            server.amp = amplitude
            audio.freq = harmonic_frequences
            audio.mul = multipliers
            
            sleep_time = end_time-time()
            sleep(sleep_time if sleep_time >= 0 else 0)
        
        TEMPO_FIX = .0925
        AMPLITUDE_FIX = .5
        
        server = pyo.Server(duplex=0).boot()
        server.amp = .1
        
        server.start()
        
        audio = pyo.Sine(freq=0, mul=.5)
        left_channel = audio.mix(voices=1).out()
        right_channel = audio.mix(voices=1).out(1)
        
        sleep_time = metronome.nextBeat() - time() - TEMPO_FIX
        sleep(sleep_time if sleep_time >= 0 else 0)
        
        current_time = time()
        
        for end_time, note, amplitude in zip(time_variations, note_variations, amplitude_variations):
            playFragment(current_time+end_time, note, amplitude)
        
        server.stop()
    
    def start(self):
        time_variations, note_variations, amplitude_variations = self.current_lesson_parameters
        
        metronome = Metronome(self.ppm)
        metronome.start()
        
        print("play")
        
        self.play(time_variations, note_variations, amplitude_variations, metronome)
        
        print("record")
        
        lesson_duration = time_variations[-1]
        self.record(lesson_duration)
        
        metronome.stop()
        metronome.join()
        
        print("end")
    
    def stop(self):
        self.lesson_state = 0
    
    def previous(self):
        self.lesson_state = 0
        self.lesson_level -= 1
        
        self.updateCurrentLessonParameters()
    
    def next(self):
        self.lesson_state = 0
        self.lesson_level += 1
        
        self.updateCurrentLessonParameters()


lesson =  {
                    "Nivel": (2, 5), 
                    "Nombre": "Nota+silencio", 
                    "Descripci�n": "Mantener la frecuencia uniforme pero separando cada nota con silencio.",
                    "Actividades": []
                }


"""
notas = [constante, variación]
amplitudes = [constante, variación, silencio]
combinaciones_posibles = [nota+silencio, nota+variación, nota+nota, variación+silencio, variación+variación, silencio+silencio]
"""
        

"""
activities = []

for step in range(1, steps):
    anglo_notes = num_notes = []
    
    for x in range(middle_note-step, middle_note+step+1):
        if num_note <= max_note:
            anglo_notes.append(numToAnglo(num_note))
            num_notes.append(num_note)
    
    
    
    #anglo_notes = [numToAnglo(x) for x in range(middle_note-step, middle_note+step+1) if x <= max_note]
    #num_notes = [x for x in range(middle_note-step, middle_note+step+1) if x <= max_note]
    
    list_notes = anglo_notes[0]
    for x in anglo_notes[1:]:
        list_notes = list_notes + ", " + x

    activities.update({"Nivel": (3, 5), "Nombre": "Lección {}: ".format(step), "Descripci�n": "Notas {}".format(list_notes), "notes": num_notes})

#funcion()
#genere diccionario del tipo {"Nivel": (4, 5), "Nombre": "Lección 1", "Descripci�n": "Notas: F#3, G3, G#3"}
#genere diccionario del tipo {"Nivel": (5, 5), "Nombre": "Nivel 1", "Descripci�n": "Sucesión: F#3, G3, G#3, G3, F#3, G#3", "parameters": {"notes": [42, 42, 43, 43, 44, 44, 43, 43, 42, 42, 44, 44], "wave_forms": ["flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence", "flat", "silence"]}

"""




"""
RESUMEN:
Calentamiento -> Ejercicio -> Comienzo
Entonaci�n   -> Nota+silencio   -> Amplitud -> Lección x (aumentando la amplitud) -> Nivel x (recorriendo los distintos intervalos posibles)
                                                    -> Memoria (con amplitud tonal máxima) -> Lección x (aumentando el tamaño de la palabra) -> Nivel x (intervalos al azar)
                                                    -> Velocidad (con amplitud máxima, tamaño de la palabra máximo) ->Lección x (aumentando la velocidad) -> Nivel x (intervalos al azar)
                     -> Nota+cambio -> Forma de onda (lineal, log, antilog, log-antilog, antilog-log, instantaneo) -> Amplitud interválica (lo que importa es la separación entre las notas) -> Lección x (ascendiendo el tamaño del intervalo) -> Nivel x (recorriendo los distintos intervalos posibles)
                     -> Vibrato -> Forma de onda (lineal, log, antilog, log-antilog, antilog-log, instantaneo) -> Amplitud tonal (1/2 semitono, 1 semitono, 2 semitonos, tal vez 4 semitonos) -> Lección x (aumentando velocidad) -> Nivel x (recorriendo los distintos intervalos posibles)

Volumen (usando nota media del registro vocal) -> Fracción+silencio  -> Amplitud -> Lección x (aumentando el número de fracciones: 1/2^x [aumenta x]) -> Nivel x (recorriendo los distintos intervalos de fracciones posibles)
                                                                                                                -> Memoria (con número de fracciones máximo) -> Lección x (aumentando el tamaño de la palabra) -> Nivel x (intervalos de fracciones al azar)
                                                                                                                -> Velocidad (con número de fracciones máximo, tamaño de la palabra máximo) ->Lección x (aumentando la velocidad) -> Nivel x (intervalos de fracciones al azar)
                                                                             -> Fracción+cambio -> Forma de cambio de amplitud (lineal, log, antilog, log-antilog, antilog-log, instantaneo) -> Amplitud interválica (lo que importa es la separación entre los niveles de volumen) -> Lección x (ascendiendo el tamaño del intervalo de fracciones) -> Nivel x (recorriendo los distintos intervalos de fracciones posibles)
                                                                             -> Vibrato -> Forma de cambio de amplitud (lineal, log, antilog, log-antilog, antilog-log, instantaneo) -> Amplitud interválica (lo que importa es la separación entre los niveles de volumen) -> Lección x (aumentando velocidad) -> Nivel x (recorriendo los distintos intervalos de fracciones posibles)

Entonaci�n y volumen (Usando todo el registro vocal y todas los niveles de volumen [fracciones] combinados, con todos los modos al máximo)

Ritmo -> Fracci�n de la pieza

Velocidad -> PPM (pulsaciones por minuto, desde 15 hasta 500)

Falta tama�o de la palabra, velocidad individual y modo al azar

"""

"""
MODELO DE CADA ELEMENTO:
{
    "Nivel": (actual, m�ximo), 
    "Nombre": str, 
    "Descripci�n": str, 
    "Actividades": dict, 
}
"""

lessons = {"Lecciones": {
    "Nivel": 3, 
    "Nombre": "Lecciones", 
    "Descripcion": "Lecciones", 
    "Actividades": {
            "Calentamiento": {
                "Nivel": 1, 
                "Nombre": "Calentamiento", 
                "Descripcion": "Ejercicios de calentamiento vocal", 
                "Actividades": {
                                        "Burbujas": {"Nivel": 1, "Nombre": "Burbujas", "Descripci�n": "Ejercicios de calentamiento vocal."},
                                        "Soplo U": {"Nivel": 1, "Nombre": "Soplo U", "Descripci�n": "Cantar con una U expulsando el aire como si se estuviera soplando"},
                                        }
            }, 
            "Entonacion": {
                "Nivel": 3, 
                "Nombre": "Entonacion", 
                "Descripcion": "Diferentes entonaciones con intervalos m�s amplios.", 
                "Actividades": {
                                        "Nota+silencio": {
                                            "Nivel": 3, 
                                            "Nombre": "Nota+silencio", 
                                            "Descripcion": "Mantener la frecuencia uniforme pero separando cada nota con silencio.",
                                            "Actividades": {
                                                                    "1. Amplitud": {
                                                                        "Nivel": 3, 
                                                                        "Nombre": "1. Amplitud",
                                                                        "Descripcion": "Entrenar variaciones tonales dentro de una amplitud m�nima y aumentar dicha amplitud hasta alcanzar el m�ximo del registro vocal.", 
                                                                        "Actividades":  [
                                                                                                {
                                                                                                }
                                                                                                ]
                                                                    },
                                                                    "2. Memoria": {
                                                                        "Nivel": 3, 
                                                                        "Nombre": "2. Memoria",
                                                                        "Descripcion": "Entrenar palabras tonales m�s grandes hasta alcanzar un tama�o aceptable, mejorando as� la memorizaci�n de tonos afinados, la amplitud tonal es la m�xima.", 
                                                                        "Actividades":  [
                                                                                                {
                                                                                                    
                                                                                                }
                                                                                                ]
                                                                    },
                                                                    "3. Velocidad": {
                                                                        "Nivel": 3, 
                                                                        "Nombre": "3. Velocidad",
                                                                        "Descripcion": "Aumentar de velocidad progresivamente para mejorar agilidad vocal, el tama�o de las palabras aumenta progresivamente tambi�n, la amplitud tonal es m�xima.", 
                                                                        "Actividades":  [
                                                                                                {
                                                                                                    
                                                                                                }
                                                                                                ]
                                                                    }
                                                                    }
                                        }
                                        }
            },
            "Vibrato": {
                "Nivel": 1, 
                "Nombre": "Vibrato", 
                "Descripcion": "Variar la frecuencia para formar vibratos de diferentes tipos."
            }
            }
    }}