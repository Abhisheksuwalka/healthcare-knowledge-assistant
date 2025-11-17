"""
RAG Performance Evaluation Framework - IMPROVED VERSION
Comprehensive metrics for Healthcare Knowledge Assistant

Metrics Measured:
1. Answer Quality (Correctness, Relevance, Faithfulness)
2. Retrieval Performance (Precision@K, Recall@K, MRR)
3. Latency & Speed (Query time, Embedding time)
4. Source Attribution Accuracy

Phase 1: Baseline measurement with current settings
Phase 2: Comparison after optimization

IMPROVEMENTS:
- Added rate limiting protection with configurable delays
- Fixed source retrieval verification
- Better error handling and diagnostics
- Document existence checks before evaluation
"""

import time
import json
import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

# Import backend components
import sys
sys.path.append('..')

from backend.rag_engine import rag_engine
from backend.document_processor import document_processor
from backend.config import settings
from backend.models import UserRole


class RAGEvaluator:
    """
    Comprehensive RAG evaluation system with multiple metrics
    """

    # Rate limiting configuration
    REQUEST_DELAY = 2.0  # Seconds to wait between API calls (adjustable)

    def __init__(self):
        """Initialize evaluator with test cases"""
        self.test_cases = self._load_test_cases()
        self.results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "retrieval_top_k": settings.RETRIEVAL_TOP_K,
                "llm_temperature": settings.LLM_TEMPERATURE,
                "llm_max_tokens": settings.LLM_MAX_TOKENS,
                "embedding_model": settings.EMBEDDING_MODEL,
                "chat_model": settings.CHAT_MODEL,
                "request_delay": self.REQUEST_DELAY
            },
            "metrics": {},
            "individual_results": []
        }

        # Check if documents are ingested
        self._verify_setup()

    def _verify_setup(self):
        """Verify that the vector database has documents"""
        doc_count = document_processor.get_document_count()
        print(f"\n{'='*70}")
        print(f"SETUP VERIFICATION")
        print(f"{'='*70}")
        print(f"📊 Documents in vector database: {doc_count}")

        if doc_count == 0:
            print("\n⚠️  WARNING: No documents found in vector database!")
            print("   Please run document ingestion first:")
            print("   1. Ensure documents are in ./data/sample_docs/")
            print("   2. Run the ingestion process")
            print("\n   The evaluation will continue but will likely fail.")
            input("\nPress Enter to continue anyway or Ctrl+C to abort...")
        else:
            print(f"✓ Vector database is ready with {doc_count} chunks")

        print(f"{'='*70}\n")

    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """
        Load comprehensive test cases covering various scenarios

        Returns:
            List of test case dictionaries
        """
        return [
            # === FACTUAL RECALL TESTS ===
            {
                "id": "TC001",
                "category": "factual_recall",
                "difficulty": "easy",
                "question": "What are the visiting hours for ICU patients?",
                "user_role": "general",
                "expected_answer_contains": ["10:00 AM", "12:00 PM", "4:00 PM", "6:00 PM"],
                "expected_source_files": ["visiting_hours.txt"],
                "ground_truth": "ICU visiting hours are 10:00 AM - 12:00 PM and 4:00 PM - 6:00 PM"
            },
            {
                "id": "TC002",
                "category": "factual_recall",
                "difficulty": "easy",
                "question": "What documents are required for hospital admission?",
                "user_role": "receptionist",
                "expected_answer_contains": ["photo ID", "insurance card", "emergency contact"],
                "expected_source_files": ["admission_policy.txt"],
                "ground_truth": "Valid government-issued photo identification, Insurance card or proof of financial arrangement, Emergency contact information"
            },
            {
                "id": "TC003",
                "category": "factual_recall",
                "difficulty": "medium",
                "question": "How much does a CT scan of the chest cost?",
                "user_role": "billing",
                "expected_answer_contains": ["900", "1400", "contrast"],
                "expected_source_files": ["diagnostics_pricing_guide.txt"],
                "ground_truth": "CT Chest without contrast costs $900, with contrast costs $1,400"
            },
            # === MULTI-HOP REASONING TESTS ===
            {
                "id": "TC004",
                "category": "multi_hop",
                "difficulty": "hard",
                "question": "If I need to schedule a dental appointment and want to know the costs, what should I do and what can I expect to pay for a routine cleaning?",
                "user_role": "general",
                "expected_answer_contains": ["call", "(555) 123-4600", "online", "$100", "$150"],
                "expected_source_files": ["dental_clinic_faq.txt"],
                "ground_truth": "Schedule by calling (555) 123-4600 or online at www.hospital.org/dental. Routine cleaning costs $100-$150"
            },
            {
                "id": "TC005",
                "category": "multi_hop",
                "difficulty": "hard",
                "question": "What financial assistance is available for uninsured patients and how do I apply?",
                "user_role": "billing",
                "expected_answer_contains": ["charity care", "income", "application", "30%"],
                "expected_source_files": ["billing_and_insurance.txt"],
                "ground_truth": "Charity Care Program available based on income. Self-pay discount of 30%. Apply at Admissions with income documentation"
            },
            # === COMPARISON/ANALYSIS TESTS ===
            {
                "id": "TC006",
                "category": "comparison",
                "difficulty": "medium",
                "question": "What's the difference between visiting hours for ICU and regular medical-surgical units?",
                "user_role": "general",
                "expected_answer_contains": ["ICU", "medical-surgical", "8:00", "10:00"],
                "expected_source_files": ["visiting_hours.txt"],
                "ground_truth": "ICU: 10 AM-12 PM and 4-6 PM. Medical-Surgical: 8 AM - 8 PM daily"
            },
            # === POLICY/PROCEDURE TESTS ===
            {
                "id": "TC007",
                "category": "policy",
                "difficulty": "medium",
                "question": "What is the hospital's cancellation policy for dental appointments?",
                "user_role": "receptionist",
                "expected_answer_contains": ["24", "hour", "$50", "fee"],
                "expected_source_files": ["dental_clinic_faq.txt"],
                "ground_truth": "24-hour notice required. Late cancellations or no-shows may result in $50 fee"
            },
            {
                "id": "TC008",
                "category": "policy",
                "difficulty": "medium",
                "question": "Can visitors bring outside food for patients?",
                "user_role": "general",
                "expected_answer_contains": ["allowed", "unless restricted", "dietary"],
                "expected_source_files": ["visiting_hours.txt"],
                "ground_truth": "Outside food allowed for patients unless medically restricted"
            },
            # === NUMERICAL/PRICING TESTS ===
            {
                "id": "TC009",
                "category": "numerical",
                "difficulty": "easy",
                "question": "How much does a complete blood count (CBC) test cost?",
                "user_role": "billing",
                "expected_answer_contains": ["$45", "45"],
                "expected_source_files": ["diagnostics_pricing_guide.txt"],
                "ground_truth": "$45"
            },
            {
                "id": "TC010",
                "category": "numerical",
                "difficulty": "medium",
                "question": "What's the price range for dental braces?",
                "user_role": "general",
                "expected_answer_contains": ["$4,000", "$7,000", "payment plans"],
                "expected_source_files": ["dental_clinic_faq.txt"],
                "ground_truth": "Traditional braces: $4,000-$7,000 with payment plans available"
            },
            # === EDGE CASES ===
            {
                "id": "TC011",
                "category": "edge_case",
                "difficulty": "hard",
                "question": "What should I do if my insurance claim is denied?",
                "user_role": "billing",
                "expected_answer_contains": ["appeal", "documentation", "30 days"],
                "expected_source_files": ["billing_and_insurance.txt"],
                "ground_truth": "Hospital will file initial appeal. Contact Patient Financial Services within 60 days with documentation"
            },
            {
                "id": "TC012",
                "category": "edge_case",
                "difficulty": "hard",
                "question": "Are there any restrictions on who can visit pediatric patients?",
                "user_role": "receptionist",
                "expected_answer_contains": ["parents", "24-hour", "siblings", "healthy"],
                "expected_source_files": ["visiting_hours.txt"],
                "ground_truth": "Parents/Guardians: 24-hour access. Siblings must be healthy (no symptoms)"
            },
            # === AMBIGUOUS/CLARIFICATION TESTS ===
            {
                "id": "TC013",
                "category": "ambiguous",
                "difficulty": "medium",
                "question": "How do I get my medical records?",
                "user_role": "general",
                "expected_answer_contains": ["Medical Records", "(555)", "first copy", "free"],
                "expected_source_files": ["billing_and_insurance.txt"],
                "ground_truth": "Request from Medical Records: (555) 123-4580. First copy free, additional copies $25"
            },
            # === OUT-OF-SCOPE TESTS (Should decline gracefully) ===
            {
                "id": "TC014",
                "category": "out_of_scope",
                "difficulty": "hard",
                "question": "What medication should I take for my headache?",
                "user_role": "general",
                "expected_answer_contains": ["don't have", "medical advice", "consult", "healthcare professional"],
                "expected_source_files": [],
                "ground_truth": "Should decline to provide medical advice",
                "expect_refusal": True
            },
            {
                "id": "TC015",
                "category": "out_of_scope",
                "difficulty": "hard",
                "question": "Can you diagnose my symptoms?",
                "user_role": "doctor",
                "expected_answer_contains": ["cannot", "diagnosis", "medical professional"],
                "expected_source_files": [],
                "ground_truth": "Should decline to provide diagnosis",
                "expect_refusal": True
            }
        ]


    def evaluate_answer_quality(
        self,
        test_case: Dict[str, Any],
        answer: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate answer quality using multiple metrics

        Args:
            test_case: Test case dictionary
            answer: Generated answer
            sources: Retrieved source documents

        Returns:
            Dictionary with quality metrics
        """
        metrics = {}

        # 1. Keyword Coverage Score
        expected_keywords = test_case.get("expected_answer_contains", [])
        if expected_keywords:
            answer_lower = answer.lower()
            matched_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
            metrics["keyword_coverage"] = len(matched_keywords) / len(expected_keywords)
            metrics["matched_keywords"] = matched_keywords
            metrics["missing_keywords"] = [kw for kw in expected_keywords if kw not in matched_keywords]
        else:
            metrics["keyword_coverage"] = 1.0
            metrics["matched_keywords"] = []
            metrics["missing_keywords"] = []

        # 2. Answer Length
        metrics["answer_length_words"] = len(answer.split())
        metrics["answer_length_chars"] = len(answer)

        # 3. Source Attribution
        metrics["sources_count"] = len(sources)

        # 4. Refusal Detection (for out-of-scope questions)
        refusal_indicators = [
            "don't have", "cannot", "can't", "unable to",
            "don't provide", "not able to", "consult",
            "medical professional", "healthcare professional"
        ]
        answer_lower = answer.lower()
        metrics["is_refusal"] = any(indicator in answer_lower for indicator in refusal_indicators)
        metrics["expected_refusal"] = test_case.get("expect_refusal", False)

        return metrics

    def evaluate_retrieval_performance(
        self,
        test_case: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate retrieval performance metrics

        Args:
            test_case: Test case dictionary
            sources: Retrieved source documents

        Returns:
            Dictionary with retrieval metrics
        """
        metrics = {}

        expected_files = test_case.get("expected_source_files", [])
        retrieved_files = [s["filename"] for s in sources]

        # Precision@K: What fraction of retrieved docs are relevant?
        if len(retrieved_files) > 0:
            relevant_retrieved = sum(1 for f in retrieved_files if any(exp in f for exp in expected_files))
            metrics["precision_at_k"] = relevant_retrieved / len(retrieved_files)
        else:
            metrics["precision_at_k"] = 0.0

        # Recall@K: What fraction of relevant docs were retrieved?
        if len(expected_files) > 0:
            retrieved_expected = sum(1 for exp in expected_files if any(exp in f for f in retrieved_files))
            metrics["recall_at_k"] = retrieved_expected / len(expected_files)
        else:
            metrics["recall_at_k"] = 1.0  # No expected files means any retrieval is acceptable

        # F1 Score
        if metrics["precision_at_k"] + metrics["recall_at_k"] > 0:
            metrics["f1_score"] = 2 * (metrics["precision_at_k"] * metrics["recall_at_k"]) / (metrics["precision_at_k"] + metrics["recall_at_k"])
        else:
            metrics["f1_score"] = 0.0

        # Mean Reciprocal Rank (MRR)
        # Find position of first relevant document
        mrr = 0.0
        for i, filename in enumerate(retrieved_files, 1):
            if any(exp in filename for exp in expected_files):
                mrr = 1.0 / i
                break
        metrics["mrr"] = mrr

        metrics["retrieved_files"] = retrieved_files
        metrics["expected_files"] = expected_files

        return metrics

    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case and collect all metrics

        Args:
            test_case: Test case dictionary

        Returns:
            Complete results for this test
        """
        print(f"\n{'='*70}")
        print(f"Running Test Case: {test_case['id']} - {test_case['category']}")
        print(f"Question: {test_case['question']}")
        print(f"{'='*70}")

        # Measure query execution time
        start_time = time.time()

        try:
            result = rag_engine.query(
                question=test_case["question"],
                user_role=UserRole(test_case["user_role"]),
                include_sources=True
            )

            query_time = time.time() - start_time

            # Evaluate metrics
            quality_metrics = self.evaluate_answer_quality(
                test_case,
                result["answer"],
                result["sources"]
            )

            retrieval_metrics = self.evaluate_retrieval_performance(
                test_case,
                result["sources"]
            )

            # Determine if test passed
            keyword_threshold = 0.5  # At least 50% of keywords should be present
            retrieval_threshold = 0.3  # At least 30% recall

            if test_case.get("expect_refusal", False):
                # For out-of-scope questions, pass if it refused
                passed = quality_metrics["is_refusal"]
            else:
                # For normal questions, check keyword coverage and retrieval
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
            print(f"✓ Sources Retrieved: {len(result['sources'])}")

            if passed:
                print(f"✅ TEST PASSED")
            else:
                print(f"❌ TEST FAILED")
                if quality_metrics["keyword_coverage"] < keyword_threshold:
                    print(f"   - Low keyword coverage: {quality_metrics['keyword_coverage']:.2%}")
                    print(f"   - Missing: {quality_metrics['missing_keywords']}")
                if retrieval_metrics["recall_at_k"] < retrieval_threshold:
                    print(f"   - Low recall: {retrieval_metrics['recall_at_k']:.2%}")

        except Exception as e:
            print(f"❌ Error during test execution: {str(e)}")
            test_result = {
                "test_id": test_case["id"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "question": test_case["question"],
                "error": str(e),
                "passed": False,
                "query_time": time.time() - start_time
            }

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test cases with rate limiting protection

        Returns:
            Complete evaluation results
        """
        print(f"\n{'='*70}")
        print(f"STARTING COMPREHENSIVE RAG EVALUATION")
        print(f"{'='*70}")
        print(f"\n⏱️  Rate Limiting: {self.REQUEST_DELAY}s delay between requests")
        print(f"📊 Total test cases: {len(self.test_cases)}\n")

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\nProgress: {i}/{len(self.test_cases)}")

            # Run test
            result = self.run_single_test(test_case)
            self.results["individual_results"].append(result)

            # RATE LIMITING: Add delay between requests (except after last one)
            if i < len(self.test_cases):
                print(f"\n⏳ Waiting {self.REQUEST_DELAY}s before next request...")
                time.sleep(self.REQUEST_DELAY)

        # Calculate aggregate metrics
        self._calculate_aggregate_metrics()

        return self.results

    def _calculate_aggregate_metrics(self):
        """Calculate aggregate metrics from all test results"""
        results = self.results["individual_results"]

        if not results:
            return

        # Filter out errored tests
        valid_results = [r for r in results if "error" not in r]

        if not valid_results:
            print("\n⚠️  No valid results to calculate metrics")
            return

        # Overall metrics
        self.results["metrics"]["total_tests"] = len(results)
        self.results["metrics"]["passed_tests"] = sum(1 for r in valid_results if r.get("passed", False))
        self.results["metrics"]["pass_rate"] = self.results["metrics"]["passed_tests"] / len(valid_results)

        # Quality metrics
        self.results["metrics"]["avg_keyword_coverage"] = statistics.mean(
            r.get("keyword_coverage", 0) for r in valid_results
        )
        self.results["metrics"]["avg_answer_length"] = statistics.mean(
            r.get("answer_length_words", 0) for r in valid_results
        )

        # Retrieval metrics
        self.results["metrics"]["avg_precision_at_k"] = statistics.mean(
            r.get("precision_at_k", 0) for r in valid_results
        )
        self.results["metrics"]["avg_recall_at_k"] = statistics.mean(
            r.get("recall_at_k", 0) for r in valid_results
        )
        self.results["metrics"]["avg_f1_score"] = statistics.mean(
            r.get("f1_score", 0) for r in valid_results
        )
        self.results["metrics"]["avg_mrr"] = statistics.mean(
            r.get("mrr", 0) for r in valid_results
        )

        # Performance metrics
        query_times = [r.get("query_time", 0) for r in valid_results]
        self.results["metrics"]["avg_query_time"] = statistics.mean(query_times)
        self.results["metrics"]["min_query_time"] = min(query_times)
        self.results["metrics"]["max_query_time"] = max(query_times)

        # Category breakdown
        categories = {}
        for test in valid_results:
            cat = test["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0}
            categories[cat]["total"] += 1
            if test.get("passed"):
                categories[cat]["passed"] += 1

        self.results["metrics"]["category_breakdown"] = {
            cat: {
                **stats,
                "pass_rate": stats["passed"] / stats["total"] if stats["total"] > 0 else 0
            }
            for cat, stats in categories.items()
        }


    def save_results(self, filename: str = None):
        """
        Save evaluation results to JSON file

        Args:
            filename: Output filename (default: auto-generated with timestamp)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rag_evaluation_results_{timestamp}.json"

        output_path = Path("results") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Results saved to: {output_path}")
        return str(output_path)

    def print_summary(self):
        """Print evaluation summary to console"""
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)

        metrics = self.results["metrics"]

        print(f"\n📊 Overall Performance:")
        print(f"   Total Tests: {metrics.get('total_tests', 0)}")
        print(f"   Passed: {metrics.get('passed_tests', 0)}")
        print(f"   Pass Rate: {metrics.get('pass_rate', 0):.2%}")

        print(f"\n📈 Quality Metrics:")
        print(f"   Avg Keyword Coverage: {metrics.get('avg_keyword_coverage', 0):.2%}")
        print(f"   Avg Precision@{settings.RETRIEVAL_TOP_K}: {metrics.get('avg_precision_at_k', 0):.2%}")
        print(f"   Avg Recall@{settings.RETRIEVAL_TOP_K}: {metrics.get('avg_recall_at_k', 0):.2%}")
        print(f"   Avg F1 Score: {metrics.get('avg_f1_score', 0):.3f}")
        print(f"   Avg MRR: {metrics.get('avg_mrr', 0):.3f}")

        print(f"\n⚡ Performance Metrics:")
        print(f"   Avg Query Time: {metrics.get('avg_query_time', 0):.3f}s")
        print(f"   Min Query Time: {metrics.get('min_query_time', 0):.3f}s")
        print(f"   Max Query Time: {metrics.get('max_query_time', 0):.3f}s")

        print(f"\n📝 Answer Quality:")
        print(f"   Avg Answer Length: {metrics.get('avg_answer_length', 0):.0f} words")

        print(f"\n📁 Category Breakdown:")
        for cat, stats in metrics.get("category_breakdown", {}).items():
            print(f"   {cat:20s}: {stats['passed']:2d}/{stats['total']:2d} ({stats['pass_rate']:.2%})")

        print("\n" + "="*70)

        # Detailed failure analysis
        failed_tests = [r for r in self.results["individual_results"] 
                       if not r.get("passed", False)]

        if failed_tests:
            print(f"\n❌ FAILED TESTS ANALYSIS ({len(failed_tests)} tests):")
            print("="*70)
            for test in failed_tests:
                print(f"\n  {test['test_id']}: {test['question'][:60]}...")
                if "error" in test:
                    print(f"    Error: {test['error']}")
                else:
                    print(f"    Keyword Coverage: {test.get('keyword_coverage', 0):.2%}")
                    print(f"    Recall@K: {test.get('recall_at_k', 0):.2%}")
                    print(f"    Sources Retrieved: {test.get('sources_count', 0)}")
                    if test.get('missing_keywords'):
                        print(f"    Missing Keywords: {test['missing_keywords']}")


def main():
    """Main execution function"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     Healthcare Knowledge Assistant - RAG Evaluator v2.0          ║
║                                                                   ║
║     Phase 1: Baseline Measurement                                ║
║     With Rate Limiting & Improved Diagnostics                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Display current configuration
    print(f"\n📋 Current Configuration:")
    print(f"   CHUNK_SIZE: {settings.CHUNK_SIZE}")
    print(f"   CHUNK_OVERLAP: {settings.CHUNK_OVERLAP}")
    print(f"   RETRIEVAL_TOP_K: {settings.RETRIEVAL_TOP_K}")
    print(f"   LLM_TEMPERATURE: {settings.LLM_TEMPERATURE}")
    print(f"   LLM_MAX_TOKENS: {settings.LLM_MAX_TOKENS}")
    print(f"   EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
    print(f"   CHAT_MODEL: {settings.CHAT_MODEL}")

    # Run evaluation
    evaluator = RAGEvaluator()
    results = evaluator.run_all_tests()

    # Print summary
    evaluator.print_summary()

    # Save results
    output_file = evaluator.save_results()

    print(f"\n✅ Evaluation complete! Results saved to: {output_file}")
    print(f"\n💡 Next Steps:")
    print(f"   1. Review the results JSON file for detailed metrics")
    print(f"   2. Identify areas for improvement")
    print(f"   3. Adjust configuration in config.py (Phase 2)")
    print(f"   4. Re-run evaluation to compare results")

    return results


if __name__ == "__main__":
    main()
