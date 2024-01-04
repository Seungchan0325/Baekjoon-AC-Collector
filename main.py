from time import sleep
import requests

# TODO token의 값을 bojautologin 토큰 값으로 바꿔야함
# Chrome 120.0.6099.200 버전 기준
# 1. https://www.acmicpc.net/ 를 로그인 상태 유지로 로그인
# 2. 개발자 모드 킨다. (Windows 단축키 F12, Mac 단축키 alt + cmd + i)
# 3. Application (어플리케이션) 탭을 선택
# 4. Storage (저장용량) 안의 Cookies (쿠키) 안에 https://www.acmicpc.net 를 클릭한다.
# 5. 이름이 bojautologin 행의 '값'을 복사하여 아래 YOUR bojautologin token 을 대체한다.
token = "YOUR bojautologin token"

# TODO 아래 user name 을 본인의 백준 닉네임(핸들)로 대체해야함
user_name = "user name"

def get_solution_ids(html: str) -> list[int]:
    ret = []
    idx = html.find("solution_ids")
    stack = 0
    while html[idx] != ';':
        if html[idx] == '[':
            stack += 1
            if stack == 2:
                id_s = ''
                idx += 1
                while html[idx] != ',':
                    id_s += html[idx]
                    idx += 1
                ret.append(int(id_s))
        elif html[idx] == ']':
            stack -= 1
        idx += 1
    return ret

def get_next_page(html: str) -> str:
    idx = html.find('다음 페이지')
    while html[idx] != 'o':
        idx -= 1
    idx += 3
    top = ''
    while html[idx] != '"':
        top += html[idx]
        idx += 1
    return f"https://www.acmicpc.net/status?user_id={user_name}&result_id=4" + "&top=" + top

transform = [
    ("&quot;", '"'),
    ("&amp;", '&'),
    ("&lt;", '<'),
    ("&gt;", '>'),
]

def get_code(html: str) -> str:
    s = html.find('<textarea')
    while html[s] != '>':
        s += 1
    s += 1
    
    e = html.find("</textarea", s)

    ret = html[s:e]

    for old, new in transform:
        ret = ret.replace(old, new)

    return ret

def get_problem_number(html: str) -> str:
    s = html.find('</a></td><td><a href="/problem/')
    s += len('</a></td><td><a href="/problem/')
    e = html.find('"', s)
    return html[s:e]

languages = [
    ("Assembly", "S"),
    ("C++", "cpp"),
    ("C", "c"),
    ("PHP", "php"),
    ("Python", "py"),
    ("PyPy", "py"),
    ("Text", "txt"),
    ("Golfscript", "gs")
]

def get_file_extension(html: str) -> str:
    for lang, extension in languages:
        if html.find("></span></td><td>"+lang) != -1:
            return extension

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/98.0.4758.102 Safari/537.36 "
}

res = requests.get(url = "https://www.acmicpc.net", headers=header)
online_judge_token = res.cookies.get_dict()["OnlineJudge"]
cookie = {"bojautologin": token, "OnlineJudge": online_judge_token}

res = requests.get(
    url=f"https://www.acmicpc.net/status?user_id={user_name}&result_id=4",
    headers=header,
    cookies=cookie
)

cnt = {}
iter = 1
while True:
    html = res.content.decode()
    solutions = get_solution_ids(html)

    for solution in solutions:
        sleep(0.1)
        res2 = requests.get(
            url="https://www.acmicpc.net/source/"+str(solution),
            headers=header,
            cookies=cookie
        )
        html2 = res2.content.decode()

        index = 0
        problem_number = get_problem_number(html2)
        extenstion = get_file_extension(html2)
        code = get_code(html2)
        if problem_number in cnt:
            if extenstion in cnt[problem_number]:
                cnt[problem_number][extenstion] += 1
                index = cnt[problem_number][extenstion]
            else:
                cnt[problem_number][extenstion] = 0
                index = 0
        else:
            cnt[problem_number] = {}
            cnt[problem_number][extenstion] = 0
            index = 0
        
        filename = str(problem_number) + "_" + str(index) + "." + extenstion
        with open("src/" + filename, 'w') as f:
            f.write(code)
            if not problem_number or not extenstion:
                f.writelines(f"\nUnknown problem. sumbmit number: {solution}")

        
        print(f"Saved {filename}")

    next = get_next_page(html)
    print(next)

    input("Press to continue.")

    res = requests.get(
        url=next,
        headers=header,
        cookies=cookie
    )
