from bson import ObjectId
from datetime import datetime
import json

def serialize_mongo_doc(doc):
    """
    Convert MongoDB document to JSON-serializable dict
    
    Args:
        doc: MongoDB document or list of documents
        
    Returns:
        JSON-serializable dict or list of dicts
    """
    if doc is None:
        return None
    
    # Handle lists of documents
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    
    # Handle ObjectId
    if isinstance(doc, ObjectId):
        return str(doc)
    
    # Handle datetime
    if isinstance(doc, datetime):
        return doc.isoformat()
    
    # Handle non-dictionary types
    if not isinstance(doc, dict):
        return doc
    
    # Process dictionary
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_mongo_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_mongo_doc(item) for item in value]
        else:
            result[key] = value
    
    return result

class MongoJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder that handles MongoDB types
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def mongo_to_json(data):
    """
    Convert MongoDB document to JSON string
    
    Args:
        data: MongoDB document or list of documents
        
    Returns:
        JSON string
    """
    return json.dumps(serialize_mongo_doc(data), cls=MongoJSONEncoder)