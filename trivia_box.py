import html
import os
import random
import textwrap
from datetime import date
from typing import Any, Dict, NewType, Tuple, List, Union
from urllib.parse import unquote

import requests
from github import Github
from github.InputFileContent import InputFileContent

RequestsData = NewType("RequestsData", Dict[str, Any])
Question = NewType("Question", Dict[str, Union[str, List[str]]])

ENV_VAR_GIST_ID = "GIST_ID"
ENV_VAR_GITHUB_TOKEN = "GH_TOKEN"
REPO_URL = 'https://github.com/ChrisCarini/trivia-box'
MAX_LINE_LENGTH = 53
# ANSWER_KEYS = ['A', 'B', 'C', 'D']
ANSWER_KEYS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']


def escape(text: str) -> str:
    return unquote(html.unescape(text))


def get_trivia_questions(category: int = 18, quantity: int = 10) -> RequestsData:
    resp = requests.get(f'https://opentdb.com/api.php?amount={quantity}&category={category}')
    return resp.json()


def filter_questions(data: RequestsData) -> Tuple[List[Question], List[Question]]:
    short_questions = []
    long_questions = []
    for question in data['results']:
        question_text = escape(question['question'])
        if len(question_text) <= MAX_LINE_LENGTH:
            short_questions.append(question)
        elif len(question_text) > MAX_LINE_LENGTH and question['type'] == 'boolean':
            short_questions.append(question)
        else:
            long_questions.append(question)
    return short_questions, long_questions


def pick_question(short_questions: List[Question], long_questions: List[Question]) -> Question:
    if len(short_questions) > 0:
        return random.choice(short_questions)
    return random.choice(long_questions)


def format_question(question: Question) -> str:
    correct_answer = question['correct_answer']
    incorrect_answers = question['incorrect_answers']
    all_answers = [correct_answer] + incorrect_answers
    question_text = f'❓ {question["question"]}'
    result = [escape(text) for text in textwrap.wrap(question_text, MAX_LINE_LENGTH)]

    # Shuffle the answers
    random.shuffle(all_answers)

    # Add answers to result
    for idx, answer in enumerate(all_answers):
        result.append(f'{ANSWER_KEYS[idx]} {escape(answer)}')
    return "\n".join(result)


def update_gist(title: str, content: str) -> None:
    """Update gist with provided title and content.

    Use gist id and github token present in environment variables.
    Replace first file in the gist.
    """
    print(f"{title}\n{content}")
    access_token = os.environ[ENV_VAR_GITHUB_TOKEN]
    gist_id = os.environ[ENV_VAR_GIST_ID]
    gist = Github(access_token).get_gist(gist_id)
    # Works only for single file. Should we clear all files and create new file?
    old_title = list(gist.files.keys())[0]
    gist.edit(
        description=title,
        files={
            old_title: InputFileContent(content=content, new_name=title),
            'INFO.md': InputFileContent(
                content=f"_🔗 [See the source code behind this gist here!]({REPO_URL})_",
                new_name=f'{title} - INFO.md'
            ),
        }
    )


def main():
    data = get_trivia_questions()

    short, long = filter_questions(data)

    question = pick_question(short, long)

    formatted_output = format_question(question)

    update_gist(
        title=f'Trivia of the Day - {date.today().isoformat()}',
        content=formatted_output
    )


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
