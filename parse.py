import os

keywords = {
    "method_start":"CODE_UNIT_STARTED",
    "method_end":"CODE_UNIT_FINISHED",
    "exe_start":"EXECUTION_STARTED",
    "exe_end":"EXECUTION_FINISHED",
    "prof_start":"CUMULATIVE_PROFILING_BEGIN",
    "prof_end":"CUMULATIVE_PROFILING_END"
}
html_escape_chars = {
    "<": "&lt;",
    ">": "&gt;",
    #"&": "&amp;",
    "\"": "&quot;",
    "'": "&#39;",
    "`": "&#96;",
    "/": "&#47;"
    # Add more HTML escape characters as needed
}

html_init = ""
html_end = ""

# This function is used to write the html content
def write_file(folder_path,filename,file_content):
    with open(os.path.join(folder_path,filename),'w') as file:
        file.write('\n'.join(file_content))

# Open log file from specified folder
def open_file(folder_path,filename):
    file_content = ""
    full_file_path = os.path.join(folder_path,filename)
    with open(full_file_path,'r') as file:
        file_content = file.read()
    return file_content

# Convert String to list of lines
def get_lines(file_content):
    if file_content is not None:
        all_lines = file_content.split("\n")
        return all_lines
    return None

# Find presence of string in the text
def find_str(string_to_find,content):
    if content is not None and string_to_find in content:
        return True
    return False

# Find the method Name from the string
def extract_method_name(line):
    if line is not None:
        parts = line.split("|")
        if len(parts) > 0:
            return parts[len(parts)-1]
    return None

# get start line and end line for the method
def chunk_method(method_name,lines,index,start_word,end_word):
    start_line = -1
    end_line = -1
    for curr_line_no,line in enumerate(lines):
        if curr_line_no >= index:
            if find_str(start_word,line) and find_str(method_name,line):
                start_line = curr_line_no
            elif start_line > -1 and find_str(end_word,line) and find_str(method_name,line):
                end_line = curr_line_no
            elif start_line > -1 and find_str(end_word,line) and start_word in [keywords["exe_start"],keywords["prof_start"]]:
                end_line = curr_line_no
        if start_line > -1 and end_line > -1:
            break
    return start_line,end_line

def get_chunk_words(line):
    start_word = ""
    end_word = ""
    chunk_stat = False
    if line is not None:
        if find_str(keywords["method_start"],line):
            return keywords["method_start"],keywords["method_end"],True
        if find_str(keywords["exe_start"],line):
            return keywords["exe_start"],keywords["exe_end"],True
        if find_str(keywords["prof_start"],line):
            return keywords["prof_start"],keywords["prof_end"],True
    return start_word,end_word,chunk_stat

def create_bundles(all_lines):
    bundles = []
    for index,line in enumerate(all_lines):
        start_word,end_word,chunk_stat = get_chunk_words(line)
        if chunk_stat:
            method_name = extract_method_name(line)
            start_line,end_line = chunk_method(method_name,all_lines,index,start_word,end_word)
            bundles.append({
                "method_name":method_name,
                "start_line":start_line,
                "end_line":end_line
                }
            )
    return bundles

def html_escape(text):
    for char,escape_char in html_escape_chars.items():
        text = text.replace(char,escape_char)
    return text

def get_html_line(current_line,line,bundles):
    line = html_escape(line)
    for index,d in enumerate(bundles):
        if d["start_line"] == current_line:
            return '<button class="accordion">'+d["method_name"]+'</button><div class="panel"><br/>'+line
        elif d["end_line"] == current_line:
            return line +"<br/></div>"
    return line+"<br/>"

def generate_new_content(all_lines,bundles):
    lines = []
    current_line = -1
    lines.append(html_init)
    for line in all_lines:
        current_line = current_line + 1
        lines.append(get_html_line(current_line,line,bundles))
    lines.append(html_end)
    return lines

if __name__ == "__main__":
    folder_path = "<<Provide path to folder>>"
    filename = "<<provide log file name>>"

    output_file_name = "output2.html"

    file_content = open_file(folder_path,filename)
    all_lines = get_lines(file_content)
    bundles = create_bundles(all_lines)
    print(bundles)
    newlines = generate_new_content(all_lines,bundles)
    write_file(folder_path,output_file_name,newlines)
