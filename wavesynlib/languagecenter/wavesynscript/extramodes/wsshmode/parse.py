# from .pattern import item_prog
import re
from wavesynlib.languagecenter.python.pattern import string as string_pattern



word_pattern = r"(?P<WORD>[^\s'\"]+)"
item_pattern = f"{string_pattern}|{word_pattern}"
item_prog = re.compile(item_pattern, re.S)
brbs_prog = re.compile(r"\)+$")



def split(command):
    result = []
    while command:
        command = command.lstrip()
        match = item_prog.match(command)
        if match is None:
            break
        match_str = match.group(0)
        if match.lastgroup == "WORD":
            if match_str.startswith("$(") and len(match_str) > 2:
                result.extend([match_str[:2], match_str[2:]])
            elif match_str.endswith(")"):
                search = brbs_prog.search(match_str)
                result.append(match_str[:search.start()])
                result.extend([*match_str[search.start():]])
            else:
                result.append(match_str)
        elif match.lastgroup == "STRING":
            result.append(eval(match_str))
        else:
            raise ValueError("Token not supported.")
        command = command[match.end():]
    return result



def group(token_list):
    result = [[""]]
    
    def _group_cmdsubs(token_list, start):
        result = ["$"]
        consume = 0
        assert token_list[start].startswith("$(")
        index = start + 1
        while index < len(token_list):
            token = token_list[index]
            if token.startswith("$("):
                cons, subs = _group_cmdsubs(token_list, index)
                result.append(subs)
                index += cons+1
                consume += cons+1
                continue
            if token == ")":
                consume += 1
                break
            result.append(token)
            index += 1
            consume += 1
        return consume, result
    
    index = 0
    while index < len(token_list):
        token = token_list[index]
        if token == "|":
            result.append(["|"])
            index += 1
            continue
        if token.startswith("$("):
            cons, subs = _group_cmdsubs(token_list, index)
            result[-1].append(subs)
            index += cons + 1
            continue
        result[-1].append(token)
        index += 1
    return result



if __name__ == "__main__":
    pass
