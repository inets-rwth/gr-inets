import converter
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolTip, 
    QPushButton, QApplication, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QFont


class converter_gui(QWidget):
    def __init__(self):
        super(converter_gui, self).__init__()
        self.con = converter.converter('/dev/ttyACM0')
        
        self.setWindowTitle('SiversIMA Converter Control')
        
        hbox = QVBoxLayout(self)

        self.bt_open = QPushButton('Connect', self)
        self.bt_open.clicked.connect(self.button_clicked)

        self.bt_tx_on = QPushButton('TX ON', self)
        self.bt_tx_on.hide()
        self.bt_rx_on = QPushButton('RX ON', self)
        self.bt_rx_on.hide()

        self.le_rx_freq = QLineEdit()
        self.le_rx_freq.hide()
        self.le_tx_freq = QLineEdit()
        self.le_tx_freq.hide()

        hbox.addWidget(self.bt_open)
        hbox.addWidget(self.bt_tx_on)
        hbox.addWidget(self.bt_rx_on)
        hbox.addWidget(self.le_tx_freq)
        hbox.addWidget(self.le_rx_freq)
        
        self.setLayout(hbox)
        self.show()

    def closeEvent(self, event):
        self.con.close()

    def button_clicked(self):
        self.con.open()
        tx_on = self.con.get_tx_on()
        rx_on = self.con.get_rx_on()
        tx_freq = self.con.get_tx_freq()
        rx_freq = self.con.get_rx_freq()
        
        self.bt_open.hide()

        self.le_rx_freq.setText(str(rx_freq))
        self.le_rx_freq.show()
        self.le_tx_freq.setText(str(tx_freq))
        self.le_tx_freq.show()
        

        if tx_on:
            self.bt_tx_on.setText('TX Off')
            self.bt_tx_on.show()
        else:
            self.bt_tx_on.setText('TX ON')
            self.bt_tx_on.show()
        if rx_on:
            self.bt_rx_on.setText('RX Off')
            self.bt_rx_on.show()
        else:
            self.bt_rx_on.setText('RX ON')
            self.bt_rx_on.show()
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    conv = converter_gui()
    sys.exit(app.exec_())
