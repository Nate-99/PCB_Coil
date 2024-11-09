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
        self.txt_turns = wx.TextCtrl(panel, value='10')
        hbox_turns.Add(self.txt_turns, proportion=1)
        vbox.Add(hbox_turns, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Durchmesser
        hbox_diameter = wx.BoxSizer(wx.HORIZONTAL)
        lbl_diameter = wx.StaticText(panel, label='Durchmesser (mm):')
        hbox_diameter.Add(lbl_diameter, flag=wx.RIGHT, border=8)
        self.txt_diameter = wx.TextCtrl(panel, value='30')
        hbox_diameter.Add(self.txt_diameter, proportion=1)
        vbox.Add(hbox_diameter, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Abstand zwischen den Windungen
        hbox_spacing = wx.BoxSizer(wx.HORIZONTAL)
        lbl_spacing = wx.StaticText(panel, label='Abstand zwischen Windungen (mm):')
        hbox_spacing.Add(lbl_spacing, flag=wx.RIGHT, border=8)
        self.txt_spacing = wx.TextCtrl(panel, value='3.127')
        hbox_spacing.Add(self.txt_spacing, proportion=1)
        vbox.Add(hbox_spacing, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Kupferbreite
        hbox_width = wx.BoxSizer(wx.HORIZONTAL)
        lbl_width = wx.StaticText(panel, label='Kupferbreite (mm):')
        hbox_width.Add(lbl_width, flag=wx.RIGHT, border=8)
        self.txt_width = wx.TextCtrl(panel, value='0.2')
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
            # Parameter für die archimedische Spirale
            a = diameter / 2
            b = (spacing + width) / (2 * np.pi)
            max_theta = turns * 2 * np.pi
            theta = np.linspace(0, max_theta, num=1000)
            r = a + b * theta
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            points = list(zip(x, y))
            msp.add_polyline2d(points)
        elif form == 'eckig':
            sides = 4  
            angle = 2 * np.pi / sides
            steps = turns * sides
            directions = np.array([
                [np.cos(i * angle), np.sin(i * angle)] for i in range(sides)
            ])
            directions[:, 1] *= -1
            # Schrittlänge erhöhen nach jeder halben Umdrehung
            increment_steps = sides // 2 if sides % 2 == 0 else sides
            step_lengths = np.zeros(steps)
            step_length = diameter / 2
            for i in range(steps):
                if i % increment_steps == 0 and i > 0:
                    step_length += (spacing + width)
                step_lengths[i] = step_length
            moves = directions[np.arange(steps) % sides] * step_lengths[:, np.newaxis]
            positions = np.vstack((np.zeros(2), np.cumsum(moves, axis=0)))
            points = [tuple(pos) for pos in positions]
            msp.add_polyline2d(points)

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
        scale = 5  # Skalierungsfaktor für die Darstellung
        w, h = self.GetSize()
        center_x = w / 2
        center_y = h / 2
        pen = wx.Pen(wx.Colour(0, 0, 0), 1)
        gc.SetPen(pen)

        if form == 'rund':
            # Parameter für die archimedische Spirale
            a = (diameter / 2) * scale
            b = ((spacing + width) / (2 * np.pi)) * scale
            max_theta = turns * 2 * np.pi
            theta = np.linspace(0, max_theta, num=1000)
            r = a + b * theta
            x = center_x + r * np.cos(theta)
            y = center_y + r * np.sin(theta)
            # Pfad zeichnen
            path = gc.CreatePath()
            path.MoveToPoint(x[0], y[0])
            for xi, yi in zip(x[1:], y[1:]):
                path.AddLineToPoint(xi, yi)
            gc.StrokePath(path)
        elif form == 'eckig':
            sides = 4
            angle = 2 * np.pi / sides
            steps = turns * sides
            directions = np.array([
                [np.cos(i * angle), np.sin(i * angle)] for i in range(sides)
            ])
            directions[:, 1] *= -1
            # Schrittlänge erhöhen nach jeder halben Umdrehung
            increment_steps = sides // 2 if sides % 2 == 0 else sides
            step_lengths = np.zeros(steps)
            step_length = (diameter / 2) * scale
            for i in range(steps):
                if i % increment_steps == 0 and i > 0:
                    step_length += (spacing + width) * scale
                step_lengths[i] = step_length
            moves = directions[np.arange(steps) % sides] * step_lengths[:, np.newaxis]
            positions = np.vstack((np.zeros(2), np.cumsum(moves, axis=0)))
            positions += np.array([center_x, center_y])
            # Pfad zeichnen
            path = gc.CreatePath()
            path.MoveToPoint(*positions[0])
            for pos in positions[1:]:
                path.AddLineToPoint(*pos)
            gc.StrokePath(path)

if __name__ == '__main__':
    app = wx.App()
    CoilGenerator(None, title='Spulengenerator')
    app.MainLoop()