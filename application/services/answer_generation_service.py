from __future__ import annotations

import time
from dataclasses import dataclass

import faiss
import numpy as np

from application.ports.embedding_model import EmbeddingModel
from application.ports.llm import LLM
from application.ports.reranker import Reranker
from domain.repositories.rag_answer_repository import RagAnswerRepository
from domain.repositories.rag_query_repository import RagQueryRepository
from domain.repositories.document_chunk_repository import DocumentChunkRepository
from domain.repositories.vector_index_repository import VectorIndexRepository
from domain.valueobjects.enums import ChunkingStrategy


@dataclass
class AnswerGenerationConfig:
    retrieve_top_n: int = 20
    rerank_top_k: int = 5
    max_context_chunks: int = 2
    max_new_tokens: int = 256
    temperature: float = 0.2
    top_p: float = 0.9
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC_SLIDING_WINDOW


def _select_context(chunks: list[str], max_chunks: int) -> str:
    return "\n\n".join(chunks[:max_chunks])


def _build_prompt(query: str, context: str) -> str:
    return f"""\
Anda adalah sistem tanya jawab berbasis dokumen.

Jawab pertanyaan dengan ketentuan berikut:
1. Kutip 1–2 kalimat dari KONTEKS yang paling relevan
2. Berdasarkan KONTEKS tersebut, berikan jawaban singkat dalam 2–3 kalimat naratif, bukan poin-poin
3. Jangan menambahkan konsep, istilah, atau penjelasan yang tidak tertulis secara eksplisit di dalam KONTEKS
3. Generate jawaban menggunakan bahasa yang sama dengan bahasa yang digunakan pada KONTEKS
4. Jika jawabannya tidak ada di KONTEKS, jawab: "Informasi tidak ditemukan dalam dokumen."

### KONTEKS
{context}

### PERTANYAAN
{query}

### JAWABAN
"""


@dataclass
class AnswerGenerationService:
    rag_query_repo: RagQueryRepository
    rag_answer_repo: RagAnswerRepository
    chunk_repo: DocumentChunkRepository
    vector_index_repo: VectorIndexRepository
    embedding_model: EmbeddingModel
    reranker: Reranker
    llm: LLM
    config: AnswerGenerationConfig

    def generate_answer(self, *, query: str, document_ids: list[str]) -> str:
        # persist query record
        scope = {"type": "DOCUMENT", "ids": document_ids}
        rag_query_id = self.rag_query_repo.create(
            query_text=query,
            scope=scope,
            embedding_model=self.embedding_model.name(),
            llm_model=self.llm.name(),
        )

        start = time.perf_counter()

        # query embedding (E5 style: "query: ")
        q = self.embedding_model.encode([f"query: {query}"]).astype(np.float32)
        faiss.normalize_L2(q)

        retrieved_texts: list[str] = []

        # retrieve for each document id
        for doc_id in document_ids:
            idx = self.vector_index_repo.get_latest_ready(
                document_id=doc_id, chunking_strategy=self.config.chunking_strategy
            )
            if idx is None:
                continue

            index = faiss.read_index(idx.index_path)
            _D, I = index.search(q, self.config.retrieve_top_n)
            ids = [int(i) for i in I[0] if i >= 0]
            if not ids:
                continue

            # load chunks for document and map by chunk_index
            chunk_rows = self.chunk_repo.list_by_document_id(doc_id)
            by_index = {int(r.chunk_index): r.content for r in chunk_rows}

            for chunk_idx in ids:
                if chunk_idx in by_index:
                    retrieved_texts.append(by_index[chunk_idx])

        # rerank across all retrieved texts
        if not retrieved_texts:
            context = ""
            prompt = _build_prompt(query, context)
            answer_text, prompt_toks, completion_toks = self.llm.generate(
                prompt=prompt,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
            )
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.rag_answer_repo.create(
                rag_query_id=rag_query_id,
                answer=answer_text,
                prompt_tokens=prompt_toks,
                completion_tokens=completion_toks,
                latency_ms=latency_ms,
            )
            return answer_text

        scores = self.reranker.score(query=query, documents=retrieved_texts)
        ranked = sorted(zip(retrieved_texts, scores), key=lambda x: x[1], reverse=True)
        top_chunks = [t for t, _ in ranked[: self.config.rerank_top_k]]

        # context selection after rerank
        context = _select_context(top_chunks, self.config.max_context_chunks)

        prompt = _build_prompt(query, context)
        answer_text, prompt_toks, completion_toks = self.llm.generate(
            prompt=prompt,
            max_new_tokens=self.config.max_new_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
        )

        latency_ms = int((time.perf_counter() - start) * 1000)
        self.rag_answer_repo.create(
            rag_query_id=rag_query_id,
            answer=answer_text,
            prompt_tokens=prompt_toks,
            completion_tokens=completion_toks,
            latency_ms=latency_ms,
        )
        return answer_text


