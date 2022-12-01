import sys
from typing import Union, Optional
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFontDatabase
from Calculator.ui.design import Ui_MainWindow
from operator import add, sub, mul, truediv
import ui.files_rc

operations = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv
}

default_font_size = 16
default_entry_font_size = 40

error_zero_div = 'Division by zero'
error_undefined = 'Result is undefined'


class Calculator(QMainWindow):
    def __init__(self):
        super(Calculator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.entry_max_len = self.ui.lineEdit.maxLength()

        QFontDatabase.addApplicationFont("fonts/Rubik-Regular.ttf")

        #digits
        self.ui.btn_0.clicked.connect(lambda: self.add_digit('0'))
        self.ui.btn_1.clicked.connect(lambda: self.add_digit('1'))
        self.ui.btn_2.clicked.connect(lambda: self.add_digit('2'))
        self.ui.btn_3.clicked.connect(lambda: self.add_digit('3'))
        self.ui.btn_4.clicked.connect(lambda: self.add_digit('4'))
        self.ui.btn_5.clicked.connect(lambda: self.add_digit('5'))
        self.ui.btn_6.clicked.connect(lambda: self.add_digit('6'))
        self.ui.btn_7.clicked.connect(lambda: self.add_digit('7'))
        self.ui.btn_8.clicked.connect(lambda: self.add_digit('8'))
        self.ui.btn_9.clicked.connect(lambda: self.add_digit('9'))

        #actions
        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_point.clicked.connect(self.add_point)
        self.ui.btn_neg.clicked.connect(self.negate)
        self.ui.btn_backspace.clicked.connect(self.backspace)

        #math
        self.ui.btn_calc.clicked.connect(self.calculate)
        self.ui.btn_add.clicked.connect(lambda: self.math_operation('+'))
        self.ui.btn_sub.clicked.connect(lambda: self.math_operation('-'))
        self.ui.btn_mul.clicked.connect(lambda: self.math_operation('*'))
        self.ui.btn_div.clicked.connect(lambda: self.math_operation('/'))

    def add_digit(self, btn_text: str) -> None:
        self.remove_error()
        self.clear_temp()
        if self.ui.lineEdit.text() == '0':
            self.ui.lineEdit.setText(btn_text)
        else:
            self.ui.lineEdit.setText(self.ui.lineEdit.text() + btn_text)
        self.adjust_entry_font_size()

    def add_point(self) -> None:
        self.clear_temp()
        if '.' not in self.ui.lineEdit.text():
            self.ui.lineEdit.setText(self.ui.lineEdit.text() + '.')
            self.adjust_entry_font_size()

    def negate(self) -> None:
        self.clear_temp()
        entry = self.ui.lineEdit.text()
        if '-' not in entry:
            if entry != '0':
                entry = '-' + entry
        else:
            entry = entry[1:]
        if len(entry) == self.entry_max_len + 1 and '-' in entry:
            self.ui.lineEdit.setMaxLength(self.entry_max_len + 1)
        else:
            self.ui.lineEdit.setMaxLength(self.entry_max_len)
        self.ui.lineEdit.setText(entry)
        self.adjust_entry_font_size()

    def clear_all(self) -> None:
        self.remove_error()
        self.ui.lineEdit.setText('0')
        self.adjust_entry_font_size()
        self.ui.label.clear()
        self.adjust_temp_font_size()

    @staticmethod
    def remove_zeros(num: str) -> str:
        n = str(float(num))
        return n[:-2] if n[-2:] == '.0' else n

    def add_temp(self, math_sign: str) -> None:
        if not self.ui.label.text() or self.get_mathsign() == '=':
            self.ui.label.setText(self.remove_zeros(self.ui.lineEdit.text()) + f' {math_sign} ')
            self.adjust_temp_font_size()
            self.ui.lineEdit.setText('0')
            self.adjust_entry_font_size()

    def get_entry(self) -> Union[int, float]:
        entry = self.ui.lineEdit.text().strip('.')
        return float(entry) if '.' in entry else int(entry)

    def get_temp(self) -> Union[int, float, None]:
        if self.ui.label.text():
            temp = self.ui.label.text().strip('.').split()[0]
            return float(temp) if '.' in temp else int(temp)

    def get_mathsign(self) -> Optional[str]:
        if self.ui.label.text():
            return self.ui.label.text().strip('.').split()[-1]

    def get_entry_text_width(self) -> int:
        return self.ui.lineEdit.fontMetrics().boundingRect(self.ui.lineEdit.text()).width()

    def get_temp_text_width(self) -> int:
        return self.ui.label.fontMetrics().boundingRect(self.ui.label.text()).width()

    def calculate(self) -> Optional[str]:
        entry = self.ui.lineEdit.text()
        temp = self.ui.label.text()
        if temp:
            try:
                result = self.remove_zeros(
                    str(operations[self.get_mathsign()](self.get_temp(), self.get_entry()))
                )
                self.ui.label.setText(temp + self.remove_zeros(entry) + ' =')
                self.adjust_temp_font_size()
                self.ui.lineEdit.setText(result)
                self.adjust_entry_font_size()
                return result
            except KeyError:
                pass
            except ZeroDivisionError:
                if self.get_temp() == 0:
                    self.show_error(error_undefined)
                else:
                    self.show_error(error_zero_div)

    def math_operation(self, math_sign: str) -> None:
        temp = self.ui.label.text()
        try:
            if not temp:
                self.add_temp(math_sign)
            else:
                if self.get_mathsign() != math_sign:
                    if self.get_mathsign() == '=':
                        self.add_temp(math_sign)
                    else:
                        self.ui.label.setText(temp[:-2] + f'{math_sign} ')
                else:
                    self.ui.label.setText(self.calculate() + f'{math_sign} ')
        except TypeError:
            pass
        self.adjust_temp_font_size()

    def backspace(self) -> None:
        self.remove_error()
        self.clear_temp()
        entry = self.ui.lineEdit.text()
        if len(entry) != 1:
            if len(entry) == 2 and '-' in entry:
                self.ui.lineEdit.setText('0')
            else:
                self.ui.lineEdit.setText(entry[:-1])
        else:
            self.ui.lineEdit.setText('0')
        self.adjust_entry_font_size()

    def clear_temp(self) -> None:
        if self.get_mathsign() == '=':
            self.ui.label.clear()
            self.adjust_temp_font_size()

    def show_error(self, text: str) -> None:
        self.ui.lineEdit.setMaxLength(len(text))
        self.ui.lineEdit.setText(text)
        self.adjust_entry_font_size()
        self.disable_btn(True)

    def remove_error(self) -> None:
        if self.ui.lineEdit.text() in (error_zero_div, error_undefined):
            self.ui.lineEdit.setMaxLength(self.entry_max_len)
            self.ui.lineEdit.setText('0')
            self.adjust_entry_font_size()
            self.disable_btn(False)

    def disable_btn(self, disable: bool) -> None:
        self.ui.btn_calc.setDisabled(disable)
        self.ui.btn_add.setDisabled(disable)
        self.ui.btn_sub.setDisabled(disable)
        self.ui.btn_mul.setDisabled(disable)
        self.ui.btn_div.setDisabled(disable)
        self.ui.btn_neg.setDisabled(disable)
        self.ui.btn_point.setDisabled(disable)

        color = 'color: #888;' if disable else 'color: black;'
        self.change_color(color)

    def change_color(self, css_color: str) -> None:
        self.ui.btn_calc.setStyleSheet(css_color)
        self.ui.btn_add.setStyleSheet(css_color)
        self.ui.btn_sub.setStyleSheet(css_color)
        self.ui.btn_mul.setStyleSheet(css_color)
        self.ui.btn_div.setStyleSheet(css_color)
        self.ui.btn_neg.setStyleSheet(css_color)
        self.ui.btn_point.setStyleSheet(css_color)

    def adjust_entry_font_size(self) -> None:
        font_size = default_entry_font_size
        while self.get_entry_text_width() > self.ui.lineEdit.width() - 15:
            font_size -= 1
            self.ui.lineEdit.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')
        font_size = 1
        while self.get_entry_text_width() < self.ui.lineEdit.width() - 60:
            font_size += 1
            if font_size > default_entry_font_size:
                break
            self.ui.lineEdit.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

    def adjust_temp_font_size(self) -> None:
        font_size = default_font_size
        while self.get_temp_text_width() > self.ui.label.width() - 10:
            font_size -= 1
            self.ui.label.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')
        font_size = 1
        while self.get_temp_text_width() < self.ui.label.width() - 60:
            font_size += 1
            if font_size > default_font_size:
                break
            self.ui.label.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

    def resizeEvent(self, event) -> None:
        self.adjust_entry_font_size()
        self.adjust_temp_font_size()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec())