# Quick Start: Vector Embedding Implementation

## 🚀 Get Started in 30 Minutes

This guide will help you implement the vector embedding phase of your AASX ETL pipeline using your existing extracted data.

---

## **Step 1: Environment Setup** (5 minutes)

### **Install Dependencies**
```bash
# Core dependencies
pip install qdrant-client openai sentence-transformers pillow pypdf2

# Optional: For local development
pip install python-dotenv
```

### **Set Up Qdrant (Vector Database)**
```bash
# Start Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant

# Verify it's running
curl http://localhost:6333/collections
```

### **Environment Variables**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "VECTOR_DB_HOST=localhost" >> .env
echo "VECTOR_DB_PORT=6333" >> .env
```

---

## **Step 2: Create Basic Structure** (10 minutes)

### **Create Directory Structure**
```bash
mkdir -p src/ai_rag/document_processors
mkdir -p src/ai_rag/embedding_models
mkdir -p src/ai_rag/vector_db
mkdir -p config
```

### **Create Configuration File**
```yaml
# config/embedding_config.yaml
vector_database:
  type: "qdrant"
  host: "localhost"
  port: 6333
  collection_name: "aasx_embeddings"

embedding_models:
  text:
    provider: "openai"
    model: "text-embedding-ada-002"
  image:
    provider: "openai"
    model: "clip-vit-base-patch32"

processing:
  batch_size: 50
  max_retries: 3
```

---

## **Step 3: Implement Core Module** (15 minutes)

### **Create `src/ai_rag/vector_embedding_upload.py`**

```python
import os
import json
from pathlib import Path
from typing import Dict, List, Any
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()

class VectorEmbeddingUploader:
    def __init__(self, config_path: str = "config/embedding_config.yaml"):
        self.config = self._load_config(config_path)
        self.client = QdrantClient(
            host=self.config["vector_database"]["host"],
            port=self.config["vector_database"]["port"]
        )
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def _load_config(self, config_path: str) -> Dict:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def create_collection(self):
        """Create vector database collection"""
        collection_name = self.config["vector_database"]["collection_name"]
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"Created collection: {collection_name}")
        except Exception as e:
            print(f"Collection may already exist: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate text embedding using OpenAI"""
        try:
            response = openai.Embedding.create(
                input=text,
                model=self.config["embedding_models"]["text"]["model"]
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def process_structured_data(self, json_file: Path, project_id: str):
        """Process structured data (JSON/YAML) files"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract meaningful text from JSON
        text_content = self._extract_text_from_json(data)
        embedding = self.embed_text(text_content)
        
        if embedding:
            # Upload to vector database
            self._upload_embedding(
                embedding=embedding,
                metadata={
                    "source_file": json_file.name,
                    "project_id": project_id,
                    "content_type": "structured_data",
                    "content_preview": text_content[:200] + "..."
                }
            )
    
    def _extract_text_from_json(self, data: Dict) -> str:
        """Extract meaningful text from JSON structure"""
        text_parts = []
        
        # Extract from assets
        if "assets" in data:
            for asset in data["assets"]:
                text_parts.append(f"Asset: {asset.get('idShort', '')} - {asset.get('description', '')}")
        
        # Extract from submodels
        if "submodels" in data:
            for submodel in data["submodels"]:
                text_parts.append(f"Submodel: {submodel.get('idShort', '')} - {submodel.get('description', '')}")
        
        return " ".join(text_parts)
    
    def _upload_embedding(self, embedding: List[float], metadata: Dict):
        """Upload embedding to vector database"""
        collection_name = self.config["vector_database"]["collection_name"]
        
        # Generate unique ID
        import uuid
        embedding_id = str(uuid.uuid4())
        
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[{
                    "id": embedding_id,
                    "vector": embedding,
                    "payload": metadata
                }]
            )
            print(f"Uploaded embedding: {embedding_id}")
        except Exception as e:
            print(f"Upload error: {e}")
    
    def process_project(self, project_dir: Path):
        """Process entire project directory"""
        project_id = project_dir.name
        
        # Process structured data files
        for json_file in project_dir.glob("*.json"):
            if not json_file.name.endswith("_original.aasx"):
                print(f"Processing: {json_file}")
                self.process_structured_data(json_file, project_id)
        
        # TODO: Add document processing (images, PDFs)
        print(f"Completed processing project: {project_id}")

def main():
    """Main function to process extracted data"""
    uploader = VectorEmbeddingUploader()
    uploader.create_collection()
    
    # Process existing extracted data
    projects_dir = Path("output/projects")
    
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            print(f"\nProcessing project: {project_dir.name}")
            uploader.process_project(project_dir)

if __name__ == "__main__":
    main()
```

---

## **Step 4: Test Implementation** (5 minutes)

### **Run the Script**
```bash
cd src/ai_rag
python vector_embedding_upload.py
```

### **Verify Results**
```bash
# Check Qdrant collections
curl http://localhost:6333/collections

# Check points in collection
curl http://localhost:6333/collections/aasx_embeddings/points?limit=5
```

---

## **Expected Output**

After running the script, you should see:
```
Created collection: aasx_embeddings
Processing project: fb35fa1d-5fbe-45a5-a5a9-fbaa1a6ce026
Processing: Example_AAS_ServoDCMotor_21.json
Uploaded embedding: 12345678-1234-1234-1234-123456789abc
Completed processing project: fb35fa1d-5fbe-45a5-a5a9-fbaa1a6ce026
```

---

## **Next Steps**

### **Immediate Enhancements**
1. **Add Image Processing**
   ```python
   def process_images(self, documents_dir: Path, project_id: str):
       for image_file in documents_dir.glob("*.jpg"):
           # Process image with CLIP
           pass
   ```

2. **Add PDF Processing**
   ```python
   def process_pdfs(self, documents_dir: Path, project_id: str):
       for pdf_file in documents_dir.glob("*.pdf"):
           # Extract text and images from PDF
           pass
   ```

3. **Add Search Functionality**
   ```python
   def search(self, query: str, limit: int = 10):
       query_embedding = self.embed_text(query)
       results = self.client.search(
           collection_name=self.config["vector_database"]["collection_name"],
           query_vector=query_embedding,
           limit=limit
       )
       return results
   ```

### **Week 1 Goals**
- [x] Basic text embedding for structured data
- [ ] Image embedding for extracted images
- [ ] PDF text extraction and embedding
- [ ] Basic search functionality
- [ ] Error handling and logging

### **Week 2 Goals**
- [ ] Batch processing optimization
- [ ] Advanced metadata linking
- [ ] Performance monitoring
- [ ] Unit tests
- [ ] RAG system integration

---

## **Troubleshooting**

### **Common Issues**

1. **Qdrant Connection Error**
   ```bash
   # Check if Qdrant is running
   docker ps | grep qdrant
   # Restart if needed
   docker restart qdrant_container
   ```

2. **OpenAI API Error**
   ```bash
   # Check API key
   echo $OPENAI_API_KEY
   # Set if missing
   export OPENAI_API_KEY="your_key_here"
   ```

3. **Import Errors**
   ```bash
   # Install missing packages
   pip install qdrant-client openai python-dotenv pyyaml
   ```

---

## **Resources**

- [Qdrant Python Client](https://qdrant.tech/documentation/guides/installation/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [Your Existing Extracted Data](output/projects/)

This quick start gets you from zero to a working vector embedding system in under 30 minutes, using your existing extracted AASX data! 