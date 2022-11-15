
import tkinter as tk
import tkinter.ttk as ttk
import requests
from tkinter import messagebox
# from enum import Enum
# from tkcalendar import DateEntry

LARGEFONT = ("Verdana", 35)
URL = "http://127.0.0.1:9000"

User = None
cook = requests.Session()
tags = None
totalNum = None
discardedNum = None
availableNum = None
dirtyNum = None
bedNum = None
sheetNum = None

class tkinterApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('800x600')
        self.title("CleanUp!")
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginPage, Menu, StartPage, Page1, Page2):

            frame = F(container, self)

            self.frames[F] = frame
            # frame.grid(row=0, column=0)

        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]           
        frame.pack( expand=True,fill=tk.NONE)

class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        self.err = None
        tk.Frame.__init__(self, parent)
        
        title = ttk.Label(self, text="Clean UP", font=LARGEFONT)
        # title.grid(row=0, column=4, padx=10, pady=10,sticky="N")
        title.grid(row=0, padx=10, pady=10, sticky="N")

        self.loginWarning = ttk.Label(self, text=None, foreground='#FF0000')

        userLabel = ttk.Label(self, text="Usuário")
        userLabel.grid(row=2, padx=10, pady=10)

        self.userEntry = ttk.Entry(self)
        self.userEntry.grid(row=3, padx=10)

        pwdLabel = ttk.Label(self, text="Senha")
        pwdLabel.grid(row=4, padx=10, pady=10)

        self.pwdEntry = ttk.Entry(self, show="*")
        self.pwdEntry.grid(row=5, padx=10)

        lgnButton = ttk.Button(self, text="LOGIN",
                               command=lambda: self.login(controller))

        lgnButton.grid(row=6, padx=10, pady=10)

    def login(self, controller):
        global User
        user_id = self.userEntry.get()
        pwd = self.pwdEntry.get()
        user_data = {
            "user_id": user_id,
            "pwd": pwd
        }
        try:
            r = cook.post(URL+"/login", json=(user_data), verify=True)
            err = r.json()["error_message"]
            if r.json()["error_message"] == "Logado!":
                User = r.json()["user"]
                self.changePage(controller)
                self.loginWarning['text'] = ""
            else:
                self.loginWarning['text'] = err
            self.loginWarning.grid(row=1, padx=10, pady=10)
            # messagebox.showinfo("Alerta", err)
        except:
            err = "Problema ao se conectar ao servidor!"
            self.loginWarning['text'] = err
            self.loginWarning.grid(row=1, padx=10, pady=10)
            # messagebox.showinfo("Alerta", err)

    def changePage(self, controller):
        global tags
        global totalNum
        global discardedNum
        global availableNum
        global dirtyNum
        global sheetNum
        self.pack_forget()
        tags = cook.get(URL+"/total_tags")
        tags = tags.json()
        items = tags
        total = items["total"]
        discarded = items["discarded"]
        available = items["available"]
        dirty = items["dirty"]
        bed = items["bed"]
        sheet = items["bed_items"]["Lençol"]
        bath = items["bath"]
        bath_items = items["bath_items"]
        totalNum['text']=total
        discardedNum['text'] = discarded
        availableNum['text'] = available
        dirtyNum['text'] = dirty
        bedNum['text'] = bed
        sheetNum['text'] = sheet
        controller.show_frame(Menu)
     


class Menu(tk.Frame):

    def __init__(self, parent, controller):
        global totalNum
        global discardedNum
        global availableNum
        global dirtyNum
        global bedNum
        global sheetNum

        ttk.Frame.__init__(self, parent)
        
        menuFrame = ttk.Labelframe(self, text="Menu")
        # menuFrame.grid(row=0, column=0, padx=10, pady=10, sticky="W")
        menuFrame.grid(row=0,padx=10,pady=10,sticky=tk.W)

        countTagButton = ttk.Button(menuFrame,text="Ler Tags")
        countTagButton.grid(row=0,padx=10,pady=10,sticky=tk.W)

        tagListButton = ttk.Button(menuFrame,text="Lista de items")
        tagListButton.grid(row=1,padx=10,pady=10,sticky=tk.W)

        supListButton = ttk.Button(menuFrame,text="Lista de Fornecedores")
        supListButton.grid(row=2,padx=10,pady=10,sticky=tk.W)

        catListButton = ttk.Button(menuFrame,text="Lista de Categorias")
        catListButton.grid(row=3,padx=10,pady=10,sticky=tk.W)

        adminDash = ttk.Labelframe(self,text="Dashboard Administrativo")
        adminDash.grid(row=1,padx=10,pady=10,sticky=tk.W)

        userRegButton = ttk.Button(adminDash,text="Cadastrar Usuários")
        userRegButton.grid(row=0,padx=10,pady=10,sticky=tk.W)

        logButton = ttk.Button(adminDash,text="Histórico de Eventos")
        logButton.grid(row=2,padx=10,pady=10,sticky=tk.W)

        supRegButton = ttk.Button(adminDash,text="Registrar Fornecedores")
        supRegButton.grid(row=1,padx=10,pady=10,sticky=tk.W)

        catRegButton = ttk.Button(adminDash,text="Registrar Categorias")
        
        logoutButton = ttk.Button(self,text="LOGOUT",command=lambda: self.logout_request(controller))
        logoutButton.grid(row=2,padx=10,pady=10)

        statsFrame = ttk.Labelframe(self,text="Estatísticas")
        statsFrame.grid(row=0,rowspan=2,column=1,padx=10,pady=10,sticky=tk.W)

        totalLabel = ttk.Label(statsFrame,text="Total:")
        totalLabel.grid(row=0,column=0,padx=10,pady=10,sticky=tk.W)

        totalNum = ttk.Label(statsFrame,text="##")
        totalNum.grid(row=0,column=1,padx=10,pady=10,sticky=tk.W)

        discardedLabel = ttk.Label(statsFrame,text="Descartados:")
        discardedLabel.grid(row=0,column=2,padx=10,pady=10,sticky=tk.W)

        discardedNum = ttk.Label(statsFrame,text="##")
        discardedNum.grid(row=0,column=3,padx=10,pady=10,sticky=tk.W)

        availableLabel = ttk.Label(statsFrame,text="Disponíveis:")
        availableLabel.grid(row=1,column=0,padx=10,pady=10,sticky=tk.W)

        availableNum = ttk.Label(statsFrame,text="##")
        availableNum.grid(row=1,column=1,padx=10,pady=10,sticky=tk.W)

        dirtyLabel = ttk.Label(statsFrame, text="Itens em lavanderia:")
        dirtyLabel.grid(row=1,column=2,padx=10,pady=10,sticky=tk.W)

        dirtyNum = ttk.Label(statsFrame,text="##")
        dirtyNum.grid(row=1,column=3,padx=10,pady=10,sticky=tk.W)

        bedLabel = ttk.Label(statsFrame, text="Itens de Cama:")
        bedLabel.grid(row=2,column=0,padx=10,pady=10,sticky=tk.W)
        
        bedNum = ttk.Label(statsFrame,text="##")
        bedNum.grid(row=2,column=1,padx=10,pady=10,sticky=tk.W)

        sheetLabel = ttk.Label(statsFrame,text="Lençol:")
        sheetLabel.grid(row=2,column=2,padx=10,pady=10,sticky=tk.W)

        sheetNum = ttk.Label(statsFrame,text="##")
        sheetNum.grid(row=2,column=3,padx=10,pady=10,sticky=tk.W)

    def total_tags(self):

        r = cook.get(URL+"/total_tags")
        tags = r.json()

        return tags

    def logout_request(self,controller):
        try:
            cook.post(URL+"/logout")
            self.pack_forget()
            controller.show_frame(LoginPage)
        except:
            err = "Problema ao se conectar ao servidor!"
            messagebox.showinfo("Alerta", err)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):

        ttk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="StartPage", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Page 1",
                             command=lambda: controller.show_frame(Page1))

        button1.grid(row=1, column=1, padx=10, pady=10)

        button2 = ttk.Button(self, text="Page 2",
                             command=lambda: controller.show_frame(Page2))

        button2.grid(row=2, column=1, padx=10, pady=10)


class Page1(tk.Frame):

    def __init__(self, parent, controller):

        ttk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="Page 1", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="StartPage",
                             command=lambda: controller.show_frame(StartPage))

        button1.grid(row=1, column=1, padx=10, pady=10)

        button2 = ttk.Button(self, text="Page2",
                             command=lambda: controller.show_frame(Page2))

        button2.grid(row=2, column=1, padx=10, pady=10)


class Page2(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="Page 2", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = ttk.Button(self, text="Page 1",
                             command=lambda: controller.show_frame(Page1))

        button1.grid(row=1, column=1, padx=10, pady=10)

        button2 = ttk.Button(self, text="Page2",
                             command=lambda: controller.show_frame(Page2))

        button2.grid(row=2, column=1, padx=10, pady=10)


# class window_type(Enum):
#     # Vai ser necessario, tela de login, menu, contagem, registro de tags, painel admin, etc...
#     main = 1
#     frame = 2
#     toplevel = 3


# class GUI():

#     def __init__(self, wdw_type, title=None, frame=None, home=None) -> None:
#         if wdw_type == window_type.main:
#             self.window = tk.Tk()
#             # self.window.geometry('800x600')
#             MainMenu = tk.Menu(self.window)
#             fileMenu = tk.Menu(MainMenu, tearoff=0)
#             fileMenu.add_command(label="Sair", command=self.window.destroy)
#             MainMenu.add_cascade(label="Opções", menu=fileMenu)
#             self.window.config(menu=MainMenu)
#         elif wdw_type == window_type.frame:
#             self.window = frame
#         else:
#             self.window = tk.Toplevel()
#         if title is not None:
#             self.window.title(title)

#     def create_Label(self, textstr, rowint=None, columnint=None, columnspanint=None, stickystr=None, padxint=None, padyint=None, show=True):
#         name = ttk.Label(self.window, text=textstr)
#         if show:
#             name.grid(row=rowint, column=columnint, columnspan=columnspanint,
#                       sticky=stickystr, padx=padxint, pady=padyint)
#         return name

#     def create_LabelFrame(self, textstr, rowint=None, columnint=None, columnspanint=None, stickystr=None, padxint=None, padyint=None, show=True, rowspanint=None):
#         name = ttk.LabelFrame(self.window, text=textstr,)
#         if show:
#             name.grid(row=rowint, column=columnint, columnspan=columnspanint,
#                       sticky=stickystr, padx=padxint, pady=padyint, rowspan=rowspanint)
#         return GUI(window_type.frame, frame=name)

#     def create_Entry(self, rowint=None, columnint=None, columnspanint=None, stickystr=None, padxint=None, padyint=None, show_pw=None, show_entry=True):
#         name = ttk.Entry(self.window, show=show_pw)
#         if show_entry:
#             name.grid(row=rowint, column=columnint, columnspan=columnspanint,
#                       sticky=stickystr, padx=padxint, pady=padyint)
#         return name

#     def create_Button(self, textstr, commandf=None, rowint=None, columnint=None, columnspanint=None, stickystr=None, padxint=None, padyint=None, show=True, ipadxint=None, ipadyint=None, state=None):
#         name = ttk.Button(self.window, text=textstr,
#                           command=commandf, state=state)
#         if show:
#             name.grid(row=rowint, column=columnint, columnspan=columnspanint,
#                       sticky=stickystr, padx=padxint, pady=padyint, ipadx=ipadxint, ipady=ipadyint)
#         return name

#     def create_Combobox(self, textstr, rowint=None, columnint=None, columnspanint=None, stickystr=None, padxint=None, padyint=None, postcommandf=None, show=True):
#         name = ttk.Combobox(self.window, postcommand=postcommandf)
#         name.set(textstr)
#         if show:
#             name.grid(row=rowint, column=columnint, columnspan=columnspanint,
#                       sticky=stickystr, padx=padxint, padyx=padyint)
#         return name

#     def create_DateEntry(self, rowint, columnint, var):
#         name = DateEntry(self.window, selectmode='day',
#                          date_pattern='dd/mm/yyyy', textvariable=var)
#         name.grid(row=rowint, column=columnint)

#     def create_Checkbutton(self, textstr, var=None, rowint=None, columnint=None, columnspanint=None, stickystr=None, padxint=None, padyint=None, show=True, ipadxint=None, ipadyint=None):
#         name = ttk.Checkbutton(self.window, text=textstr, variable=var)
#         if show:
#             name.grid(row=rowint, column=columnint, columnspan=columnspanint,
#                       sticky=stickystr, padx=padxint, pady=padyint, ipadx=ipadxint, ipady=ipadyint)
#         return name


# def create_IntVar():
#     var = tk.IntVar()
#     return var


# def create_StringVar():
#     var = tk.StringVar()
#     return var

if __name__ == '__main__':
    app = tkinterApp()
    
    app.mainloop()
