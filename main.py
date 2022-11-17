
import tkinter as tk
import tkinter.ttk as ttk
import requests
from tkinter import messagebox
from serial.tools import list_ports
import serial
from time import sleep
from collections import deque
from threading import *
from tkcalendar import DateEntry

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
tagsWarn = None
regBtn = None
changeBtn = None
itemList = []
# tagsNum = None
# countBtn = None
# arduinoLabel = None

subcats = ["Toalha de banho", "Toalha de rosto", "Tapete banheiro","Lençol", "Fronha", "Edredom"]
suppliers = ["Fornecedor 1","Fornecedor 2","Fornecedor 3","Fornecedor 4"]

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

        for F in (LoginPage, Menu, TagList, TagCount,TagRegPage, TagChangePage, LogList, Page1, Page2):

            frame = F(container, self)

            self.frames[F] = frame
            # frame.grid(row=0, column=0)

        self.show_frame(LoginPage)

    def show_frame(self, cont):  
        frame = self.frames[cont]           
        frame.pack( expand=True,fill=tk.NONE)
        if cont == TagList:
            items = cook.get(URL+"/get_tags").json()
            m = 3
            for item in items:
                for j in range(len(item)-1):
                    e = ttk.Label(frame,text=item[j])
                    e.grid(row=m,column=j,padx=10,pady=10)
                m+=1
        elif cont == LogList:
            logs = cook.get(URL+"/get_log").json()
            m=3
            for log in logs:
                for j in range(len(log)):
                    e = ttk.Label(frame,text=log[j])
                    e.grid(row=m,column=j,padx=10,pady=10)
                m+=1
        elif cont == TagChangePage:
            global regTags
            m = frame.updatePage()
            frame.renderChange(m)
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

        adminDash = ttk.Labelframe(self,text="Dashboard Administrativo")
        adminDash.grid(row=1,padx=10,pady=10,sticky=tk.W)

        userRegButton = ttk.Button(adminDash,text="Cadastrar Usuários")
        userRegButton.grid(row=0,padx=10,pady=10,sticky=tk.W)

        logButton = ttk.Button(adminDash,text="Histórico de Eventos", command=lambda: self.seeLog(controller))
        logButton.grid(row=2,padx=10,pady=10,sticky=tk.W)
        
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

        controller.show_frame(TagList)
    
    def countTags(self,controller):
        self.pack_forget()

        controller.show_frame(TagCount)

    def seeLog(self,controller):
        self.pack_forget()
        controller.show_frame(LogList)

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

class TagList(tk.Frame):
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

class TagCount(tk.Frame):

    def __init__(self, parent, controller):
        global tagsWarn
        global regBtn
        global changeBtn
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

        tagsWarn = ttk.Label(self, text=None, foreground='#FF0000')
        tagsWarn.grid(row=4,padx=10,pady=10)

        changeBtn = ttk.Button(self,text="Visualizar tags registradas", command=lambda: self.goToChange(controller))
        changeBtn.grid(row=5,padx=10,pady=10)
        changeBtn.state(['disabled'])

        regBtn = ttk.Button(self,text="Registrar tags", command=lambda: self.goToReg(controller))
        regBtn.grid(row=6,padx=10,pady=10) 
        regBtn.state(['disabled'])


        returnBtn = ttk.Button(self,text="Voltar", command=lambda: self.returnMenu(controller))
        returnBtn.grid(row=7,padx=10,pady=10)

        updateTagLabel(tagsNum)
        setArduino(arduinoLabel,countBtn)

    def returnMenu(self,controller):
        # stopCount(button,label)
        self.pack_forget()
        controller.show_frame(Menu)

    def goToReg(self,controller):
        self.pack_forget()
        controller.show_frame(TagRegPage)

    def goToChange(self,controller):
        self.pack_forget()
        global regTags
        # m = 4
        # for regTag in regTags:
        #     for j in range(len(regTag[0])-1):
        #         print(regTag)
        #         print(regTag[0][0])
        #         e = ttk.Label(se,text=regTag[0][j])
        #         e.grid(row=m,column=j,padx=10,pady=10)
        #     m+=1
        controller.show_frame(TagChangePage)

class TagRegPage(tk.Frame):

    def __init__(self, parent, controller):
        self.err = None
        tk.Frame.__init__(self, parent)
        
        title = ttk.Label(self, text="Registro de Tags", font=LARGEFONT)
        title.grid(row=0,columnspan=2, padx=10, pady=10, sticky="N")

        returnBtn = ttk.Button(self,text="Voltar", command=lambda: self.returnPage(controller))
        returnBtn.grid(row=1,columnspan=2,padx=10,pady=10)

        self.regWarning = ttk.Label(self, text=None, foreground='#FF0000')
        self.regWarning.grid(row=2,padx=10,pady=10)

        aqDate = ttk.Label(self,text="Data de aquisição: ")
        aqDate.grid(row=3,column=0,padx=10,pady=10)

        cal = DateEntry(self,selectmode='day')
        cal.grid( row=3,column=1,padx=10,pady=10)

        catLabel = ttk.Label(self,text="Categoria:")
        catLabel.grid(row=4,column=0,padx=10,pady=10)

        cat = tk.StringVar(self)
        catMenu = ttk.OptionMenu(self,cat,*subcats)
        catMenu.grid(row=4,column=1,padx=10,pady=10)

        supLabel = ttk.Label(self,text="Fornecedor:")
        supLabel.grid(row=5,column=0,padx=10,pady=10)

        sup = tk.StringVar(self)
        supMenu = ttk.OptionMenu(self,sup,*suppliers)
        supMenu.grid(row=5,column=1,padx=10,pady=10)

        clean = tk.IntVar(self)
        cleanLabel = ttk.Label(self,text="Limpo?")
        cleanLabel.grid(row=6,column=0,padx=10,pady=10)

        cleanCheck = ttk.Checkbutton(self,variable=clean,onvalue=1,offvalue=0)
        cleanCheck.grid(row=6,column=1,padx=10,pady=10)

        damage = tk.IntVar(self)
        dmgLabel = ttk.Label(self,text="Danificado?")
        dmgLabel.grid(row=7,column=0,padx=10,pady=10)

        dmgCheck = ttk.Checkbutton(self,variable=damage,onvalue=1,offvalue=0)
        dmgCheck.grid(row=7,column=1,padx=10,pady=10)

        status = tk.IntVar(self)
        statusLabel = ttk.Label(self,text="Ativo?")
        statusLabel.grid(row=8,column=0,padx=10,pady=10)

        statusCheck = ttk.Checkbutton(self,variable=status,onvalue=1,offvalue=0)
        statusCheck.grid(row=8,column=1,padx=10,pady=10)

        submitBtn = ttk.Button(self,text="Registrar Tags", command=lambda: self.submit(cal,cat,sup,clean,damage,status))
        submitBtn.grid(row=9,column=0,columnspan=2,padx=10,pady=10)
             
    def returnPage(self,controller):
        self.pack_forget()
        controller.show_frame(TagCount)

    def submit(self, date, cat, sup, clean, damage, status):

        body = {
            "tag_list": unregTags,
            "aquisition_date": date.get(),
            "category": cat.get(),
            "supplier": sup.get(),
            "clean": clean.get(),
            "damage": damage.get(),
            "status": status.get()
        }
        r = cook.post(URL+"/reg_tags", json=(body), verify=True)
        sleep(1)
        
        self.regWarning['text'] = r.json()["message"]
                
class TagChangePage(tk.Frame):

    def __init__(self, parent, controller):
        self.err = None
        self.cont = controller
        tk.Frame.__init__(self, parent)
        
        cats = ["ID","Data de Aquisição","Categoria","Subcategoria","Fornecedor","Limpo?","Danificado?","Status"]

        returnBtn = ttk.Button(self,text="Voltar", command=lambda: self.returnPage(controller))
        returnBtn.grid(row=0,padx=10,pady=10)

        title = ttk.Label(self, text="Visualização de Tags", font=LARGEFONT)
        title.grid(row=1,columnspan=len(cats), padx=10, pady=10, sticky="N")

        

        self.regWarning = ttk.Label(self, text=None, foreground='#FF0000')
        self.regWarning.grid(row=2,padx=10,pady=10)



        i=0
        for cat in cats:
            e = ttk.Label(self,text=cat)
            e.grid(row=3,column=i,padx=10,pady=10)
            i+=1

    def returnPage(self,controller):
        self.pack_forget()
        controller.show_frame(TagCount)

    def renderChange(self,m):
        
        events = ["Limpa","Suja","Ativa","Inativa","Danificada","Restaurada"]

        changeLabel = ttk.Label(self,text="Alterar Tag")
        changeLabel.grid(row=m,padx=10,pady=10)
        tagVals = []
        tag = tk.StringVar(self)
        for regTag in regTags:
            tagVals.append(regTag[0][0])

        tagLabel = ttk.Label(self,text="Tag: ")
        tagLabel.grid(row=m+1,column=0,padx=10,pady=10)
        tagOption = ttk.OptionMenu(self,tag,*tagVals)
        tagOption.grid(row=m+1,column=1,padx=10,pady=10)
 
        event = tk.StringVar(self)
        eventLabel = ttk.Label(self,text="Evento: ")
        eventLabel.grid(row=m+2,column=0,padx=10,pady=10)
        eventOption = ttk.OptionMenu(self,event,*events)
        eventOption.grid(row=m+2,column=1,padx=10,pady=10)

        subBtn = ttk.Button(self,text="Alterar",command=lambda: self.submitChange(tag,event))
        subBtn.grid(row=m+3,padx=10,pady=10)

    def submitChange(self,tag,event):
        tag = tag.get()
        event = event.get()
        body = {
            "tag": tag,
            "event": event
        }
        print(body)
        r = cook.post(URL+"/change_tags", json=(body), verify=True)
        if r.text == "OK":
            self.regWarning['text']="Alterado com sucesso!"


    def updatePage(self):
        global regTags
        global itemList
        m = 4
        for item in itemList:
            item.grid_forget()
        for regTag in regTags:
            for j in range(len(regTag[0])-1):
                print(regTag)
                print(regTag[0][0])
                e = ttk.Label(self,text=regTag[0][j])
                itemList.append(e)
                e.grid(row=m,column=j,padx=10,pady=10)

            m+=1
        
        return m


class LogList(tk.Frame):
 #(tag_id,event,date,staffname)
    def __init__(self, parent, controller):

        ttk.Frame.__init__(self, parent)

        cats = ["ID","Evento","Data","Nome"]
        
        returnBtn = ttk.Button(self,text="Voltar", command=lambda: self.returnMenu(controller))
        returnBtn.grid(row=0,padx=10,pady=10)

        label = ttk.Label(self, text="HISTÓRICO", font=LARGEFONT)
        label.grid(row=1, padx=10, pady=10,columnspan=len(cats), sticky="N")

        i=0
        for cat in cats:
            e = ttk.Label(self,text=cat)
            e.grid(row=2,column=i,padx=10,pady=10)
            i+=1

    def returnMenu(self,controller):
        self.pack_forget()
        controller.show_frame(Menu)


def startCount(btn,label):
    global countFlag
    global t1
    global tagsWarn
    tagsWarn['text'] = " "
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

def checkTags(tagList):
    global unregTags
    global regTags
    global tagsWarn
    global changeBtn
    global regBtn
    body = {
        "tags": tagList
    }
    r = cook.post(URL+"/check_tags",json=(body),verify=True)
    unregTags = r.json()["non_registered"]
    regTags = r.json()["registered"]
    if len(unregTags) > 0 and len(regTags) > 0:
        tagsWarn['text'] = f"{len(unregTags)} tags não registradas e {len(regTags)} tags registradas foram detectadas"
        changeBtn.state(['!disabled'])
        regBtn.state(['!disabled'])
    elif len(unregTags) > 0:
        tagsWarn['text'] = f"{len(unregTags)} tags não registradas foram detectadas"
        changeBtn.state(['disabled'])
        regBtn.state(['!disabled'])
    elif len(regTags) > 0:
        tagsWarn['text'] = f"{len(regTags)} tags registradas foram detectadas"
        changeBtn.state(['!disabled'])
        regBtn.state(['disabled'])
    
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


if __name__ == '__main__':
    app = tkinterApp()
    

    app.mainloop()
