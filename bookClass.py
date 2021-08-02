import re
import streamlit as st


def spaces_generator(book_text):
    return [[m.start() for m in re.finditer(" ", chapter)] for chapter in book_text]

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
            sections = lr(1, 6)
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
