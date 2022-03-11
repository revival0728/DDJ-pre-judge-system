import sys
import os
import Msg
from termcolor import colored as _c

class IO:
    def __init__(self, main_obj: object):
        self.help_text = f'''\
{_c("******************************************************************************************************", "cyan")}

You can enter the following command to "Submit" or "View a Problem"
    - {self._command_info("submit", "[Problem_ID] [File_Name_And_Path]", "submit a problem")}
    - {self._command_info("view", "[Problem_ID]", "view a problem statement")}
    - {self._command_info("help", "", "show this text")}
    - {self._command_info("timer", "", "show the timer in the terminal")}
    - {self._command_info("dump", "[Problem ID]", "dump a specific problem submission to SUBMIT_FILE.cpp")}
    - {self._command_info("status", "", "show the submit result of each problem")}

{_c("******************************************************************************************************", "cyan")}
'''
        self.react = main_obj()
        self.all_command = {
            'view': self._view, 
            'submit': self._submit, 
            'help': self._help,
            'timer': self._timer,
            'dump': self._dump,
            'status': self._status
        }

    def _command_info(self, command: str, args: str, info: str):
        return f'{_c(command, "yellow")} {_c(args, "blue")}: {info}'

    def _argument_err_msg(self, expected: int, got: int):
        self.output('system', f'argument expected {expected} got {got}')

    def _view(self, args: tuple):
        if(len(args) != 1):
            self._argument_err_msg(1, len(args))
            return
        self.react.show_problem(args[0])

    def _submit(self, args: tuple):
        if(len(args) != 2):
            self._argument_err_msg(2, len(args))
            return
        self.react.submit_problem(args[0], args[1])

    def _help(self, args: tuple =tuple()):
        if(len(args) != 0):
            self._argument_err_msg(0, len(args))
            return
        print(self.help_text)

    def _timer(self, args: tuple =tuple()):
        if(len(args) != 0):
            self._argument_err_msg(0, len(args))
            return
        self.react.show_timer()

    def _dump(self, args: tuple):
        if len(args) != 1:
            self._argument_err_msg(1, len(args))
            return
        self.react.dump_submit_file(args[0])
        self.output('system', f'problem {args[0]} successfully dumped')

    def _status(self, args: tuple):
        if len(args) != 0:
            self._argument_err_msg(0, len(args))
            return
        result = self.react.get_status()
        print()
        for p in result:
            if result[p] == 'AC':
                print(f'\t- {p}: {_c("[", "cyan")}{_c(result[p], "green")}{_c("]", "cyan")}')
            elif result[p] == '-':
                print(f'\t- {p}: {_c("[", "cyan")}{result[p]}{_c("]", "cyan")}')
            else:
                print(f'\t- {p}: {_c("[", "cyan")}{_c(result[p], "red")}{_c("]", "cyan")}')
        print()

    def start(self):
        _input = input('Please enter init file path: ')
        if _input == '':
            _input = './options.json'
        self.output('system', 'Initializing the system')
        try:
            self.react.init(_input)
        except FileNotFoundError:
            self.output('system', 'init file not found')
            os.system('pause')
            sys.exit()
        while True:
            try:
                self.react.wait_to_start()
            except KeyboardInterrupt:
                continue
            except Msg.ContestStarted:
                break
            except Msg.ContestOver:
                self.output('system', 'Contest is over')
                os.system('pause')
                sys.exit()
            except Msg.PracticeMode:
                break
        self._help()
        while True:
            try:
                print(f'{_c("[", "cyan")}In{_c("]", "cyan")}: ', end='')
                _input = input()
                self.react.is_contest_over()
                commands = _input.strip().split()
                if len(commands) == 0:
                    continue
                if not (commands[0] in self.all_command):
                    continue
                self.all_command[commands[0]](tuple(commands[1:]))
                self.react.main()
            except Msg.WrongAnswer as sr:
                self.output(_c('WA', 'red'), f'At line {sr.at_line}\n{_c("Your answer: ", "blue")}\n{sr.user_output}\n{_c("Correct answer:", "blue")}\n{sr.correct_output}')
            except Msg.CompileError as sr:
                self.output(_c('CE', 'red'), f'{_c("Compiler message: ", "blue")}\n{sr.compile_msg}')
            except Msg.TimeLimitExceed as sr:
                self.output(_c('TLE', 'red'), f'Execution time: {sr.execution_time}s')
            except Msg.OutputLimitExceed as sr:
                line_msg = lambda x: ['lines', 'line'][int(x==1)]
                self.output(_c('OLE', 'red'), f'Expected {sr.ans_line} {line_msg(sr.ans_line)} got {sr.user_line} {line_msg(sr.user_line)}')
            except Msg.Accept as sr:
                self.output(_c('AC', 'green'), 'Accepted')
            except Msg.ContestOver:
                self.output('system', 'Contest is over')
                self.output('system', 'dumping out SUBMIT_FILE.cpp...')
                self.react.dump_all()
                self.output('system', 'SUBMIT_FILE.cpp successfully dumped')
                self.output('system', 'please submit it to online judge system')
                os.system('pause')
                sys.exit()
            except Msg.PracticeModeError as err:
                self.output(_c('NOTE', 'yellow'), f'{_c("Your in practice mode", "blue")}: {err.msg}')
            except Msg.ContestModeError as err:
                self.output(_c('NOTE', 'yellow'), f'{_c("Your in contest mode", "blue")}: {err.msg}')
            except KeyboardInterrupt:
                print()
            except FileNotFoundError:
                self.output('system', 'submit file not found')
            except Msg.ProblemNotFound:
                self.output('system', 'problem id not found')
            except Msg.RuntimeError as sr:
                self.output(_c('RE', 'red'), f'{_c("In stderr: ", "blue")}\n{sr.return_msg}')

    def output(self, pre_msg: str, msg: str):
        print(f'{_c("[", "cyan")}{pre_msg}{_c("]", "cyan")}: {msg}')
