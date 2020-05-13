from tkinter import Tk, Toplevel, Frame 
from tkinter import Button as tkButton
from tkinter.ttk import Button as ttkButton

import datetime



def sub2ind(row, col):
    return row*7 + col


def ind2sub(ind):
    return ind//7, ind%7



class MonthCalendar(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        upper_frame = Frame(self)
        upper_frame.pack(fill="x")

        minus_button = ttkButton(
            upper_frame, 
            text="<", 
            width=2,
            command=lambda: self.month_adjust(inc=False))
        minus_button.pack(side="left")

        year_month_button = ttkButton(upper_frame)
        year_month_button.pack(side="left", fill="x", expand="yes")
        self.__year_month_button = year_month_button

        plus_button = ttkButton(
            upper_frame, 
            text=">", 
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
                style = {**button_style, "fg":"lime green"}
            elif text == "Su":
                style = {**button_style, "fg":"red"}
            else:
                style = button_style
            style = {**style, "text":text}
            tkButton(middle_frame, **style).grid(row=0, column=index)

        lower_frame = Frame(self)
        lower_frame.pack(fill="x")

        date_buttons = []
        for r in range(6):
            for c in range(7):
                date_button = tkButton(lower_frame, **button_style)
                date_button.grid(row=r, column=c)
                date_buttons.append(date_button)

        self.__date_buttons = date_buttons

        self.__month = None
        self.__year = None
        self.__date = None
        self.__default_fg = date_buttons[0]["fg"]
        self.__default_bg = date_buttons[0]["bg"]


    def clear_buttons(self):
        for button in self.__date_buttons:
            button["text"] = ""
            button["fg"] = self.__default_fg
            button["bg"] = self.__default_bg


    def set_month(self, year, month):
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


    def set_date(self, year, month, day):
        self.set_month(year, month)
        date = datetime.date(year, month, day)
        self.__date = date
        first_month_day = datetime.date(year, month, 1)
        first_monday = first_month_day - datetime.timedelta(days=first_month_day.weekday())
        index = (date - first_monday).days
        self.__date_buttons[index]["bg"] = "cornflower blue"


    def month_adjust(self, inc=True):
        if self.__month is None:
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



def show_date(date):
    win = Toplevel()
    win.resizable(False, False)
    win.title("WaveSyn-Calendar")
    mc = MonthCalendar(win)
    mc.pack(fill="both")
    mc.set_date(date.year, date.month, date.day)



if __name__ == "__main__":
    root = Tk()
    mc = MonthCalendar(root)
    mc.pack(fill="both")
    mc.set_month(2020, 5)
    root.resizable(False, False)
    root.mainloop()
