# Project Overview

**RAG Legal Assistant** is an experimental Retrieval-Augmented Generation (RAG) project focused on processing and retrieving information from Polish legal documents. The current implementation uses the Polish Penal Code (*Kodeks karny*) as its primary dataset.

The project explores how the structural organization of legal documents can be preserved and utilized throughout the document processing pipeline. Instead of treating a legal document as a continuous block of text, the system extracts its structural elements, divides the content into meaningful chunks, enriches them with metadata, and generates semantic embeddings.

The current pipeline includes document ingestion, text cleaning, article-based chunking, chapter metadata extraction, and embedding generation using the **OPI-PIB/PolDense-400M** model. Generated embeddings are stored both alongside their corresponding text and metadata in JSON format and separately as a NumPy matrix.

An important part of the ongoing development is a **hierarchical, structure-aware chunking engine** designed to identify document boundaries and adapt the chunking strategy to the structural level of each text segment. The goal is to preserve as much legal context as possible while respecting the token limits of the embedding model.

The project is currently under active development. Document processing and embedding generation have been implemented, while the hierarchical chunking mechanism and semantic retrieval pipeline are still being developed.

RAG Legal Assistant is also a component of a broader **AI Inbox** concept, where document processing and semantic retrieval are intended to support more advanced document analysis workflows.

# Project Goals

The main goal of this project is to develop a modular document processing and semantic retrieval pipeline for structured legal documents, using the Polish Penal Code as the initial use case.

The project focuses on the following objectives:

* **Document ingestion and validation** – process structured text extracted from PDF and OCR pipelines while preserving document content and source information.

* **Text preprocessing** – normalize extracted text, correct common OCR-related artifacts, and prepare the content for further structural analysis.

* **Document structure detection** – identify hierarchical elements such as chapters, articles, paragraphs, points, and subpoints, preserving their relationships and boundaries.

* **Structure-aware chunking** – develop an adaptive chunking mechanism that selects an appropriate segmentation strategy based on the document hierarchy and embedding model token limits. The objective is to preserve meaningful legal context rather than rely exclusively on fixed-size text splitting.

* **Metadata preservation** – associate each generated chunk with relevant structural information, including its source, chapter, article, paragraph, and original document location whenever available.

* **Semantic embedding generation** – use domain-appropriate multilingual embedding models, currently PolDense-400M, to transform document chunks into numerical vector representations.

* **Semantic retrieval** – develop a similarity-based search mechanism that identifies and ranks document fragments according to their semantic relevance to a user query.

* **Modularity and reusability** – progressively separate document loading, preprocessing, structure detection, chunking, and embedding generation into reusable components that can be applied to different document types.

Ultimately, the project aims to establish a foundation for a RAG-based system capable of retrieving contextually relevant information from complex legal documents while maintaining traceability to the original source.

* **Context-aware retrieval** – retrieve the top 3 most semantically relevant chunks for a given query and expand the retrieved context by including neighboring chunks. This approach is intended to preserve continuity between related legal provisions and provide the language model with sufficient surrounding information.

* **Context window management** – target a maximum of approximately 2,000 tokens per chunk, despite the embedding model supporting inputs of up to 7,999 tokens. This provides room for neighboring chunks and additional contextual information within the overall model input, helping balance retrieval precision and contextual completeness.

# System Architecture

The project is designed around two main components: an offline document processing pipeline and a query-time semantic retrieval pipeline.

The first component prepares legal documents for semantic search by extracting, cleaning, structuring, chunking, and embedding their content. The second component is intended to retrieve relevant document fragments and assemble contextual information for a downstream language model.

### 1. Document Processing Pipeline

The document processing pipeline transforms OCR-extracted content into structured text chunks and their corresponding vector representations.

```text
             Document AI
                  |
                  v
          OCR Output (JSON)
                  |
                  v
          Document Ingestion
                  |
                  v
           Data Validation
                  |
                  v
           Text Cleaning
                  |
                  v
         Structure Detection
                  |
                  v
          Article Chunking
                  |
                  v
         Metadata Enrichment
                  |
                  v
          Embedding Generation
                  |
                  v
          Embedding Storage
             /         \
            v           v
       JSON Storage   NumPy Matrix
```

The current implementation includes:

* Loading and validating OCR-extracted document data.
* Text normalization and correction of common OCR formatting artifacts.
* Article-based document segmentation.
* Extraction and assignment of chapter metadata.
* Embedding generation using the PolDense-400M model.
* Storage of text, metadata, and vector representations.

A more advanced structure-aware chunking mechanism is currently under development.

### 2. Hierarchical Chunking Engine

The planned chunking engine is designed to analyze the hierarchical organization of a document and select an appropriate segmentation strategy.

Rather than applying a fixed-size splitting method, it will process document elements from larger structural units to smaller ones.

When a structural unit exceeds the target token limit, the engine will recursively consider smaller elements within that unit, preserving document boundaries and contextual relationships.

The target chunk size is approximately 2,000 tokens.

This approach is intended to preserve meaningful legal context while providing flexibility for different document structures and embedding models.

### 3. Semantic Retrieval Pipeline

The retrieval component is designed to identify the most relevant document fragments for a given user query.

The planned workflow consists of:

1. Encoding the user query into a vector representation.
2. Calculating cosine similarity between the query embedding and stored document embeddings.
3. Ranking the results by semantic similarity.
4. Retrieving the top 3 matching chunks.
5. Expanding the retrieved results with neighboring chunks to preserve surrounding legal context.
6. Preparing the expanded context for a downstream language model.

The retrieval and context assembly components are still under development.

### 4. Context Assembly and Language Model Integration

The retrieved chunks are intended to be combined with their neighboring document segments before being passed to a language model.

This provides additional context that may not be fully represented in an individual matching chunk.

The embedding model supports inputs of up to approximately 7,999 tokens, while the target chunk size is approximately 2,000 tokens. The smaller target is a deliberate design choice intended to leave room for neighboring chunks and additional contextual information.

The final context assembly mechanism will need to control the total token budget, preserve the original document order, and avoid duplicating overlapping segments.

### 5. Design Principles

The architecture follows several principles:

* **Modularity** – document ingestion, preprocessing, chunking, embedding generation, and retrieval are treated as separate responsibilities.
* **Structural awareness** – document hierarchy is preserved rather than discarded during text segmentation.
* **Context preservation** – retrieved fragments should retain their relationships with surrounding document content.
* **Model independence** – processing and chunking components should progressively support different embedding models and document types.
* **Traceability** – generated chunks retain metadata that allows them to be associated with their original document locations.

The architecture is being developed incrementally, with the current implementation serving as the foundation for a more modular and reusable RAG pipeline.

# Document Ingestion

The RAG pipeline consumes structured OCR output generated by the companion **Document AI** project. Its ingestion component is responsible for loading and validating the extracted document content while preserving both textual and spatial information.

This separation establishes clear responsibilities between document recognition, structural processing, semantic retrieval, and language generation.

# Input Data Contract

The current ingestion interface expects a JSON file containing a list of document pages.

Each page contains three main fields:

* `page` – original document page number.
* `text` – complete extracted text of the page.
* `lines` – a list of individually recognized text lines with associated spatial metadata.

Each line contains:

* `text` – recognized line content.
* `bbox` – bounding box coordinates.
* `center_y` – vertical center position of the line.
* `height` – height of the detected text region.
* `gap_after` – vertical distance to the following line.
* `gap_ratio` – normalized spacing ratio relative to line height.

This representation preserves more than the extracted text. It also retains information about the original spatial organization of the document.

## Why Preserve Line-Level Metadata?

Spatial information can provide useful signals for identifying document structure.

For example:

* Larger vertical gaps may indicate paragraph or section boundaries.
* Line height and position can help distinguish headings from regular body text.
* Bounding boxes preserve the original location of recognized text.
* Line-level content provides a more granular representation than page-level text alone.

These properties are particularly relevant to the planned hierarchical chunking engine, which aims to identify structural boundaries and select an appropriate segmentation strategy.

## Loading and Validation

The `document_loader.py` module loads the OCR-generated JSON data and performs basic structural validation.

The `audit_data.py` module provides additional diagnostics to inspect the extracted content and identify potential inconsistencies.

# Component Integration

The intended data flow connects three main components:

```text
        Source Document
               |
               v
           Document AI
         (OCR / Extraction)
               |
               v
        Structured JSON
      /                \
     v                  v
 Page-level text    Line-level data
     |                  |
     +--------+---------+
              |
              v
             RAG
   (Cleaning / Structure Detection /
       Chunking / Embeddings)
              |
              v
       Semantic Retrieval
              |
              v
       Retrieved Context
              |
              v
             LLM
      (Response Generation)
```

Currently, Document AI and RAG are maintained as separate projects, with the JSON file serving as their integration interface.

The long-term objective is to combine OCR, RAG, and LLM components into a unified application while preserving a consistent data contract between processing stages.

# Input Data

The RAG pipeline is designed to process structured document data generated by the companion Document AI component.

The system is intended to support multiple document formats:

* **DOCX files** – text and document structure extracted during document processing.
* **Scanned PDF files** – content extracted using OCR.
* **Text-based PDF files** – text extracted directly from the PDF's native text layer, without requiring OCR.

Regardless of the original document format, the processing pipeline is designed to consume a unified data structure.

This separation allows the RAG component to remain independent of the document source and extraction method. Its responsibility begins with processing the extracted content, including text cleaning, structural analysis, metadata extraction, chunking, and embedding generation.

The unified input contract is currently under development and will be documented once the output format of the Document AI component has been finalized.

# Integration with Document AI

The RAG component is designed to work alongside the Document AI pipeline as part of a larger document processing architecture.

Document AI is responsible for extracting content from source documents, including DOCX files, scanned PDFs, and PDFs containing a native text layer. Its output is passed to the RAG pipeline through a structured data interface.

The RAG component consumes this extracted content and performs subsequent processing:

1. **Input validation** – checks the structure and consistency of the incoming data.
2. **Text preprocessing** – normalizes extracted text and handles common OCR artifacts.
3. **Structure detection** – identifies document elements and their hierarchical relationships.
4. **Chunking** – divides the document into context-aware text segments while preserving structural information.
5. **Metadata enrichment** – associates chunks with relevant document references and structural metadata.
6. **Embedding generation** – converts text chunks into vector representations for semantic retrieval.

### Component Separation

Both components are developed as independent modules with clearly defined responsibilities.

* **Document AI** focuses on document ingestion, text extraction, OCR, and layout analysis.
* **RAG** focuses on text processing, structural analysis, chunking, embedding generation, and information retrieval.

This separation allows each component to evolve independently while maintaining compatibility through a shared input contract.

### Integration Roadmap

Currently, the components are developed separately, and structured JSON serves as the interface between them.

The long-term goal is to integrate both components into a unified application, allowing extracted document content to be passed directly between processing stages without relying on intermediate files.

# Data Validation

Data validation is the first stage of the RAG processing pipeline. Its purpose is to verify the structure and basic consistency of the input data before further processing begins.

The validation process is designed to check:

* **Input format** – verifies whether the provided data follows the expected input structure.
* **Required fields** – checks whether essential fields are present.
* **Data types** – verifies that fields contain values of the expected types.
* **Content availability** – identifies missing or empty text content.
* **Page structure** – checks page numbering and the consistency of page-level data.
* **Data integrity** – identifies potential inconsistencies that could affect subsequent processing stages.

The project currently includes basic input validation in `document_loader.py` and diagnostic checks in `audit_data.py`.

These checks help identify malformed or incomplete input data early, reducing the risk of errors during text preprocessing, structural analysis, and chunking.

The validation layer will be extended alongside the development of the unified input contract shared with the Document AI component.

# Text Preprocessing

Text preprocessing prepares extracted document content for structural analysis, chunking, and embedding generation.

The preprocessing pipeline focuses on normalizing text while preserving meaningful document information and structural elements.

### Text Cleaning

The cleaning stage handles common inconsistencies introduced during document extraction, particularly OCR-related artifacts.

Current operations include:

* Normalizing line endings and whitespace.
* Removing unnecessary spacing and formatting inconsistencies.
* Reconstructing words split across lines by hyphenation.
* Cleaning text while preserving meaningful punctuation and document content.

The main implementation is located in `text_cleaning.py`.

### Structure Detection

Legal documents contain hierarchical elements that must be identified before effective chunking can take place.

The project includes functionality for inspecting and detecting structural patterns such as:

* Articles.
* Paragraphs.
* Chapters.
* Other document elements and their boundaries.

Structural analysis is particularly important for legal documents, where the meaning of a passage often depends on its position within the document hierarchy.

The current implementation includes `inspect_structure.py` and the experimental `text_structure.py` module, which is being developed into a hierarchical structure-aware chunking engine.

### Metadata Extraction

Structural information is used to enrich document content with metadata that allows individual chunks to retain their original context and location.

The current pipeline extracts chapter information and associates it with article-based chunks.

Available metadata includes:

* Article identifiers.
* Chapter identifiers.
* Chapter titles.
* Original page references (`page_start`, `page_end`).

The implementation is split between `chunk_articles.py` and `add_chapter_metadata.py`.

This metadata provides the foundation for traceability and context-aware retrieval in later stages of the RAG pipeline.

## Text Cleaning

The text cleaning module is responsible for normalizing extracted document text and correcting common formatting inconsistencies before structural analysis and chunking.

Document extraction, particularly OCR, can introduce artifacts that affect text quality and interfere with subsequent processing stages.

The current implementation in `text_cleaning.py` focuses on:

* **Line ending normalization** – standardizes line breaks across different input sources.
* **Hyphenation handling** – detects and reconstructs words split across lines.
* **Whitespace normalization** – removes redundant spaces and normalizes spacing.
* **Text consistency** – reduces formatting inconsistencies while preserving meaningful content and punctuation.

The cleaning process is designed to improve text consistency without removing information relevant to document structure or meaning.

This stage provides cleaner input for structural detection, metadata extraction, and the hierarchical chunking engine.

# Structure Detection

Structure detection identifies the logical organization of a document and extracts its hierarchical elements before chunking.

This stage is particularly important when processing legal documents, where the meaning and interpretation of a passage depend not only on its content but also on its position within the document.

The current implementation focuses primarily on identifying structural patterns in the Polish Penal Code, including:

* **Chapters** – chapter headings and their identifiers.
* **Articles** – article numbers and boundaries.
* **Paragraphs** – paragraph markers within articles.
* **Points and subpoints** – lower-level elements of legal provisions.

The project uses text patterns and structural markers to identify these elements and determine their boundaries.

## Hierarchical Structure

The long-term goal is to represent documents as hierarchical structures rather than flat text.

For legal documents, the hierarchy may include:

`Act → Title → Chapter → Section → Article → Paragraph → Point → Subpoint`

Not every document contains all of these levels, so the structure detection process must account for different document layouts and missing elements.

## Current Implementation

Structural inspection and detection are currently handled by:

* `inspect_structure.py` – used to inspect document content and identify structural patterns.
* `text_structure.py` – contains experimental functionality for hierarchical structure analysis and serves as the foundation for the planned structure-aware chunking engine.

The hierarchical detection logic is still under development, particularly regarding boundary resolution, missing structural markers, and nested document elements.

The extracted structural information will be used by the chunking engine to preserve document hierarchy, maintain context, and associate each chunk with its original location.

# Metadata Extraction

Metadata extraction enriches document content with structural and positional information identified during document processing.

In legal documents, metadata is essential for preserving the relationship between individual text fragments and their original location within the document.

The current implementation focuses on extracting and assigning metadata to article-based chunks.

## Extracted Metadata

The current dataset includes the following metadata fields:

* **Article identifier** – identifies the article associated with a chunk.
* **Chapter identifier** – identifies the chapter containing the article.
* **Chapter title** – stores the corresponding chapter heading.
* **Page start** – indicates the first page containing the chunk.
* **Page end** – indicates the last page containing the chunk.

## Metadata Enrichment

Metadata enrichment is performed in separate processing stages:

* `chunk_articles.py` creates article-based chunks and preserves their original page references.
* `add_chapter_metadata.py` extracts chapter information and associates it with the corresponding chunks.

The resulting data structure combines text content with its associated metadata, allowing each chunk to retain its document context.

## Future Development

As the hierarchical chunking engine evolves, metadata extraction will be extended to support additional structural levels, including paragraphs, points, and subpoints.

The target is to preserve document hierarchy and traceability at every stage of processing, enabling more precise semantic retrieval and context reconstruction.

# Hierarchical Chunking Engine

The Hierarchical Chunking Engine is designed to divide documents into context-aware text segments while preserving their original structural organization.

Unlike conventional fixed-size chunking approaches, the engine uses the document hierarchy to determine how content should be segmented.

The main objective is to preserve the logical boundaries of document elements and avoid splitting related content unnecessarily.

## Hierarchical Segmentation Strategy

The engine follows a top-down approach, starting with the largest available structural units and progressively moving to smaller elements when a unit exceeds the target token limit.

For legal documents, the hierarchy may follow this structure:

`Act → Title → Chapter → Section → Article → Paragraph → Point → Subpoint`

The segmentation process is designed to:

1. Identify the largest available structural unit.
2. Measure its token count against the configured target size.
3. Keep the entire unit as a chunk if it fits within the limit.
4. If the unit exceeds the limit, identify its boundaries and inspect the next lower structural level.
5. Repeat the process until suitable chunk boundaries are found.
6. Preserve the relationship between each resulting chunk and its parent structural elements.

This approach allows the engine to adapt chunk boundaries to the actual organization of a document rather than relying exclusively on arbitrary character or token positions.

## Chunk Size and Context Preservation

The initial target chunk size is approximately **2,000 tokens**.

Although the embedding model supports inputs of up to approximately 8,000 tokens, smaller chunks are preferred to provide additional capacity for neighboring content during retrieval and context assembly.

This design supports a future retrieval strategy in which the most relevant chunks can be expanded with their neighboring segments to reconstruct a broader legal context.

## Metadata and Traceability

Each generated chunk is intended to retain relevant structural metadata, including:

* Document and source references.
* Structural hierarchy and element identifiers.
* Parent element references.
* Original page boundaries.
* Chunking level and segmentation information.
* Token count.

This information will allow the retrieval pipeline to identify not only the relevant text but also its position within the original document.

## Current Development Status

The hierarchical chunking engine is currently under development in `text_structure.py`.

The implementation focuses on structural boundary detection, hierarchical traversal, and adaptive segmentation.

Current development challenges include handling missing structural markers, resolving terminal boundaries, and processing documents with incomplete or inconsistent hierarchies.

The engine is intended to become a reusable component capable of processing different document types and hierarchical structures, rather than being limited to the Polish Penal Code.

# Chunking Strategies

The project explores multiple chunking strategies for segmenting legal documents while preserving their meaning, structure, and context.

The current implementation uses article-based chunking. Structure-aware and adaptive chunking strategies are under development as part of the Hierarchical Chunking Engine.

## Article-Based Chunking

The current pipeline splits the Polish Penal Code into article-based chunks.

Each chunk contains the text of an article and preserves relevant metadata, including its article identifier and original page boundaries. Chapter information is added in a subsequent processing stage.

Article-based chunking provides a practical baseline for embedding generation and semantic retrieval while preserving the primary organizational units of the legal document.

## Structure-Aware Chunking

Structure-aware chunking aims to use the document's hierarchy to determine chunk boundaries instead of relying only on fixed text or token lengths.

The planned engine will recognize structural elements such as chapters, articles, paragraphs, points, and subpoints. It will use these elements to keep related content together and preserve the relationship between each chunk and its position in the document.

This approach is intended to reduce arbitrary splits and retain legal context that may be lost when text is segmented without considering its structure.

## Adaptive Chunking Strategy Selection

The planned adaptive strategy will select chunk boundaries based on the structure and size of each document element.

The engine is designed to start with the largest available structural unit and move to smaller units when the current unit exceeds the target token limit. If a unit fits within the configured limit, it can be kept as a single chunk; otherwise, the engine will inspect its child elements and continue segmenting within the unit's boundaries.

The initial target chunk size is approximately **2,000 tokens**. This is a design target, not a fixed limit imposed by the embedding model.

The strategy is intended to support different document hierarchies and avoid splitting content unnecessarily, while retaining the metadata needed for traceability and future context expansion during retrieval.

# Embedding Generation

The embedding generation stage converts text chunks into vector representations that can be used for semantic similarity search.

The current implementation uses the `OPI-PIB/PolDense-400M` model through the Sentence Transformers interface.

## Processing Pipeline

The embedding generation process:

1. Loads the prepared chunks and their associated metadata.
2. Encodes each chunk's text using the embedding model.
3. Produces a vector representation for each chunk.
4. Stores the vectors alongside the chunk content and metadata, and in a separate NumPy matrix.

The model-loading logic is centralized in `model_loader.py`, while `embed_chunks.py` handles embedding generation.

## Embedding Output

The current dataset contains **459 chunk embeddings**, each with **1,024 dimensions**.

The vectors are stored in two formats:

* **JSON** – preserves the chunk text, metadata, and its embedding vector.
* **NumPy (`.npy`)** – stores the embedding vectors as a matrix for efficient numerical operations.

Both outputs contain the same embedding vectors. The JSON representation retains the associated text and metadata, while the NumPy file provides a compact matrix for vector-based processing.

## Current Implementation

Embedding generation is implemented and has been tested on the current chunk dataset.

The resulting vectors provide the foundation for semantic retrieval. The retrieval pipeline—including query embedding, similarity ranking, and context expansion—is a separate stage and is still under development.

# PolDense-400M

The project uses `OPI-PIB/PolDense-400M` to generate dense vector representations of legal text chunks.

The model is integrated through the Sentence Transformers interface and is used to encode both document chunks and, as part of the planned retrieval pipeline, user queries.

## Role in the Pipeline

For each input chunk, the model generates a **1,024-dimensional embedding**. These vectors represent the semantic content of the text and provide the basis for comparing chunks with query embeddings.

The current dataset contains 459 chunk embeddings generated with this model.

## Model Configuration

The model is loaded through the shared model-loading module, `model_loader.py`. This keeps model initialization separate from the embedding and retrieval logic.

The model's maximum input length is approximately **8,000 tokens**. The project uses an initial target chunk size of approximately **2,000 tokens**, leaving room for neighboring chunks and additional context during later retrieval and context assembly.

## Current Status

Embedding generation with PolDense-400M is implemented. Query encoding and semantic retrieval are planned as subsequent stages of the RAG pipeline.

# Tokenization and Encoding

Tokenization and encoding are the steps that convert text chunks into numerical representations suitable for embedding generation.

## Tokenization

Before the text is processed by the embedding model, it is tokenized into smaller units that the model can process.

The project uses the tokenizer associated with `OPI-PIB/PolDense-400M`. Tokenization also provides a way to inspect input length and check whether a text segment fits within the model's input limit.

The initial target chunk size is approximately **2,000 tokens**, while the model supports inputs of approximately **8,000 tokens**. These values serve different purposes: the chunk target guides segmentation, while the model's input limit defines the maximum length it can process.

## Encoding

The current implementation uses the Sentence Transformers `encode()` interface to process chunk text and generate embeddings.

The encoding stage:

1. Receives the text of each chunk.
2. Tokenizes the text using the model's tokenizer.
3. Processes the tokenized input through PolDense-400M.
4. Returns a **1,024-dimensional embedding** for each chunk.

Chunks are encoded in batches to process the dataset efficiently. The resulting vectors are stored with their corresponding chunk data and metadata, and in a separate NumPy matrix.

## Current Status

Tokenization and chunk encoding are implemented as part of the embedding generation pipeline.

The tokenizer can also be used to inspect token counts during chunking development. The final integration of token-count checks into the hierarchical chunking engine is still under development.

# Semantic Search

Semantic search is intended to retrieve document chunks that are semantically relevant to a user query, even when the query and the source text do not use exactly the same wording.

The planned retrieval pipeline will encode the query using the same embedding model as the document chunks, compare the resulting query vector with stored chunk embeddings, and rank the chunks by similarity.

## Cosine Similarity

The project uses cosine similarity to compare embedding vectors.

Cosine similarity measures the angle between two vectors and is used to estimate how closely their semantic representations are aligned. A higher similarity score indicates a closer match between the query and a chunk's embedding.

The current `search.py` module contains experimental similarity calculations. A complete query-to-document retrieval pipeline has not yet been implemented.

## Similarity Ranking

The planned ranking stage will sort candidate chunks by their similarity to the query and return the highest-ranked results.

The intended retrieval strategy is to select the **top 3 matching chunks**, then expand the retrieved context with neighboring chunks where appropriate. This is intended to preserve surrounding legal context that may be necessary to interpret a provision correctly.

The final retrieval process will need to account for duplicate or overlapping chunks, document order, and the available context budget.

## Current Status

Cosine similarity has been explored experimentally, while full semantic retrieval is still under development.

The next steps include query encoding, similarity calculation against the stored embedding matrix, top-k ranking, and context expansion using neighboring chunks.

# Retrieval Pipeline

The retrieval pipeline is designed to identify document chunks that are semantically relevant to a user query and assemble them into a context suitable for downstream processing by an LLM.

## Planned Retrieval Workflow

The intended retrieval process consists of the following stages:

1. **Query encoding** – encode the user query using the same embedding model used to generate document embeddings.
2. **Similarity calculation** – compare the query embedding with the stored chunk embeddings using cosine similarity.
3. **Similarity ranking** – rank candidate chunks by their similarity scores.
4. **Top-k selection** – select the three highest-ranked chunks as the initial retrieval results.
5. **Context expansion** – retrieve neighboring chunks where appropriate to preserve surrounding legal context.
6. **Context assembly** – combine the selected and neighboring chunks, remove duplicates, and preserve their original document order.

## Context Assembly

Legal provisions may depend on information contained in adjacent passages. For this reason, the retrieval strategy is designed to expand the initial results with neighboring chunks rather than relying only on isolated matches.

The context assembly stage is intended to:

* Preserve the original order of retrieved content.
* Avoid including duplicate or overlapping chunks.
* Retain relevant structural metadata and source references.
* Respect a configurable context budget.

The initial chunking target is approximately **2,000 tokens**. This is intended to leave room for neighboring chunks and additional context, while the final context budget will depend on the LLM selected for downstream generation.

## Current Status

The retrieval pipeline is under development. The current `search.py` module contains experimental similarity calculations, but query encoding, top-k retrieval, neighboring-chunk expansion, and context assembly have not yet been implemented as a complete pipeline.

The planned retrieval stage will connect the existing document processing and embedding components to the future LLM integration.

# Data Structure and Storage

The project stores processed document content, chunk metadata, and embedding vectors in structured files.

The current pipeline uses JSON for content and metadata, and NumPy for storing embedding vectors in matrix form.

## JSON Data

JSON files preserve the document text and its associated structural information throughout the processing pipeline.

The current dataset includes:

* `kk.json` – source document data used by the processing pipeline.
* `kk_chunks.json` – article-based chunks generated from the source text.
* `kk_chunks_with_chapters.json` – chunks enriched with chapter identifiers and titles.
* `kk_chunks_embeded.json` – chunks containing text, metadata, and their corresponding embedding vectors.

The files represent different stages of processing rather than interchangeable copies.

## NumPy Embedding Matrix

The file `kk_embeddings.npy` stores the embedding vectors as a NumPy matrix.

The current matrix contains **459 embeddings**, each with **1,024 dimensions**, corresponding to the chunks in the current dataset.

The NumPy matrix supports efficient numerical operations, while the JSON representation preserves the text and metadata associated with each vector.

## Data Consistency

The current JSON embedding output and NumPy matrix contain the same embedding vectors. Their separation allows the project to retain a readable, metadata-rich representation while also providing a compact matrix for similarity calculations.

The retrieval pipeline will need to maintain a consistent mapping between each embedding vector and its corresponding chunk and metadata.

## Storage Design

The current file-based approach supports experimentation and inspection during development. As the project evolves, the storage layer may be extended to support more scalable vector retrieval and document collections.

# Project Structure

The repository is organized into Python modules for document processing and embedding generation, alongside JSON and NumPy files containing intermediate and processed data.

```text
rag-legal-assistant/
├── data/
│   ├── kk.json
│   ├── kk_chunks.json
│   ├── kk_chunks_with_chapters.json
│   ├── kk_chunks_embeded.json
│   └── kk_embeddings.npy
├── add_chapter_metadata.py
├── audit_data.py
├── chunk_articles.py
├── document_loader.py
├── embed_chunks.py
├── inspect_structure.py
├── model_loader.py
├── search.py
├── test_chunks.py
├── test_cleaning.py
├── text_cleaning.py
├── text_structure.py
├── .gitignore
└── README.md
```

## Python Modules

| Module                    | Responsibility                                                                              |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| `document_loader.py`      | Loads and performs basic validation of input document data.                                 |
| `audit_data.py`           | Runs diagnostic checks on the input data.                                                   |
| `text_cleaning.py`        | Normalizes extracted text and handles common text-cleaning issues.                          |
| `inspect_structure.py`    | Inspects document content and identifies structural patterns.                               |
| `chunk_articles.py`       | Creates article-based chunks and preserves page references.                                 |
| `add_chapter_metadata.py` | Adds chapter identifiers and titles to chunks.                                              |
| `text_structure.py`       | Contains experimental hierarchical structure analysis and chunking logic under development. |
| `model_loader.py`         | Centralizes loading of the embedding model.                                                 |
| `embed_chunks.py`         | Generates embeddings for prepared chunks.                                                   |
| `search.py`               | Contains experimental similarity calculations; full retrieval is under development.         |
| `test_chunks.py`          | Contains checks for chunking behavior.                                                      |
| `test_cleaning.py`        | Contains checks for text-cleaning behavior.                                                 |

## Data Directory

The `data/` directory contains the source document data and outputs produced by successive processing stages.

The JSON files preserve text and metadata, while `kk_embeddings.npy` stores the embedding vectors as a NumPy matrix. The files represent different stages or representations of the pipeline data; they are not all interchangeable.

The repository structure reflects the current development state. The hierarchical chunking engine and complete retrieval pipeline are still under development.

# Installation and Requirements

## Requirements

The project requires:

* Python.
* PyTorch.
* Sentence Transformers.
* NumPy.

The embedding model used by the project is `OPI-PIB/PolDense-400M`. It is loaded through the Sentence Transformers interface.

A compatible GPU is optional. Embedding generation can also run on CPU, although processing may be slower.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Matw737/rag-legal-assistant.git
   cd rag-legal-assistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows:

   ```bash
   .venv\Scripts\activate
   ```

   On Linux or macOS:

   ```bash
   source .venv/bin/activate
   ```

3. Install the required packages:

   ```bash
   pip install torch sentence-transformers numpy
   ```

   For GPU acceleration, install a PyTorch build compatible with the system's CUDA environment. Refer to the official PyTorch installation instructions for the appropriate command.

## Model Download

The first run of the embedding pipeline may download `OPI-PIB/PolDense-400M` from Hugging Face. Ensure that the environment has internet access and sufficient disk space for the model files.

## Data

The processing scripts expect the project data files to be available in the `data/` directory. The input document must follow the data structure expected by the current loader.

The input contract and document-processing workflow are under development, so the exact input format may change as the Document AI component is updated.

# Usage

The current workflow processes document data through a sequence of Python modules. The exact input contract is being updated alongside the Document AI component.

## Processing Workflow

1. **Prepare the input data**
   Place the extracted document data in the expected input location. The current loader expects the data structure supported by the existing implementation.

2. **Load and validate the data**
   Use `document_loader.py` to load the input and `audit_data.py` to inspect its basic structure and consistency.

3. **Clean the extracted text**
   Use `text_cleaning.py` to normalize text and handle common formatting issues.

4. **Inspect document structure**
   Use `inspect_structure.py` to examine structural patterns in the document.

5. **Generate article-based chunks**
   Run `chunk_articles.py` to create article-based chunks and preserve their page references.

6. **Add chapter metadata**
   Use `add_chapter_metadata.py` to enrich the chunks with chapter identifiers and titles.

7. **Generate embeddings**
   Run `embed_chunks.py` to encode the prepared chunks with `OPI-PIB/PolDense-400M`.

8. **Inspect similarity experiments**
   Use `search.py` for the current experimental similarity calculations. A complete query-based retrieval workflow is not yet implemented.

## Development and Testing

The repository also includes diagnostic and test scripts:

* `test_cleaning.py` – checks text-cleaning behavior.
* `test_chunks.py` – checks chunking behavior.

The hierarchical chunking engine in `text_structure.py` and the complete semantic retrieval pipeline are still under development. Their usage and interfaces may change as the implementation evolves.

# Current Implementation Status

The project is under active development. The current implementation covers document loading, text preprocessing, article-based chunking, metadata enrichment, and embedding generation. Hierarchical chunking and semantic retrieval are still being developed.

## Implemented

* **Document loading and basic validation** – loads structured input data and performs basic checks.
* **Data auditing** – provides diagnostic checks for the input dataset.
* **Text cleaning** – normalizes extracted text and handles common formatting artifacts.
* **Article-based chunking** – splits the current Polish Penal Code dataset into article-based chunks.
* **Chapter metadata enrichment** – associates chunks with chapter identifiers and titles.
* **Embedding generation** – generates 1,024-dimensional embeddings using `OPI-PIB/PolDense-400M`.
* **Embedding storage** – saves chunk text and metadata in JSON and embedding vectors in JSON and NumPy formats.

## Experimental and In Progress

* **Hierarchical structure analysis** – experimental logic for identifying document structure and resolving element boundaries.
* **Hierarchical chunking** – development of a top-down, structure-aware strategy that adapts chunk boundaries to document hierarchy and token limits.
* **Similarity search** – experimental cosine similarity calculations in `search.py`.

## Planned

* **Complete semantic retrieval** – query encoding, similarity ranking, and top-k chunk selection.
* **Neighboring-chunk expansion** – extending initial retrieval results with surrounding chunks to preserve legal context.
* **Context assembly** – ordering and deduplicating retrieved content while respecting a configurable context budget.
* **LLM integration** – using retrieved context to support answer generation.
* **Unified Document AI integration** – connecting document extraction and RAG processing through a finalized shared input contract.

The current implementation is a foundation for a larger RAG workflow, rather than a complete question-answering assistant. The repository and this documentation will evolve as the remaining components are implemented.

# Limitations

The project is under active development and has several limitations that affect its current functionality and scope.

## Document and Input Support

* The current processing workflow is primarily developed and tested with the Polish Penal Code.
* The input contract shared with the Document AI component is being updated.
* Support for DOCX files, scanned PDFs, and PDFs with a native text layer depends on the corresponding extraction and normalization workflow in Document AI.
* Documents with different layouts or inconsistent structural markers may require additional processing logic.

## Structure Detection and Chunking

* The current article-based chunking implementation does not yet provide complete hierarchical segmentation.
* The hierarchical chunking engine is experimental and is still being developed.
* Missing or inconsistent structural markers can make it difficult to determine element boundaries reliably.
* Adaptive chunking and fallback behavior for oversized structural elements are not fully implemented.

## Semantic Retrieval

* The current `search.py` module contains experimental similarity calculations rather than a complete semantic retrieval pipeline.
* Query encoding, top-k ranking, neighboring-chunk expansion, and context assembly are not yet implemented as a complete workflow.
* Retrieval quality has not yet been systematically evaluated.

## Storage and Scalability

* The current pipeline uses JSON and NumPy files for data and embedding storage.
* This file-based approach supports development and inspection but does not yet provide a dedicated vector database or scalable retrieval layer.
* The retrieval implementation will need to maintain consistent mappings between embedding vectors, chunks, and their metadata.

## LLM Integration

* The project does not currently provide a complete question-answering workflow.
* LLM-based answer generation and its integration with retrieved context are planned future stages.
* The quality and reliability of generated answers have not yet been evaluated.

# Future Development

The project is being developed incrementally, with a focus on completing the document processing and retrieval pipeline before integrating it with an LLM.

## 1. Complete Hierarchical Chunking

* Finalize structural boundary detection and hierarchical traversal.
* Implement adaptive chunking based on document structure and token limits.
* Handle missing structural markers and incomplete document hierarchies.
* Preserve structural metadata and source references for every generated chunk.

## 2. Implement Semantic Retrieval

* Encode user queries using the same embedding model as document chunks.
* Implement cosine similarity search and top-k ranking.
* Retrieve the most relevant chunks and expand results with neighboring content.
* Preserve document order and remove duplicate or overlapping chunks.

## 3. Build Context Assembly

* Combine retrieved chunks into a coherent context.
* Apply a configurable context budget.
* Preserve source references and structural metadata for traceability.
* Prepare the assembled context for downstream LLM processing.

## 4. Finalize Document AI Integration

* Finalize the shared input contract between Document AI and RAG.
* Support a unified processing workflow for DOCX files, scanned PDFs, and PDFs with a native text layer.
* Reduce dependence on intermediate files as the components are integrated into a unified application.

## 5. Evaluate Retrieval Quality

* Create representative queries and expected relevant passages.
* Evaluate retrieval results and tune chunking and ranking behavior.
* Test whether neighboring-chunk expansion improves the preservation of legal context.

## 6. Extend the Application

* Integrate an LLM to generate answers grounded in retrieved document content.
* Preserve references to source passages to support answer traceability.
* Explore more scalable storage and retrieval options as the document collection grows.

The immediate development focus is completing the hierarchical chunking engine and implementing the semantic retrieval pipeline. LLM integration and broader application-level features will follow once these components are in place.

# Related Projects

This project is part of a broader portfolio exploring document processing and AI-assisted information retrieval.

* **Document AI / OCR** — extracts text and structural information from documents. The RAG project is intended to consume its output through a shared data contract.
* **LLM-based Legal Assistant** — a planned application layer that will use retrieved legal passages to generate answers grounded in source documents.

These components are currently developed separately. Their integration is a future development goal.
