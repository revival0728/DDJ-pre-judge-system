import os

def main():
    pre_cmd = 'py -m pip install {}'

    os.system(pre_cmd.format('colorama'))
    os.system(pre_cmd.format('termcolor'))
    os.system(pre_cmd.format('requests'))
    os.system(pre_cmd.format('bs4'))

    os.system('pause')

if __name__ == '__main__':
    main()