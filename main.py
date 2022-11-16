
import tkinter as tk
import tkinter.ttk as ttk
import requests
from tkinter import messagebox
from serial.tools import list_ports
import serial
from time import sleep
from collections import deque
from threading import *
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
pillowcaseNum = None
duvetNum = None
bathNum = None
bathtowelNum = None
facetowelNum = None
bathmatNum = None
countFlag = 0
messageQueue = deque()
inputList = []
ser = None
t1 = None
regTags = []
unregTags = []
# tagsNum = None
# countBtn = None
# arduinoLabel = None

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

        for F in (LoginPage, Menu, tagList, tagCount, StartPage, Page1, Page2):

            frame = F(container, self)

            self.frames[F] = frame
            # frame.grid(row=0, column=0)

        self.show_frame(LoginPage)

    def show_frame(self, cont):  
        frame = self.frames[cont]           
        frame.pack( expand=True,fill=tk.NONE)
        if cont == tagList:
            items = cook.get(URL+"/get_tags").json()
            m = 3
            for item in items:
                for j in range(len(item)-1):
                    e = ttk.Label(frame,text=item[j])
                    e.grid(row=m,column=j,padx=10,pady=10)
                m+=1
        elif cont == Menu:
            global tags
            global totalNum
            global discardedNum
            global availableNum
            global dirtyNum
            global sheetNum
            global pillowcaseNum
            global duvetNum
            global bathNum
            global bathtowelNum
            global facetowelNum
            global bathmatNum
            tags = cook.get(URL+"/total_tags")
            tags = tags.json()
            items = tags
            total = items["total"]
            discarded = items["discarded"]
            available = items["available"]
            dirty = items["dirty"]
            bed = items["bed"]
            sheet = items["bed_items"]["Lençol"]
            pillowcase = items["bed_items"]["Fronha"]
            duvet = items["bed_items"]["Edredom"]
            bath = items["bath"]
            bathtowel = items["bath_items"]["Toalha de banho"]
            facetowel = items["bath_items"]["Toalha de rosto"]
            bathmat = items["bath_items"]["Tapete banheiro"]
            totalNum['text']=total
            discardedNum['text'] = discarded
            availableNum['text'] = available
            dirtyNum['text'] = dirty
            bedNum['text'] = bed
            sheetNum['text'] = sheet
            pillowcaseNum['text']=pillowcase
            duvetNum['text'] = duvet
            bathNum['text'] = bath
            bathtowelNum["text"] = bathtowel
            facetowelNum["text"] = facetowel
            bathmatNum['text'] = bathmat
        # elif cont == tagCount:
        #     global tagsNum
        #     global countBtn
        #     global arduinoLabel
        #     setArduino(arduinoLabel,countBtn)
        #     updateTagLabel(tagsNum)

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
        self.pack_forget()
        controller.show_frame(Menu)
     


class Menu(tk.Frame):

    def __init__(self, parent, controller):
        global totalNum
        global discardedNum
        global availableNum
        global dirtyNum
        global bedNum
        global sheetNum
        global pillowcaseNum
        global duvetNum
        global bathNum
        global bathtowelNum
        global facetowelNum
        global bathmatNum

        ttk.Frame.__init__(self, parent)
        
        menuFrame = ttk.Labelframe(self, text="Menu")
        # menuFrame.grid(row=0, column=0, padx=10, pady=10, sticky="W")
        menuFrame.grid(row=0,padx=10,pady=10,sticky=tk.W)

        countTagButton = ttk.Button(menuFrame,text="Ler Tags", command= lambda: self.countTags(controller))
        countTagButton.grid(row=0,padx=10,pady=10,sticky=tk.W)

        tagListButton = ttk.Button(menuFrame,text="Lista de items",command= lambda: self.seeTags(controller))
        tagListButton.grid(row=1,padx=10,pady=10,sticky=tk.W)

        supListButton = ttk.Button(menuFrame,text="Lista de Fornecedores")
        supListButton.grid(row=2,padx=10,pady=10,sticky=tk.W)

        adminDash = ttk.Labelframe(self,text="Dashboard Administrativo")
        adminDash.grid(row=1,padx=10,pady=10,sticky=tk.W)

        userRegButton = ttk.Button(adminDash,text="Cadastrar Usuários")
        userRegButton.grid(row=0,padx=10,pady=10,sticky=tk.W)

        logButton = ttk.Button(adminDash,text="Histórico de Eventos")
        logButton.grid(row=2,padx=10,pady=10,sticky=tk.W)

        supRegButton = ttk.Button(adminDash,text="Registrar Fornecedores")
        supRegButton.grid(row=1,padx=10,pady=10,sticky=tk.W)
        
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

        pillowcaseLabel = ttk.Label(statsFrame,text="Fronha:")
        pillowcaseLabel.grid(row=2,column=4,padx=10,pady=10,sticky=tk.W)

        pillowcaseNum = ttk.Label(statsFrame, text="##")
        pillowcaseNum.grid(row=2,column=5,padx=10,pady=10,sticky=tk.W)

        duvetLabel = ttk.Label(statsFrame,text="Edredom:")
        duvetLabel.grid(row=2,column=6,padx=10,pady=10,sticky=tk.W)

        duvetNum = ttk.Label(statsFrame,text="##")
        duvetNum.grid(row=2,column=7,padx=10,pady=10,sticky=tk.W)

        bathLabel = ttk.Label(statsFrame, text="Itens de Banho:")
        bathLabel.grid(row=3,column=0,padx=10,pady=10,sticky=tk.W)

        bathNum = ttk.Label(statsFrame,text="##")
        bathNum.grid(row=3,column=1,padx=10,pady=10,sticky=tk.W)

        bathtowelLabel = ttk.Label(statsFrame,text="Toalha de Banho:")
        bathtowelLabel.grid(row=3,column=2,padx=10,pady=10,sticky=tk.W)

        bathtowelNum = ttk.Label(statsFrame,text="##")
        bathtowelNum.grid(row=3,column=3,padx=10,pady=10,sticky=tk.W)

        facetowelLabel = ttk.Label(statsFrame,text="Toalha de Rosto:")
        facetowelLabel.grid(row=3,column=4,padx=10,pady=10,sticky=tk.W)

        facetowelNum = ttk.Label(statsFrame,text="##")
        facetowelNum.grid(row=3,column=5,padx=10,pady=10,sticky=tk.W)

        bathmatLabel = ttk.Label(statsFrame,text="Tapete banheiro:")
        bathmatLabel.grid(row=3,column=6,padx=10,pady=10,sticky=tk.W)

        bathmatNum = ttk.Label(statsFrame,text="##")
        bathmatNum.grid(row=3,column=7,padx=10,pady=10,sticky=tk.W)

    def seeTags(self,controller):
        self.pack_forget()

        controller.show_frame(tagList)
    
    def countTags(self,controller):
        self.pack_forget()

        controller.show_frame(tagCount)

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


class tagList(tk.Frame):
 #(tag_id,aquisition_date, category, sub_category, supplier, clean, damage, status, staff_name)
    def __init__(self, parent, controller):

        ttk.Frame.__init__(self, parent)

        cats = ["ID","Data de Aquisição","Categoria","Subcategoria","Fornecedor","Limpo?","Danificado?","Status"]
        
        returnBtn = ttk.Button(self,text="Voltar", command=lambda: self.returnMenu(controller))
        returnBtn.grid(row=0,padx=10,pady=10)

        label = ttk.Label(self, text="INVENTÁRIO", font=LARGEFONT)
        label.grid(row=1, padx=10, pady=10,columnspan=len(cats), sticky="N")

        i=0
        for cat in cats:
            e = ttk.Label(self,text=cat)
            e.grid(row=2,column=i,padx=10,pady=10)
            i+=1

    def returnMenu(self,controller):
        self.pack_forget()
        controller.show_frame(Menu)

class tagCount(tk.Frame):

    def __init__(self, parent, controller):
        # global tagsNum
        # global countBtn
        # global arduinoLabel
        ttk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="Leitura de tags", font=LARGEFONT)
        label.grid(row=0, padx=10, pady=10, sticky=tk.N)

        arduinoLabel = ttk.Label(self,text="Aguardando...")
        arduinoLabel.grid(row=1, padx=10, pady=10, sticky=tk.N)

        tagsLabel = ttk.Label(self,text="Número de tags lidas: ")
        tagsLabel.grid(row=2,column=0,padx=10,pady=10,sticky=tk.W)

        tagsNum = ttk.Label(self,text="0")
        tagsNum.grid(row=2,column=1,padx=10,pady=10)

        countBtn = ttk.Button(self,text="Contar", command=lambda: startCount(countBtn,tagsNum))
        countBtn.grid(row=3,padx=10,pady=10)

        changeBtn = ttk.Button(self,text="Alterar tags registradas", command=lambda: startCount(countBtn,tagsNum))
        changeBtn.grid(row=4,padx=10,pady=10)
        changeBtn.state(['disabled'])

        regBtn = ttk.Button(self,text="Registrar tags", command=lambda: startCount(countBtn,tagsNum))
        regBtn.grid(row=5,padx=10,pady=10) 
        regBtn.state(['disabled'])


        returnBtn = ttk.Button(self,text="Voltar", command=lambda: self.returnMenu(controller,countBtn,tagsNum))
        returnBtn.grid(row=6,padx=10,pady=10)

        updateTagLabel(tagsNum)
        setArduino(arduinoLabel,countBtn)

    def returnMenu(self,controller,button,label):
        # stopCount(button,label)
        self.pack_forget()
        controller.show_frame(Menu)

def startCount(btn,label):
    global countFlag
    global t1
    countFlag = 0
    label['text'] = 0
    btn.configure(text = "Parar", command = lambda: stopCount(btn,label))
    if t1 is not None:
        t1.join()
    t1 = Thread(target = readTags)
    t1.setDaemon(True)
    t1.start()
    

def stopCount(btn,label):
    global countFlag
    global inputList
    countFlag = 1
    btn.configure(text = "Contar", command = lambda: startCount(btn,label))
    if len(inputList) != 0:
        checkTags(inputList)

def checkTags(tag_list):
    global unregTags
    global regTags
    body = {
        "tags": tag_list
    }
    r = cook.post(URL+"/check_tags",json=(body),verify=True)
    unregTags = r.json()["non_registered"]
    regTags = r.json()["registered"]
    

def readTags():
    global countFlag
    global inputList
    global ser
    inputList = []
    port = findArduinoPort()
    if ser is not None:
        ser.close()
        sleep(1)
    ser = serial.Serial(port, 9600, timeout=1)
    while countFlag == 0:
        serBytes = ser.readline()
        if countFlag == 0:
            decodedBytes = str(serBytes[1:len(serBytes)-2].decode("utf-8")).replace(' ','')
            if inputList.count(decodedBytes) == 0 and decodedBytes != '':
                inputList.append(decodedBytes)
                messageQueue.append(len(inputList))
                sleep(1)
                print(f'Added {decodedBytes} to the read tags list.')


def setArduino(label,button):
    global countFlag
    port = findArduinoPort()
    if port is not None:
        label['text'] = f'Arduino conectado na porta {port}'
        button.state(['!disabled'])
    else:
        label['text'] = 'Arduino não está conectado'
        # stopCount(button,label2)
        button.state(['disabled'])
    
    label.after(1000,setArduino,label,button)


def findArduinoPort():
        devices = list(list_ports.comports())
        for device in devices:
            manufacturer = device.manufacturer
            if manufacturer is not None and 'arduino' in manufacturer.lower():
                return device.device

def updateTagLabel(num):
    try:
        num['text'] = messageQueue.popleft()
    except IndexError: pass
    num.after(1000,updateTagLabel,num)

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
