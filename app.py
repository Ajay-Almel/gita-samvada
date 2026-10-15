
import streamlit as st

st.set_page_config(
    page_title="Gita Samavada",
    page_icon="🙏",
    layout="centered"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Yatra+One&display=swap');

h1.gita-title {
    font-family: 'Yatra One', serif !important;
    color: #D4AF37 !important;
    text-align: center;
    font-size: 3.2rem;
    font-weight: normal;
    margin-top: 0;
    margin-bottom: 0;
    padding-bottom: 0;
}

/* Reduce the gap below the app introduction */
div[data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<h1 class="gita-title"> Gita-Samavada</h1>',
    unsafe_allow_html=True
)



st.markdown("""
<p style="
    text-align: center;
    margin-top: 0;
    margin-bottom: 0;
    font-size: 1.05rem;
">
    Explore the wisdom of the Bhagavad Gita
    through its verses and simple explanations.
</p>
""", unsafe_allow_html=True)

st.divider()

st.subheader("Ask a Question")

question = st.text_input(
    "What would you like to know?",
    placeholder="Example: What does Krishna teach about the soul?"
)


if st.button("Seek the Gita"):
    if question.strip():
        try:
            from src.generate_full_gita_answer import answer_question

            with st.spinner("Seeking the Bhagavad Gita..."):
                result = answer_question(question)

            st.subheader("Relevant Verses")

            if result["verses"]:
                for verse in result["verses"]:
                    metadata = verse["metadata"]

                    st.markdown(
                        f"**Bhagavad Gita "
                        f"{metadata.get('chapter')}:"
                        f"{metadata.get('verse_start')}**"
                    )
                    st.write(verse["text"])
                    st.divider()
            else:
                st.info("No matching verse translations were found.")

            st.subheader("Understanding the Gita")
            st.write(result["answer"])

        except Exception:
            st.error(
                "We couldn't generate an answer right now. "
                "Please try again shortly."
            )
    else:
        st.info("Please enter your question, or discover a random verse below! 🙏")



st.divider()

st.subheader("Discover the Gita")

if st.button("🎲 Discover a Random Verse"):
    try:
        import random
        from src.generate_full_gita_answer import collection

        with st.spinner("Finding a verse..."):
            records = collection.get(
                where={"kind": "verse_translation"},
                include=["documents", "metadatas"],
                limit=1000
            )

        if records["ids"]:
            index = random.randrange(len(records["ids"]))

            verse_text = records["documents"][index]
            metadata = records["metadatas"][index]

            st.markdown(
                f"### Bhagavad Gita "
                f"{metadata.get('chapter')}:"
                f"{metadata.get('verse_start')}"
            )

            st.write(verse_text)

        else:
            st.info("No verses were found.")

    except Exception:
        st.error(
            "We couldn't load a verse right now. "
            "Please try again."
        )
