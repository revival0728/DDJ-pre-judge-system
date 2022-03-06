#!python3.9

import requests as rqs
from bs4 import BeautifulSoup as bsp

class GetProblem:
    def __init__(self):
        self.blocks = dict()
        self.test_data = dict()

        self.url = 'https://dandanjudge.fdhs.tyc.edu.tw/'
        self.pid = 'a001'

    def make_md(self, problem: dict):
        return \
        f'''\
# {problem['title']}
---
## 題目敘述
{problem['content']}
---
## 輸入格式
{problem['input']}
---
## 輸出格式
{problem['output']}
---
## 範例輸入
{problem['sample_input']}
---
## 範例輸出
{problem['sample_output']}
---
## 測資資訊
{problem['information']}
---
## 提示
{problem['hint']}
---
## 題目資訊
### 標籤
{problem['tag']}
### 出處
{problem['source']}
    '''

    def make_html(self, innerHTML):
        MathJax_settings = '''\
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
tex2jax: {inlineMath: [['$','$']]}
});
</script>
'''
        return f'''\
<!DOCTYPE html>
<head>
<meta charset='utf-8'>
<style>
pre {"{background-color: rgb(217, 217, 217); padding: 10px; border-radius: 3px;}"}
a {"{color: blue;}"}
hr {"{background-color: black;}"}
p {"{font-family: Arial;}"}
h1, h2 {"{font-family: Arial; background-color: rgb(230, 230, 230); padding: 5px; border-radius: 3px;}"}
</style>
{MathJax_settings}
<script type="text/javascript" async
src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>
</head>
<body>
{innerHTML}
</body>
    '''

    def process_textp(self, content, pkeys: list, name: str): # 題目敘述、輸入說明、輸出說明、提示
        pkeys_id = 0
        for id in [0, 1, 2, 5]:
            i = content[id]
            ok = False
            data = i.find_all(name=name)
            if len(data) != 0:
                for j in data:
                    img = j.find(name='img')
                    if not (img is None):
                        self.blocks[pkeys[pkeys_id]] += (f"![image]({img.get('src')})" + '\n\n')
                    else:
                        self.blocks[pkeys[pkeys_id]] += (j.text.strip('#') + '\n\n')
                    ok = True
            else:
                self.blocks[pkeys[pkeys_id]] += i.text.strip('#') + '\n\n'
                ok = True

            if ok:
                pkeys_id += 1

    def process_textpre(self, content, pkeys: list, name: str): # 範例輸入、範例輸出
        pkeys_id = 0
        for i in content:
            ok = False
            text = '```\n'
            for j in i.find_all(name=name):
                text_list = j.text.strip().split('\n')
                for t in text_list:
                    text += t.strip() + '\n'
                ok = True

            if ok:
                self.test_data[pkeys[pkeys_id]] += text
                self.blocks[pkeys[pkeys_id]] += text + '```\n'
                pkeys_id += 1
        for k in self.test_data:
            self.test_data[k] = self.test_data[k][3:]

    def process_tag(self, content): # 標籤
        material = content[-2].find_all(name='a')
        for i in material:
            self.blocks['tag'] += f"[{i.text}]({self.url+ i.get('href')[1:].replace(' ', '%')}) "

    def process_source(self, content): # 出處(作者)
        material = content[-1].find_all(name='a')
        if len(material) == 1:
            for i in material:
                self.blocks['source'] += f"[{i.text}]({self.url + i.get('href')[1:].replace(' ', '%')})"
        elif len(material) >= 2:
            for i in range(0, len(material)-1):
                self.blocks['source'] += f"[{material[i].text}]({self.url + material[i].get('href')[1:].replace(' ', '%')})"
            self.blocks['source'] += f" authered by [{material[-1].text}]({self.url + material[-1].get('href')[1:].replace(' ', '%')})"

    def process_title(self, content): # 題目名稱
        material = content.find_all(name='div', attrs={'class', 'h1'})
        self.blocks['title'] = material[0].text[0:5] + ' ' +material[0].find(name='span').text

    def process_information(self, content): # 測資資訊
        material = content.find_all(name='div', attrs={'class', 'panel-body'})
        info = material[-1].get_text(strip=True).split()
        self.blocks['information'] += f"```\n{info[0]}{info[1]}MB\n```\n```\n"
        del info[0]
        del info[0]
        for i in range(0, len(info)-1, 5):
            M_index = info[i].find('M')
            if M_index == -1:
                M_index = info[i].find('K')
            if i != 0:
                self.blocks['information'] += info[i][0:M_index+1] + '\n'
                self.blocks['information'] += f"{info[i][M_index+1:]} {info[i+1]}{info[i+2]} {info[i+3]}{info[i+4]} "
            else:
                self.blocks['information'] += f"{info[i][2:]} {info[i+1]}{info[i+2]} {info[i+3]}{info[i+4]} "
        self.blocks['information'] += info[-1] + '\n```\n\n'

    def _init(self):
        self.blocks = {  # texts // str
            'title': '',
            'content': '',
            'input': '',
            'output': '',
            'sample_input': '',
            'sample_output': '',
            'hint': '',
            'tag': '',
            'information': '',
            'source': ''
        }
        self.test_data = {'sample_input': '', 'sample_output': ''}

    def save_problem(self, _file_name, _save_path) -> str:
        to_html_res = rqs.post('https://api.github.com/markdown', json= {
            'text': self.make_md(self.blocks),
            'mode': 'markdown'
        })

        if _save_path[-1] != '/':
            _save_path += '/'

        if _file_name[-5:] != '.html':
            _file_name += '.html'

        with open(_save_path + _file_name, 'w', encoding='utf-8') as f:
            f.write(self.make_html(to_html_res.text))

        return f'saved problem {self.blocks["title"]}'

    def get_problem(self, _pid):
        self.url, self.pid = 'https://dandanjudge.fdhs.tyc.edu.tw', _pid
        response = None
        self._init()

        try:
            response = rqs.get(f'{self.url}/ShowProblem?problemid={self.pid}')
        except Exception:
            response = rqs.get('https://dandanjudge.fdhs.tyc.edu.tw/ShowProblem?problemid=a001')
        html = bsp(response.text, 'html.parser')
        content = html.find_all(name='div', attrs={'class', 'problembox'})

        self.process_textp(content, ['content', 'input', 'output', 'hint'], 'p')
        self.process_textpre(content, ['sample_input', 'sample_output'], 'pre')
        self.process_tag(content)
        self.process_source(content)
        self.process_title(html)
        self.process_information(html)

        for i in self.blocks:
            if self.blocks[i].strip() == '':
                self. blocks[i] = '未提供此資訊\n\n'

    def get_test_data(self):
        return {
            'input': self.test_data['sample_input'], 
            'output': self.test_data['sample_output']
        }

if __name__ == '__main__':
    test = GetProblem()
    test.get_problem('a752')
    test.save_problem('test', './problem')