#!/usr/bin/env python3
"""
Quick test to verify RAG retrieval is working
"""

import sys
sys.path.append('..')

# from backend.rag_engine import rag_engine
from backend.models import UserRole
from backend.rag_engine import RAGEngine
rag_engine = RAGEngine()


print("="*70)
print("TESTING RAG ENGINE RETRIEVAL")
print("="*70)

# Test query
result = rag_engine.query(
    question='What are the visiting hours for ICU?',
    user_role=UserRole.GENERAL,
    include_sources=True
)

# Check results
sources_count = len(result["sources"])
answer_preview = result["answer"][:150] if result["answer"] else "No answer"

print(f"\n✅ Sources retrieved: {sources_count}")
print(f"✅ Answer preview: {answer_preview}...")

if sources_count > 0:
    print('\n🎉 SUCCESS! RAG retrieval is working!')
    print(f"\nSources found:")
    for i, source in enumerate(result['sources'][:3], 1):
        print(f"  {i}. {source.get('filename', 'unknown')}")
    print(f"\n✅ You can now run the full evaluation:")
    print(f"   cd tests")
    print(f"   python rag_evaluation.py")
else:
    print('\n❌ PROBLEM: Still returning 0 sources')
    print('   Check that the fix was applied correctly to rag_engine.py')
    print('   The query() method should refresh vectorstore at the start.')

print("\n" + "="*70)