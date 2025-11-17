"""
RAG API Evaluation Script - Production Ready
=============================================

Tests the running FastAPI backend through HTTP requests.
Includes rate limiting, comprehensive metrics, and detailed reporting.

Usage:
    python api_evaluation.py --base-url http://localhost:8000
"""

import requests
import time
import json
import statistics
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import argparse


class APIEvaluator:
    """
    Evaluates RAG system via API endpoints
    """

    def __init__(self, base_url: str = "http://localhost:8000", request_delay: float = 2.0):
        """
        Initialize API evaluator

        Args:
            base_url: Base URL of the API
            request_delay: Delay between requests (seconds)
        """
        self.base_url = base_url.rstrip('/')
        self.request_delay = request_delay
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": base_url,
                "request_delay": request_delay
            },
            "metrics": {},
            "individual_results": []
        }

    def check_health(self) -> Dict[str, Any]:
        """Check if API is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to API at {self.base_url}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current API statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch stats: {e}")
            return {}

    def query_api(self, question: str, user_role: str = "general", 
                  include_sources: bool = True) -> Dict[str, Any]:
        """
        Query the API

        Args:
            question: Question to ask
            user_role: User role (general, doctor, receptionist, billing)
            include_sources: Whether to include source documents

        Returns:
            API response
        """
        payload = {
            "question": question,
            "user_role": user_role,
            "include_sources": include_sources
        }

        response = requests.post(
            f"{self.base_url}/query",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases"""
        return [
            {
                "id": "TC001",
                "category": "factual_recall",
                "difficulty": "easy",
                "question": "What are the visiting hours for ICU patients?",
                "user_role": "general",
                "expected_answer_contains": ["10:00 AM", "12:00 PM", "4:00 PM", "6:00 PM"],
                "expected_source_files": ["visiting_hours.txt"]
            },
            {
                "id": "TC002",
                "category": "factual_recall",
                "difficulty": "easy",
                "question": "What documents are required for hospital admission?",
                "user_role": "receptionist",
                "expected_answer_contains": ["photo ID", "insurance card", "emergency contact"],
                "expected_source_files": ["admission_policy.txt"]
            },
            {
                "id": "TC003",
                "category": "factual_recall",
                "difficulty": "medium",
                "question": "How much does a CT scan of the chest cost?",
                "user_role": "billing",
                "expected_answer_contains": ["900", "1400", "contrast"],
                "expected_source_files": ["diagnostics_pricing_guide.txt"]
            },
            {
                "id": "TC004",
                "category": "multi_hop",
                "difficulty": "hard",
                "question": "If I need to schedule a dental appointment and want to know the costs, what should I do?",
                "user_role": "general",
                "expected_answer_contains": ["call", "555", "online", "100", "150"],
                "expected_source_files": ["dental_clinic_faq.txt"]
            },
            {
                "id": "TC005",
                "category": "comparison",
                "difficulty": "medium",
                "question": "What's the difference between ICU and regular visiting hours?",
                "user_role": "general",
                "expected_answer_contains": ["ICU", "medical", "8:00", "10:00"],
                "expected_source_files": ["visiting_hours.txt"]
            },
            {
                "id": "TC006",
                "category": "policy",
                "difficulty": "medium",
                "question": "Can visitors bring outside food for patients?",
                "user_role": "general",
                "expected_answer_contains": ["allowed", "unless", "dietary"],
                "expected_source_files": ["visiting_hours.txt"]
            },
            {
                "id": "TC007",
                "category": "numerical",
                "difficulty": "easy",
                "question": "How much does a complete blood count test cost?",
                "user_role": "billing",
                "expected_answer_contains": ["45"],
                "expected_source_files": ["diagnostics_pricing_guide.txt"]
            },
            {
                "id": "TC008",
                "category": "policy",
                "difficulty": "medium",
                "question": "What is the hospital's cancellation policy for dental appointments?",
                "user_role": "receptionist",
                "expected_answer_contains": ["24", "hour", "50", "fee"],
                "expected_source_files": ["dental_clinic_faq.txt"]
            },
            {
                "id": "TC009",
                "category": "out_of_scope",
                "difficulty": "hard",
                "question": "What medication should I take for my headache?",
                "user_role": "general",
                "expected_answer_contains": ["don't", "cannot", "consult", "medical professional"],
                "expected_source_files": [],
                "expect_refusal": True
            },
            {
                "id": "TC010",
                "category": "edge_case",
                "difficulty": "hard",
                "question": "What should I do if my insurance claim is denied?",
                "user_role": "billing",
                "expected_answer_contains": ["appeal", "documentation", "Patient Financial"],
                "expected_source_files": ["billing_and_insurance.txt"]
            }
        ]

    def evaluate_answer_quality(self, test_case: Dict[str, Any], 
                                answer: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate answer quality"""
        metrics = {}

        # Keyword coverage
        expected_keywords = test_case.get("expected_answer_contains", [])
        if expected_keywords:
            answer_lower = answer.lower()
            matched = [kw for kw in expected_keywords if kw.lower() in answer_lower]
            metrics["keyword_coverage"] = len(matched) / len(expected_keywords)
            metrics["matched_keywords"] = matched
            metrics["missing_keywords"] = [kw for kw in expected_keywords if kw not in matched]
        else:
            metrics["keyword_coverage"] = 1.0
            metrics["matched_keywords"] = []
            metrics["missing_keywords"] = []

        # Answer length
        metrics["answer_length_words"] = len(answer.split())
        metrics["answer_length_chars"] = len(answer)

        # Sources count
        metrics["sources_count"] = len(sources)

        # Refusal detection
        refusal_indicators = [
            "don't have", "cannot", "can't", "unable to",
            "don't provide", "not able to", "consult", "medical professional"
        ]
        answer_lower = answer.lower()
        metrics["is_refusal"] = any(ind in answer_lower for ind in refusal_indicators)
        metrics["expected_refusal"] = test_case.get("expect_refusal", False)

        return metrics

    def evaluate_retrieval(self, test_case: Dict[str, Any], 
                          sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate retrieval performance"""
        metrics = {}

        expected_files = test_case.get("expected_source_files", [])
        retrieved_files = [s.get("filename", "") for s in sources]

        # Precision@K
        if len(retrieved_files) > 0:
            relevant = sum(1 for f in retrieved_files if any(exp in f for exp in expected_files))
            metrics["precision_at_k"] = relevant / len(retrieved_files)
        else:
            metrics["precision_at_k"] = 0.0

        # Recall@K
        if len(expected_files) > 0:
            retrieved = sum(1 for exp in expected_files if any(exp in f for f in retrieved_files))
            metrics["recall_at_k"] = retrieved / len(expected_files)
        else:
            metrics["recall_at_k"] = 1.0

        # F1 Score
        p = metrics["precision_at_k"]
        r = metrics["recall_at_k"]
        if p + r > 0:
            metrics["f1_score"] = 2 * (p * r) / (p + r)
        else:
            metrics["f1_score"] = 0.0

        metrics["retrieved_files"] = retrieved_files
        metrics["expected_files"] = expected_files

        return metrics

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        print(f"\n{'='*70}")
        print(f"Test: {test_case['id']} - {test_case['category']}")
        print(f"Q: {test_case['question']}")
        print(f"{'='*70}")

        start_time = time.time()

        try:
            # Query API
            result = self.query_api(
                question=test_case["question"],
                user_role=test_case["user_role"],
                include_sources=True
            )

            query_time = time.time() - start_time

            # Evaluate
            quality_metrics = self.evaluate_answer_quality(
                test_case,
                result["answer"],
                result.get("sources", [])
            )

            retrieval_metrics = self.evaluate_retrieval(
                test_case,
                result.get("sources", [])
            )

            # Determine pass/fail
            keyword_threshold = 0.5
            retrieval_threshold = 0.3

            if test_case.get("expect_refusal", False):
                passed = quality_metrics["is_refusal"]
            else:
                passed = (
                    quality_metrics["keyword_coverage"] >= keyword_threshold and
                    retrieval_metrics["recall_at_k"] >= retrieval_threshold
                )

            # Compile results
            test_result = {
                "test_id": test_case["id"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "question": test_case["question"],
                "answer": result["answer"],
                "query_time": round(query_time, 3),
                "passed": passed,
                **quality_metrics,
                **retrieval_metrics
            }

            # Print summary
            print(f"✓ Keyword Coverage: {quality_metrics['keyword_coverage']:.2%}")
            print(f"✓ Query Time: {query_time:.3f}s")
            print(f"✓ Sources Retrieved: {len(result.get('sources', []))}")
            print(f"{'✅ TEST PASSED' if passed else '❌ TEST FAILED'}")

            if not passed:
                if quality_metrics["keyword_coverage"] < keyword_threshold:
                    print(f"   - Low keyword coverage: {quality_metrics['keyword_coverage']:.2%}")
                    print(f"   - Missing: {quality_metrics['missing_keywords']}")
                if retrieval_metrics["recall_at_k"] < retrieval_threshold:
                    print(f"   - Low recall: {retrieval_metrics['recall_at_k']:.2%}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            test_result = {
                "test_id": test_case["id"],
                "category": test_case["category"],
                "question": test_case["question"],
                "error": str(e),
                "passed": False,
                "query_time": time.time() - start_time
            }

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases"""
        test_cases = self._load_test_cases()

        print(f"\n{'='*70}")
        print("API-BASED RAG EVALUATION")
        print(f"{'='*70}")
        print(f"Base URL: {self.base_url}")
        print(f"Rate Limit: {self.request_delay}s between requests")
        print(f"Total Tests: {len(test_cases)}\n")

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nProgress: {i}/{len(test_cases)}")

            result = self.run_single_test(test_case)
            self.results["individual_results"].append(result)

            # Rate limiting
            if i < len(test_cases):
                print(f"⏳ Waiting {self.request_delay}s...")
                time.sleep(self.request_delay)

        # Calculate aggregates
        self._calculate_aggregates()

        return self.results

    def _calculate_aggregates(self):
        """Calculate aggregate metrics"""
        results = self.results["individual_results"]
        valid = [r for r in results if "error" not in r]

        if not valid:
            return

        # Overall metrics
        self.results["metrics"]["total_tests"] = len(results)
        self.results["metrics"]["passed_tests"] = sum(1 for r in valid if r.get("passed"))
        self.results["metrics"]["pass_rate"] = self.results["metrics"]["passed_tests"] / len(valid)

        # Quality
        self.results["metrics"]["avg_keyword_coverage"] = statistics.mean(
            r.get("keyword_coverage", 0) for r in valid
        )
        self.results["metrics"]["avg_answer_length"] = statistics.mean(
            r.get("answer_length_words", 0) for r in valid
        )

        # Retrieval
        self.results["metrics"]["avg_precision_at_k"] = statistics.mean(
            r.get("precision_at_k", 0) for r in valid
        )
        self.results["metrics"]["avg_recall_at_k"] = statistics.mean(
            r.get("recall_at_k", 0) for r in valid
        )
        self.results["metrics"]["avg_f1_score"] = statistics.mean(
            r.get("f1_score", 0) for r in valid
        )

        # Performance
        query_times = [r.get("query_time", 0) for r in valid]
        self.results["metrics"]["avg_query_time"] = statistics.mean(query_times)
        self.results["metrics"]["min_query_time"] = min(query_times)
        self.results["metrics"]["max_query_time"] = max(query_times)

    def print_summary(self):
        """Print evaluation summary"""
        print(f"\n{'='*70}")
        print("EVALUATION SUMMARY")
        print(f"{'='*70}")

        metrics = self.results["metrics"]

        print(f"\n📊 Overall Performance:")
        print(f"   Total Tests: {metrics.get('total_tests', 0)}")
        print(f"   Passed: {metrics.get('passed_tests', 0)}")
        print(f"   Pass Rate: {metrics.get('pass_rate', 0):.2%}")

        print(f"\n📈 Quality Metrics:")
        print(f"   Avg Keyword Coverage: {metrics.get('avg_keyword_coverage', 0):.2%}")
        print(f"   Avg Precision@K: {metrics.get('avg_precision_at_k', 0):.2%}")
        print(f"   Avg Recall@K: {metrics.get('avg_recall_at_k', 0):.2%}")
        print(f"   Avg F1 Score: {metrics.get('avg_f1_score', 0):.3f}")

        print(f"\n⚡ Performance:")
        print(f"   Avg Query Time: {metrics.get('avg_query_time', 0):.3f}s")
        print(f"   Min Query Time: {metrics.get('min_query_time', 0):.3f}s")
        print(f"   Max Query Time: {metrics.get('max_query_time', 0):.3f}s")

        print(f"\n{'='*70}")

    def save_results(self, filename: str = None):
        """Save results to JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_evaluation_results_{timestamp}.json"

        output_path = Path("results") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Results saved: {output_path}")
        return str(output_path)


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Evaluate RAG API")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="Base URL of the API")
    parser.add_argument("--delay", type=float, default=2.0,
                       help="Delay between requests (seconds)")
    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     Healthcare RAG API Evaluation - Production Test          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Initialize evaluator
    evaluator = APIEvaluator(base_url=args.base_url, request_delay=args.delay)

    # Check API health
    print(f"\n🔍 Checking API health at {args.base_url}...")
    try:
        health = evaluator.check_health()
        print(f"✅ API Status: {health.get('status')}")
        print(f"✅ Documents: {health.get('document_count')}")
        print(f"✅ Vector DB: {health.get('vector_db_status')}")

        if health.get('document_count', 0) == 0:
            print("\n⚠️  WARNING: No documents in vector database!")
            print("   Run /ingest endpoint first.")
            return

    except ConnectionError as e:
        print(f"❌ {e}")
        print("\nMake sure the API is running:")
        print("   python -m backend.main")
        return

    # Get stats
    stats = evaluator.get_stats()
    if stats:
        print(f"\n📋 Configuration:")
        print(f"   Chunk Size: {stats.get('chunk_size')}")
        print(f"   Top K: {stats.get('retrieval_top_k')}")
        print(f"   Model: {stats.get('chat_model')}")

    # Run evaluation
    results = evaluator.run_all_tests()

    # Print summary
    evaluator.print_summary()

    # Save results
    evaluator.save_results()

    print(f"\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()
