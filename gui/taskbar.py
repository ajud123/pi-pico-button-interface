import wx
import wx.adv
from wx.adv import TaskBarIcon
import gui
import gui.bboxGUI

class TaskIcon(TaskBarIcon):
    
    def __init__(self, frame: gui.bboxGUI.ButtonBoxGUI):
        TaskBarIcon.__init__(self)
        self.frame = frame
        
        img = wx.Image("icon.png", wx.BITMAP_TYPE_ANY)
        bmp = wx.Bitmap(img)
        # bmp = wx.BitmapFromImage(img)
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(bmp)
        
        self.SetIcon(self.icon)
        self.Bind(wx.adv.EVT_TASKBAR_CLICK, self.OnTaskBarRightClick)
        # self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=2)
        # self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)


 
    #----------------------------------------------------------------------
    def OnTaskBarActivate(self, evt):
        pass
 
    #----------------------------------------------------------------------
    def OnTaskBarClose(self, evt):
        self.frame.Close()
 
    #----------------------------------------------------------------------
    def OnTaskBarRightClick(self, evt):
        if(self.frame.Shown):
            self.frame.Hide()
        else:
            self.frame.Show()
            self.frame.Restore()
