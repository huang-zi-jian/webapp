from jieba import analyse
import pynlpir
"""
please run Create_addWords.py to create a add-word list thus 
it will easy to match the key word you just spider load
"""


def slice_sentence(line):
    """
    to slice a sentence i hope loop it outside
    :param line: a sentence —— can long or short
    :return: the add-word shortcut_list
    """
    pynlpir.open()
    list1 = pynlpir.get_key_words(line, 10)
    list2 = analyse.extract_tags(line, topK=10, allowPOS=('n', 'vn', 'v', 'a', 'd', 'vd', 'un'))
    list3 = analyse.textrank(line, topK=10, allowPOS=('n', 'vn', 'v', 'a', 'd', 'vd', 'un'))
    temp = set(list1).union(set(list2)).union(set(list3))
    return list(temp)


def write_file(path, add_words):
    with open(path, 'w', encoding='utf-8') as file:
        for word in add_words:
            file.writelines(word + " 1.0\n")


def read_file(path):
    add_words = set()
    with open(path, encoding='utf-8') as file:
        string_list = file.readlines()
        for sentence in string_list:
            sentence.replace('\n', '')
            sentence.replace('<br/>', '')
            sentence.replace('"', '')
            add_words.update(slice_sentence(sentence))

    return add_words


if __name__ == '__main__':
    write_file('addword.txt', read_file('../require_data.txt'))
