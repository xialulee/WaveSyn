from __future__ import annotations

from typing import Callable, Tuple
from tkinter import Tk, Toplevel, Frame 
from tkinter import Button as tkButton
from tkinter.ttk import Button as ttkButton

import datetime



def sub2ind(row: int, col: int) -> int:
    return row*7 + col


def ind2sub(ind: int) -> Tuple[int, int]:
    return ind//7, ind%7



class MonthCalendar(Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        upper_frame = Frame(self)
        upper_frame.pack(fill="x")

        minus_button = ttkButton(
            upper_frame, 
            text="\u25c4", 
            width=2,
            command=lambda: self.month_adjust(inc=False))
        minus_button.pack(side="left")

        year_month_button = ttkButton(upper_frame)
        year_month_button.pack(side="left", fill="x", expand="yes")
        self.__year_month_button = year_month_button

        plus_button = ttkButton(
            upper_frame, 
            text="\u25ba", 
            width=2,
            command=lambda: self.month_adjust(inc=True))
        plus_button.pack(side="right")

        middle_frame = Frame(self)
        middle_frame.pack(fill="x")

        button_style = dict(
            width="3",
            relief="groove"
        )

        for index, text in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            if text == "Sa":
                fg = {"fg": "lime green"}
            elif text == "Su":
                fg = {"fg": "red"}
            else:
                fg = {}
            style = button_style | fg
            style |= {"text": text}
            tkButton(middle_frame, **style).grid(row=0, column=index)

        lower_frame = Frame(self)
        lower_frame.pack(fill="x")

        date_buttons = []
        for r in range(6):
            for c in range(7):
                date_button = tkButton(lower_frame, **button_style)
                date_button["command"] = lambda button=date_button: \
                    self.__picker_callback(
                        self.__year, 
                        self.__month, 
                        int(button["text"])
                    )
                date_button.grid(row=r, column=c)
                date_buttons.append(date_button)

        self.__date_buttons = date_buttons

        self.__month = None
        self.__year = None
        self.__date = None
        self.__default_fg = date_buttons[0]["fg"]
        self.__default_bg = date_buttons[0]["bg"]
        self.__picker_callback: Callable[[int|None, int|None, int|None], None] \
            = lambda y, m, d: None


    def clear_buttons(self) -> None:
        for button in self.__date_buttons:
            button["text"] = ""
            button["fg"] = self.__default_fg
            button["bg"] = self.__default_bg
            button["state"] = "disable"


    def pick_date(self, 
            callback: Callable[[int|None, int|None, int|None], None]
        ) -> None:
        self.__picker_callback = callback


    def set_month(self, year: int, month: int) -> None:
        self.__year = year
        self.__month = month
        self.__year_month_button["text"] = f"{year}-{month}"
        first_day = datetime.date(year, month, 1)
        first_monday = first_day - datetime.timedelta(days=first_day.weekday())
        one_day = datetime.timedelta(days=1)

        self.clear_buttons()

        date = first_monday
        flag0 = False
        flag1 = False
        for button in self.__date_buttons:
            button["text"] = f"{date.day: 2d}"
            if date.month != month:
                button["fg"] = "gray"
            else:
                button["state"] = "normal"
                if date.weekday() == 5:
                    button["fg"] = "lime green"
                elif date.weekday() == 6:
                    button["fg"] = "red"
                else:
                    button["fg"] = "black"
            date += one_day
            if date.year >= year and date.month > month:
                flag0 = True
            if flag0 and date.weekday() == 0:
                flag1 = True
            if flag0 and flag1:
                break


    def set_date(self, year: int, month: int, day: int) -> None:
        self.set_month(year, month)
        date = datetime.date(year, month, day)
        self.__date = date
        first_month_day = datetime.date(year, month, 1)
        first_monday = first_month_day - datetime.timedelta(days=first_month_day.weekday())
        index = (date - first_monday).days
        self.__date_buttons[index]["bg"] = "cornflower blue"


    def month_adjust(self, inc: bool = True) -> None:
        if self.__month is None or self.__year is None:
            return
        self.__month += 1 if inc else -1
        if self.__month == 0:
            self.__year -= 1
            self.__month = 12
        elif self.__month == 13:
            self.__year += 1
            self.__month = 1
        if self.__date and \
            self.__date.year == self.__year and \
            self.__date.month == self.__month:
            self.set_date(
                self.__date.year,
                self.__date.month,
                self.__date.day)
        else:
            self.set_month(self.__year, self.__month)



def show_date(date: datetime.date) -> None:
    win = Toplevel()
    win.resizable(False, False)
    win.title("WaveSyn-Calendar")
    (calendar := MonthCalendar(win)).pack(fill="both")
    calendar.set_date(date.year, date.month, date.day)



def pick_date() -> datetime.date | None:
    win = Toplevel()
    win.resizable(False, False)
    win.title("WaveSyn-DatePicker")
    calendar = MonthCalendar(win)
    today = datetime.date.today()
    calendar.set_date(today.year, today.month, today.day)
    calendar.pack(fill="both")
    retval = None
    def callback(year: int, month: int, day: int) -> None:
        nonlocal retval
        retval = datetime.date(year, month, day)
        win.quit()
    calendar.pick_date(callback)

    win.protocol("WM_DELETE_WINDOW", lambda:0)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    return retval



if __name__ == "__main__":
    root = Tk()
    mc = MonthCalendar(root)
    mc.pack(fill="both")
    mc.set_month(2020, 5)
    root.resizable(False, False)
    root.mainloop()
