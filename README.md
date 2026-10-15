# Gita Samavada 🙏

**Explore the wisdom of the Bhagavad Gita through verses and simple explanations.**

Gita Samavada is a non-commercial learning project built to explore Retrieval-Augmented Generation (RAG), semantic search, vector databases, and generative AI.

## Features

- Ask questions about the Bhagavad Gita.
- Retrieve relevant verses with chapter and verse references.
- Generate simple-English explanations using Google's Gemini model.
- Discover a random verse from the Bhagavad Gita.

## Technology Stack

- Python
- Streamlit
- Google Gemini API
- ChromaDB
- Sentence Transformers
- LangChain text splitters

## Data Sources and Acknowledgements

**Romanized verse dataset**

The project uses verse data from [The Gita Initiative repository](https://github.com/gita/gita/tree/main/data). Refer to the repository's [license](https://github.com/gita/gita/blob/main/LICENSE) for the terms applicable to the material used.

**Bhagavad-gītā As It Is**

The local development dataset includes text extracted from *Bhagavad-gītā As It Is*, by A. C. Bhaktivedanta Swami Prabhupāda. [PDF reference](https://www.prabhupada-books.de/pdf/Bhagavad-gita-As-It-Is.pdf).

The original PDF and extracted book text are not included in this public repository.

## Run Locally

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the packages listed in `requirements.txt`.
4. Configure your Gemini API key in a local `.env` file.
5. Run the Streamlit application.

The application also requires its full-Gita vector database and verse data to be available. Deployment setup instructions will be finalized once the data distribution approach is confirmed.

## Disclaimer

This is an independent educational project. It is not an official ISKCON or Bhaktivedanta Book Trust project, and no endorsement is implied.

AI-generated explanations may contain errors. Please consult the original text for authoritative interpretation.