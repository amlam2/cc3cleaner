#!/usr/bin/env python
# coding=utf-8

# подключение необходимых модулей
import os
import wx
import time
import zipfile
import shutil
from liblore import opsDict
from re import compile, split

# Глобальные переменные
###############################################################################
# каталоги программы
###############################################################################
programmDir = os.path.split(os.getcwd())[0]
binDir  = os.path.join(programmDir, 'bin')
outDir  = os.path.join(programmDir, 'out')
picsDir = os.path.join(programmDir, 'pics')
tempDir = os.path.join(programmDir, 'temp')
sendDir = '\\\\WXFR\\FTP\\CC2\\%s\\OUT'

windowTitle     = u'Очистка СС3'       # заголовок окна
applicationIcon = os.path.join(picsDir, 'cc3cleaner.png')  # иконка приложения

# подключение диалогов
import result       # диалог проверки списка ПО и отправки на ОПС

###############################################################################
# Начало класса окна приложения (CC3CleanerFrame)
#
class CC3CleanerFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, *args, **kwds)

        #######################################################################
        # создание виджетов
        #
        self.panel = wx.Panel(self, -1)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        ### > статические подсказки
        self.txt1 = wx.StaticText(self.panel, -1,
            u'''Программа генерирует корректирующий файл СС3 для удаления стикеров
            из списка ПО во вкладке "Отправка в центр"''')
        self.txt2 = wx.StaticText(self.panel, -1, u"Текст, содержащий стикеры ПО:")
        ###

        ### > поле ввода стикеров ПО
        self.input = wx.TextCtrl(self.panel, -1, size=(-1, -1),
                    style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.OnNextBtnEnable, self.input)
        ###

        ### > линия
        self.line = wx.StaticLine(self.panel, -1, size=(385, 3))
        ###

        ### > кнопка "Далее >>"
        self.buttonGenerate = wx.Button(self.panel, -1, label=u"Далее >>", size=(100, 25))
        self.buttonGenerate.SetToolTipString(u"Проверьте правильность введённой информации")
        self.Bind(wx.EVT_BUTTON, self.OnGenerate, self.buttonGenerate)
        ###

        ### > кнопка "Закрыть"
        self.buttonClose = wx.Button(self.panel, -1, label=u"Закрыть", size=(100, 25))
        self.buttonClose.SetToolTipString(u"Выйти из программы")
        self.Bind(wx.EVT_BUTTON, self.OnQuit, self.buttonClose)
        ###

        #
        #######################################################################

        self.__do_layout()
        self.__set_properties()
        #self.__do_layout()

    # --- начальные установки -------------------------------------------------
    def __set_properties(self):
        self.SetTitle(windowTitle)
        self.SetSize((410, 495))
        self.Centre()

        ### > установка иконки приложения
        self.SetIcon(wx.IconFromBitmap(wx.Bitmap(applicationIcon)))
        ###

        ### > создание строки состояния
        #self.CreateStatusBar()
        ###

        ### > начальные установки элементов интерфейса
        self.input.SetEditable(True)
        self.buttonGenerate.Disable()
        self.buttonClose.SetFocus()
        ###

    # --- размещение виджетов на сайзерах -------------------------------------
    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)

        vSizer.Add(self.txt1, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vSizer.Add(self.txt2, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vSizer.Add(self.input, 1, wx.EXPAND | wx.ALL, 5)
        vSizer.Add(self.line, 0, wx.ALIGN_CENTER | wx.ALL, 3)

        hSizer.Add(self.buttonGenerate, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        hSizer.Add(self.buttonClose, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        vSizer.Add(hSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.panel.SetSizer(vSizer)

        mainSizer.Add(self.panel, 1, wx.EXPAND, 0)

        self.SetSizer(mainSizer)

        mainSizer.Fit(self)

        self.Layout()

    ###########################################################################
    # Функции-обработчики событий
    ###########################################################################

    # --- обработка закрытия окна програмы крестиком --------------------------
    def OnCloseWindow(self, event):
        self.Destroy()

    # --- обработка выхода из программы ---------------------------------------
    def OnQuit(self, event):
        self.Close()

    # --- обработка события вставки текста в поле ввода -----------------------
    ''' при отсутствии текста в поле ввода кнопка "Далее >>" недоступна,
        при наличии - становится доступной '''
    def OnNextBtnEnable(self, event):
        if len(event.GetString()) != 0:
            self.buttonGenerate.Enable()
        else:
            self.buttonGenerate.Disable()

    # --- обработка нажатия кнопки "Далее >>" ---------------------------------
    ''' верификация списка стикеров, генерация корректирующего транспортного
        файла СС3, отправка на выбранное ОПС '''
    def OnGenerate(self, event):
        '''
        RR025456852BY
        CV236478951LT#F8F7E7#FFFFFF
        PZ123852456BY
        '''

        ### > сформировать список стикеров, обработав текст поля ввода
        separators = r'\W'
        stickerList = split(separators, self.input.GetValue().upper())#.encode('cp1251'))
        # убрать пустые элементы списка
        # stickerList = [sticker for sticker in stickerList if len(sticker) != 0]
        ###

        ### > проверка на внешнее соответствие стикера почтовым нормам
        pattern1 = compile(r'^[A-Z]{2}?[0-9]{9}?[A-Z]{2}$')
        pattern2 = compile(r'^[A-Z]{3}?[0-9]{8}?[A-Z]{2}$')
        for sticker in stickerList[:]:
            if len(sticker) != 13:
                stickerList.remove(sticker)
            elif (pattern1.search(sticker) is None) and (pattern2.search(sticker) is None):
                wx.MessageBox(u"В идентификаторе %s ошибка. Удалён из списка." % sticker.decode('cp1251'),
                                    windowTitle, wx.OK | wx.ICON_EXCLAMATION, self)
                stickerList.remove(sticker)
        ###

        if len(stickerList) == 0:
            wx.MessageBox(u"Нет стикеров! Проверьре правильность ввода!",
                                windowTitle, wx.OK | wx.ICON_EXCLAMATION, self)
        else:
            ### > отображение диалога проверки списка стикеров ПО и отправки на ОПС
            resultDlg = result.Result(stickerList, CC3CleanerFrame)
            if (resultDlg.ShowModal() == wx.ID_OK):
                ### > получение данных из диалога
                selectList = list(resultDlg.checkListBox.GetChecked())
                whom = resultDlg.comboBox.GetValue()
                ###

                ### > генератор списка отмеченных стикеров
                stickerList = [stickerList[i] for i in selectList]
                ###

                ### > для списка стикеров ПО сгенерировать xml-файл с командой "Р"
                fileName = '401_' + time.strftime('%y%m%d%H%M%S', time.localtime())
                xmlFileName = fileName + '.xml'
                xmlFile = open(xmlFileName, 'w')
                xmlFile.write('<?xml version="1.0" encoding="windows-1251"?>\n')
                xmlFile.write('<CC2 ver="1" APM="3.0.4.15" DB="3.0.4.6">\n')
                xmlFile.write(2*' ' + '<P>\n')

                for sticker in stickerList:
                    if sticker[0] == 'P' or sticker[0] == 'А':
                        if sticker[:2] == 'PE':
                            tagType = 'Mail'
                        else:
                            tagType = 'Bag'
                    else:
                        tagType = 'Mail'
                    xmlFile.write(4*' ' + '<' + tagType + ' id="' + sticker + '"></' + tagType + '>\n')

                xmlFile.write(2*' ' + '</P>\n')
                xmlFile.write('</CC2>\n')
                xmlFile.close()
                ###

                ### > упаковать сгенерированный xml-файл
                arcFileName = fileName + '.cc2'
                zf = zipfile.ZipFile(arcFileName, 'w', allowZip64 = True)
                zf.write(xmlFileName, os.path.basename(xmlFileName), zipfile.ZIP_DEFLATED)
                zf.close()
                os.remove(xmlFileName)      # удалить xml-файл
                ###

                ### > отправить корректирующий транспортный файл СС3 на ОПС
                if whom != u'':
                    for index in opsDict:
                        if whom == opsDict[index].get('nameOPS'):
                            ops = index[-3:]
                            break
                    shutil.move(arcFileName, os.path.join(sendDir % ops, arcFileName))
                    wx.MessageBox(u"Корректирующий файл СС3\nуспешно отправлен ОПС " + whom,
                                        windowTitle, wx.OK | wx.ICON_INFORMATION, self)
                else:
                    shutil.move(arcFileName, os.path.join(outDir, arcFileName))
                    wx.MessageBox(u"Корректирующий файл СС3\nнаходится в каталоге 'out' программы",
                                        windowTitle, wx.OK | wx.ICON_INFORMATION, self)

                ###
            resultDlg.Destroy()
        ###

#
# Конец класса CC3CleanerFrame
###############################################################################


###############################################################################
# Начало класса приложения (CC3CleanerApp)
#
class CC3CleanerApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = CC3CleanerFrame(None, -1, "")
        self.SetTopWindow(frame)
        frame.Show()
        return True
#
# Конец класса CC3CleanerApp
###############################################################################

def main():
    os.chdir(tempDir)
    app = CC3CleanerApp(0)
    app.MainLoop()

if __name__ == "__main__":
    main()
