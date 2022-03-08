#!python3.9

import time
from termcolor import colored as _c
import sys
import Msg

class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def set_time(self, start_time: tuple, end_time: tuple):
        self.start_time = time.struct_time((
            start_time[0],
            start_time[1],
            start_time[2],
            start_time[3],
            start_time[4],
            start_time[5],
            start_time[6],
            self._calc_yday(start_time),
            0
        ))
        self.end_time = time.struct_time((
            end_time[0],
            end_time[1],
            end_time[2],
            end_time[3],
            end_time[4],
            end_time[5],
            end_time[6],
            self._calc_yday(end_time),
            0
        ))

    def _progress_line(self, until_start, left, line_len):
        ch = '█'
        line, color, ret = [ch for i in range(line_len)], None, ''
        if left/until_start >= 1.6/3:
            color = 'green'
        elif left/until_start >= 1/5:
            color = 'yellow'
        else:
            color = 'red'
        block_count = 1 - (left/until_start)
        for i in range(int(block_count*line_len)):
            line[i] = _c(ch, color)
        for i in line:
            ret += i
        return f'|{ret}| {_c(self._to_HMS(left), color)}'
    
    def _to_HMS(self, sec):
        ts = lambda x: ['', '0'][x<10] + str(x)
        h, m, s = 0, 0, sec
        m, s = s/60, s%60
        h, m = m/60, m%60
        return f'{ts(int(h))}:{ts(int(m))}:{ts(int(s))}'

    def check_start_time(self):
        now_time = time.time()
        until_start = time.mktime(self.start_time) - now_time
        if time.mktime(self.end_time) - now_time <= 0:
            raise Msg.ContestOver
        left = until_start
        if left <= 0:
            return
        while left > 0:
            print(f'{_c("[", "cyan")}Until Start{_c("]", "cyan")} {self._progress_line(until_start, left, 90)}', end='\r')
            time.sleep(1)
            left -= 1
        print(f'{_c("[", "cyan")}Until Start{_c("]", "cyan")} {self._progress_line(1, 0, 90)}', end='\r')
        print()
        raise Msg.ContestStarted

    def is_end_time(self):
        now_time = time.time()
        left = time.mktime(self.end_time) - now_time
        if left <= 0:
            raise Msg.ContestOver

    def timer(self):
        now_time = time.time()
        left = time.mktime(self.end_time) - time.mktime(self.start_time)
        count = now_time - time.mktime(self.start_time)
        if count >= left:
            print(f'{_c("[", "cyan")}system{_c("]", "cyan")}: Contest is over')
            raise Msg.ContestOver()
        while count < left:
            print(f'{_c("[", "cyan")}Time Left{_c("]", "cyan")} {self._progress_line(left, left-count, 90)}', end='\r')
            time.sleep(1)
            count += 1
        print(f'{_c("[", "cyan")}Time Left{_c("]", "cyan")} {self._progress_line(1, 0, 90)}', end='\r')
        print()

    def _calc_yday(self, t: list):
        ret = t[2]
        month_day_list = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if t[0]%400 == 0 or (t[0]%4 == 0 and t[0]%100 != 0):
            month_day_list[1] = 29
        for d, m in zip(month_day_list, range(t[1]-1)):
            ret += d
        return ret

if __name__ == '__main__':
    start_time, end_time = eval(sys.argv[1]), eval(sys.argv[2])
    tm = Timer()
    tm.set_time(start_time, end_time)
    tm.timer()

#if __name__ == '__main__':
#    tm = Timer((2022, 3, 6, 14, 28, 30, 6), (2022, 3, 6, 18, 0, 0, 6))
#    tm.timer()
