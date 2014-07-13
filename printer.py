import serial
import os
from collections import deque
from atom.api import Atom, Unicode, observe, Typed, Property, Int, List, Bool
import enaml
from enaml.qt.qt_application import QtApplication


class Printer(Atom):

    port = Unicode()

    baudrate = Unicode()

    # List of all lines to be sent to the printer
    buffer = Typed(deque, ())

    # The user selected path to send to the printer
    path = Unicode(os.path.expanduser('~'))

    # Whether or not the current print is paused
    paused = Bool()

    s = Typed(serial.Serial)

    ### Observers  ############################################################

    @observe('path')
    def _path_changed(self, change):
        print 'path changed!!!', self.path
        if os.path.isfile(self.path):
            self.load_file(self.path)

    ### Printer interface  ####################################################

    def connect(self):
        port, baudrate = self.port, int(self.baudrate)
        self.s = serial.Serial(port, baudrate)

    def load_file(self, filename):
        with open(filename) as f:
            self.buffer = deque(f.readlines())

        print self.buffer

    def empty_buffer(self):
        self.paused = False
        while len(self.buffer) != 0:
            line = self.buffer.popleft()
            if '@pause' in line:
                self.pause()
                return
            if not line.endswith('\n'):
                line += '\n'
            print 'SENDING:', line
            self.s.write(line)

    def pause(self):
        self.paused = True



if __name__ == '__main__':
    with enaml.imports():
        from view import View
    printer = Printer()
    app = QtApplication()
    view = View(model=printer)
    view.show()
    app.start()
