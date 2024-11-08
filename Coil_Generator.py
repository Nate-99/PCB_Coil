import wx
import numpy as np
import ezdxf

class CoilGenerator(wx.Frame):
    def __init__(self, parent, title):
        super(CoilGenerator, self).__init__(parent, title=title, size=(400, 500))
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Form der Spule
        hbox_form = wx.BoxSizer(wx.HORIZONTAL)
        lbl_form = wx.StaticText(panel, label='Form der Spule:')
        hbox_form.Add(lbl_form, flag=wx.RIGHT, border=8)
        self.choice_form = wx.ComboBox(panel, choices=['rund', 'eckig'], style=wx.CB_READONLY)
        self.choice_form.SetSelection(0)
        hbox_form.Add(self.choice_form, proportion=1)
        vbox.Add(hbox_form, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Anzahl der Windungen
        hbox_turns = wx.BoxSizer(wx.HORIZONTAL)
        lbl_turns = wx.StaticText(panel, label='Anzahl der Windungen:')
        hbox_turns.Add(lbl_turns, flag=wx.RIGHT, border=8)
        self.txt_turns = wx.TextCtrl(panel)
        hbox_turns.Add(self.txt_turns, proportion=1)
        vbox.Add(hbox_turns, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Durchmesser
        hbox_diameter = wx.BoxSizer(wx.HORIZONTAL)
        lbl_diameter = wx.StaticText(panel, label='Durchmesser (mm):')
        hbox_diameter.Add(lbl_diameter, flag=wx.RIGHT, border=8)
        self.txt_diameter = wx.TextCtrl(panel)
        hbox_diameter.Add(self.txt_diameter, proportion=1)
        vbox.Add(hbox_diameter, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Abstand zwischen den Windungen
        hbox_spacing = wx.BoxSizer(wx.HORIZONTAL)
        lbl_spacing = wx.StaticText(panel, label='Abstand zwischen Windungen (mm):')
        hbox_spacing.Add(lbl_spacing, flag=wx.RIGHT, border=8)
        self.txt_spacing = wx.TextCtrl(panel)
        hbox_spacing.Add(self.txt_spacing, proportion=1)
        vbox.Add(hbox_spacing, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Kupferbreite
        hbox_width = wx.BoxSizer(wx.HORIZONTAL)
        lbl_width = wx.StaticText(panel, label='Kupferbreite (mm):')
        hbox_width.Add(lbl_width, flag=wx.RIGHT, border=8)
        self.txt_width = wx.TextCtrl(panel)
        hbox_width.Add(self.txt_width, proportion=1)
        vbox.Add(hbox_width, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Zeichnen und Speichern Buttons
        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn_draw = wx.Button(panel, label='Spule zeichnen')
        btn_save = wx.Button(panel, label='Spule speichern')
        hbox_buttons.Add(btn_draw)
        hbox_buttons.Add(btn_save, flag=wx.LEFT | wx.BOTTOM, border=5)
        vbox.Add(hbox_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        # Event-Bindings
        btn_draw.Bind(wx.EVT_BUTTON, self.OnDraw)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSave)

        panel.SetSizer(vbox)

    def OnDraw(self, event):
        params = self.GetParameters()
        if params:
            self.DrawCoil(params)

    def OnSave(self, event):
        params = self.GetParameters()
        if params:
            with wx.FileDialog(self, "Spule speichern", wildcard="DXF files (*.dxf)|*.dxf",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                pathname = fileDialog.GetPath()
                self.SaveAsDXF(params, pathname)

    def GetParameters(self):
        try:
            form = self.choice_form.GetValue()
            turns = int(self.txt_turns.GetValue())
            diameter = float(self.txt_diameter.GetValue())
            spacing = float(self.txt_spacing.GetValue())
            width = float(self.txt_width.GetValue())

            if turns <= 0 or diameter <= 0 or spacing < 0 or width <= 0:
                wx.MessageBox('Bitte geben Sie gültige positive Werte ein.', 'Fehler', wx.OK | wx.ICON_ERROR)
                return None

            params = {
                'form': form,
                'turns': turns,
                'diameter': diameter,
                'spacing': spacing,
                'width': width
            }
            return params
        except ValueError:
            wx.MessageBox('Bitte geben Sie gültige numerische Werte ein.', 'Fehler', wx.OK | wx.ICON_ERROR)
            return None

    def DrawCoil(self, params):
        # Neues Fenster zum Zeichnen der Spule
        draw_frame = CoilDrawFrame(None, 'Spule', params)
        draw_frame.Show()

    def SaveAsDXF(self, params, filename):
        form = params['form']
        turns = params['turns']
        diameter = params['diameter']
        spacing = params['spacing']
        width = params['width']

        doc = ezdxf.new(dxfversion='R2010')
        msp = doc.modelspace()

        if form == 'rund':
            for i in range(turns):
                radius_outer = (diameter / 2) + i * (spacing + width)
                radius_inner = radius_outer - width

                # Äußerer Kreis
                msp.add_circle((0, 0), radius_outer)
                # Innerer Kreis (falls positiv)
                if radius_inner > 0:
                    msp.add_circle((0, 0), radius_inner)
        elif form == 'eckig':
            for i in range(turns):
                size_outer = diameter + 2 * i * (spacing + width)
                size_inner = size_outer - 2 * width

                # Äußeres Quadrat
                points_outer = [
                    (-size_outer / 2, -size_outer / 2),
                    (size_outer / 2, -size_outer / 2),
                    (size_outer / 2, size_outer / 2),
                    (-size_outer / 2, size_outer / 2),
                    (-size_outer / 2, -size_outer / 2)
                ]
                msp.add_lwpolyline(points_outer)

                # Inneres Quadrat (falls Größe positiv)
                if size_inner > 0:
                    points_inner = [
                        (-size_inner / 2, -size_inner / 2),
                        (size_inner / 2, -size_inner / 2),
                        (size_inner / 2, size_inner / 2),
                        (-size_inner / 2, size_inner / 2),
                        (-size_inner / 2, -size_inner / 2)
                    ]
                    msp.add_lwpolyline(points_inner)

        try:
            doc.saveas(filename)
            wx.MessageBox('Spule erfolgreich als DXF gespeichert.', 'Erfolg', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f'Fehler beim Speichern der Datei:\n{e}', 'Fehler', wx.OK | wx.ICON_ERROR)

class CoilDrawFrame(wx.Frame):
    def __init__(self, parent, title, params):
        super(CoilDrawFrame, self).__init__(parent, title=title, size=(600, 600))
        self.params = params
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Centre()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        self.DrawCoil(gc, self.params)

    def DrawCoil(self, gc, params):
        form = params['form']
        turns = params['turns']
        diameter = params['diameter']
        spacing = params['spacing']
        width = params['width']

        # Skalierungsfaktor für die Darstellung
        scale = 5  # Passen Sie diesen Wert an, um die Größe der Darstellung zu ändern

        # Mittelpunkt der Zeichnung
        w, h = self.GetSize()
        center_x = w / 2
        center_y = h / 2

        # Stift für die Zeichnung
        pen = wx.Pen(wx.Colour(0, 0, 0), 1)
        gc.SetPen(pen)

        if form == 'rund':
            for i in range(turns):
                radius_outer = ((diameter / 2) + i * (spacing + width)) * scale
                radius_inner = radius_outer - width * scale

                # Äußerer Kreis
                gc.DrawEllipse(center_x - radius_outer, center_y - radius_outer, radius_outer * 2, radius_outer * 2)

                # Innerer Kreis (falls positiv)
                if radius_inner > 0:
                    gc.DrawEllipse(center_x - radius_inner, center_y - radius_inner, radius_inner * 2, radius_inner * 2)
        elif form == 'eckig':
            for i in range(turns):
                size_outer = (diameter + 2 * i * (spacing + width)) * scale
                size_inner = size_outer - 2 * width * scale

                # Äußeres Quadrat
                gc.DrawRectangle(center_x - size_outer / 2, center_y - size_outer / 2, size_outer, size_outer)

                # Inneres Quadrat (falls Größe positiv)
                if size_inner > 0:
                    gc.DrawRectangle(center_x - size_inner / 2, center_y - size_inner / 2, size_inner, size_inner)

if __name__ == '__main__':
    app = wx.App()
    CoilGenerator(None, title='Spulengenerator')
    app.MainLoop()