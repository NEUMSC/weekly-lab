from pypinyin import slug, Style

if __name__ == '__main__':
    with open('data.csv', 'r') as f:
        lines = f.readlines()

    new_lines = [lines[0]]
    for line in lines:
        new_lines.append(slug(line, style=Style.NORMAL, separator=''))

    with open('data.csv', 'w') as f:
        f.writelines(new_lines)
