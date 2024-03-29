from books import galatians, romans, john, firstcor, secondcor
from bookClass import bookClass
from quizClass import quizClass
import streamlit as st



st.set_page_config(layout="centered",
                   page_title = f"{'Bible' if 'book_object' not in st.session_state else st.session_state['book_object'].title} Practice")

def intro():
    st.title("BCM 205/209/317 Exam Practice")
    if 'book_object' in st.session_state:
        st.image(f"images/{st.session_state['book_object'].title.lower()}_img.jpg")
    else:
        st.image(f"images/bible_img.jpg")
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
    st.subheader("Pick a book to practice.")

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
                            value=(7, 15), min_value=1, max_value=40,
                            help="The program randomly chooses a length from your specified range of lengths. "
                                 "If you put both ends of the slider on one number, then the excerpt will "
                                 "always be that long.", key="drill_range")

    number_of_context_words = st.slider("Upon guessing a chapter, how much context do you want "
                                        "surrounding the except?", min_value=0, max_value=30, value = 10,
                                        help="A value of 0 removes the context feature entirely.")
    return [number_of_questions, drill_range, number_of_context_words]

def del_ss(text):
    if text in st.session_state:
        del st.session_state[text]

def clear_session_state():
    del_ss('last_chapter')
    del_ss('phrase')
    del_ss('context')
    del_ss('count')
    del_ss('correct')


def main():
    intro()
    col = st.columns(5)
    book_titles = ['Galatians', 'Romans', 'John', '1 Corinthians', '2 Corinthians']
    all_book_texts = [galatians.galatians, romans.romans, john.john, firstcor.firstcor, secondcor.secondcor]
    for indx, title_of_book in enumerate(book_titles):
        if col[indx].button(title_of_book):
            #Upon switching books, clear some session_state data so that the computer "starts over"
            if 'book_object' in st.session_state:
                st.write("Clearing quiz score...")
                clear_session_state()
            st.session_state['book_object'] = bookClass(title_of_book, all_book_texts[indx])
            #book_title = title_of_book
            #st.error(book_title)
    if 'book_object' in st.session_state:
        #image_container.image(f"images/{st.session_state['book_object'].title.lower()}_img.jpg")
        st.session_state['book_object'].phrase_lookup()
        params = get_params()
        if any(['count' in st.session_state, 'phrase' in st.session_state, st.button("Start")]):
            quiz_object = quizClass(st.session_state['book_object'], *params)
            quiz_object.run_quiz_iters()


if __name__ == "__main__":
    main()
