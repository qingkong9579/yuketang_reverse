import requests
import json
import re
import time
import sys

def make_request_with_rate_limit(url, json_data, headers, max_retries=3):
    """处理请求，自动处理速率限制并重试"""
    for retry in range(max_retries):
        response = requests.post(url, json=json_data, headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code != 429:
            return response
        
        # 处理 429 错误
        detail = response.json().get('detail', '')
        print(f"速率限制: {detail}")
        wait_time = 5  # 默认等待5秒
        
        # 尝试从错误消息中提取等待时间
        match = re.search(r'Expected available in (\d+\.?\d*) seconds', detail)
        if match:
            wait_time = float(match.group(1)) + 2  # 加2秒作为缓冲
        
        print(f"等待 {wait_time:.1f} 秒后重试... (尝试 {retry+1}/{max_retries})")
        
        # 实现倒计时显示
        total_seconds = int(wait_time)
        for remaining in range(total_seconds, 0, -1):
            sys.stdout.write(f"\r剩余等待时间: {remaining} 秒...")
            sys.stdout.flush()
            time.sleep(1)
        
        # 清除倒计时行并显示继续执行的信息
        sys.stdout.write("\r等待完成，正在重试请求...                \n")
        sys.stdout.flush()
    
    # 如果所有重试都失败，返回最后一次响应
    return response

post_url = 'https://www.yuketang.cn/mooc-api/v1/lms/exercise/problem_apply/'
# {"classroom_id":25012730,"problem_id":54710287,"answer":["A"]}

headers = {
    'authority': 'www.yuketang.cn',
    'method': 'POST',
    'path': '/mooc-api/v1/lms/exercise/problem_apply/',
    'scheme': 'https',
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh,zh-CN;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'classroom-id': '25012730',
    'content-type': 'application/json;charset=UTF-8',
    'cookie': 'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221957ac5e45eb33-084f0329161f9b-4c657b58-2621440-1957ac5e45f2034%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk1N2FjNWU0NWViMzMtMDg0ZjAzMjkxNjFmOWItNGM2NTdiNTgtMjYyMTQ0MC0xOTU3YWM1ZTQ1ZjIwMzQifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%221957ac5ecfdc76-08daeab826c4cb-4c657b58-2621440-1957ac5ecfe2043%22%7D; _did=web_6945855734EA1758; UM_distinctid=19637e0379845-0e4e52b96771eb-4c657b58-280000-19637e0379928d7; CNZZDATA1281406241=59515539-1744694163-%7C1744694706; _ga=GA1.2.1001135291.1744717443; django_language=zh-cn; uv_id=2686; university_id=2686; platform_id=3; classroomId=25012730; classroom_id=25012730; xtbz=ykt; platform_type=0; login_type=WX; csrftoken=7nPEcUW1LwNSmsvE9F56pikjeLPvwMue; sessionid=tkti71cba25so2nd9q8zx872983cqwy7',
    'origin': 'https://www.yuketang.cn',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.yuketang.cn/v2/web/cloud/student/exercise/25012730/63114755/12460269',
    'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'university-id': '2686',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'uv-id': '2686',
    'x-client': 'web',
    'x-csrftoken': '7nPEcUW1LwNSmsvE9F56pikjeLPvwMue',
    'xt-agent': 'web',
    'xtbz': 'ykt'
}
json_data = {
    "classroom_id": 25012730,
    "problem_id": 54710288,
    "answer": ["A", "B"],
}
with open('data.json', 'r') as file:
    data = json.load(file)
    # print(data)
data = data['data']
font_url = data['font']
problems = data['problems']
# 从第80个题开始处理
# problems = problems[80:]
for problem in problems:
    index = problem.get('index', None)
    content = problem.get('content', None)
    ProblemID = content.get('ProblemID', None)
    Type = content.get('Type', None)
    
    # 获取所有可用选项
    Options = content.get('Options', None)
    options_keys = []
    if Options:
        print("Problem Options:")
        for option in Options:
            key = option.get('key', '')
            options_keys.append(key)
    
    print(f"\n处理题目 {index}, ID: {ProblemID}, 类型: {Type}")
    print(f"可用选项: {options_keys}")
    
    found_answer = False
    if Type == 'SingleChoice':
        # 依次尝试每个选项
        for option_key in options_keys:
            answer = [option_key]
            print(f"尝试答案: {answer}")
            
            json_data = {
                "classroom_id": 25012730,
                "problem_id": ProblemID,
                "answer": answer,
            }
            
            response = make_request_with_rate_limit(post_url, json_data, headers)
            
            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                print(response_json['data'])
                
                if response_json['data']['is_correct']:
                    print(f"✓ 找到正确答案: {answer}")
                    found_answer = True
                    break
                else:
                    print(f"✗ 答案错误: {answer}")
                    time.sleep(1)  # 等待1秒再尝试下一个选项
            else:
                print(f"请求失败，状态码: {response.status_code}")
        
        if not found_answer:
            print(f"警告：未能找到题目 {index} (ID: {ProblemID}) 的正确答案")
    elif Type == 'MultipleChoice':
        # 提交整个选项列表
        answer = options_keys
        print(f"尝试答案: {answer}")
        json_data = {
            "classroom_id": 25012730,
            "problem_id": ProblemID,
            "answer": answer,
        }
        
        response = make_request_with_rate_limit(post_url, json_data, headers)
        
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            my_answers = response_json['data']['my_answers']
            # 提取正确答案
            correct_answers = [key for key, value in my_answers.items() if value]
            # 提取错误答案
            wrong_answers = [key for key, value in my_answers.items() if not value]
            
            # 重新提交正确答案
            json_data = {
                "classroom_id": 25012730,
                "problem_id": ProblemID,
                "answer": correct_answers,
            }
            response = make_request_with_rate_limit(post_url, json_data, headers)
            print(f"状态码: {response.status_code}")
            response_json = response.json()
            if response_json['data']['is_correct']:
                print(f"✓ 找到正确答案: {correct_answers}")
                found_answer = True
            else:
                print(f"✗ 答案错误: {correct_answers}")
    elif Type == 'Judgement':
        # 依次尝试每个选项
        for option_key in options_keys:
            answer = [option_key]
            print(f"尝试答案: {answer}")
            
            json_data = {
                "classroom_id": 25012730,
                "problem_id": ProblemID,
                "answer": answer,
            }
            
            response = make_request_with_rate_limit(post_url, json_data, headers)
            
            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                print(response_json['data'])
                
                if response_json['data']['is_correct']:
                    print(f"✓ 找到正确答案: {answer}")
                    found_answer = True
                    break
                else:
                    print(f"✗ 答案错误: {answer}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
        
        if not found_answer:
            print(f"警告：未能找到题目 {index} (ID: {ProblemID}) 的正确答案")