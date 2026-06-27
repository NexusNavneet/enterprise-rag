import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Golden dataset — 10 questions with known answers
# In real project this would be 100+ questions
GOLDEN_DATASET = [
    {
        "question": "What is the leave policy for employees?",
        "ground_truth": "Employees are entitled to annual leave as per company policy. Leave must be approved by the manager."
    },
    {
        "question": "What are the password requirements?",
        "ground_truth": "Employees must follow password policy guidelines for system security."
    },
    {
        "question": "What is the GDPR compliance policy?",
        "ground_truth": "The organization follows GDPR guidelines for data privacy and protection."
    },
    {
        "question": "What happens if I violate the code of conduct?",
        "ground_truth": "Violations may result in verbal warning, suspension, or termination depending on severity."
    },
    {
        "question": "How do I request work from home?",
        "ground_truth": "Employees must follow the work from home policy and get manager approval."
    },
    {
        "question": "What is the data backup policy?",
        "ground_truth": "IT department manages data backup procedures as per the data backup policy."
    },
    {
        "question": "What are the travel reimbursement rules?",
        "ground_truth": "Employees can claim travel reimbursement as per the travel reimbursement policy."
    },
    {
        "question": "What is the whistleblower policy?",
        "ground_truth": "The organization has a whistleblower policy to protect employees who report violations."
    },
    {
        "question": "How do I install software on my work computer?",
        "ground_truth": "Software installation must follow IT policy and requires approval."
    },
    {
        "question": "What is the dress code policy?",
        "ground_truth": "Employees must follow the dress code policy as defined by HR department."
    }
]


def evaluate_single(question, ground_truth, retrieved_chunks, answer):
    """
    Evaluate a single Q&A pair
    Computes simple versions of RAGAS metrics
    """
    
    context = " ".join([chunk.page_content for chunk in retrieved_chunks])
    
    # Metric 1 — Context Recall
    # How much of the ground truth is covered by retrieved context?
    truth_words = set(ground_truth.lower().split())
    context_words = set(context.lower().split())
    context_recall = len(truth_words.intersection(context_words)) / len(truth_words)
    
    # Metric 2 — Context Precision
    # How relevant are the retrieved chunks to the question?
    question_words = set(question.lower().split())
    relevant_chunks = sum(
        1 for chunk in retrieved_chunks
        if any(word in chunk.page_content.lower() for word in question_words)
    )
    context_precision = relevant_chunks / len(retrieved_chunks)
    
    # Metric 3 — Answer Relevance
    # How much does the answer address the question?
    answer_words = set(answer.lower().split())
    relevance = len(question_words.intersection(answer_words)) / len(question_words)
    
    # Metric 4 — Faithfulness
    # Is the answer supported by the context?
    answer_words_set = set(answer.lower().split())
    faithful_words = answer_words_set.intersection(context_words)
    faithfulness = len(faithful_words) / len(answer_words_set) if answer_words_set else 0
    
    return {
        "context_recall": round(context_recall, 3),
        "context_precision": round(context_precision, 3),
        "answer_relevance": round(relevance, 3),
        "faithfulness": round(faithfulness, 3)
    }


def run_evaluation(pipeline_func, iteration=1):
    """
    Run evaluation across all golden dataset questions
    Saves results to evaluation report
    """
    
    print(f"\n{'='*50}")
    print(f"RAGAS EVALUATION — ITERATION {iteration}")
    print(f"{'='*50}")
    
    results = []
    
    for i, item in enumerate(GOLDEN_DATASET):
        print(f"\n[{i+1}/{len(GOLDEN_DATASET)}] Evaluating: {item['question'][:50]}...")
        
        try:
            # Run pipeline
            result = pipeline_func(item["question"])
            
            # Get retrieved chunks info
            from langchain_core.documents import Document
            mock_chunks = [
                Document(
                    page_content=source["preview"],
                    metadata={
                        "category": source["category"],
                        "filename": source["filename"]
                    }
                )
                for source in result["sources"]
            ]
            
            # Evaluate
            metrics = evaluate_single(
                item["question"],
                item["ground_truth"],
                mock_chunks,
                result["answer"]
            )
            
            results.append({
                "question": item["question"],
                "answer": result["answer"],
                "metrics": metrics
            })
            
            print(f"   Context Recall: {metrics['context_recall']}")
            print(f"   Context Precision: {metrics['context_precision']}")
            print(f"   Answer Relevance: {metrics['answer_relevance']}")
            print(f"   Faithfulness: {metrics['faithfulness']}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            continue
    
    # Calculate averages
    if results:
        avg_recall = sum(r["metrics"]["context_recall"] for r in results) / len(results)
        avg_precision = sum(r["metrics"]["context_precision"] for r in results) / len(results)
        avg_relevance = sum(r["metrics"]["answer_relevance"] for r in results) / len(results)
        avg_faithfulness = sum(r["metrics"]["faithfulness"] for r in results) / len(results)
        
        print(f"\n{'='*50}")
        print(f"ITERATION {iteration} SUMMARY")
        print(f"{'='*50}")
        print(f"Average Context Recall:    {avg_recall:.3f}")
        print(f"Average Context Precision: {avg_precision:.3f}")
        print(f"Average Answer Relevance:  {avg_relevance:.3f}")
        print(f"Average Faithfulness:      {avg_faithfulness:.3f}")
        
        # Save report
        save_evaluation_report(results, iteration, {
            "context_recall": avg_recall,
            "context_precision": avg_precision,
            "answer_relevance": avg_relevance,
            "faithfulness": avg_faithfulness
        })
    
    return results


def save_evaluation_report(results, iteration, averages):
    """Save evaluation results to a markdown file"""
    
    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/evaluation_iteration_{iteration}.md"
    
    with open(report_path, "w") as f:
        f.write(f"# RAGAS Evaluation Report — Iteration {iteration}\n\n")
        f.write(f"## Summary Metrics\n\n")
        f.write(f"| Metric | Score |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Context Recall | {averages['context_recall']:.3f} |\n")
        f.write(f"| Context Precision | {averages['context_precision']:.3f} |\n")
        f.write(f"| Answer Relevance | {averages['answer_relevance']:.3f} |\n")
        f.write(f"| Faithfulness | {averages['faithfulness']:.3f} |\n")
        f.write(f"\n## Detailed Results\n\n")
        
        for i, result in enumerate(results):
            f.write(f"### Question {i+1}\n")
            f.write(f"**Q:** {result['question']}\n\n")
            f.write(f"**A:** {result['answer']}\n\n")
            f.write(f"**Metrics:**\n")
            for metric, score in result['metrics'].items():
                f.write(f"- {metric}: {score}\n")
            f.write(f"\n")
    
    print(f"\n💾 Report saved to {report_path}")


if __name__ == "__main__":
    print("RAGAS Evaluation will run when API quota resets.")
    print("Golden dataset has", len(GOLDEN_DATASET), "questions ready.")
    print("Run this tomorrow after quota resets!")