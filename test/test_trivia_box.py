import os

from unittest import mock
from unittest.mock import MagicMock, PropertyMock

import trivia_box

from trivia_box import (
    Question,
    build_url,
    escape,
    filter_questions,
    format_question,
    get_trivia_questions,
    pick_question,
)

MOCK_DATA = {
    'results': [
        {
            'category': 'Science: Computers',
            'type': 'multiple',
            'difficulty': 'easy',
            'question': 'What does the &quot;MP&quot; stand for in MP3?',
            'correct_answer': 'Moving Picture',
            'incorrect_answers': [
                'Music Player',
                'Multi Pass',
                'Micro Point',
            ],
        },
        {
            'category': 'Science: Computers',
            'type': 'multiple',
            'difficulty': 'medium',
            'question': 'Moore&#039;s law originally stated that the # of transistors on a µP chip would 2x every...',
            'correct_answer': 'Year',
            'incorrect_answers': [
                'Four Years',
                'Two Years',
                'Eight Years',
            ],
        },
        {
            'category': 'Science: Computers',
            'type': 'boolean',
            'difficulty': 'medium',
            'question': 'Early RAM was directly seated onto the motherboard and could not be easily removed.',
            'correct_answer': 'True',
            'incorrect_answers': [
                'False',
            ],
        },
    ]
}


def test_escape():
    # given
    input_text = 'What does the &quot;MP&quot; stand for in MP3?'

    # when
    result = escape(text=input_text)

    # then
    assert result == 'What does the "MP" stand for in MP3?'


def test_build_url():
    # given
    category = 123
    quantity = 456

    # when
    result = build_url(category=category, quantity=quantity)

    # then
    assert str(category) in result
    assert str(quantity) in result


def test_get_trivia_questions(requests_mock):
    # given
    category = 123
    quantity = 3

    requests_mock.get(
        f'https://opentdb.com/api.php?amount={quantity}&category={category}',
        json=MOCK_DATA,
    )

    # when
    result = get_trivia_questions(category=category, quantity=quantity)

    # then
    assert len(result['results']) == 3, 'We expect to get 3 questions back.'


def test_filter_questions():
    # given

    # when
    # noinspection PyTypeChecker
    short_result, long_result = filter_questions(data=MOCK_DATA)

    # then
    assert len(short_result) == 2, 'We expect 2 short questions'
    assert len(long_result) == 1, 'We expect 1 long questions'


def test_pick_question():
    # given
    question1_s: Question = MagicMock()
    question2_s: Question = MagicMock()
    question3_l: Question = MagicMock()
    short_questions = [question1_s, question2_s]
    long_questions = [question3_l]

    # when
    result = pick_question(short_questions=short_questions, long_questions=long_questions)

    # then
    assert result in short_questions, 'If short questions exist, we expect the result to be picked from there.'

    # given
    short_questions = []
    long_questions = [question3_l]

    # when
    result = pick_question(short_questions=short_questions, long_questions=long_questions)

    # then
    assert result in long_questions, 'If no short questions exist, we expect the result to be a long question.'


def test_format_question():
    # given
    # noinspection PyTypeChecker
    question: Question = {
        'category': 'Science: Computers',
        'type': 'multiple',
        'difficulty': 'easy',
        'question': 'What does the &quot;MP&quot; stand for in MP3?',
        'correct_answer': 'Moving Picture',
        'incorrect_answers': [
            'Music Player',
            'Multi Pass',
            'Micro Point',
        ],
    }
    # when
    result = format_question(question=question)

    # then
    assert '❓ What does the "MP" stand for in MP3?\n' in result
    assert 'Music Player' in result
    assert 'Multi Pass' in result
    assert 'Micro Point' in result
    assert 'Moving Picture' in result
    assert result.count('\n') == 4, 'There should be 4 new lines in the result.'


@mock.patch(f'{trivia_box.__name__}.{trivia_box.Github.__name__}')
def test_update_gist(mock_Github: MagicMock):  # title: str, content: str) -> None:
    # given
    my_title = 'my title'
    old_title = 'file_title.txt'
    mock_gist = MagicMock()
    mock_gist = PropertyMock(files={old_title: '_'})
    mock_Github.return_value.get_gist.return_value = mock_gist

    # set env vars
    os.environ[trivia_box.ENV_VAR_GITHUB_TOKEN] = 'access_token'
    os.environ[trivia_box.ENV_VAR_GIST_ID] = 'gist_id'

    # when
    trivia_box.update_gist(title=my_title, content='my content')

    # then
    mock_Github.return_value.get_gist.assert_called_once()
    mock_gist.edit.assert_called_once_with(
        description=my_title,
        files={
            old_title: mock.ANY,
            my_title: mock.ANY,
            f'{my_title} - INFO.md': mock.ANY,
        },
    )
