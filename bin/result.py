#coding=utf-8

import wx
from cc3cleaner import applicationIcon
from cc3cleaner import windowTitle
from liblore import opsDict

msgBoxTitle = u"Проверка и отправка"
windowTitle += u" [ %s ]" % msgBoxTitle

###############################################################################
# Начало класса диалога проверки списка стикеров ПО и отправки на ОПС (Result)
#
class Result(wx.Dialog):
    def __init__(self, stickerList, parent):
        self.stickerList = stickerList
        wx.Dialog.__init__(self, None, -1, windowTitle, size=(-1, 450))

        ### > иконка приложения
        self.SetIcon(wx.IconFromBitmap(wx.Bitmap(applicationIcon)))
        ###

        ### > формирование списка ОПС
        allOPSList = []
        for index in opsDict:
            allOPSList.append(opsDict[index].get('nameOPS'))
        allOPSList.sort()

        ### > надпись на форме
        txt = wx.StaticText(self, -1, u"Уточните список стикеров ПО:")
        ###

        ### > окно проверки списка стикеров ПО
        self.checkListBox = wx.CheckListBox(self, -1, (5, 5), (-1, -1),\
                                self.stickerList, wx.LB_SINGLE)
        self.checkListBox.SetChecked(range(len(self.stickerList)))
        ###

        ### > галочка отправлять или нет
        self.checkBox = wx.CheckBox(self, -1, u"отправить на ОПС:")
        self.checkBox.SetValue(False)
        self.checkBox.Bind(wx.EVT_CHECKBOX, self.onToggleCheckBox)
        ###

        ### > выбор ОПС
        self.comboBox = wx.ComboBox(self, 500, u'', (90, 50),
                                  (150, -1), allOPSList,
                                  wx.CB_DROPDOWN|wx.CB_READONLY|wx.TE_PROCESS_ENTER)
        self.comboBox.SetToolTipString(u"Выберите ОПС")
        self.comboBox.Disable()
        ###

        ### > линия
        line = wx.StaticLine(self, -1, pos=(-1, -1), size=(380, 3))
        ###

        ### > кнопка "ОК"
        self.okToolTip = u"Сгенерировать"
        self.okButton = wx.Button(self, wx.ID_OK, u"ОК", size =(100, 25))
        self.okButton.SetToolTipString(self.okToolTip)
        self.okButton.SetFocus()
        ###

        ### > кнопка "Отмена"
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, u"Отмена", size =(100, 25))
        self.cancelButton.SetToolTipString(u"Закрыть диалог")
        ###

        ### > размещение виджетов на сайзерах
        hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer1.Add(self.checkBox, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        hsizer1.Add(self.comboBox, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(self.okButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        hsizer2.Add(self.cancelButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(txt, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vsizer.Add(self.checkListBox, 1, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(hsizer1, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        vsizer.Add(line, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        vsizer.Add(hsizer2, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        ###

        self.SetSizer(vsizer)
        self.Layout()

    # --- обработка события изменения состояния чекбокса ----------------------
    def onToggleCheckBox(self, event):
        if event.GetInt():
            self.comboBox.Enable()
            self.okToolTip = u"Сгенерировать и отправить"
            self.okButton.SetToolTipString(self.okToolTip)
        else:
            self.comboBox.SetValue(u'')
            self.comboBox.Disable()
            self.okToolTip = u"Сгенерировать"
            self.okButton.SetToolTipString(self.okToolTip)
#
# Конец класса диалога Result
###############################################################################
