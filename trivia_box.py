import html
import os
import random
import textwrap

from typing import Any, Dict, List, NewType, Optional, Tuple, TypedDict
from urllib.parse import unquote

import requests

from github import Github
from github.InputFileContent import InputFileContent

RequestsData = NewType("RequestsData", Dict[str, Any])


class Question(TypedDict):
    category: str
    type: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]


ENV_VAR_GIST_ID = "GIST_ID"
ENV_VAR_GITHUB_TOKEN = "GH_TOKEN"
REPO_URL = "https://github.com/ChrisCarini/trivia-box"
MAX_LINE_LENGTH = 53
# ANSWER_KEYS = ['A', 'B', 'C', 'D']
ANSWER_KEYS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]


def escape(text: str) -> str:
    return unquote(html.unescape(text))


def build_url(category: int, quantity: int) -> str:
    return f"https://opentdb.com/api.php?amount={quantity}&category={category}"


def get_trivia_questions(category: int = 18, quantity: int = 10) -> RequestsData:
    url = build_url(category=category, quantity=quantity)
    resp = requests.get(url=url)
    return resp.json()


def filter_questions(data: RequestsData) -> Tuple[List[Question], List[Question]]:
    short_questions = []
    long_questions = []
    for question in data["results"]:
        question_text = escape(question["question"])
        if len(question_text) <= MAX_LINE_LENGTH:
            short_questions.append(question)
        elif len(question_text) > MAX_LINE_LENGTH and question["type"] == "boolean":
            short_questions.append(question)
        else:
            long_questions.append(question)
    return short_questions, long_questions


def pick_question(
    short_questions: List[Question], long_questions: List[Question]
) -> Question:
    if len(short_questions) > 0:
        return random.choice(short_questions)
    return random.choice(long_questions)


def format_question(question: Question) -> str:
    correct_answer: str = question["correct_answer"]
    incorrect_answers: List[str] = question["incorrect_answers"]
    all_answers = [correct_answer] + incorrect_answers
    question_text = f"❓ {question['question']}"
    result = [escape(text) for text in textwrap.wrap(question_text, MAX_LINE_LENGTH)]

    # Shuffle the answers
    random.shuffle(all_answers)

    # Add answers to result
    for idx, answer in enumerate(all_answers):  # type: int, str
        result.append(f"{ANSWER_KEYS[idx]} {escape(answer)}")
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
    # First, we clear all the contents of any / all the existing files in the Gist.
    files: Dict[str, Optional[InputFileContent]] = {
        filename: None for filename in list(gist.files.keys())
    }
    # Then, we add our new file + 'INFO.md' w/ the respective content to the Gist.
    files[title] = InputFileContent(content=content, new_name=title)
    files[f"{title} - INFO.md"] = InputFileContent(
        content=f"_🔗 [See the source code behind this gist here!]({REPO_URL})_",
        new_name=f"{title} - INFO.md",
    )
    # Finally, update the gist.
    gist.edit(description=title, files=files)
