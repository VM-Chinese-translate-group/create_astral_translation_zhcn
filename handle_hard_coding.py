#!/usr/bin/env python3
import json, glob
import os, shutil

def copy_tree(src, dst, symlinks=False, ignore=None):
    if os.path.isfile(src):
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy2(src, dst)
        return

    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_tree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

def handle_custom_machinery(work_dir):
    machines_path = os.path.join(work_dir, "global_packs/required_data/zLaky Core/data/createastral/machines")
    
    # 键名为自定义机器的英文原文，值为翻译
    with open(os.path.join('v2.0', 'hard_coding', 'custom_machinery.json'), 'r', encoding='utf-8') as fp:
        machineries = json.load(fp)

    json_files = glob.glob(os.path.join(machines_path, "*.json"))

    for json_file in json_files:
        with open(json_file, 'r', encoding="utf-8") as fp:
            content = fp.read()
        for key, value in machineries.items():
            content = content.replace(f'"{key}"', f'"{value}"')
        with open(json_file, 'w', encoding="utf-8") as fp:
            fp.write(content)        

def find_the_matched_bracket(text, left_index):
    left_brackets =  r"[{"
    right_brackets = r"]}"
    if text[left_index] not in left_brackets: return -1
    stack = []

    for index in range(left_index, len(text)):
        if text[index] in left_brackets:
            stack.append(index)
        elif text[index] in right_brackets:
            if len(stack) == 0:
                return -1
            else:
                stack.pop()
                if len(stack) == 0:
                    return index
    return -1

def handle_ftb_quests(work_dir):
    last_chapter = os.path.join(work_dir, "config/ftbquests/quests/chapters/6_raow.snbt")

    with open(last_chapter, 'r', encoding="utf-8") as f:
        content = f.read()
    feature_str = 'quests: ['
    left_index = content.find(feature_str) + len(feature_str) - 1
    assert(content[left_index] == '[')
    right_index = find_the_matched_bracket(content, left_index)
    assert(right_index != -1 and content[right_index] == ']')
    insert_index = content.rfind('\n', left_index, right_index) + 1

    with open(os.path.join('v2.0', 'hard_coding', 'trans_acknowledgements.snbt'), 'r', encoding='utf-8') as fp:
        acknowledgements = fp.read()
    
    insert_content = acknowledgements.replace('\n', "\n\t\t")
    content = content[:insert_index] + f"\t\t{insert_content}\n" + content[insert_index:]

    with open(last_chapter, 'w', encoding="utf-8") as f:
        f.write(content)

def handle_startup_js(work_dir):
    startup_js_path = os.path.join(work_dir, "kubejs/startup_scripts/startup.js")

    with open(os.path.join('v2.0', 'hard_coding', 'startup.json'), 'r', encoding='utf-8') as fp:
        trans_dict = json.load(fp)
    
    with open(startup_js_path, 'r', encoding="utf-8") as f:
        content = f.read()
    
    for key, value in trans_dict.items():
        content = content.replace(f"Text.of('{key}", f"Text.of('{value}")
        content = content.replace(f'Text.of("{key}', f'Text.of("{value}')
        content = content.replace(f"tooltip: '{key}", f"tooltip: '{value}")
        content = content.replace(f'tooltip: "{key}', f'tooltip: "{value}')

    with open(startup_js_path, 'w', encoding="utf-8") as f:
        f.write(content)

def start_handle_hard_coding(official_dir, release_dir):

    if not os.path.isdir(official_dir):
        print("[ERROR] Please pull the repository of the official integration package to the same level directory first!")
        os._exit(-1)
    
    required_paths = [
        "kubejs/startup_scripts/startup.js",
        "config/ftbquests/quests/chapters/6_raow.snbt",
        "global_packs/required_data/zLaky Core/data/createastral/machines",
    ]

    for required_path in required_paths:
        src = os.path.join(official_dir, required_path)
        dict = os.path.join(release_dir, required_path)
        copy_tree(src, dict)

    handle_startup_js(release_dir)
    handle_custom_machinery(release_dir)
    handle_ftb_quests(release_dir)

if __name__ == "__main__":
    start_handle_hard_coding("release")
