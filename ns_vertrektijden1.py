import tkinter as tk
import requests
import xmltodict


class Program(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('Kaart automaat')
        # de container laat ons frames stapelen, de gene die wel laten zien halen we naar boven
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, TijdenPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # Hier stoppen we alle paginas/frames op de zelfde plek.

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#ffc61e')
        self.controller = controller

        frame1 = tk.Frame(self, bg='#ffc61e')
        frame2 = tk.Frame(self, bg='#ffc61e')
        label1 = tk.Label(frame1, text='Welkom bij NS', padx=250, pady=50, fg='#00337f', bg='#ffc61e')
        label1.config(font=("Courier", 35))
        statusbar = tk.Label(self, bd=1, relief=tk.SUNKEN, padx=10, pady=20,
                             bg='#00337f', text="Copyright© V1L groep 1")
        button1 = tk.Button(frame2, text='Ik heb geen \n OV-Chipkaart', height=5, width=23, fg='white', bg='#00337f')
        button2 = tk.Button(frame2, text='Ik wil naar \n het buitenland', height=5, width=23, fg='white', bg='#00337f')
        button3 = tk.Button(frame2, text='Ik wil de actuele \n vertrektijden zien', height=5, width=23,
                            fg='white', bg='#00337f', command=lambda: controller.show_frame("TijdenPage"))

        frame1.pack(pady=100, expand=tk.TRUE)
        frame2.pack(expand=tk.TRUE)
        label1.pack(side=tk.TOP, fill=tk.X)
        statusbar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        button1.pack(side=tk.LEFT, fill=tk.X, padx=5)
        button2.pack(side=tk.LEFT, fill=tk.X, padx=5)
        button3.pack(side=tk.LEFT, fill=tk.X, padx=5)

        # NS Logo
        photo_image = tk.PhotoImage(file="NSlogoklein.png")
        photo_label = tk.Label(self, image=photo_image, width=220, height=80, padx=10, pady=10)
        photo_label.image = photo_image
        photo_label.pack(side=tk.BOTTOM, anchor="e", padx=10, pady=10)


class TijdenPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, background="#ffc61e")
        self.controller = controller

        statusbar = tk.Label(self, bd=1, relief=tk.SUNKEN, padx=10, pady=20, bg='#00337f',
                             text="Copyright© V1L groep 1")
        statusbar.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # zie bij on_configure() waarom canvas global is
        global canvas
        canvas = tk.Canvas(self, background="#ffc61e")
        canvas.pack(side=tk.LEFT, fill="y", expand=tk.TRUE)

        scrollbar = tk.Scrollbar(self, command=canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill='y')

        canvas.configure(yscrollcommand=scrollbar.set, bg='#ffc61e', width=1500, height=900)
        canvas.bind('<Configure>', on_configure)

        frame3 = tk.Frame(canvas)
        frame3.configure(background="#ffc61e")

        canvas.create_window((0, 0), window=frame3, anchor='nw')

        # knoppen---------------------------------------------------------------------------------------
        # hier staat de code voor de knoppen om het desbetrefende station te zoeken
        # en terug te gaan naar het startscherm.

        menu = tk.Frame(self)
        menu.configure(background="#ffc61e")
        menu.pack(side=tk.TOP, expand=tk.FALSE, fill="x", padx=50)

        invoer = tk.Entry(menu, background="#ffc61e")
        invoer.pack(side=tk.LEFT)
        invoer.insert(0, "Utrecht")

        run = tk.Button(menu, text="vind", font=("Arial", 22, "bold"), foreground="white", background="#00337f",
                        command=lambda: station(invoer, frame3))
        run.pack(side=tk.LEFT)

        terug = tk.Button(menu, text="terug", font=("Arial", 22, "bold"), foreground="white", background="#00337f",
                          command=lambda: (controller.show_frame("StartPage"), invoer.delete(0, 'end'),
                                           invoer.insert(0, "Utrecht"), station(invoer, frame3)))
        terug.pack(side=tk.RIGHT)

        # logo van de NS (LET OP! zet NSlogoklein.png in dezelfde map als dit python bestand)
        # de achtergrond van NS is blauw == #00337f en geel == #ffc61e
        photo_image_2 = tk.PhotoImage(file="NSlogoklein.png")
        photo_label_2 = tk.Label(self, image=photo_image_2, width=220, height=80)
        photo_label_2.image = photo_image_2
        photo_label_2.pack(side=tk.BOTTOM, anchor="e", padx=10, pady=10)

        station(invoer, frame3)

# zonder een parameter (event) werkt de scrollbar niet
# deze functie zorgt dat de grootte van de canvas wordt doorgegeven aan de scrollbar

# Canvas is een globale variabele omdat
# de functie "on_configure" geen variabele kan ontvangen


def on_configure(event):
    global canvas
    canvas.configure(scrollregion=canvas.bbox('all'))


# haalt het opgegeven station uit de entry

def station(invoer, frame):
    plek = invoer.get()
    connect_and_print(plek, frame)


def connect_and_print(plek, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    link = 'http://webservices.ns.nl/ns-api-avt?station=' + plek
    user = 'akiikimel@gmail.com'
    wachtwoord = 'h8YWmp9c23L0VovKZxa8AvWJMf6sotmcoTy8K75m0PSIGMaG6_KoJA'

    response = requests.get(link, auth=(user, wachtwoord))  # logt in en haalt de api op
    vertrekxml = xmltodict.parse(response.text)

    # deze regels zorgen voor een header voor de informatie
    tekst_set_1 = tk.Label(frame, text="| vertrektijd", background="#ffc61e", font="bold")
    tekst_set_2 = tk.Label(frame, text="| eindbestemming", background="#ffc61e", font="bold")
    tekst_set_3 = tk.Label(frame, text="| via", background="#ffc61e", font="bold")
    tekst_set_4 = tk.Label(frame, text="| spoor", background="#ffc61e", font="bold")
    tekst_set_5 = tk.Label(frame, text="| type", background="#ffc61e", font="bold")
    tekst_set_6 = tk.Label(frame, text="| vertraging", background="#ffc61e", font="bold")
    tekst_set_7 = tk.Label(frame, text="| rit", background="#ffc61e", font="bold")

    tekst_set_1.grid(row=0, column=0, sticky=tk.W)
    tekst_set_2.grid(row=0, column=1, sticky=tk.W)
    tekst_set_3.grid(row=0, column=2, sticky=tk.W)
    tekst_set_4.grid(row=0, column=3, sticky=tk.W)
    tekst_set_5.grid(row=0, column=4, sticky=tk.W)
    tekst_set_6.grid(row=0, column=5, sticky=tk.W)
    tekst_set_7.grid(row=0, column=6, sticky=tk.W)

    # hieronder leest hij de api uit en brengt de info naar het scherm
    rij = 1
    try:
        for vertrek in vertrekxml['ActueleVertrekTijden']['VertrekkendeTrein']:

            eindbestemming = vertrek['EindBestemming']
            try:
                spoor = vertrek["VertrekSpoor"]["#text"]
            except KeyError:
                spoor = "Nvt"
            soort = vertrek["TreinSoort"]
            rit = vertrek["RitNummer"]
            try:
                via = vertrek["RouteTekst"]
            except KeyError:
                via = "Nvt"

            try:
                vertraging = vertrek["VertrekVertragingTekst"]
            except KeyError:
                vertraging = " "
            vertrektijd = vertrek['VertrekTijd']  # 2016-09-27T18:36:00+0200
            vertrektijd = vertrektijd[11:16]  # 18:36

            tekst_set_1 = tk.Label(frame, text="| " + vertrektijd, background="#ffc61e", font="bold")
            tekst_set_2 = tk.Label(frame, text="| " + eindbestemming, background="#ffc61e", font="bold")
            tekst_set_3 = tk.Label(frame, text="| " + via, background="#ffc61e", font="bold")
            tekst_set_4 = tk.Label(frame, text="| " + spoor, background="#ffc61e", font="bold")
            tekst_set_5 = tk.Label(frame, text="| " + soort, background="#ffc61e", font="bold")
            tekst_set_6 = tk.Label(frame, text="| " + vertraging, background="#ffc61e", font="bold")
            tekst_set_7 = tk.Label(frame, text="| " + rit, background="#ffc61e", font="bold")

            tekst_set_1.grid(row=rij, column=0, sticky=tk.W)
            tekst_set_2.grid(row=rij, column=1, sticky=tk.W)
            tekst_set_3.grid(row=rij, column=2, sticky=tk.W)
            tekst_set_4.grid(row=rij, column=3, sticky=tk.W)
            tekst_set_5.grid(row=rij, column=4, sticky=tk.W)
            tekst_set_6.grid(row=rij, column=5, sticky=tk.W)
            tekst_set_7.grid(row=rij, column=6, sticky=tk.W)

            rij += 1
    except KeyError:
        error_message = "Geef een geldig station op."
        error_set_1 = tk.Label(frame, text=error_message, background="#ffc61e", font="bold")
        error_set_1.grid(row=1, column=0, columnspan=5, sticky=tk.W)


if __name__ == "__main__":
    app = Program()
    app.mainloop()
