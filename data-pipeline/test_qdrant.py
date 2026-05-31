from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(url='http://localhost:16333')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def search_news(query, limit=5):
    vec = model.encode(query).tolist()
    results = client.query_points(collection_name='news_chunks', query=vec, limit=limit)
    print(f'Search: "{query}"')
    print(f"Found: {len(results.points)} results")
    for r in results.points:
        print(f"  Score: {r.score:.4f} | {r.payload.get('title','')[:70]}")
    print()

search_news('ACB ngân hàng lợi nhuận')
search_news('dầu Brent giá dầu thế giới')
search_news('VN-Index chứng khoán thị trường')
search_news('vàng thế giới tăng')
