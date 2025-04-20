import json
import hashlib
from typing import Dict, List
import fontTools.ttLib as ttLib
import requests
import os

def is_chinese_char(unicodes: List[int]) -> bool:
    """检查 Unicode 码点是否属于中文字符范围"""
    return any(0x4E00 <= code <= 0x9FFF for code in unicodes)

def hash_glyph(commands: List) -> str:
    """计算字形路径命令的 SHA-1 哈希值"""
    command_str = str(commands).encode('utf-8')
    return hashlib.sha1(command_str).hexdigest()

def load_font(font_path: str):
    """加载字体文件"""
    try:
        return ttLib.TTFont(font_path)
    except Exception as e:
        raise Exception(f"加载字体文件失败: {e}")

def extract_glyph_mapping(font_path: str) -> Dict[str, int]:
    """
    从字体文件中提取字形哈希到Unicode的映射
    
    参数:
        font_path: 字体文件路径
    返回:
        字形哈希到Unicode的映射字典
    """
    # 加载字体
    font = load_font(font_path)
    
    # 获取字形映射
    glyphs_to_uni = {}
    
    cmap = font.getBestCmap()
    
    for unicode_val, glyph_name in cmap.items():
        glyph = font.getGlyphSet().get(glyph_name)
        if glyph and hasattr(glyph, 'draw'):
            # 使用一个自定义路径对象来捕获绘制命令
            path_collector = PathCollector()
            glyph.draw(path_collector)
            
            glyph_hash = hash_glyph(path_collector.commands)
            
            # 如果哈希已存在则跳过 (处理碰撞)
            if glyph_hash not in glyphs_to_uni:
                glyphs_to_uni[glyph_hash] = unicode_val
    
    return glyphs_to_uni

def generate_glyph_mapping(font_path: str) -> None:
    """
    生成字形哈希到 Unicode 的映射并保存为 JSON 文件
    
    参数:
        font_path: 字体文件路径
    """
    try:
        glyphs_to_uni = extract_glyph_mapping(font_path)
        
        # 写入 JSON 文件
        with open('./original_glyph_to_uni.json', 'w', encoding='utf-8') as f:
            json.dump(glyphs_to_uni, f, 
                     ensure_ascii=False,
                     indent=2)
        
        print(f"成功生成字形映射，共 {len(glyphs_to_uni)} 个字符")
    
    except Exception as e:
        print(f"生成字形映射失败: {e}")

def download_font(font_url: str, save_dir: str = './') -> str:
    """
    下载加密字体文件，保留原始文件名
    
    参数:
        font_url: 字体文件URL
        save_dir: 保存目录
    返回:
        字体文件保存路径
    """
    try:
        response = requests.get(font_url, stream=True)
        response.raise_for_status()
        
        # 从URL中提取文件名
        file_name = os.path.basename(font_url)
        if '?' in file_name:  # 处理URL中可能包含的查询参数
            file_name = file_name.split('?')[0]
        
        # 如果没有提取到文件名，使用默认名称
        if not file_name or not file_name.endswith(('.woff', '.ttf', '.otf')):
            file_name = 'encrypted_font.woff'
            
        # 构建完整的保存路径
        save_path = os.path.join(save_dir, file_name)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"字体文件已下载到: {save_path}")
        return save_path
    except Exception as e:
        print(f"下载字体文件失败: {e}")
        return None

def generate_encrypted_mapping(font_path: str, output_path: str = './encrypted_glyph_to_uni.json') -> Dict:
    """
    生成加密字体的字形哈希到Unicode的映射
    
    参数:
        font_path: 加密字体文件路径
        output_path: 输出JSON文件路径
    返回:
        字形哈希到Unicode的映射字典
    """
    try:
        glyphs_to_uni = extract_glyph_mapping(font_path)
        
        # 写入 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(glyphs_to_uni, f, 
                     ensure_ascii=False,
                     indent=2)
        
        print(f"成功生成加密字体字形映射，共 {len(glyphs_to_uni)} 个字符")
        return glyphs_to_uni
    
    except Exception as e:
        print(f"生成加密字体字形映射失败: {e}")
        return {}

def create_unicode_mapping(original_mapping_path: str, encrypted_mapping_path: str, output_path: str = './unicode_mapping.json') -> Dict:
    """
    创建加密Unicode到正确Unicode的映射表
    
    参数:
        original_mapping_path: 原始字体字形到Unicode的映射文件路径
        encrypted_mapping_path: 加密字体字形到Unicode的映射文件路径
        output_path: 输出映射表的文件路径
    返回:
        加密Unicode到正确Unicode的映射字典
    """
    try:
        # 加载原始映射和加密映射
        with open(original_mapping_path, 'r', encoding='utf-8') as f:
            original_mapping = json.load(f)
        
        with open(encrypted_mapping_path, 'r', encoding='utf-8') as f:
            encrypted_mapping = json.load(f)
        
        # 创建反向映射（字形哈希 -> 原始Unicode）
        hash_to_original_unicode = original_mapping
        
        # 创建反向映射（字形哈希 -> 加密Unicode）
        hash_to_encrypted_unicode = encrypted_mapping
        
        # 创建加密Unicode到原始Unicode的映射
        unicode_mapping = {}
        
        # 对于每个字形哈希，找到对应的加密Unicode和原始Unicode
        for glyph_hash in hash_to_original_unicode:
            if glyph_hash in hash_to_encrypted_unicode:
                encrypted_unicode = hash_to_encrypted_unicode[glyph_hash]
                original_unicode = hash_to_original_unicode[glyph_hash]
                
                # 将加密Unicode映射到原始Unicode
                unicode_mapping[str(encrypted_unicode)] = original_unicode
        
        # 写入JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unicode_mapping, f, 
                     ensure_ascii=False,
                     indent=2)
        
        print(f"成功创建Unicode映射表，共 {len(unicode_mapping)} 个映射")
        return unicode_mapping
    
    except Exception as e:
        print(f"创建Unicode映射表失败: {e}")
        return {}

# 实现一个简单的路径收集器
class PathCollector:
    def __init__(self):
        self.commands = []
    
    def moveTo(self, p):
        self.commands.append(('moveTo', p[0], p[1]))
    
    def lineTo(self, p):
        self.commands.append(('lineTo', p[0], p[1]))
    
    def curveTo(self, *points):
        self.commands.append(('curveTo', *[(p[0], p[1]) for p in points]))
    
    def qCurveTo(self, *points):
        self.commands.append(('qCurveTo', *[(p[0], p[1]) for p in points]))
    
    def closePath(self):
        self.commands.append(('closePath',))

# 使用示例:
if __name__ == "__main__":
    with open('data.json', 'r') as file:
        data = json.load(file)
    data = data['data']
    font_url = data['font']
    
    # 原始映射文件路径
    original_mapping_path = './original_glyph_to_uni.json'
    
    # 如果原始映射文件不存在，则生成
    if not os.path.exists(original_mapping_path):
        print("原始字形映射文件不存在，开始生成...")
        original_font_path = './SourceHanSansSC-VF.ttf'  # 请确保此路径指向您的原始字体文件
        generate_glyph_mapping(original_font_path)
    
    # 下载加密字体
    encrypted_font_path = download_font(font_url, './')
    
    if encrypted_font_path:
        # 生成加密字体映射
        encrypted_mapping_path = './encrypted_glyph_to_uni.json'
        generate_encrypted_mapping(encrypted_font_path, encrypted_mapping_path)
        
        # 创建Unicode映射表
        unicode_mapping = create_unicode_mapping(original_mapping_path, encrypted_mapping_path)
        
        print("映射表生成完成！可以使用unicode_mapping.json将加密字符转换为正确的Unicode")
