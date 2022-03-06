# DDJ-pre-judge-system
A program that runs code locally for DanDanJudge

## 製作動機
因為我在復旦程式設計班身為一個進階助教，
看到沒有好的方法可以練習`APCS`的賽後評測，
於是我就寫了這個程式。

## 下載
從 Github 的 release 下載 `DDJ-pre-judge-system.exe` 就可以使用了

## 使用方法
打開執行檔後會先要求出入 `init file` 可以選擇輸入完整的檔名+位置，
如果在執行檔同個目錄下有`options.json`則可以直接按`enter`。

## `options.json` 範例
```json
{
    "language": "c++",
    "submit_file_name": "user.cpp",
    "submit_commands" : {
        "compile": "g++ -std=c++11 user.cpp -o user",
        "run": "./user.exe"
    },
    "main_code_path": "C:\\Codes\\Dev-cpp\\test\\main_code.cpp",
    "problem_list": {
        "A": "a520", 
        "B": "a752",
        "C": "a001"
    },
    "mode": "contest",
    "contest_info": {
        "start_time": [2022, 3, 6, 17, 30, 0, 6],
        "end_time": [2022, 3, 6, 17, 30, 10, 6]
    }
}
```
除了 `mode` 選項為 `practice` 時可以沒有 `contest_info` 以外，
其他都要出現在 `options.json` 裡面。
值得注意的是 `start_time` 裡面包的是 `[年, 月, 日, 幾點, 幾分, 幾秒, 星期幾]`。

## `main_code` 範例
雖然自訂選項裡面有 `language`，
但目前只支援 `c++`，
這裡就先只放 `c++` 的版本。

```cpp
#define __submit__

/*[SUBMIT IDS]*/

/*[USER CODE]*/

int main() {
#ifdef __A__
	SolutionA solA;
	solA.main();
#endif
#ifdef __B__
	SolutionB solB;
	solB.main();
#endif
#ifdef __C__
	SolutionC solC;
	solC.main();
#endif
}
```

`#define __submit__` 是可以讓參與競賽的人方便利用此巨集來本機測試 (範例程式碼如下)

```cpp
#include <iostream>
using namespace std;

class SolutionC {
	public:
		int main() {
			string s;
			while(cin >> s) {
				cout << "hello, " << s << '\n';
			}
		}
};

#ifndef __submit__
int main() {
	SolutionC sol;
	sol.main();
}
#endif
```

`/*[SUBMIT IDS]*/` 是他配底下的 `#ifdef __A__` 等同性質的巨集使用，
在程式碼打包完成後，
會被取代成跟題目ID有關的巨集，
這樣做為了要達到賽後只送出一次的效果，
是為了確認哪些題目是沒有程式碼的，
這樣才不會導致在線上測試時 `CE`。

