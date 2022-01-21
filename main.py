import tkinter as tk
from tkcalendar import Calendar, DateEntry
import datetime

class MainWindow:
    def __init__(self, master, satellites, predictCallback, updateCallback):
        self.master = master
        self.predictCallback = predictCallback
        self.updateCallback = updateCallback
        self.satCheckboxVars = []
        tk.Label(master, text='Satellites:').grid(column=0)
        for (intDes, name) in satellites.items():
            var = tk.StringVar()
            var.set('0')
            checkbox = tk.Checkbutton(master, text=name, onvalue=intDes, offvalue='0', variable=var)
            checkbox.grid(column=0, sticky='W')
            self.satCheckboxVars.append(var)

        tk.Label(master, text='Dates:').grid(column=2, row=0)
        tk.Label(master, text='Start date:').grid(column=1, row=1, sticky='E')
        self.dateEntry = DateEntry(master, date_pattern='dd/MM/yyyy')
        self.dateEntry.grid(column=2, row=1)

        def validateNumber(char):
            if char.isdigit():
                return True
            else:
                master.bell()
                return False
        vcmd = (master.register(validateNumber), '%S')
        tk.Label(master, text='Days to predict for:').grid(column=1, row=2, sticky='E')
        self.daysEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=3)
        self.daysEntry.insert(0, '7')
        self.daysEntry.grid(column=2, row=2)

        tk.Button(self.master, text="Update orbits", command=self.updateCallback).grid(column=3, row=1)
        tk.Button(self.master, text="Predict passes", command=self.predictCallback).grid(column=3, row=3)

        master.grid_columnconfigure(0, minsize=150)
        master.grid_columnconfigure(2, minsize=150)
        master.grid_columnconfigure(3, minsize=150)

    def getStartDate(self):
        return self.dateEntry.get_date()

    def getDaysToPredictFor(self):
        return int(self.daysEntry.get())

    def getSelectedSats(self):
        sats = []
        for c in self.satCheckboxVars:
            if c.get() != '0':
                sats.append(c.get())
        return sats
    
    def displayTableWindow(self, table):
        newWindow = tk.Toplevel(self.master)
        for row in range(len(table)):
            for col in range(len(table)):
                cell = tk.Entry(newWindow)
                cell.insert(tk.END, table[row][col])
                cell['state'] = tk.DISABLED
                cell.grid(row=row, column=col)
        tk.Button(newWindow, text='Close', command=newWindow.destroy).grid()

class OrbitManager:
    def __init__(self, satellites):
        self.satellites = satellites

    def predictPasses(self, intDesigs):
        passes = []
        for intDes in intDesigs:

    def updateOrbits(self):
        pass

    def __getTle(self, intDes):
        pass

    def __updateTle(self, intDes):
        pass
            
def p():
    window.displayTableWindow([['AB','AC'], ['KE','VZ']])

def u():
    print("Update")
    
root = tk.Tk()
window = MainWindow(root, {'AM':'NOAA-19', 'Stalin':'Meteor M2', 'SSI':'ISS'}, p, u)
root.mainloop()
