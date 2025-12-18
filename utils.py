import re
import pdb
def replace_latex_math(latex_text:str):
    """
    更健壮的替换函数，处理可能的嵌套和复杂情况
    """
    # 创建副本以避免修改原始字符串
    result = latex_text
    # 处理行内公式：\( ... \) 转换为 $ ... $
    result = re.sub(r'\\\((.*?)\\\)', r'$\1$', result)
    # 处理行内公式：$ ... $ 保持不变（已经是 Markdown 格式）
    # 这里主要是处理其他格式的 LaTeX 公式
    # 处理行间公式：\[ ... \] 转换为 $$ ... $$
    result = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', result)
    # 处理行间公式：$$ ... $$ 保持不变
    # 这里主要是处理其他格式的 LaTeX 公式
    # 处理环境公式：\begin{equation} ... \end{equation}
    result = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', r'$$\1$$', result, flags=re.DOTALL)
    # 处理环境公式：\begin{align} ... \end{align}
    result = re.sub(r'\\begin\{align\}(.*?)\\end\{align\}', r'$$\1$$', result, flags=re.DOTALL)
    # 处理环境公式：\begin{gather} ... \end{gather}
    result = re.sub(r'\\begin\{gather\}(.*?)\\end\{gather\}', r'$$\1$$', result, flags=re.DOTALL)
    # 处理环境公式：\begin{multline} ... \end{multline}
    result = re.sub(r'\\begin\{multline\}(.*?)\\end\{multline\}', r'$$\1$$', result, flags=re.DOTALL)
    result = result.replace("$ ","$")
    result = result.replace(" $","$")
    result = result.replace("\]","$$")
    result = result.replace("\[","$$")
    return result

def parse_bibtex(bibtex_str):
    """解析BibTeX字符串，提取元数据"""
    # 提取字段
    fields = {}

    # 匹配字段的正则表达式
    field_pattern = r'(\w+)\s*=\s*{([^}]*)}'

    matches = re.findall(field_pattern, bibtex_str)
    for field_name, field_value in matches:
        fields[field_name.lower()] = field_value.strip()

    return fields

def format_authors_bibtex(authors_str):
    """格式化作者姓名（从BibTeX格式转换）"""
    if not authors_str:
        return ""

    # 分割作者
    authors = [author.strip() for author in authors_str.split(' and ')]

    # 如果作者数量超过3个，只显示前3个，然后加 "et al."
    if len(authors) > 3:
        formatted_authors = []
        for i, author in enumerate(authors[:3]):
            # 处理 "姓, 名" 格式或 "名 姓" 格式
            if ',' in author:
                # 格式：Last, First
                parts = author.split(',')
                if len(parts) >= 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # 处理中间名
                    first_parts = first_name.split()
                    if len(first_parts) > 1:
                        # 将中间名缩写，但不加点
                        abbreviated_first = ' '.join([name[0] for name in first_parts])
                        formatted_author = f"{last_name} {abbreviated_first}"
                    else:
                        # 只有一个名字，取首字母但不加点
                        formatted_author = f"{last_name} {first_name[0]}" if first_name else last_name
                else:
                    formatted_author = author
            else:
                # 格式：First Last
                parts = author.split()
                if len(parts) >= 2:
                    last_name = parts[-1]
                    first_names = parts[:-1]
                    # 将名字缩写，但不加点
                    abbreviated_first = ' '.join([name[0] for name in first_names])
                    formatted_author = f"{last_name} {abbreviated_first}"
                else:
                    formatted_author = author

            formatted_authors.append(formatted_author)

        # 用逗号连接前3个作者，然后加 "et al."
        return ", ".join(formatted_authors) + ", et al."
    else:
        formatted_authors = []
        for author in authors:
            # 处理 "姓, 名" 格式或 "名 姓" 格式
            if ',' in author:
                # 格式：Last, First
                parts = author.split(',')
                if len(parts) >= 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # 处理中间名
                    first_parts = first_name.split()
                    if len(first_parts) > 1:
                        # 将中间名缩写，但不加点
                        abbreviated_first = ' '.join([name[0] for name in first_parts])
                        formatted_author = f"{last_name} {abbreviated_first}"
                    else:
                        # 只有一个名字，取首字母但不加点
                        formatted_author = f"{last_name} {first_name[0]}" if first_name else last_name
                else:
                    formatted_author = author
            else:
                # 格式：First Last
                parts = author.split()
                if len(parts) >= 2:
                    last_name = parts[-1]
                    first_names = parts[:-1]
                    # 将名字缩写，但不加点
                    abbreviated_first = ' '.join([name[0] for name in first_names])
                    formatted_author = f"{last_name} {abbreviated_first}"
                else:
                    formatted_author = author

            formatted_authors.append(formatted_author)

        # 用逗号连接作者
        if len(formatted_authors) == 1:
            return formatted_authors[0]
        else:
            return ", ".join(formatted_authors[:-1]) + ", " + formatted_authors[-1]

def format_title(title, entry_type):
    """格式化标题，并根据文献类型添加标识符"""
    if not title:
        return ""

    # 根据文献类型确定标识符
    if entry_type.lower() == 'article':
        identifier = "[J]"
    elif entry_type.lower() == 'inproceedings' or entry_type.lower() == 'conference':
        identifier = "[C]"
    elif entry_type.lower() == 'book':
        identifier = "[M]"
    elif entry_type.lower() == 'phdthesis' or entry_type.lower() == 'mastersthesis':
        identifier = "[D]"
    elif entry_type.lower() == 'techreport':
        identifier = "[R]"
    elif entry_type.lower() == 'patent':
        identifier = "[P]"
    else:
        identifier = "[Z]"  # 其他未定义类型

    # 确保标题以句点结束
    if not title.endswith('.'):
        title += '.'

    return title.strip('.') + identifier + '.'

def markdown_postprocess(content):
    """
    高级Markdown后处理函数：
    1. 确保##开头的标题行前面有空行
    2. 确保table数字开头的行后面有空行（兼容大小写）
    3. 确保非行首数学公式前后有且仅有一个空格（公式后是标点则不加空格）
    
    Args:
        content (str): 输入的Markdown内容
        
    Returns:
        str: 处理后的Markdown内容
    """
    lines = content.split('\n')
    processed_lines = []
    
    for i, line in enumerate(lines):
        current_line = line.rstrip()
        
        # 处理##开头的标题行
        if current_line.startswith('##'):
            # 确保标题行前面有空行（除非是文档开头）
            if processed_lines and processed_lines[-1] != '':
                processed_lines.append('')
            processed_lines.append(current_line)
            continue
        
        # 处理table数字开头的行（使用正则匹配，兼容大小写和前后空格）
        table_pattern = r'^\s*table\s*\d+'
        if re.match(table_pattern, current_line, re.IGNORECASE):
            processed_lines.append(current_line)
            # 确保table行后面有空行（除非是文档结尾）
            if i < len(lines) - 1 and lines[i+1].strip() != '':
                processed_lines.append('')
            continue
        
        # 处理数学公式的空格格式
        processed_line = format_math_formulas(current_line)
        processed_lines.append(processed_line)
    
    # 清理多余的空行（连续多个空行保留一个）
    cleaned_lines = []
    prev_empty = False
    for line in processed_lines:
        if line == '':
            if not prev_empty:
                cleaned_lines.append(line)
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
    
    return '\n'.join(cleaned_lines)

def format_math_formulas(line):
    """
    格式化行中的数学公式，确保非行首公式前后有适当的空格
    
    Args:
        line (str): 输入行
        
    Returns:
        str: 格式化后的行
    """
    # 匹配行内数学公式：$...$ 和 \(...\)
    # 使用非贪婪匹配，避免跨公式匹配
    math_pattern = r'(\$[^$]+\$)' 
    def replace_math(match):
        math_expr = match.group(1)
        start_pos = match.start()
        end_pos = match.end()
        
        # 如果是行首的公式，不处理
        if start_pos == 0:
            return math_expr
        
        # 获取公式前后的字符
        prev_char = line[start_pos - 1] if start_pos > 0 else ''
        next_char = line[end_pos] if end_pos < len(line) else ''
        
        # 标点符号集合（公式后是这些符号时不加空格）
        punctuation = ',.;:!?，。；：！？)）]】}」》'
        
        # 处理公式前面的空格
        if prev_char != ' ' and prev_char != '' and prev_char not in '({\[（【{「《':
            math_with_space = ' ' + math_expr
        else:
            math_with_space = math_expr
        
        # 处理公式后面的空格
        if (next_char != ' ' and next_char != '' and 
            next_char not in punctuation and
            next_char not in '({\[（【{「《'):
            math_with_space = math_with_space + ' '
        
        return math_with_space
    
    # 使用正则替换处理所有数学公式
    formatted_line = re.sub(math_pattern, replace_math, line)
    
    # 清理可能出现的多余空格（连续多个空格变为一个）
    formatted_line = re.sub(r' +', ' ', formatted_line)
    
    return formatted_line

def format_journal_info(journal, volume, issue, pages, year, doi=None):
    """格式化期刊信息"""
    parts = []

    if journal:
        parts.append(journal)

    if year:
        parts.append(f"{year}")

    if volume:
        if issue:
            parts.append(f"{volume}({issue})")
        else:
            parts.append(f"{volume}")

    if pages:
        # 处理页码格式，确保是连字符而不是短横线
        pages = pages.replace('--', '-').replace('–', '-').replace('—', '-')
        parts.append(f"{pages}")

    result = ", ".join(parts) + "."

    # 添加DOI（如果存在）
    if doi:
        result += f" DOI:{doi}"

    return result

def bibtex_to_gbt7714(bibtex_str):
    """将BibTeX转换为GB/T 7714格式"""
    try:
        fields = parse_bibtex(bibtex_str)

        # 提取必要字段
        authors = format_authors_bibtex(fields.get('author', ''))

        # 确定文献类型
        entry_type = 'article'  # 默认为期刊文章
        if 'booktitle' in fields and 'journal' not in fields:
            entry_type = 'inproceedings'  # 会议论文

        title = format_title(fields.get('title', ''), entry_type)
        journal = fields.get('journal', '') or fields.get('booktitle', '')
        volume = fields.get('volume', '')
        issue = fields.get('number', '') or fields.get('issue', '')
        pages = fields.get('pages', '')
        year = fields.get('year', '')
        doi = fields.get('doi', '')

        # 构建GB/T 7714格式
        gbt7714_parts = []

        if authors:
            gbt7714_parts.append(authors)

        if title:
            gbt7714_parts.append(title)

        journal_info = format_journal_info(journal, volume, issue, pages, year, doi)
        if journal_info:
            gbt7714_parts.append(journal_info)

        return " ".join(gbt7714_parts)

    except Exception as e:
        return f"转换错误: {str(e)}"

if __name__=="__main__":
     print(bibtex_to_gbt7714( '@Article{Chen2021AnatomyAware3H,\n author = {Tianlang Chen and Chengjie Fang and Xiaohui Shen and Yiheng Zhu and Zhili Chen and Jiebo Luo},\n booktitle = {IEEE transactions on circuits and systems for video technology (Print)},\n journal = {IEEE Transactions on Circuits and Systems for Video Technology},\n pages = {198-209},\n title = {Anatomy-Aware 3D Human Pose Estimation With Bone-Based Pose Decomposition},\n volume = {32},\n year = {2021}\n}\n'))
     print(bibtex_to_gbt7714( '@Article{Chen2017CascadedPN,\n author = {Yilun Chen and Zhicheng Wang and Yuxiang Peng and Zhiqiang Zhang and Gang Yu and Jian Sun},\n booktitle = {2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition},\n journal = {2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition},\n pages = {7103-7112},\n title = {Cascaded Pyramid Network for Multi-person Pose Estimation},\n year = {2017}\n}\n'))
