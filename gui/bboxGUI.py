# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6-dirty)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class ButtonBoxGUI
###########################################################################

class ButtonBoxGUI ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Button Box Settings"), pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.portPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        portSizer = wx.StaticBoxSizer( wx.StaticBox( self.portPanel, wx.ID_ANY, _(u"Serial ports") ), wx.VERTICAL )

        self.c_onlyDescription = wx.CheckBox( portSizer.GetStaticBox(), wx.ID_ANY, _(u"Display only ports with descriptions"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.c_onlyDescription.SetValue(True)
        portSizer.Add( self.c_onlyDescription, 0, wx.ALL, 5 )

        portComboConnect = wx.BoxSizer( wx.HORIZONTAL )

        portsChoices = [ _(u"aaa"), _(u"bbb") ]
        self.ports = wx.ComboBox( portSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, portsChoices, 0 )
        portComboConnect.Add( self.ports, 0, wx.ALL, 5 )

        self.b_serialConnect = wx.Button( portSizer.GetStaticBox(), wx.ID_ANY, _(u"Connect"), wx.DefaultPosition, wx.DefaultSize, 0 )
        portComboConnect.Add( self.b_serialConnect, 0, wx.ALL, 5 )


        portSizer.Add( portComboConnect, 1, wx.EXPAND, 5 )

        self.t_err = wx.StaticText( portSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.t_err.Wrap( -1 )

        portSizer.Add( self.t_err, 0, wx.ALL, 5 )


        self.portPanel.SetSizer( portSizer )
        self.portPanel.Layout()
        portSizer.Fit( self.portPanel )
        bSizer1.Add( self.portPanel, 1, wx.EXPAND |wx.ALL, 5 )

        self.modulePanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        moduleSizer = wx.StaticBoxSizer( wx.StaticBox( self.modulePanel, wx.ID_ANY, _(u"Modules") ), wx.VERTICAL )

        self.b_refreshModules = wx.Button( moduleSizer.GetStaticBox(), wx.ID_ANY, _(u"Refresh"), wx.DefaultPosition, wx.DefaultSize, 0 )
        moduleSizer.Add( self.b_refreshModules, 0, wx.ALL, 5 )

        moduleListChoices = []
        self.moduleList = wx.CheckListBox( moduleSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, moduleListChoices, 0 )
        moduleSizer.Add( self.moduleList, 0, wx.ALL, 5 )


        self.modulePanel.SetSizer( moduleSizer )
        self.modulePanel.Layout()
        moduleSizer.Fit( self.modulePanel )
        bSizer1.Add( self.modulePanel, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass


