# AI Coding Agent Instructions for RAG Example Project

## Project Overview
This is a Retrieval-Augmented Generation (RAG) evaluation project comparing different text chunking strategies for document retrieval. The codebase implements and benchmarks fixed-size, sentence-based, and semantic clustering chunking methods using FAISS indexing and multilingual embeddings.

## Architecture
- **Data Source**: PDF documents in `dataset/` directory (e.g., `sample.pdf`)
- **Chunking Strategies**: 
  - Fixed-size with overlap (`chunk_fixed_with_overlap`)
  - Sentence-based (`chunk_sentence`)
  - Semantic clustering using K-means (`chunk_semantic`)
- **Embedding**: SentenceTransformer 'intfloat/multilingual-e5-base' with asymmetric prefixes ("chunk: " for documents, "query: " for queries)
- **Indexing**: FAISS IndexFlatIP for cosine similarity search
- **Evaluation**: Multiple metrics (Recall@k, MRR, MAP, NDCG) with substring and semantic relevance checking

## Key Patterns
- **Embedding Prefixes**: Always use "chunk: {text}" for document chunks and "query: {text}" for search queries to leverage the model's asymmetric capabilities
- **FAISS Normalization**: Apply `faiss.normalize_L2()` to embeddings before adding to index and before search queries
- **Evaluation Thresholds**: Use 0.75 for semantic relevance on long chunks, 0.80+ for sentence chunks
- **Chunking Overlap**: Implement 50-token overlap in fixed-size chunking to maintain context continuity

## Development Workflow
- **Execution**: Run notebook cells sequentially from top to bottom
- **Data Loading**: Use `load_pdf()` from `fitz` (PyMuPDF) for PDF text extraction
- **Query Format**: Queries are in Indonesian; ground truths are key phrases for substring matching
- **Metrics Calculation**: Implement custom evaluation functions rather than using libraries for fine-grained control

## Dependencies
- `sentence-transformers` for multilingual embeddings
- `faiss-cpu` for vector indexing
- `PyMuPDF` (fitz) for PDF processing
- `scikit-learn` for K-means clustering
- Standard libraries: `numpy`, `math`, `re`

## File Structure
- `main.ipynb`: Complete implementation and evaluation pipeline
- `dataset/sample.pdf`: Example document (Indonesian text, likely Communist Manifesto)

## Conventions
- Use Indonesian queries and ground truths matching the document language
- K=5 for retrieval evaluation
- Normalize text to lowercase for substring matching
- Semantic relevance uses cosine similarity on passage-prefixed embeddings</content>
<parameter name="filePath">/Python/rag-example/.github/copilot-instructions.md
