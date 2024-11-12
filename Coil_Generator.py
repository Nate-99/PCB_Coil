import wx
import numpy as np
import ezdxf

class CoilGenerator(wx.Frame):
    def __init__(self, parent, title):
        super(CoilGenerator, self).__init__(parent, title=title, size=(400, 600))
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
        self.choice_form = wx.ComboBox(panel, choices=['rund', 'eckig', 'segment'], style=wx.CB_READONLY)
        self.choice_form.SetSelection(0)
        hbox_form.Add(self.choice_form, proportion=1)
        vbox.Add(hbox_form, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Event-Binding für die Auswahländerung
        self.choice_form.Bind(wx.EVT_COMBOBOX, self.OnFormChange)

        # Anzahl der Windungen
        self.hbox_turns = wx.BoxSizer(wx.HORIZONTAL)
        lbl_turns = wx.StaticText(panel, label='Anzahl der Windungen:')
        self.hbox_turns.Add(lbl_turns, flag=wx.RIGHT, border=8)
        self.txt_turns = wx.TextCtrl(panel, value='10')
        self.hbox_turns.Add(self.txt_turns, proportion=1)
        vbox.Add(self.hbox_turns, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Durchmesser (nur für 'rund' und 'eckig')
        self.hbox_diameter = wx.BoxSizer(wx.HORIZONTAL)
        lbl_diameter = wx.StaticText(panel, label='Durchmesser (mm):')
        self.hbox_diameter.Add(lbl_diameter, flag=wx.RIGHT, border=8)
        self.txt_diameter = wx.TextCtrl(panel, value='30')
        self.hbox_diameter.Add(self.txt_diameter, proportion=1)
        vbox.Add(self.hbox_diameter, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Winkel (nur für 'segment')
        self.hbox_angle = wx.BoxSizer(wx.HORIZONTAL)
        lbl_angle = wx.StaticText(panel, label='Winkel (Grad):')
        self.hbox_angle.Add(lbl_angle, flag=wx.RIGHT, border=8)
        self.txt_angle = wx.TextCtrl(panel, value='90')
        self.hbox_angle.Add(self.txt_angle, proportion=1)
        vbox.Add(self.hbox_angle, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Innerer Radius (nur für 'segment')
        self.hbox_inner_radius = wx.BoxSizer(wx.HORIZONTAL)
        lbl_inner_radius = wx.StaticText(panel, label='Innerer Radius (mm):')
        self.hbox_inner_radius.Add(lbl_inner_radius, flag=wx.RIGHT, border=8)
        self.txt_inner_radius = wx.TextCtrl(panel, value='10')
        self.hbox_inner_radius.Add(self.txt_inner_radius, proportion=1)
        vbox.Add(self.hbox_inner_radius, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Äußerer Radius (nur für 'segment')
        self.hbox_outer_radius = wx.BoxSizer(wx.HORIZONTAL)
        lbl_outer_radius = wx.StaticText(panel, label='Äußerer Radius (mm):')
        self.hbox_outer_radius.Add(lbl_outer_radius, flag=wx.RIGHT, border=8)
        self.txt_outer_radius = wx.TextCtrl(panel, value='20')
        self.hbox_outer_radius.Add(self.txt_outer_radius, proportion=1)
        vbox.Add(self.hbox_outer_radius, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Abstand zwischen den Windungen
        hbox_spacing = wx.BoxSizer(wx.HORIZONTAL)
        lbl_spacing = wx.StaticText(panel, label='Abstand zwischen Windungen (mm):')
        hbox_spacing.Add(lbl_spacing, flag=wx.RIGHT, border=8)
        self.txt_spacing = wx.TextCtrl(panel, value='0.2')
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

        # Initiale Sichtbarkeit der Felder einstellen
        self.OnFormChange(None)

    def OnFormChange(self, event):
        form = self.choice_form.GetValue()
        is_segment = (form == 'segment')

        # Sichtbarkeit der Felder einstellen
        self.hbox_angle.Show(is_segment)
        self.hbox_inner_radius.Show(is_segment)
        self.hbox_outer_radius.Show(is_segment)
        self.hbox_diameter.Show(not is_segment)

        # Layout aktualisieren
        self.Layout()

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
            spacing = float(self.txt_spacing.GetValue())
            width = float(self.txt_width.GetValue())

            if spacing < 0 or width <= 0:
                wx.MessageBox('Bitte geben Sie gültige positive Werte für Abstand und Kupferbreite ein.', 'Fehler', wx.OK | wx.ICON_ERROR)
                return None

            params = {
                'form': form,
                'spacing': spacing,
                'width': width
            }

            if form == 'segment':
                angle_degrees = float(self.txt_angle.GetValue())
                inner_radius = float(self.txt_inner_radius.GetValue())
                outer_radius = float(self.txt_outer_radius.GetValue())
                turns = int(self.txt_turns.GetValue())

                if angle_degrees <= 0 or inner_radius <= 0 or outer_radius <= inner_radius or turns <= 0:
                    wx.MessageBox('Bitte geben Sie gültige Werte für Winkel, Radien und Windungen ein.', 'Fehler', wx.OK | wx.ICON_ERROR)
                    return None

                params.update({
                    'angle_degrees': angle_degrees,
                    'inner_radius': inner_radius,
                    'outer_radius': outer_radius,
                    'turns': turns
                })
            else:
                turns = int(self.txt_turns.GetValue())
                diameter = float(self.txt_diameter.GetValue())

                if turns <= 0 or diameter <= 0:
                    wx.MessageBox('Bitte geben Sie gültige positive Werte für Windungen und Durchmesser ein.', 'Fehler', wx.OK | wx.ICON_ERROR)
                    return None

                params.update({
                    'turns': turns,
                    'diameter': diameter
                })

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
        spacing = params['spacing']
        width = params['width']
        doc = ezdxf.new(dxfversion='R2010')
        msp = doc.modelspace()

        if form == 'rund':
            turns = params['turns']
            diameter = params['diameter']
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
            turns = params['turns']
            diameter = params['diameter']
            sides = 4
            angle = 2 * np.pi / sides
            steps = turns * sides
            directions = np.array([
                [np.cos(i * angle), np.sin(i * angle)] for i in range(sides)
            ])
            directions[:, 1] *= -1  # Y-Achse invertieren für DXF
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
        elif form == 'segment':
            angle_degrees = params['angle_degrees']
            inner_radius = params['inner_radius']
            outer_radius = params['outer_radius']
            turns = params['turns']

            angle_radians = np.radians(angle_degrees)
            start_angle = -angle_radians / 2
            end_angle = angle_radians / 2

            path_points = []
            current_inner_radius = inner_radius
            current_outer_radius = outer_radius

            for turn in range(turns):
                # Kreisbogen entlang des inneren Radius
                theta_inner = np.linspace(start_angle, end_angle, num=100)
                x_inner = current_inner_radius * np.cos(theta_inner)
                y_inner = current_inner_radius * np.sin(theta_inner)
                if turn == 0:
                    path_points.extend(zip(x_inner, y_inner))
                else:
                    path_points.extend(zip(x_inner[1:], y_inner[1:]))

                # Gerade Linie zum äußeren Radius
                x_line = [x_inner[-1], current_outer_radius * np.cos(end_angle)]
                y_line = [y_inner[-1], current_outer_radius * np.sin(end_angle)]
                path_points.extend(zip(x_line, y_line))

                # Kreisbogen entlang des äußeren Radius in entgegengesetzter Richtung
                theta_outer = np.linspace(end_angle, start_angle, num=100)
                x_outer = current_outer_radius * np.cos(theta_outer)
                y_outer = current_outer_radius * np.sin(theta_outer)
                path_points.extend(zip(x_outer, y_outer))

                # Gerade Linie zurück zum inneren Radius (mit Versatz)
                if turn < turns - 1:
                    next_inner_radius = current_inner_radius + (spacing + width)
                    x_line = [x_outer[-1], next_inner_radius * np.cos(start_angle)]
                    y_line = [y_outer[-1], next_inner_radius * np.sin(start_angle)]
                    path_points.extend(zip(x_line, y_line))
                    current_inner_radius = next_inner_radius
                    current_outer_radius -= (spacing + width)
                else:
                    # Letzte Verbindungslinie zum Startpunkt
                    x_line = [x_outer[-1], path_points[0][0]]
                    y_line = [y_outer[-1], path_points[0][1]]
                    path_points.extend(zip(x_line, y_line))

            # Pfad zur DXF hinzufügen
            msp.add_polyline2d(path_points, close=True)

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
        spacing = params['spacing']
        width = params['width']
        scale = 5  # Skalierungsfaktor für die Darstellung
        w, h = self.GetSize()
        center_x = w / 2
        center_y = h / 2
        gc.Translate(center_x, center_y)
        pen = wx.Pen(wx.Colour(0, 0, 0), 1)
        gc.SetPen(pen)

        if form == 'rund':
            turns = params['turns']
            diameter = params['diameter']
            # Parameter für die archimedische Spirale
            a = (diameter / 2) * scale
            b = ((spacing + width) / (2 * np.pi)) * scale
            max_theta = turns * 2 * np.pi
            theta = np.linspace(0, max_theta, num=1000)
            r = a + b * theta
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            # Pfad zeichnen
            path = gc.CreatePath()
            path.MoveToPoint(x[0], y[0])
            for xi, yi in zip(x[1:], y[1:]):
                path.AddLineToPoint(xi, yi)
            gc.StrokePath(path)
        elif form == 'eckig':
            turns = params['turns']
            diameter = params['diameter']
            sides = 4
            angle = 2 * np.pi / sides
            steps = turns * sides
            directions = np.array([
                [np.cos(i * angle), np.sin(i * angle)] for i in range(sides)
            ])
            directions[:, 1] *= -1
            increment_steps = sides // 2 if sides % 2 == 0 else sides
            step_lengths = np.zeros(steps)
            step_length = (diameter / 2) * scale
            for i in range(steps):
                if i % increment_steps == 0 and i > 0:
                    step_length += (spacing + width) * scale
                step_lengths[i] = step_length
            moves = directions[np.arange(steps) % sides] * step_lengths[:, np.newaxis]
            positions = np.vstack((np.zeros(2), np.cumsum(moves, axis=0)))
            positions += np.array([0, 0])  # Verschiebung zum Mittelpunkt
            # Pfad zeichnen
            path = gc.CreatePath()
            path.MoveToPoint(*positions[0])
            for pos in positions[1:]:
                path.AddLineToPoint(pos[0], pos[1])
            gc.StrokePath(path)
        elif form == 'segment':
            angle_degrees = params['angle_degrees']
            inner_radius = params['inner_radius']
            outer_radius = params['outer_radius']
            turns = params['turns']

            angle_radians = np.radians(angle_degrees)
            start_angle = -angle_radians / 2
            end_angle = angle_radians / 2

            current_inner_radius = inner_radius * scale
            current_outer_radius = outer_radius * scale

            path = gc.CreatePath()

            for turn in range(turns):
                # Kreisbogen entlang des inneren Radius
                theta_inner = np.linspace(start_angle, end_angle, num=100)
                x_inner = current_inner_radius * np.cos(theta_inner)
                y_inner = current_inner_radius * np.sin(theta_inner)
                if turn == 0:
                    path.MoveToPoint(x_inner[0], y_inner[0])
                else:
                    path.AddLineToPoint(x_inner[0], y_inner[0])
                for xi, yi in zip(x_inner[1:], y_inner[1:]):
                    path.AddLineToPoint(xi, yi)

                # Gerade Linie zum äußeren Radius
                path.AddLineToPoint(current_outer_radius * np.cos(end_angle), current_outer_radius * np.sin(end_angle))

                # Kreisbogen entlang des äußeren Radius in entgegengesetzter Richtung
                theta_outer = np.linspace(end_angle, start_angle, num=100)
                x_outer = current_outer_radius * np.cos(theta_outer)
                y_outer = current_outer_radius * np.sin(theta_outer)
                for xi, yi in zip(x_outer, y_outer):
                    path.AddLineToPoint(xi, yi)

                # Gerade Linie zurück zum inneren Radius (mit Versatz)
                if turn < turns - 1:
                    next_inner_radius = current_inner_radius + (spacing + width) * scale
                    path.AddLineToPoint(next_inner_radius * np.cos(start_angle), next_inner_radius * np.sin(start_angle))
                    current_inner_radius = next_inner_radius
                    current_outer_radius -= (spacing + width) * scale
                else:
                    # Letzte Verbindungslinie zum Startpunkt
                    path.AddLineToPoint(inner_radius * scale * np.cos(start_angle), inner_radius * scale * np.sin(start_angle))

            gc.StrokePath(path)

if __name__ == '__main__':
    app = wx.App()
    CoilGenerator(None, title='Spulengenerator')
    app.MainLoop()