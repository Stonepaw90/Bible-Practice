from galatians import galatians
from romans import romans
from john import john
from firstcor import firstcor
from secondcor import secondcor
import streamlit as st
import random
import re

st.set_page_config(layout="centered",
                   page_title = f"{'Bible' if 'book_object' not in st.session_state else st.session_state['book_object'].title} Practice")

def spaces_generator(book):
    return [[m.start() for m in re.finditer(" ", i)] for i in book]


def intro():
    st.title("Exam Practice")
    st.image("galatians_img.jpg")
    st.markdown("### Coded by [Abraham Holleran](https://github.com/Stonepaw90) :sunglasses:")
    st.write("This gives you a randomly chosen excerpt from your chosen book of the bible (NRSV), "
             "then you write what chapter, or chapter range,  the excerpt is from. "
             "Upon guessing, if enabled, the program would write the context surrounding this quote. "
             "By default, this is set to 10 words.")
    st.write("For example, here is a nine-word selection from Galatians.")
    st.markdown(">...I beg you, become as I am, for I...")
    st.write("You would enter \"Chapter 4\". The program would write:")
    st.markdown(">The context for this verse is:"
                "<p> afraid that my work for you may have been wasted. Friends, <span style=\"color:#6eb52f\">"
                "I beg you, become as I am, for I</span> also have become as you are. You have done me </p>",
                unsafe_allow_html = True)
    st.markdown("""---""")
    st.subheader("Pick the book to practice.")


def get_params():
    # st.write("Hover over the ? for more information.")
    range_options = [*range(1, 101), "Inf"]
    number_of_questions = st.select_slider("How many questions do you want to be quizzed on?"
                                           " Your score will be shown afterward.",
                                           help="If you select Inf, then you'll get neverending questions, "
                                                "and you won't be shown a score.", options=range_options, value=10,
                                           key="num_questions")
    if number_of_questions == "Inf":
        number_of_questions = 10000
    drill_range = st.slider("How many words long should the excerpt be?",
                            value=(7, 15), min_value=1, max_value=30,
                            help="The program randomly chooses a length from your specified range of lengths. "
                                 "If you put both ends of the slider on one number, then the excerpt will "
                                 "always be that long.", key="drill_range")

    number_of_context_words = st.slider("Upon guessing a chapter, how much context do you want "
                                        "surrounding the except?", min_value=0, max_value=20,
                                        help="A value of 0 removes the context feature entirely.")
    return [number_of_questions, drill_range, number_of_context_words]


class bookClass:
    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.spaces = spaces_generator(text)
        self.num_chapters = len(text)

    def get_sections(self):
        # galatians = 1-6
        # romans = 1-6, 6-11, 11-16
        # 1 Cor: chs. 1-5; 6-10; 11-16
        # 2 Cor: chs. 1-5; 6-9; 10-13
        # John: chs. 1-7; 8-14; 15-21
        def lr(a, b):
            return list(range(a, b + 1))

        if self.title == "Galatians":
            sections = lr(1, 7)
        elif self.title == "Romans":
            # Chapters 6 and 11 are in 2 sections each, as intended!
            sections = [lr(1, 6),
                        lr(6, 11),
                        lr(11, 16)]
        else:
            if self.title == "John":
                breaks = [7, 14]
            elif self.title == "1 Corinthians":
                breaks = [5, 10]
            elif self.title == "2 Corinthians":
                breaks = [5, 9]
            sections = [lr(1, breaks[0]),
                        lr(breaks[0] + 1, breaks[1]),
                        lr(breaks[1] + 1, self.num_chapters)]
        return sections

    def phrase_lookup(self):
        if 'text_to_find' in st.session_state:
            val = st.session_state['text_to_find']
        else:
            val = "You foolish Galatians!"
        text_to_find = st.text_input(f"Want to check what chapter of {self.title} "
                                     f"a phrase is from? Enter the phrase here.",
                                     value=val)
        st.session_state['text_to_find'] = text_to_find
        found = False
        for i in range(self.num_chapters):
            if text_to_find in self.text[i]:
                st.write(f"The phrase '{text_to_find}' is in {self.title} Chapter {i + 1}.")
                found = True
        if not found:
            st.write(f"The phrase '{text_to_find}', as you wrote it, is not in {self.title} (NRSV).")


class quizClass():
    def __init__(self, book, num_questions, d_range, num_context_words):
        self.book = book
        self.n = num_questions
        self.range = d_range
        self.context = num_context_words
        self.correct_count = 0
        self.iter = num_questions
        self.button_col = None

    def generate_phrase(self, chapter):
        chapter_spaces = self.book.spaces[chapter]
        phrase_len = random.randint(*self.range)
        if self.context == 0:
            start = random.choice(chapter_spaces[1:-phrase_len])
        else:
            context_buffer = phrase_len + self.context
            start = random.choice(chapter_spaces[self.context:-context_buffer])
        end = chapter_spaces[chapter_spaces.index(start) + phrase_len]
        phrase = self.book.text[chapter][start:end]
        phrase = phrase.replace("\\", "")
        return phrase, start, end

    def get_answer(self):
        # For Galatians, returns a num from 1-6
        # Otherwise, it returns a list like [6, 7, 8, 9, 10, 11]
        sections_list = self.book.get_sections()

        if self.button_col is None:
            self.button_col = st.beta_columns(len(sections_list))
        for idx, option in enumerate(sections_list):
            if self.book.title == "Galatians":
                button_text = f"Chapter {option}"
            else:
                button_text = f"Chapters {option[0]}-{option[-1]}"
            if self.button_col[idx].button(button_text, key = f"{self.iter}_{idx}"):
                st.session_state['answer'] = option
        if 'answer' in st.session_state:
            return st.session_state['answer']
        # if answer is not None:
        #    return answer

    def check_answer(self, user_answer, correct_answer):
        if type(user_answer) is list and correct_answer in user_answer:
            return True
        else:
            return user_answer == correct_answer

    def show_result(self, bool, entered, correct_chapter):
        if self.book.title == "Galatians":
            text = f"Chapter {entered}"
        else:
            text = f"Chapters {entered[0]}-{entered[-1]}"
        to_print = f"{'Correct' if bool else 'Wrong'}, " \
                   f"this is from Chapter {str(correct_chapter)}, " \
                   f"{'and' if bool else 'but'} you entered {text}."
        st.write(to_print)

    def show_context(self, chapter, start, end):
        chapter_spaces = self.book.spaces[chapter]
        c_start = chapter_spaces[chapter_spaces.index(start) - self.context]
        c_end = chapter_spaces[chapter_spaces.index(end) + self.context]
        #c_phrase = self.book.text[chapter][c_start:c_end]
        #c_phrase = c_phrase.replace("\\", "")
        c_phrase_beg = self.book.text[chapter][c_start:start].replace("\\", "")
        c_phrase_med = self.book.text[chapter][start:end].replace("\\", "")
        c_phrase_end = self.book.text[chapter][end:c_end].replace("\\", "")
        st.markdown(f">The context for this verse is: <p> {c_phrase_beg}<span style=\"color:#6eb52f\">{c_phrase_med}</span>{c_phrase_end} </p>", unsafe_allow_html = True)
        #st.markdown(f">The context for this verse is: <p> {c_phrase} </p>", unsafe_allow_html = True)


    def run_quiz(self):
        if 'answer' in st.session_state:
            del st.session_state['answer']
        random_chapter = random.randint(1, self.book.num_chapters) - 1
        phrase, start_num, end_num = self.generate_phrase(random_chapter)
        #location.code(phrase, language=None)
        #st.markdown(f"><span style=\"color:black\">{phrase}</span>", unsafe_allow_html = True)
        st.markdown(f">...{phrase}...")
        entered_answer = self.get_answer()
        st.title(entered_answer)
        st.title('answer' in st.session_state)
        if 'answer' in st.session_state:
            correct_answer = self.check_answer(entered_answer, random_chapter + 1)
            if correct_answer:
                self.correct_count += 1
            self.show_result(correct_answer, entered_answer, random_chapter + 1)
            if self.context != 0:
                self.show_context(random_chapter, start_num, end_num)
        else:
            st.stop()

    def print_results(self):
        st.write(f"You got {self.correct_count}/{self.n} correct.")
        self.correct_count = 0

    def repeat_quiz(self):
        self.run_quiz()
        self.iter -= 1
        while self.iter > 0 and 'answer' in st.session_state:
            self.run_quiz()
            self.iter -= 1


def main():
    intro()
    col = st.beta_columns(5)
    book_titles = ['Galatians', 'Romans', 'John', '1 Corinthians', '2 Corinthians']
    all_book_texts = [galatians, romans, john, firstcor, secondcor]
    for indx, title_of_book in enumerate(book_titles):
        if col[indx].button(title_of_book):
            book_object = bookClass(title_of_book, all_book_texts[indx])
            st.session_state['book_object'] = book_object
    if 'book_object' in st.session_state:
        st.session_state['book_object'].phrase_lookup()
        quiz_object = quizClass(st.session_state['book_object'], *get_params())
        #excerpt_loc = st.empty()
        #quiz_object.run_quiz()
        quiz_object.repeat_quiz()
        quiz_object.print_results()


if __name__ == "__main__":
    main()
