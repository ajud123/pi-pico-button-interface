import asyncio
import json
import os
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import wx
from serialmgr import SerialManager
from gui.bboxGUI import ButtonBoxGUI
from gui.taskbar import TaskIcon
from bboxmgr import ButtonBoxManager

class MainApp(WxAsyncApp):
    def OnInit(self):
        window = ButtonBoxGUI(None)
        self.window = window
        self.started = False
        self._enabledModules = []

        window.ports.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.RefreshPorts)
        self.RefreshPorts(None)
        window.b_serialConnect.Bind(wx.EVT_BUTTON, self.Connect)

        self.RefreshModules()
        window.b_refreshModules.Bind(wx.EVT_BUTTON, self.RefreshModules)

        window.Show(True) 

        self.taskbar = TaskIcon(window)
        window.Bind(wx.EVT_CLOSE, self.onClose)

        return True
    
    def onClose(self, event):
        self.taskbar.Destroy()
        self.Destroy()

    def Connect(self, arg1):
        window = self.window
        if not self.started:
            port = str(self.window.ports.Value).split('-')[0].strip()
            if port != '':
                window.t_err.Label = ""
                loop = asyncio.get_running_loop()
                loop.create_task(ButtonBoxManager.Start(port))
                self.window.b_serialConnect.Label = "Disconnect"
                self.started = True
                # print(f"make connection to {port}")
            else:
                window.t_err.Label = "Please select a port."
        else:
            ButtonBoxManager.Stop()
            self.started = False
            self.window.b_serialConnect.Label = "Connect"
    
    def RefreshPorts(self, arg1 = None):
        print("refreshing ports")
        window = self.window
        window.ports.Clear()
        onlyDesc: bool = window.c_onlyDescription.Value
        ports = SerialManager.GetPorts()
        for port in ports:
            if onlyDesc and port.description and port.description != "n/a":
                window.ports.Append(f"{port.device} - {port.description}")
        pass

    def RefreshModules(self, arg1 = None):
        filenames = next(os.walk("modules"), (None, None, []))[2]
        filemap = {}
        self.window.moduleList.Clear()

        with open('modules.json', 'r') as f:
            modules = json.load(f)
            for module in modules:
                if not module.endswith(".py"):
                    filemap[module] = True
                    module += ".py"
                else:
                    filemap[module[0:-3]] = True

        for filename in filenames:
            if filename.endswith(".py"):
                self.window.moduleList.Append(filename[0:-3])
                if filename[0:-3] in filemap:
                    self.window.moduleList.SetCheckedItems([len(self.window.moduleList.GetStrings())-1])
                    ButtonBoxManager.modules.append(filename)


        self.window.moduleList.SetCheckedStrings(filemap)

        pass

        

    pass

def main_async():
    application = MainApp(0)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.MainLoop())

main_async()