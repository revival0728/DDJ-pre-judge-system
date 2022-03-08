import json

def get_input(arg: str, tip: str =''):
    if tip == '':
        return input(f'Please input argument {arg}: ').strip()
    else:
        return input(f'Please input argument {arg} ({tip}): ').strip()

def main():
    args = {
        'language': '',
        "submit_file_name": '',
        'submit_commands' : {
            'compile': '',
            'run': ''
        },
        'main_code_path': '',
        'problem_list': {},
        'mode': '',
        'contest_info': {
            'start_time': [],
            'end_time': []
        }
    }

    args['language'] = get_input('language', 'c++, python, ...')
    args['submit_file_name'] = get_input('submit_file_name', 'user.cpp, user.py, ...')
    if args['language'] in ('c++'):
        args['submit_commands']['compile'] = get_input('compile command')
    args['submit_commands']['run'] = get_input('run command')
    args['main_code_path'] = get_input('main_code_path')
    ret = get_input('problem_list', '"a001, a002, a003", ...')
    plst = ret.split()
    for i in range(len(plst)):
        args['problem_list'][chr(65+i)] = plst[i]
    args['mode'] = get_input('mode', 'practice/contest')
    if args['mode'] == 'contest':
        for j in ['start_time', 'end_time']:
            print(f'Please input argument {j}: ')
            for i in [
                ['year', '(2022, ...)'], 
                ['month', '(1-12)'], 
                ['day', '(1-31)'], 
                ['hour', '(0-23)'], 
                ['minute', '(0-59)'], 
                ['second', '(0-59)'], 
                ['week day', '(1-7)']
            ]:
                args['contest_info'][j].append(int(get_input(i[0], i[1])))

    with open('./options.json', 'w') as jsfile:
        json.dump(args, jsfile)

if __name__ == '__main__':
    main()