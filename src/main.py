import GetProblem
import IO
import Msg
import Timer

import json
import subprocess
import webbrowser
import pathlib
import colorama

class Main:
    def __init__(self):
        self.options = None
        self.HtmlMaker = GetProblem.GetProblem()
        self.test_data = dict()
        self.Timer = Timer.Timer()
        self.submissions = dict()
        self.main_code = ''

    def init(self, init_file_path: str):
        with open(init_file_path, 'r', encoding='utf-8') as jsfile:
            self.options = json.loads(jsfile.read())
        for k in self.options['problem_list']:
            self.HtmlMaker.get_problem(self.options['problem_list'][k])
            self.test_data[k] = self.HtmlMaker.get_test_data()
            self.submissions[k] = {'result': '', 'code': ''}
            self.HtmlMaker.save_problem(k, '.')
        if self.options['mode'] == 'contest':
            self.Timer.set_time(self.options['contest_info']['start_time'], self.options['contest_info']['end_time'])

    def wait_to_start(self):
        if self.options['mode'] == 'contest':
            self.Timer.check_start_time()
        else:
            raise Msg.PracticeMode

    def is_contest_over(self):
        if self.options['mode'] == 'contest':
            self.Timer.is_end_time()

    def show_problem(self, pid: str):
        if not (pid in self.options['problem_list']):
            raise Msg.ProblemNotFound
        file_path = str(pathlib.Path(__file__).parent.resolve()).replace('\\', '/')
        file_path += '/' + pid + '.html'
        webbrowser.open(f'file:///{file_path}')

    def update_submissions(self, pid: str, result: str, code: str):
        if not (pid in self.options['problem_list']):
            raise Msg.ProblemNotFound
        if self.submissions[pid]['result'] == 'AC' and result == 'AC':
            self.submissions[pid]['code'] = code
        elif self.submissions[pid]['result'] != 'AC':
            self.submissions[pid]['result'] = result
            self.submissions[pid]['code'] = code

    def submit_problem(self, pid: str, file_np: str):
        if not (pid in self.options['problem_list']):
            raise Msg.ProblemNotFound
        process_output = lambda x: x.strip().replace('\r', '').split('\n')
        submit_code = ''
        with open(file_np, 'r', encoding='utf-8') as user_file:
            with open(self.options['main_code_path'], 'r', encoding='utf-8') as main_code:
                with open(self.options['submit_file_name'], 'w', encoding='utf-8') as submit_file:
                    submit_code = user_file.read()
                    self.main_code = main_code.read()
                    submit_file.write(self.main_code
                        .replace('/*[USER CODE]*/', submit_code)
                        .replace('/*[SUBMIT IDS]*/', f'#define __{pid}__')
                    )
        comp_outs, comp_errs = None, None
        run_outs, run_errs = None, None
        if self.options['language'] in ('c++'): # Language that needs to compile
            compiler = subprocess.Popen(self.options['submit_commands']['compile'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                comp_outs, comp_errs = compiler.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                compiler.kill()
                comp_outs, comp_errs = compiler.communicate()
            comp_outs, comp_errs = comp_outs.decode('utf-8'), comp_errs.decode('utf-8')
            if compiler.returncode != 0:
                self.update_submissions(pid, 'CE', submit_code)
                raise Msg.CompileError(comp_errs)
        run = subprocess.Popen(self.options['submit_commands']['run'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            run_outs, run_errs = run.communicate(input=self.test_data[pid]['input'].encode('utf-8'), timeout=10)
        except subprocess.TimeoutExpired:
            run.kill()
            run_outs, run_errs = run.communicate()
            self.update_submissions(pid, 'TLE', submit_code)
            raise Msg.TimeLimitExceed(10)
        run_outs, run_errs = run_outs.decode('utf-8'), run_errs.decode('utf-8')
        if run.returncode != 0:
            self.update_submissions(pid, 'RE', submit_code)
            raise Msg.RuntimeError(run_errs)
        user_list, ans_list = process_output(run_outs), process_output(self.test_data[pid]['output'])
        if len(ans_list) > len(user_list):
            self.update_submissions(pid, 'WA', submit_code)
            raise Msg.WrongAnswer(len(user_list)+1, ans_list[len(user_list)], '')
        if len(ans_list) < len(user_list):
            self.update_submissions(pid, 'OLE', submit_code)
            raise Msg.OutputLimitExceed(len(ans_list), len(user_list))
        for line, (user, ans) in enumerate(zip(user_list, ans_list)):
            if user.strip() != ans.strip():
                self.update_submissions(pid, 'WA', submit_code)
                raise Msg.WrongAnswer(line+1, ans, user)
        self.update_submissions(pid, 'AC', submit_code)
        raise Msg.Accept()

    def show_timer(self):
        if self.options['mode'] == 'practice':
            raise Msg.PracticeModeError('there is no timer in practice mode')
        self.Timer.timer()

    def dump(self, code: str, dumped_problem: str):
        with open('./SUBMIT_FILE.cpp', 'w', encoding='utf-8') as f:
            f.write(self.main_code
                .replace('/*[USER CODE]*/', code)
                .replace('/*[SUBMIT IDS]*/', dumped_problem)
            )

    def dump_submit_file(self, pid: str):
        if not (pid in self.options['problem_list']):
            raise Msg.ProblemNotFound
        if self.options['mode'] == 'contest':
            raise Msg.ContestModeError('you cannot dump out the files before contest ended')
        if self.options['language'] in ('c++'):
            self.dump(self.submissions[pid]['code'], f'#define __{pid}__')

    def dump_all(self):
        if self.options['language'] in ('c++'):
            all_code = ''
            dumped_problem = ''
            for p in self.submissions:
                if self.submissions[p]['result'] != 'CE' and self.submissions[p]['result'] != '':
                    all_code += self.submissions[p]['code'] + '\n\n'
                    dumped_problem += f'#define __{p}__\n'
            self.dump(all_code, dumped_problem)

    def get_status(self):
        ret = dict()
        for k in self.options['problem_list']:
            ret[k] = '-'
        for k in self.submissions:
            if self.submissions[k]['result'] != '':
                ret[k] = self.submissions[k]['result']
        return ret

    def main(self):
        pass

if __name__ == '__main__':
    colorama.init()
    program = IO.IO(Main)
    program.start()