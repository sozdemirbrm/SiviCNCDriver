import serial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from sivicncdriver import settings
from sivicncdriver.settings import logger


class ReadThread(QThread):
    """
    A thread to read the serial link.
    """
    print_message = pyqtSignal(str, str)
    send_confirm = pyqtSignal(bool)

    def __init__(self, serial_manager):
        """
        The __init__ method.

        :param serial_manager: The main window's serial manager
        :type serial_manager: SerialManager
        """
        QThread.__init__(self)
        self.serial_manager = serial_manager
        self.user_stop = False
        self.read_allowed = True

    def __del__(self):
        self.wait()

    @pyqtSlot(bool)
    def set_read_allowed(self, st):
        """
        Allows or not the thread to read.

        :param st: Is it allowed ?
        """
        logger.debug("Set reading allowed to {}".format(st))
        self.read_allowed = st

    @pyqtSlot()
    def stop(self):
        """
        A simple slot to tell the thread to stop.
        """
        self.user_stop = True

    def run(self):
        """
        Runs the thread.

        The commands are sent using the serial manager. If an error occurs or if
        the thread is stopped by the user, then it quits.
        """
        while not self.user_stop:
            l = None
            if self.read_allowed:
                try:
                    l = self.serial_manager.serial.readline().decode('ascii')
                except serial.serialutil.SerialException as e:
                    logger.error("Serial error : {}".format(e))
                    self.print_message.emit("Serial error while reading.", "error")
                except UnicodeDecodeError as e:
                    logger.error("Serial error : {}".format(e))
                    self.print_message.emit("Serial error while reading.", "error")
            if l:
                logger.info("Received {}".format(repr(l)))
                if "error" in l.lower():
                    self.print_message.emit(l, "error")
                else:
                    self.print_message.emit("m> {}".format(l), "machine")
                self.send_confirm.emit("ok" in l.lower())
