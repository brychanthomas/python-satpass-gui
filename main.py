import tkinter as tk
from tkcalendar import Calendar, DateEntry
from orbit_predictor.sources import get_predictor_from_tle_lines
from orbit_predictor.locations import Location
import datetime
import json
import requests

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

        tk.Label(master, text='Parameters:').grid(column=2, row=0)
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

        tk.Label(master, text='Max elevation at least:').grid(column=1, row=3, sticky='E')
        self.elevationEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=2)
        self.elevationEntry.insert(0, '10')
        self.elevationEntry.grid(column=2, row=3)

        tk.Label(master, text='After hour:').grid(column=1, row=4, sticky='E')
        self.afterHourEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=2)
        self.afterHourEntry.grid(column=2, row=4)
        self.afterHourEntry.insert(0, '0')
        tk.Label(master, text='Before hour:').grid(column=1, row=5, sticky='E')
        self.beforeHourEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=2)
        self.beforeHourEntry.grid(column=2, row=5)
        self.beforeHourEntry.insert(0, '24')
        
        tk.Label(master, text='Location:').grid(column=1, row=6, sticky='E')
        self.locationEntry = tk.Entry(master)
        self.locationEntry.grid(column=2, row=6)
        def getLatLng():
            if len(self.locationEntry.get()) < 2:
                return
            r = requests.get('https://nominatim.openstreetmap.org/search?format=json&q='+self.locationEntry.get())
            loc = json.loads(r.text)[0]
            self.locationEntry.delete(0, 'end')
            self.locationEntry.insert(0, loc['display_name'])
            self.latEntry.delete(0, 'end')
            self.latEntry.insert(0, loc['lat'])
            self.lngEntry.delete(0, 'end')
            self.lngEntry.insert(0, loc['lon'])
        tk.Button(text='Get coordinates', command=getLatLng).grid(column=2, row=7)

        tk.Label(text='Latitude:').grid(column=1, row=8, sticky='E')
        self.latEntry = tk.Entry(master, width=11)
        self.latEntry.grid(column=2, row=8)
        self.latEntry.insert(0, 51.4816546)
        tk.Label(text='Longitude:').grid(column=1, row=9, sticky='E')
        self.lngEntry = tk.Entry(master, width=11)
        self.lngEntry.grid(column=2, row=9)
        self.lngEntry.insert(0, -3.1791934)

        self.updateButton = tk.Button(self.master, text="Update orbits", command=self.updateCallback)
        self.updateButton.grid(column=3, row=1)
        self.predictButton = tk.Button(self.master, text="Predict passes", command=self.predictCallback)
        self.predictButton.grid(column=3, row=3)

        master.grid_columnconfigure(0, minsize=150)
        master.grid_columnconfigure(2, minsize=150)
        master.grid_columnconfigure(3, minsize=150)

    def getStartDate(self):
        return self.dateEntry.get_date()

    def getDaysToPredictFor(self):
        return int(self.daysEntry.get())

    def getMaxElevation(self):
        return int(self.elevationEntry.get())

    def getLatitude(self):
        return float(self.latEntry.get())

    def getLongitude(self):
        return float(self.lngEntry.get())

    def getSelectedSats(self):
        sats = []
        for c in self.satCheckboxVars:
            if c.get() != '0':
                sats.append(c.get())
        return sats
    
    def displayTableWindow(self, table):
        newWindow = tk.Toplevel(self.master)
        newWindow.geometry("740x500")
        canvas = tk.Canvas(newWindow)
        frame = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(newWindow, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4,4), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        for row in range(len(table)):
            for col in range(len(table[0])):
                if row == 0:
                    cell = tk.Entry(frame, width=11, font='Helevica 12 bold')
                else:
                    cell = tk.Entry(frame, width=11)
                cell.configure({"disabledforeground":"black"})
                cell.insert(tk.END, table[row][col])
                cell['state'] = tk.DISABLED
                cell.grid(row=row, column=col)
        csv = '\n'.join(map(lambda p: ','.join(p), table))
        def copyCsv():
            newWindow.clipboard_clear()
            newWindow.clipboard_append(csv)
        tk.Button(newWindow, text='Copy CSV', command=copyCsv).pack(side="top")
        tk.Button(newWindow, text='Close', command=newWindow.destroy).pack(side="bottom")

    def setButtonsEnabled(self, enabled):
        if enabled:
            self.predictButton['state'] = tk.NORMAL
            self.updateButton['state'] = tk.NORMAL
        else:
            self.predictButton['state'] = tk.DISABLED
            self.updateButton['state'] = tk.DISABLED

class OrbitManager:
    def __init__(self, satellites):
        self.satellites = satellites

    def predictPasses(self, intDesigs, startTime, daysToPredictFor, maxElevationAtLeast, lat, lng):
        loc = Location("location", lat, lng, 10)
        endTime = startTime + datetime.timedelta(days=daysToPredictFor)
        endTime = endTime.replace(hour=0, minute=0)
        passes = []
        for intDes in intDesigs:
            predictor = get_predictor_from_tle_lines(self.__getTle(intDes))
            for p in predictor.passes_over(loc, startTime):
                if p.aos > endTime:
                    break
                if p.max_elevation_deg >= maxElevationAtLeast:
                    satName = self.satellites[intDes]
                    passDate = p.aos.astimezone(None).strftime('%d/%m/%y')
                    aosTime = p.aos.astimezone(None).strftime('%H:%M:%S')
                    maxElTime = p.max_elevation_date.astimezone(None).strftime('%H:%M:%S')
                    maxEl = round(p.max_elevation_deg, 1)
                    duration = str(round(p.duration_s//60))+':'+str(round(p.duration_s%60)).zfill(2)
                    passes.append([satName, passDate, aosTime, maxElTime, str(maxEl), duration, p.aos])
        passes = sorted(passes, key=lambda x: x[-1])
        for p in passes:
            p.pop()
        passes.insert(0, ['Name', 'Date', 'Start time', 'Max el. time', 'Max el. (°)', 'Duration'])
        return passes
                
    def updateOrbits(self):
        for intDes in self.satellites.keys():
            self.__updateTle(intDes)

    def __getTle(self, intDes):
        with open('TLEs\\'+intDes+'.tle', 'r') as file:
            tle = file.read().split('\n')[:2]
            file.close()
        return tle

    def __updateTle(self, intDes):
        req = requests.get('https://celestrak.com/satcat/tle.php?INTDES='+intDes)
        if req.status_code != 200:
            print ("Error fetching TLE for "+intDes)
            return
        tle = req.text.replace('\r','').split('\n')[1:3]
        with open('TLEs\\'+intDes+'.tle', 'w') as file:
            file.write('\n'.join(tle))
            file.close()
            

class Controller:
    def __init__(self):
        with open('satellites.json', 'r') as file:
            satellites = json.loads(file.read())
            file.close()
        root = tk.Tk()
        defaultFont = tk.font.nametofont("TkDefaultFont")
        defaultFont.configure(size=12)
        root.option_add("*Font", defaultFont)
        self.view = MainWindow(root, satellites, self.predictPressed, self.updatePressed)
        self.model = OrbitManager(satellites)
        root.mainloop()

    def predictPressed(self):
        if self.view.getStartDate() == datetime.datetime.today().date():
            startTime = datetime.datetime.utcnow()
        else:
            midnight = datetime.datetime.min.time()
            startTime = datetime.datetime.combine(self.view.getStartDate(), midnight)
        passes = self.model.predictPasses(self.view.getSelectedSats(), startTime, self.view.getDaysToPredictFor(), self.view.getMaxElevation(), self.view.getLatitude(), self.view.getLongitude())
        self.view.displayTableWindow(passes)

    def updatePressed(self):
        self.view.setButtonsEnabled(False)
        self.model.updateOrbits()
        self.view.setButtonsEnabled(True)
    
c = Controller()
