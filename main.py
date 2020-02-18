# coding: utf-8
'''
Created on 5 ago. 2019

@author: Facundo
'''
#
from activities import BaseLesson, lessons

from math import log
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plot
import numpy
import parselmouth # package name: "praat-parselmouth"

class Figure:
    def __init__(self, vocal_range, main_frame, current_lesson):
        def create():      
            figure = plot.figure()
            figure.set_size_inches([8.5, 8.])
            
            canvas = FigureCanvasTkAgg(figure, master=self.main_frame)
            plot_widget = canvas.get_tk_widget()
            plot_widget.grid(row=1, column=0)
            
            return figure
        
        self.vocal_range = vocal_range
        self.main_frame = main_frame
        self.current_lesson = current_lesson
        self.anglo_notation = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.current_plot = False
        
        self.figure = create()
        self.clear()
    
    def angloToNum(self, semitone):
        octave = int(semitone[-1])
        anglo_semitone = semitone[:-1]
        
        semitone_index = self.anglo_notation.index(anglo_semitone)
        numerate_semitone = (octave*12+semitone_index)
        
        return numerate_semitone
    
    def numToAnglo(self, semitone):
        octave = semitone//12
        numerate_semitone = semitone%12
        
        anglo_semitone = self.anglo_notation[numerate_semitone] + str(octave)
        
        return anglo_semitone
    
    def clear(self):
        plot.clf()
        
        time_variations, note_variations, _ = self.current_lesson.current_lesson_parameters
        lesson_duration = time_variations[-1]
        
        _time_variations, _note_variations = [], []
        
        _time_variations.insert(0, 0)
        _note_variations.insert(0, note_variations[0])
        
        
        for i in range(len(time_variations)):
            _time_variations.append(time_variations[i])
            _note_variations.append(note_variations[i])

            if i%2 == 0:
                _time_variations.append(numpy.nan)
                _note_variations.append(numpy.nan)
                
        x_ticks = [x for x in range(int(lesson_duration+1))]
        plot.xticks(x_ticks)
        plot.xlim([0, lesson_duration])
        plot.xlabel("Tiempo (seg)")
        
        min_note = self.angloToNum(self.vocal_range[0])
        max_note = self.angloToNum(self.vocal_range[1])
        
        y_ticks = [x for x in range(min_note, max_note+1)]
        y_labels = [self.numToAnglo(x) for x in y_ticks]
        plot.yticks(y_ticks, y_labels)
        plot.ylim(min_note, max_note)
        plot.ylabel("Semitonos")
        
        print((_time_variations, _note_variations))
        plot.plot(_time_variations, _note_variations, linewidth=2)
        
        plot.grid(True)
        
        self.figure.canvas.draw()      
    
    def hidePreviousPlot(self):
        if self.current_plot:
            self.current_plot.set_visible(False)
            self.figure.canvas.draw()
    
    def plotAnswer(self):
        base = 1.059463
        C0_frequency = 16.351593
        
        snd = parselmouth.Sound("output.wav")
        pitch = snd.to_pitch()
        
        pitch_values = [log(x/C0_frequency, base) if x != 0 else numpy.nan for x in pitch.selected_array['frequency']]
        time_fragments = pitch.xs()
        
        self.current_plot, = plot.plot(time_fragments, pitch_values, linewidth=1)
        self.figure.canvas.draw()

class Interface:
    def __init__(self, lessons, vocal_range):
        self.vocal_range = vocal_range
        self.picked = "Lecciones"
        self.pickeds = []
        
        self.page = -1
        self.max_pages = 3
        self.page_elements = {}
        
        self.current_lesson = lessons
        
        self.root = tkinter.Tk()
        self.root.title("Práctica de Canto")
        
        """
        sizex = 480
        sizey = 300
        posx  = 0
        posy  = 0
        self.root.minsize(300,300)
        self.root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
        """
        
        self.nextButton()
        self.root.mainloop()
    
    def createButtons(self, main_frame, _row, _column):
        frame = tkinter.Frame(main_frame)
        frame.grid(row=_row, column=_column)
        
        blank_label = tkinter.Label(frame, width=20, height=1)
        blank_label.pack(side=tkinter.LEFT, fill=tkinter.BOTH, pady=5)
        
        left_button = tkinter.Button(frame, width=10, height=1)
        left_button.pack(side=tkinter.LEFT, fill=tkinter.BOTH, pady=5)
    
        right_button = tkinter.Button(frame, width=10, height=1)
        right_button.pack(side=tkinter.LEFT, fill=tkinter.BOTH, pady=5)
        
        return left_button, right_button
    
    def createMainPage(self):
        def createTitleLabel():
            frame = tkinter.Frame(main_frame)
            frame.grid(row=0, column=0)
            
            title_label = tkinter.Label(frame, text="Práctica de Canto", width=20, height=1, font=('times', 15))
            title_label.pack(side=tkinter.TOP, fill=tkinter.BOTH, pady=5)
            
            return title_label
        
        def createInfoBox():
            frame = tkinter.Frame(main_frame)
            frame.grid(row=1, column=0)
            
            text_box = tkinter.Text(frame, width=40, height=13)
            text_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=5, pady=5)
            return text_box
                
        main_frame = tkinter.Frame(self.root)
        main_frame.grid(row=0, column=0)
        
        title_label = createTitleLabel()
        info_box = createInfoBox()
        left_button, right_button = self.createButtons(main_frame, 2, 0)
        
        self.page_elements.clear()
        self.page_elements.update({"main_frame": main_frame,"title_label": title_label, "info_box": info_box, "left_button": left_button, "right_button": right_button})
    
    def createActivityPage(self):
        def createListBox():
            frame = tkinter.Frame(main_frame)
            frame.grid(row=0, column=0)
            
            label_frame = tkinter.LabelFrame(frame, text="Actividad", font=('times', 15))
            label_frame.pack(fill="both", expand="yes", padx=10, pady=5)
            
            list_box = tkinter.Listbox(label_frame, width=20, height=10, font=('times', 13))
            list_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=5, pady=5)
            
            return list_box
    
        def createTextBox():
            frame = tkinter.Frame(main_frame)
            frame.grid(row=0, column=1)
            
            label_frame = tkinter.LabelFrame(frame, text="Descripción", font=('times', 15))
            label_frame.pack(fill="both", expand="yes", padx=10, pady=5)
            
            text_box = ScrolledText(label_frame, width=40, height=13)
            text_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=5, pady=5)
            
            return text_box
    
        self.page_elements["main_frame"].destroy()
    
        main_frame = tkinter.Frame(self.root)
        main_frame.grid(row=0, column=0)
        
        list_box = createListBox()
        text_box = createTextBox()
        left_button, right_button = self.createButtons(main_frame, 1, 1)
       
        self.page_elements.clear()
        self.page_elements.update({"main_frame": main_frame, "list_box": list_box, "text_box": text_box, "left_button": left_button, "right_button": right_button})
    
    def updateActivityList(self):
        def updateTextBox(text):
            text_box = self.page_elements["text_box"]
            text_box.configure(state='normal')
            text_box.delete("1.0",tkinter.END)
            text_box.insert(tkinter.INSERT, text)
            text_box.configure(state='disabled')
        
        def CurSelet(event):
            widget = event.widget
            selection = widget.curselection()
            picked = widget.get(selection[0])
            updateTextBox(descriptions[picked])
            self.picked = picked
        
        list_box = self.page_elements["list_box"]
        list_box.delete(0, tkinter.END)
        list_box.bind('<<ListboxSelect>>', CurSelet)
        
        descriptions = {}
        
        for lesson in self.current_lesson.values():
            list_box.insert(tkinter.END, lesson["Nombre"])
            descriptions[lesson["Nombre"]] = (lesson["Descripcion"])
        
    def updateButtons(self, left_text, right_text, left_function, right_function):
        left_button = self.page_elements["left_button"]    
        left_button.configure(text=left_text, command=left_function)
        
        right_button = self.page_elements["right_button"]
        right_button.configure(text=right_text, command=right_function)
    
    def previousButton(self):
        self.page = self.page - 1
        
        if self.page == -1:
            self.root.destroy()
            exit()
        
        elif self.page == self.max_pages:
            self.page = 0
            self.max_pages = 2
            self.pickeds = []
            self.nextButton()
        
        else:
            if self.page == 0:
                self.page_elements["main_frame"].destroy()
                self.createMainPage()
                left_button_text = "Salir"
                next_button_text = "Continuar"
            
            else:
                self.pickeds.pop()
                self.updateActivityList()
                left_button_text = "Atras"
                next_button_text = "Siguiente"
            
            self.updateButtons(left_button_text, next_button_text, self.previousButton, self.nextButton)
        
    def nextButton(self):
        self.page = self.page + 1
                        
        if self.page == self.max_pages+1:
            self.page_elements["main_frame"].destroy()
            
            self.createLessonPage(BaseLesson)
        
        else:
            if self.page == 0:
                self.createMainPage()
                left_button_text = "Salir"
                next_button_text = "Continuar"
            
            else:
                if self.page == self.max_pages:
                    left_button_text = "Atras"
                    next_button_text = "Comenzar"
    
                else:
                    if self.page == 1:
                        self.createActivityPage()
                    
                    self.max_pages = self.current_lesson[self.picked]["Nivel"]
                    
                    left_button_text = "Atras"
                    next_button_text = "Siguiente"
                    
                self.pickeds.append(self.picked)
                self.current_lesson = self.current_lesson[self.picked]["Actividades"]
                self.updateActivityList()
        
            self.updateButtons(left_button_text, next_button_text, self.previousButton, self.nextButton)
        
    def createLessonPage(self, Lesson):
        def createInfoLabel():
            frame = tkinter.Frame(main_frame)
            frame.grid(row=0, column=0)
            
            string_var = tkinter.StringVar()
            info_label = tkinter.Label(frame, textvariable=string_var, width=100, height=1, font=('calibri', 13))
            info_label.pack(side=tkinter.TOP, fill=tkinter.BOTH, pady=5)
            
            string_var.set('Pulse "Nueva Pregunta" cuando lo desee - Escuche la frase melódica y memorícela (un clic de metrónomo es un tono).')
            
            return info_label
                
        def createButtons():
            def startRetryLesson():
                play_button = self.page_elements["buttons"][3]
                state_button = self.page_elements["buttons"][2]
                
                figure.hidePreviousPlot()
                lesson.stop = False                
                play_button.configure(state='disabled')
                state_button.configure(text="Detener", command=stopLesson)
                
                stopped = lesson.start()
                
                state_button.configure(text="Reintentar", command=startRetryLesson)               
                
                if not stopped:
                    figure.plotAnswer()
                    play_button.configure(state='normal')

            def stopLesson():
                lesson.stop()
            
            def playAnswer():
                lesson.playAnswer()
                            
            def previousLesson():
                play_button = self.page_elements["buttons"][3]
                state_button = self.page_elements["buttons"][2]

                lesson.previous()
                play_button.configure(state='disabled')
                state_button.configure(text="Comenzar", command=startRetryLesson)
                figure.clear()
                
            def nextLesson():
                play_button = self.page_elements["buttons"][3]
                state_button = self.page_elements["buttons"][2]
                
                lesson.next()
                play_button.configure(state='disabled')
                state_button.configure(text="Comenzar", command=startRetryLesson)
                figure.clear()
                
            def goActivityPage():
                lesson.save()
                self.previousButton()             
            
            buttons_config = [("Volver a Actividades", goActivityPage), ("Lección Anterior", previousLesson), ("Comenzar", startRetryLesson), ("Tocar Respuesta", playAnswer), ("Siguiente Lección", nextLesson)]
            
            frame = tkinter.Frame(main_frame)
            frame.grid(row=2, column=0)
            
            buttons = []
            
            for text, function in buttons_config:
                button = tkinter.Button(frame, width=20, height=1)
                button.pack(side=tkinter.LEFT, fill=tkinter.BOTH, pady=5)
                button.configure(text=text, command=function)
                buttons.append(button)
            
            buttons[3].configure(state='disabled')
            
            return buttons
                
        main_frame = tkinter.Frame(self.root)
        main_frame.grid(row=0, column=0)
        
        lesson = Lesson(self.vocal_range)
        figure = Figure(self.vocal_range, main_frame, lesson)
        
        info_label = createInfoLabel()
        buttons = createButtons()
        
        self.page_elements.clear()
        self.page_elements.update({"main_frame": main_frame, "info_label": info_label, "figure": figure, "buttons": buttons})

if __name__ == "__main__":
    vocal_range = ("G2", "F#4")

    interface = Interface(lessons, vocal_range)
    interface.nextButton()
