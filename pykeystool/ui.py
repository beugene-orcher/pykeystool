import curses
import sys
from curses import textpad
from pykeystool.converter import KeyConverter
from pykeystool.menu_description import menu_dict


class Form():

    def __init__(self, stdscr, win):
        self.stdscr = stdscr
        self.count_y_x(win)
        self.window = stdscr.subwin(self.lines, self.cols, self.y, self.x)
        self.window.clear()
        self.set_window_border_and_title()
        self.window.keypad(1)
        self.window.refresh()

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

    def count_y_x(self, win):
        max_y, max_x = self.stdscr.getmaxyx()
        max_y, max_x = int(0.9 * max_y), int(0.9 * max_x)
        y0, x0 = 1, 1
        y1, x1 = int(0.6 * max_y), int(0.2 * max_x)
        if win == 'menu':
            self.y, self.x = y0, x0
            self.lines, self.cols = max_y, x1
        if win == 'message':
            self.y, self.x = y0, x1
            self.lines, self.cols = y1-1, max_x - x1
        if win == 'input':
            self.y, self.x = y1, x1
            self.lines, self.cols = max_y - y1 + 1, max_x - x1


class MenuForm(Form):
    menu_dict = menu_dict
    title = ' Menu '

    def __init__(self, stdscr):
        super().__init__(stdscr, 'menu')
        self.position = 0

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.menu_dict):
            self.position = len(self.menu_dict) - 1

    def display(self):
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
    title = ' Messages '

    def __init__(self, stdscr):
        super().__init__(stdscr, 'message')
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
    title = ' Input '

    def __init__(self, stdscr):
        super().__init__(stdscr, 'input')

    def display(self, mode):
        self.window.clear()
        self.set_window_border_and_title()

        if mode == 0:
            # Decrypt key submenu
            self.window.addstr(2, 4, 'Master key: ')
            widget = self.get_pretty_textbox(3, 35, 28, 65)
            self.window.addstr(5, 4, 'Encrypted key: ')
            widget2 = self.get_pretty_textbox(3, 51, 31, 65)
            self.window.addstr(8, 4, 'ECB/CBC (0/1): ')
            widget3 = self.get_pretty_textbox(3, 4, 34, 65)
            self.window.addstr(11, 4, 'IV: ')
            widget4 = self.get_pretty_textbox(3, 19, 37, 65)
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
        try:
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
        except Exception as e:
            if 'ERR' in repr(e):
                raise Exception('Terminal window is too small, '
                                'please resize the '
                                'terminal window and run the app again')
            else:
                raise e

    def set_styles(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)

    def set_cursor(self):
        try:
            self.screen.leaveok(True)
        except Exception:
            raise Exception("Terminal doesn't support a cursor")
