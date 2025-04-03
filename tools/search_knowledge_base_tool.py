from vespa.application import Vespa, VespaQueryResponse
from typing import Optional, Dict, Any, List
import os
import uuid
from agents import function_tool

@function_tool(
    name_override="search_knowledge_base",
    description_override="Retrieve data that best match a provided query from the knowledge base.",
    strict_mode=True
)
def search_knowledge_base(
    query: str,
    tenant_id: str,
    limit: int,  
    document_id: Optional[str] = None,
    collection_id: Optional[str] = None,
):
    """
    Retrieve data that best match a provided query from the knowledge base.

        Args:
            query: The search query text
            tenant_id: The tenant ID to filter by (mandatory)
            limit: Maximum number of results to return
            document_id: Optional single document ID to filter by
            collection_id: Optional collection ID to filter by

        Returns:
            dict: Query results including matched documents
    """
    print("="*50)
    print("::::[TOOL CALLED] SEARCH KNOWLEDGE BASE::::")
    print(f"Parameters:")
    print(f"  - query: {query}")
    print(f"  - tenant_id: {tenant_id}")
    print(f"  - limit: {limit}")
    print(f"  - document_id: {document_id}")
    print(f"  - collection_id: {collection_id}")
    print("="*50)
    
    try:
        app = Vespa(
            url=os.getenv("VESPA_URL"),
            port=int(os.getenv("VESPA_PORT")),
        )

        def is_valid_uuid(value: str) -> bool:
            """
            Check if a string is a valid UUID.

            Args:
                value: String to validate

            Returns:
                bool: True if string is a valid UUID, False otherwise
            """
            if not value:
                return False

            try:
                uuid_obj = uuid.UUID(value)
                return str(uuid_obj) == value.lower()
            except (ValueError, AttributeError, TypeError):
                return False

        def get_validated_uuid(value: Optional[str]) -> Optional[str]:
            """
            Validate a UUID string and return it if valid, None otherwise.

            Args:
                value: UUID string to validate

            Returns:
                str or None: The validated UUID string if valid, None otherwise
            """
            if value and is_valid_uuid(value):
                return value
            return None

        def construct_hybrid_query(
            tenant_id: str,
            query: str,
            limit: int,
            document_id: Optional[str] = None,
            document_ids: Optional[list[str]] = None,
            collection_id: Optional[str] = None,
            ranking_profile: str = "hybrid",
        ) -> dict:
            """
            Construct a hybrid search query combining text, BM25, and vector search with filters.

            Args:
                tenant_id: The tenant ID to filter by (mandatory)
                query: The search query text
                limit: Maximum number of results to return
                document_id: Optional single document ID to filter by
                document_ids: Optional list of document IDs to filter by
                collection_id: Optional collection ID to filter by
                ranking_profile: Ranking profile to use (default: "hybrid")

            Returns:
                dict: Query parameters including YQL and body parameters
            """
            if not tenant_id:
                raise ValueError("tenant_id is mandatory")

            # Build the base conditions for hybrid search (text + vector)
            base_conditions = [
                "userQuery()",
                "({targetHits: 100}nearestNeighbor(embedding, q))",
            ]

            # Add mandatory tenant filter
            filters = [f"tenant_id contains '{tenant_id}'"]

            # Handle document filtering logic
            if document_id:
                filters.append(f"id contains'{document_id}'")  # Exact match for ID
            elif document_ids:
                id_conditions = [f"id = '{id}'" for id in document_ids]
                filters.append(f"({' or '.join(id_conditions)})")

            # Add collection filter if provided
            if collection_id:
                filters.append(f"collection_id = '{collection_id}'")

            # Construct the final YQL query
            yql = f"""
                select * from tenant_documents
                where ({' or '.join(base_conditions)})
                and ({' and '.join(filters)})
                limit {limit}
            """.strip()

            print(yql, "query")

            # Construct complete query parameters
            query_params = {
                "yql": yql,
                "query": query,
                "body": {
                    "input.query(q)": "embed(e5, @query)",  # For dense retrieval (E5 model)
                    "input.query(qt)": "embed(colbert, @query)",  # For late interaction (ColBERT model)
                },
                "ranking.features.query(match_features)": "max_sim cos_sim bm25(content)",
            }

            return query_params

        def get_embeddings(
            query: str,
            tenant_id: str,
            limit: int,
            document_id: Optional[str] = None,
            document_ids: Optional[list[str]] = None,
            collection_id: Optional[str] = None,
            ranking_profile: str = "hybrid",
        ):
            """
            Get embeddings with hybrid search capabilities using text, BM25, and vector search.

            Args:
                query: The search query text
                tenant_id: The tenant ID to filter by (mandatory)
                limit: Maximum number of results to return
                document_id: Optional single document ID to filter by
                document_ids: Optional list of document IDs to filter by
                collection_id: Optional collection ID to filter by
                ranking_profile: Ranking profile to use (default: "hybrid")
            """
            # Get query parameters
            query_params = construct_hybrid_query(
                tenant_id=tenant_id,
                query=query,
                limit=limit,
                document_id=document_id,
                document_ids=document_ids,
                collection_id=collection_id,
                ranking_profile=ranking_profile,
            )

            # Execute the query
            with app.syncio(connections=1) as session:
                response: VespaQueryResponse = session.query(**query_params)

                assert response.is_successful()

                records = []
                for hit in response.hits:
                    record = {}
                    # Include more fields based on schema
                    for field in ["content", "title", "id", "chunk_id", "source"]:
                        if field in hit["fields"]:
                            record[field] = hit["fields"][field]
                    records.append(record)

            return records

        validated_document_id = get_validated_uuid(document_id)
        validated_collection_id = get_validated_uuid(collection_id)

        data = get_embeddings(
            query,
            tenant_id,
            limit=limit,
            document_id=validated_document_id,
            collection_id=validated_collection_id,
        )
        result = {"result": data, "error": None}
        
        # Print the result
        print("="*50)
        print("SEARCH KNOWLEDGE BASE RESULT:")
        print(f"Number of results: {len(data) if data else 0}")
        if data:
            print("\nCOMPLETE RESULTS:")
            for i, item in enumerate(data):  # Print all results
                print(f"\nResult {i+1}:")
                for key, value in item.items():
                    # Print complete values without truncation
                    print(f"  {key}: {value}")
        print("="*50)
        
        return result
    except Exception as e:
        error_result = {"result": None, "error": str(e)}
        
        # Print the error
        print("="*50)
        print("SEARCH KNOWLEDGE BASE ERROR:")
        print(f"Error: {str(e)}")
        print("="*50)
        
        return error_result