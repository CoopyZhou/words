from flask import Flask, render_template, request, redirect, url_for
import os
import json
import datetime

app = Flask(__name__)

ebbinghaus_intervals = [1, 2, 4, 7, 15]

# ... load_words函数的代码 ...
def load_words():
    if not os.path.exists('words.txt'):
        return {}

    with open('words.txt', 'r') as file:
        loaded_words = json.load(file)

    if not loaded_words or isinstance(loaded_words, dict):
        return loaded_words

    new_words = {}
    for word, explanation in loaded_words.items():
        new_words[word] = {
            'explanation': explanation,
            'ebbinghaus_index': 0,
            'added_date': datetime.date.today().isoformat()
        }
    save_words(new_words)
    return new_words

# ... save_words函数的代码 ...
def save_words(words_to_save):
    with open('words.txt', 'w') as file:
        json.dump(words_to_save, file)

# ... update_word_review函数的代码 ...
def update_word_review(word, remembered):
    if word not in words:
        return

    if remembered:
        words[word]['ebbinghaus_index'] += 1
    else:
        words[word]['ebbinghaus_index'] = 0
        words[word]['added_date'] = datetime.date.today().isoformat()  # 更新添加日期

    save_words(words)

import sys
# ... get_word_to_review函数的代码 ...
def get_word_to_review():
    current_date = datetime.date.today()
    print(words, file=sys.stderr)
    for word, info in words.items():
        ebbinghaus_index = info['ebbinghaus_index']

        if ebbinghaus_index >= len(ebbinghaus_intervals):
            continue

        added_date = datetime.date.fromisoformat(info['added_date'])
        days_since_added = (current_date - added_date).days
        interval = ebbinghaus_intervals[ebbinghaus_index]

        if days_since_added >= interval:
            words[word]['ebbinghaus_index'] = 0  # 将单词的艾宾浩斯指数重置为 0
            save_words(words)
            return word

    return None


words = load_words()

@app.route('/')
def home():
    word_to_review = get_word_to_review()
    return render_template('home.html', word=word_to_review, show_explanation=False, words=words)

# 添加显示添加单词页面的路由
@app.route('/add', methods=['GET'])
def add_word_page():
    return render_template('add_word.html')

# 添加处理添加单词表单提交的路由
@app.route('/add', methods=['POST'])
def add_word():
    word = request.form['word']
    explanation = request.form['explanation']
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    words[word] = {
        'explanation': explanation,
        'ebbinghaus_index': 0,
        'added_date': yesterday.isoformat()
    }
    save_words(words)
    return redirect(url_for('add_word_page'))

# 添加显示生词本中的所有单词及其解释的路由
@app.route('/list')
def word_list():
    return render_template('word_list.html', words=words)

@app.route('/remember', methods=['POST'])
def remember_word():
    word = request.form['word']
    update_word_review(word, remembered=True)
    return redirect(url_for('home'))

@app.route('/forget', methods=['POST'])
def forget_word():
    word = request.form['word']
    update_word_review(word, False)  # 更新单词的艾宾浩斯指数
    return render_template('home.html', word=word, show_explanation=True, words=words)  # 重新渲染主页并显示解释

@app.route('/next', methods=['POST'])
def next_word():
    return redirect(url_for('home'))  # 重定向回主页

if __name__ == '__main__':
    app.run(debug=True)

