import json
import os
import requests
from bs4 import BeautifulSoup


# 加载Unicode映射表
def load_unicode_mapping(mapping_path: str = './unicode_mapping.json') -> dict:
    """
    加载Unicode映射表
    
    参数:
        mapping_path: 映射表文件路径
    返回:
        加密Unicode到原始Unicode的映射字典
    """
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        print(f"已加载Unicode映射表，共 {len(mapping)} 个映射")
        return mapping
    except Exception as e:
        print(f"加载Unicode映射表失败: {e}")
        return {}

# 解密文本
def decrypt_text(encrypted_text: str, unicode_mapping: dict) -> str:
    """
    使用Unicode映射表解密文本
    
    参数:
        encrypted_text: 加密的文本
        unicode_mapping: Unicode映射表
    返回:
        解密后的文本
    """
    result = ""
    for char in encrypted_text:
        # 获取字符的Unicode码点
        unicode_point = str(ord(char))
        # 如果在映射表中找到对应项，则替换为原始字符
        if unicode_point in unicode_mapping:
            original_unicode = unicode_mapping[unicode_point]
            result += chr(int(original_unicode))
        else:
            # 如果没有找到映射，保留原字符
            result += char
    return result

# 解密HTML内容
def decrypt_html_content(html_content: str, unicode_mapping: dict) -> str:
    """
    解密HTML内容中的加密文本
    
    参数:
        html_content: 包含加密文本的HTML内容
        unicode_mapping: Unicode映射表
    返回:
        解密后的HTML内容
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for span in soup.find_all('span', class_='xuetangx-com-encrypted-font'):
        encrypted_text = span.get_text()
        decrypted_text = decrypt_text(encrypted_text, unicode_mapping)
        span.string = decrypted_text
        # 替换加密文本的标签为普通文本
    return str(soup)

# 将HTML转换为纯文本
def html_to_plain_text(html_content: str) -> str:
    """
    将HTML内容转换为纯文本
    
    参数:
        html_content: HTML内容
    返回:
        提取的纯文本
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除脚本和样式元素
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    
    # 获取文本
    text = soup.get_text()
    
    # 处理多余的空白字符
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text


with open('data.json', 'r') as file:
    data = json.load(file)
    # print(data)
data = data['data']
font_url = data['font']
problems = data['problems']

# 加载Unicode映射表
unicode_mapping = load_unicode_mapping()

# 创建一个列表来存储所有问题的数据
all_problems_data = []

for problem in problems:
    index = problem.get('index', None)
    content = problem.get('content', None)
    Type = content.get('Type', None)
    Body = content.get('Body', None)
    Options = content.get('Options', None)

    
    print(f"Problem Index: {index}")
    print(f"Problem Type: {Type}")
    # print(f"Problem Body: {Body}")
    
    # 解密整个HTML内容
    decrypted_html = decrypt_html_content(Body, unicode_mapping)
    
    # 将解密后的HTML转换为纯文本
    plain_text = html_to_plain_text(decrypted_html)
    print(f"Plain Text: {plain_text}")
    
    # 处理选项
    options_data = {}
    if Options:
        print("Problem Options:")
        for option in Options:
            key = option.get('key', '')
            value = option.get('value', '')
            
            # 解密选项值
            decrypted_value = decrypt_html_content(value, unicode_mapping)
            
            # 将选项转换为纯文本
            option_text = html_to_plain_text(decrypted_value)
            print(f"  Option {key} (Plain Text): {option_text}")
            options_data[key] = option_text
    
    # 准备答案和解释
    answer = None
    explain = None
    user = problem.get('user', None)
    if user:
        if user.get('is_right', None):
            answer = user.get('answer', None)
            explain = user.get('explain', None)
            print(f"Answers: {answer}")
            print(f"Explanation: {explain}")
    
    # 将当前问题的数据添加到列表
    problem_data = {
        "index": index,
        "type": Type,
        "question": plain_text,
        "options": options_data,
        "answers": answer,
        "explanation": explain
    }
    all_problems_data.append(problem_data)
    
    print("=" * 80)

# 将所有问题数据保存为JSON文件
with open('problems_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_problems_data, f, ensure_ascii=False, indent=4)
    print(f"已将 {len(all_problems_data)} 个问题的数据保存到 problems_data.json")

print(f"Font: {font_url}")

