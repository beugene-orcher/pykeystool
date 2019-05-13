import curses
import sys
from curses import panel
from curses import textpad
from pykeystool.converter import KeyConverter
from pykeystool.menu_description import menu_dict


class Form():

    def __init__(self, stdscr):
        self.max_y, self.max_x = stdscr.getmaxyx()
        self.set_h_w()
        self.window = stdscr.subwin(self.lines, self.cols, self.y, self.x)
        self.window.clear()
        self.set_window_border_and_title()
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

    def set_h_w(self):
        self.lines = int(self.coef_lines * self.max_y)
        self.cols = int(self.coef_cols * self.max_x)

    def set_window_border_and_title(self):
        self.window.attron(curses.color_pair(1))
        self.window.border()
        self.window.attroff(curses.color_pair(1))
        self.window.attron(curses.color_pair(1))
        self.window.addstr(0, 5, self.title)
        self.window.attroff(curses.color_pair(1))

    def get_pretty_textbox(self, lines, cols, y, x):
        sub_win = self.window.subwin(lines, cols, y, x)
        sub_win.border()
        sub_text = sub_win.subwin(1, cols-2, y+1, x+1)
        tp = textpad.Textbox(sub_text, insert_mode=True)
        return tp


class MenuForm(Form):
    menu_dict = menu_dict
    coef_lines, coef_cols = 0.9, 0.2
    y, x = 2, 2
    title = ' Menu '

    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.position = 0

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.menu_dict):
            self.position = len(self.menu_dict) - 1

    def display(self):
        self.panel.show()

        while True:
            self.window.refresh()
            curses.doupdate()

            for index, item in self.menu_dict.items():
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                self.window.addstr(2+index, 3, item.get('label'), mode)

            key = self.window.getch()

            if key in (curses.KEY_ENTER, 10, 13):
                if self.position == len(self.menu_dict) - 1:
                    sys.exit(1)
                else:
                    message = self.menu_dict.get(self.position).get('message')
                    return message, self.position

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)


class MessageForm(Form):
    coef_lines, coef_cols = 0.6, 0.7
    y, x = 2, 38
    title = ' Messages '

    def __init__(self, stdscr):
        super().__init__(stdscr)
        self.window.keypad(0)

    def display(self, text, mode):
        self.window.clear()
        self.set_window_border_and_title()
        if mode == 0:
            # text viewer
            self.window.addstr(2, 2, text)
            self.set_window_border_and_title()
        if mode == 1:
            # output mode viewer
            y, x, counter = 2, 2, 0
            result = KeyConverter(text).get_result()
            if len(result.errors) == 0 and len(result.result) > 0:
                self.window.addstr(2, 2, 'Output')
                for i in result.result:
                    y += 2
                    counter += 1
                    self.window.addstr(y, x+2, '%s) %s' % (str(counter), i))
            if not len(result.errors) == 0:
                self.window.addstr(2, 2, 'There are problems with data:')
                for i in result.errors:
                    y += 2
                    counter += 1
                    self.window.addstr(y, x+2, '%s) %s' % (str(counter), i))

        self.window.refresh()
        curses.doupdate()


class InputForm(Form):
    coef_lines, coef_cols = 0.3, 0.7
    y, x = 31, 38
    title = ' Input '

    def __init__(self, stdscr):
        super().__init__(stdscr)

    def display(self, mode):
        self.window.clear()
        self.set_window_border_and_title()

        if mode == 0:
            # Decrypt key level
            self.window.addstr(2, 4, 'Master key: ')
            widget = self.get_pretty_textbox(3, 35, 32, 65)

            self.window.addstr(5, 4, 'Encrypted key: ')
            widget2 = self.get_pretty_textbox(3, 51, 35, 65)

            self.window.addstr(8, 4, 'ECB/CBC (0/1): ')
            widget3 = self.get_pretty_textbox(3, 4, 38, 65)

            self.window.addstr(11, 4, 'IV: ')
            widget4 = self.get_pretty_textbox(3, 19, 41, 65)

            self.window.refresh()
            self.mk = widget.edit().strip()
            self.ek = widget2.edit().strip()
            self.mode = widget3.edit().strip()
            self.iv = widget4.edit().strip() if self.mode == '1' else None

        self.window.refresh()
        curses.doupdate()

    def get_values(self):
        return {'mk': self.mk,
                'ek': self.ek,
                'mode': self.mode,
                'iv': self.iv}


class MyApp():

    def __init__(self, stdscr):
        self.screen = stdscr
        self.set_cursor()
        self.set_styles()
        menu_form = MenuForm(self.screen)
        mess_form = MessageForm(self.screen)
        input_form = InputForm(self.screen)
        while True:
            result = menu_form.display()
            mess_form.display(result[0], 0)
            input_form.display(result[1])
            mess_form.display(input_form.get_values(), 1)

    def set_styles(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)

    def set_cursor(self):
        try:
            self.screen.leaveok(True)
        except Exception:
            raise Exception("Your terminal doesn't support a cursor")
