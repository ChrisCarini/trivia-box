from datetime import date

from trivia_box import filter_questions, format_question, get_trivia_questions, pick_question, update_gist


def main():
    data = get_trivia_questions()

    short, long = filter_questions(data)

    question = pick_question(short, long)

    formatted_output = format_question(question)

    update_gist(title=f'Trivia of the Day - {date.today().isoformat()}', content=formatted_output)


if __name__ == '__main__':
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f'{__file__} executed in {elapsed:0.2f} seconds.')
