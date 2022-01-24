import tkinter as tk
from tkcalendar import Calendar, DateEntry
from orbit_predictor.sources import get_predictor_from_tle_lines
from orbit_predictor.locations import Location
import datetime
import json
import requests

#class to create and manage UI
class MainWindow:
    def __init__(self, master, satellites, predictCallback, updateCallback):
        self.master = master
        self.predictCallback = predictCallback
        self.updateCallback = updateCallback
        self.satCheckboxVars = []
        tk.Label(master, text='Satellites:').grid(column=0)
        for (intDes, name) in satellites.items(): #add a checkbox for each satellite
            var = tk.StringVar()
            var.set('0')
            checkbox = tk.Checkbutton(master, text=name, onvalue=intDes, offvalue='0', variable=var)
            checkbox.grid(column=0, sticky='W')
            self.satCheckboxVars.append(var)

        tk.Label(master, text='Parameters:').grid(column=2, row=0)
        tk.Label(master, text='Start date:').grid(column=1, row=1, sticky='E') #add start date entry
        self.dateEntry = DateEntry(master, date_pattern='dd/MM/yyyy')
        self.dateEntry.grid(column=2, row=1)

        def validateNumber(char): #validate that a character is a digit
            if char.isdigit():
                return True
            else:
                master.bell()
                return False
        vcmd = (master.register(validateNumber), '%S') #register validation function
        tk.Label(master, text='Days to predict for:').grid(column=1, row=2, sticky='E')
        self.daysEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=3) #days to predict for entry
        self.daysEntry.insert(0, '7')
        self.daysEntry.grid(column=2, row=2)

        tk.Label(master, text='Max elevation at least:').grid(column=1, row=3, sticky='E')
        self.elevationEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=2) #min MEL entry
        self.elevationEntry.insert(0, '10')
        self.elevationEntry.grid(column=2, row=3)

        tk.Label(master, text='After hour:').grid(column=1, row=4, sticky='E')
        self.afterHourEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=2) #minimum hour entry
        self.afterHourEntry.grid(column=2, row=4)
        self.afterHourEntry.insert(0, '0')
        tk.Label(master, text='Before hour:').grid(column=1, row=5, sticky='E')
        self.beforeHourEntry = tk.Entry(master, validate='key', vcmd=vcmd, width=2) #maximum hour entry
        self.beforeHourEntry.grid(column=2, row=5)
        self.beforeHourEntry.insert(0, '24')
        
        tk.Label(master, text='Location:').grid(column=1, row=6, sticky='E') #location entry
        self.locationEntry = tk.Entry(master)
        self.locationEntry.grid(column=2, row=6)
        def getLatLng(): #function to retrieve latitude and longitude from OSM based on user location
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
        tk.Button(text='Get coordinates', command=getLatLng).grid(column=2, row=7) #button to get coordinates from location

        tk.Label(text='Latitude:').grid(column=1, row=8, sticky='E')
        self.latEntry = tk.Entry(master, width=11) #observer latitude entry
        self.latEntry.grid(column=2, row=8)
        self.latEntry.insert(0, 51.4816546)
        tk.Label(text='Longitude:').grid(column=1, row=9, sticky='E')
        self.lngEntry = tk.Entry(master, width=11) #observer longitude entry
        self.lngEntry.grid(column=2, row=9)
        self.lngEntry.insert(0, -3.1791934)

        self.updateButton = tk.Button(self.master, text="Update orbits", command=self.updateCallback)
        self.updateButton.grid(column=3, row=1) #button to update TLEs
        self.predictButton = tk.Button(self.master, text="Predict passes", command=self.predictCallback)
        self.predictButton.grid(column=3, row=3) #button to predict passes

        master.grid_columnconfigure(0, minsize=150)
        master.grid_columnconfigure(2, minsize=150)
        master.grid_columnconfigure(3, minsize=150)

    #get start date for predictions set by user
    def getStartDate(self):
        return self.dateEntry.get_date()

    #get the number of days to predict for set by user
    def getDaysToPredictFor(self):
        return int(self.daysEntry.get())

    #get the minimum MEL set by the user
    def getMaxElevation(self):
        return int(self.elevationEntry.get())

    #get the observer latitude set by the user
    def getLatitude(self):
        return float(self.latEntry.get())

    #get the observer longitude set by the user
    def getLongitude(self):
        return float(self.lngEntry.get())

    #get the minimum hour of the day set by the user
    def getAfterHour(self):
        return int(self.afterHourEntry.get())

    #get the maximum hour of the day set by the user
    def getBeforeHour(self):
        return int(self.beforeHourEntry.get())

    #get the satellites selected by the user as a list of international designator strings
    def getSelectedSats(self):
        sats = []
        for c in self.satCheckboxVars:
            if c.get() != '0':
                sats.append(c.get())
        return sats

    #display a window with a table, a close button and a copy CSV button
    def displayTableWindow(self, table):
        newWindow = tk.Toplevel(self.master)
        newWindow.geometry("740x500")
        canvas = tk.Canvas(newWindow) #elements must be embedded in a canvas to get scrollbar
        frame = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(newWindow, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4,4), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        for row in range(len(table)): #add disabled entry for each table cell
            for col in range(len(table[0])):
                if row == 0: #first row is bold font
                    cell = tk.Entry(frame, width=11, font='Helevica 12 bold')
                else:
                    cell = tk.Entry(frame, width=11)
                cell.configure({"disabledforeground":"black"})
                cell.insert(tk.END, table[row][col])
                cell['state'] = tk.DISABLED
                cell.grid(row=row, column=col)
        csv = '\n'.join(map(lambda p: ','.join(p), table))
        def copyCsv(): #copy csv version of table
            newWindow.clipboard_clear()
            newWindow.clipboard_append(csv)
        tk.Button(newWindow, text='Copy CSV', command=copyCsv).pack(side="top")
        tk.Button(newWindow, text='Close', command=newWindow.destroy).pack(side="bottom")

    #enable/disable the predict and update buttons
    def setButtonsEnabled(self, enabled):
        if enabled:
            self.predictButton['state'] = tk.NORMAL
            self.updateButton['state'] = tk.NORMAL
        else:
            self.predictButton['state'] = tk.DISABLED
            self.updateButton['state'] = tk.DISABLED

#class to predict satellite passes and retrieve TLEs
class OrbitManager:
    def __init__(self, satellites):
        self.satellites = satellites

    #predict passes for specified satellits from specified start time. Returns them as a 2D array
    def predictPasses(self, intDesigs, startTime, daysToPredictFor, maxElevationAtLeast, lat, lng, minHour, maxHour):
        loc = Location("location", lat, lng, 10)
        endTime = startTime + datetime.timedelta(days=daysToPredictFor)
        endTime = endTime.replace(hour=0, minute=0)
        passes = []
        for intDes in intDesigs:
            predictor = get_predictor_from_tle_lines(self.__getTle(intDes))
            for p in predictor.passes_over(loc, startTime):
                if p.aos > endTime: #if passed end of prediction interval
                    break
                hour = p.max_elevation_date.astimezone(None).hour
                #if pass satisfies MEL and time requirements, add it to the table
                if p.max_elevation_deg >= maxElevationAtLeast and hour >= minHour and hour <=maxHour:
                    satName = self.satellites[intDes]
                    passDate = p.aos.astimezone(None).strftime('%d/%m/%y')
                    aosTime = p.aos.astimezone(None).strftime('%H:%M:%S')
                    maxElTime = p.max_elevation_date.astimezone(None).strftime('%H:%M:%S')
                    maxEl = round(p.max_elevation_deg, 1)
                    duration = str(round(p.duration_s//60))+':'+str(round(p.duration_s%60)).zfill(2)
                    passes.append([satName, passDate, aosTime, maxElTime, str(maxEl), duration, p.aos])
        passes = sorted(passes, key=lambda x: x[-1]) #sort by start time
        for p in passes:
            p.pop()
        passes.insert(0, ['Name', 'Date', 'Start time', 'Max el. time', 'Max el. (°)', 'Duration'])
        return passes

    #update TLEs for all satellites
    def updateOrbits(self):
        for intDes in self.satellites.keys():
            self.__updateTle(intDes)

    #download a TLE for a specific international designator from Celestrak
    def __getTle(self, intDes):
        with open('TLEs\\'+intDes+'.tle', 'r') as file:
            tle = file.read().split('\n')[:2]
            file.close()
        return tle

    #download a TLE for a specific international designator from Celestrak
    def __updateTle(self, intDes):
        req = requests.get('https://celestrak.com/satcat/tle.php?INTDES='+intDes)
        if req.status_code != 200:
            print ("Error fetching TLE for "+intDes)
            return
        tle = req.text.replace('\r','').split('\n')[1:3]
        with open('TLEs\\'+intDes+'.tle', 'w') as file:
            file.write('\n'.join(tle))
            file.close()
            
#class to actually run the application
class Controller:
    def __init__(self):
        with open('satellites.json', 'r') as file: #load satellites from file
            satellites = json.loads(file.read())
            file.close()
        root = tk.Tk()
        defaultFont = tk.font.nametofont("TkDefaultFont")
        defaultFont.configure(size=12)
        root.option_add("*Font", defaultFont)
        self.view = MainWindow(root, satellites, self.predictPressed, self.updatePressed)
        self.model = OrbitManager(satellites)
        root.mainloop()

    #callback when predict button pressed
    def predictPressed(self):
        #if start day is today, set start time to now, otherwise set it to 00:00
        if self.view.getStartDate() == datetime.datetime.today().date():
            startTime = datetime.datetime.utcnow()
        else:
            midnight = datetime.datetime.min.time()
            startTime = datetime.datetime.combine(self.view.getStartDate(), midnight)
        passes = self.model.predictPasses(self.view.getSelectedSats(), startTime, self.view.getDaysToPredictFor(),
                                          self.view.getMaxElevation(), self.view.getLatitude(), self.view.getLongitude(),
                                          self.view.getAfterHour(), self.view.getBeforeHour())
        self.view.displayTableWindow(passes)

    #callback when update button pressed
    def updatePressed(self):
        self.view.setButtonsEnabled(False)
        self.model.updateOrbits()
        self.view.setButtonsEnabled(True)
    
c = Controller()
