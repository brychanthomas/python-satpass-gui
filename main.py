import tkinter as tk
from tkcalendar import Calendar, DateEntry
from orbit_predictor.sources import get_predictor_from_tle_lines
from orbit_predictor.locations import Location
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
            for col in range(len(table[0])):
                cell = tk.Entry(newWindow)
                cell.insert(tk.END, table[row][col])
                cell['state'] = tk.DISABLED
                cell.grid(row=row, column=col)
        tk.Button(newWindow, text='Close', command=newWindow.destroy).grid()

class OrbitManager:
    def __init__(self, satellites):
        self.satellites = satellites

    def predictPasses(self, intDesigs, startTime, daysToPredictFor):
        card = Location("Cardiff", 55.95, -3.2, 10)
        endTime = startTime + datetime.timedelta(days=daysToPredictFor)
        endTime = endTime.replace(hour=0, minute=0)
        passes = []
        for intDes in intDesigs:
            predictor = get_predictor_from_tle_lines(self.__getTle(intDes))
            for p in predictor.passes_over(card, startTime):
                if p.aos > endTime:
                    break
                satName = self.satellites[intDes]
                passDate = p.aos.strftime('%d/%m/%y')
                aosTime = p.aos.strftime('%H:%M:%S')
                maxElTime = p.max_elevation_date.strftime('%H:%M:%S')
                maxEl = round(p.max_elevation_deg, 1)
                passes.append([satName, passDate, aosTime, maxElTime, maxEl, p.aos])
        passes = sorted(passes, key=lambda x: x[-1])
        for p in passes:
            p.pop()
        return passes
                

    def updateOrbits(self):
        pass

    def __getTle(self, intDes):
        with open('TLEs\\'+intDes+'.tle', 'r') as file:
            tle = file.read().split('\n')[:2]
            file.close()
        return tle

    def __updateTle(self, intDes):
        pass
            
def p():
    a = OrbitManager({'2013':'satellite name'})
    if window.getStartDate() == datetime.datetime.today().date():
        startTime = datetime.datetime.utcnow()
    else:
        midnight = datetime.datetime.min.time()
        startTime = datetime.datetime.combine(window.getStartDate(), midnight)
    passes = a.predictPasses(window.getSelectedSats(), startTime, window.getDaysToPredictFor())
    window.displayTableWindow(passes)

def u():
    print("Update")
    
root = tk.Tk()
window = MainWindow(root, {'2013':'satellite name'}, p, u)
root.mainloop()
