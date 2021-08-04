import random
import streamlit as st

#random.seed(42)

def index_by_vector(vector):
    #Takes vector [F, F, T, F] with only one true
    #Returns 2
    if True in vector:
        return vector.index(True)
    else:
        return []

def initialize_or_iterate_session_state(variable_str):
    if variable_str not in st.session_state:
        st.session_state[variable_str] = 1
    else:
        st.session_state[variable_str] += 1

class quizClass():
    def __init__(self, book, num_questions, d_range, num_context_words):
        self.book = book
        self.n = num_questions
        self.range = d_range
        self.context = num_context_words
        self.isContext = self.context != 0

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


    def get_button_text(self, num_or_list):
        if self.book.title == "Galatians":
            button_text = f"Chapter {num_or_list}"
        else:
            button_text = f"Chapters {num_or_list[0]}-{num_or_list[-1]}"
        return button_text


    def store_answer(self):
        # For Galatians, returns a num from 1-6
        # Otherwise, it returns a list like [6, 7, 8, 9, 10, 11]
        sections_list = self.book.get_sections()
        col = st.beta_columns(len(sections_list))
        for idx, option in enumerate(sections_list):
            if col[idx].button(self.get_button_text(option)):
                st.session_state['user_answer'] = option


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
        show_wrong = True
        if show_wrong:
            to_print = f"Question {st.session_state['count']}: {'Correct' if bool else 'Wrong'}, " \
                   f"this is from Chapter {str(correct_chapter)}, " \
                   f"{'and' if bool else 'but'} you entered {text}."
        else:
            to_print = f"Question {st.session_state['count']}: {'Correct' if bool else 'Wrong'}, " \
                   f"this is from Chapter {str(correct_chapter)}."
        st.write(to_print)

    def return_context(self, chapter, start, end):
        chapter_spaces = self.book.spaces[chapter]
        c_start = chapter_spaces[chapter_spaces.index(start) - self.context]
        c_end = chapter_spaces[chapter_spaces.index(end) + self.context]
        c_phrase_beg = self.book.text[chapter][c_start:start].replace("\\", "")
        c_phrase_med = self.book.text[chapter][start:end].replace("\\", "")
        c_phrase_end = self.book.text[chapter][end:c_end].replace("\\", "")
        return f">The context for this verse is: <p> {c_phrase_beg}<span style=\"color:#6eb52f\">{c_phrase_med}</span>{c_phrase_end} </p>"
        #st.markdown(f">The context for this verse is: <p> {c_phrase} </p>", unsafe_allow_html = True)

    def print_and_reset_score(self):
        st.write(f"You got {st.session_state['correct'] if 'correct' in st.session_state else str(0)}/{self.n} correct.")
        st.session_state['correct'] = 0
        st.session_state['count'] = 0

    def empty_space(self, n):
        for _ in range(n):
            st.write("#")

    def run_quiz_iters(self):
        random_chapter = random.randint(1, self.book.num_chapters) - 1
        if 'last_chapter' not in st.session_state:
            st.session_state['last_chapter'] = random_chapter
        phrase, start_num, end_num = self.generate_phrase(random_chapter)
        st.write(f"Your excerpt is:")
        #If first runthrough, prints phrase. Else, prints old phrase.
        if 'phrase' not in st.session_state:
            st.session_state['phrase'] = phrase
        st.markdown(f">...{st.session_state['phrase']}...", unsafe_allow_html = True)


        if self.isContext:
            context_text = self.return_context(random_chapter, start_num, end_num)
            #If first runthrough or next_question pressed, store context.
            if 'context' not in st.session_state:
                st.session_state['context'] = context_text

        self.store_answer()
 

        if 'user_answer' in st.session_state:
            initialize_or_iterate_session_state('count')
            user_answer = st.session_state['user_answer']
            #Deletes answer so we can wait upon an answer in the future.
            del st.session_state['user_answer']

            is_correct_answer = self.check_answer(user_answer, st.session_state['last_chapter'] + 1)
            if is_correct_answer:
                initialize_or_iterate_session_state('correct')
            self.show_result(is_correct_answer, user_answer, st.session_state['last_chapter'] + 1)
            st.session_state['last_chapter'] = random_chapter
            if self.isContext:
                st.markdown(f"{st.session_state['context']}", unsafe_allow_html = True)
                st.session_state['context'] = context_text
            st.session_state['phrase'] = phrase
            if st.session_state['count'] < self.n:
                if st.button("Next Question (or Press \"r\")"):
                    pass
            else:
                self.print_and_reset_score()
                if st.button("Go again (or Press \"r\")"):
                    pass
        else:
            self.empty_space(6)