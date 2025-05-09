import os
import json
import pandas as pd
import dspy
from dotenv import load_dotenv
import openai
from rules import scoring_rules
import unicodedata

# Load environment variables
load_dotenv(".env.local")

# Set up OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in .env.local file")

# Set up DSPY with new LM configuration
lm = dspy.LM('openai/gpt-4o', api_key=openai_api_key)
dspy.configure(lm=lm)


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


# New embedding functions
def get_embedding(text):
    try:
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {str(e)}")
        return None

def cosine_similarity(a, b):
    import numpy as np
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class AnalyzeRuleWithCoT(dspy.Signature):
    """Analyze rule triggering with RAG and chain-of-thought reasoning."""
    context_chunks = dspy.InputField(desc="Relevant interview context from RAG")
    interview_response = dspy.InputField()
    rule_id = dspy.InputField()
    rule_condition = dspy.InputField()
    reasoning = dspy.OutputField(prefix="Analisi passo-passo:", 
                                desc="Valutazione dell'applicabilità della regola")
    is_triggered = dspy.OutputField(
        desc="'Vero'/'Falso'/'Non Trigger' basato sull'analisi"
    )
    relevant_sentence = dspy.OutputField(
        desc="Frase rilevante dall'intervista, se 'Non Trigger' restituisci 'Nessuna frase rilevante'"
    )


class RuleAnalyzerCoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.cot = dspy.ChainOfThought(AnalyzeRuleWithCoT)
    
    def forward(self, interview_response, rule_id, rule_condition):
        # Generate embeddings for RAG
        rule_embedding = get_embedding(rule_condition)
        interview_chunks = [interview_response[i:i+500] for i in range(0, len(interview_response), 500)]
        
        # Find most relevant chunks
        context_chunks = []
        for chunk in interview_chunks:
            chunk_embedding = get_embedding(chunk)
            if chunk_embedding and rule_embedding:
                similarity = cosine_similarity(rule_embedding, chunk_embedding)
                if similarity > 0.7:  # Adjust threshold as needed
                    context_chunks.append(chunk)
        
        return self.cot(
            context_chunks="\n".join(context_chunks[:3]),  # Top 3 relevant chunks
            interview_response=interview_response,
            rule_id=rule_id,
            rule_condition=f"""Analizza ogni risposta del candidato:
1. Per la regola {rule_id} valuta se la trigger_condition {rule_condition}
2. La frase che hai applicato alla trigger_condition, si applica al fatto che il candidato ha fatto l'azione all'interno della situazione che sta descrivendo?
3. Se si, restituisci 'Vero', se no restituisci 'Falso', se invece non è applicabile la regola, o il candidato si sta autovalutando, restituisci 'Non Trigger'"""

        )

    def __call__(self, interview_response, rule_id, rule_condition):
        max_chars = 3000
        truncated_response = interview_response[:max_chars] + ("..." if len(interview_response) > max_chars else "")
        
        try:
            response = self.forward(truncated_response, rule_id, rule_condition)
            return dspy.Prediction(
                is_triggered=response.is_triggered,
                relevant_sentence=remove_accents(response.relevant_sentence),
            )
        except Exception as e:
            print(f"Error during CoT analysis: {str(e)}")
            return dspy.Prediction(
                is_triggered="Non Trigger",
                relevant_sentence="Error during analysis"
            )


def read_interview(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def analyze_interview(interview_response, scoring_rules):
    """Analyze interview using standard method."""
    scores = {category: 0 for category in scoring_rules.keys()}
    evaluations = []

    for category, rules in scoring_rules.items():
        for rule in rules:
            evaluation = evaluate_single_question(interview_response, rule)
            evaluations.append(evaluation)
            scores[category] += evaluation["Punti"]

    return scores, evaluations


def evaluate_single_question(interview_response, rule):
    analyzer = RuleAnalyzerCoT()
    result = analyzer(
        interview_response=interview_response,
        rule_id=rule["id"],
        rule_condition=rule["trigger_condition"],
    )

    # Modified parsing logic to handle multiple triggers
    is_triggered_text = result.is_triggered.lower().replace("non trigger", "").strip()
    
    # Split and count triggers
    trigger_count = {
        "vero": is_triggered_text.count("vero"),
        "falso": is_triggered_text.count("falso")
    }
    
    # Calculate points using rule's scoring values
    points = (trigger_count["vero"] * rule["true_score"]) + (trigger_count["falso"] * rule["false_score"])

    evaluation = {
        "ID Regola": rule["id"],
        "Tag": remove_accents(rule["tag"]),
        "Descrizione": remove_accents(rule["description"]),
        "Tag aggiunto": is_triggered_text.capitalize(),
        "Punti vero": rule["true_score"],
        "Punti falso": rule["false_score"],
        "Punti non trigger": rule["notrigger_score"],
        "Punti": points,
        "Verita": is_triggered_text.capitalize(),
        "Frase rilevante": [
            remove_accents(sentence.strip()) 
            for sentence in result.relevant_sentence.split('"Candidate:')
            if sentence.strip()
        ],
    }
    return evaluation


def generate_category_summary(category_name, evaluations):
    """Generate a natural language summary for a category based on evaluations."""
    category_evals = [e for e in evaluations if e["Tag"] in [rule["tag"] for rule in scoring_rules[category_name]]]
    
    true_count = sum(1 for e in category_evals if e["Verita"].lower() == "vero")
    false_count = sum(1 for e in category_evals if e["Verita"].lower() == "falso")
    
    # Get significant behaviors (both positive and negative)
    positive_behaviors = [e["Tag"] for e in category_evals if e["Verita"].lower() == "vero"]
    negative_behaviors = [e["Tag"] for e in category_evals if e["Verita"].lower() == "falso"]
    
    summary = f"\nValutazione {category_name}:\n"
    summary += f"Il candidato ha mostrato {true_count} comportamenti positivi e {false_count} comportamenti negativi in questa area.\n"
    
    if true_count > 0:
        summary += "\nPunti di forza principali:\n"
        for behavior in positive_behaviors[:3]:  # Top 3 positive behaviors
            summary += f"- {behavior}\n"
            
    if false_count > 0:
        summary += "\nAree di miglioramento:\n"
        for behavior in negative_behaviors[:3]:  # Top 3 negative behaviors
            summary += f"- {behavior}\n"
            
    overall_sentiment = ""
    if true_count > false_count * 2:
        overall_sentiment = "Dimostra una forte competenza in quest'area."
    elif true_count > false_count:
        overall_sentiment = "Mostra una discreta competenza in quest'area, con spazio per miglioramento."
    elif true_count == false_count:
        overall_sentiment = "Mostra risultati contrastanti in quest'area, necessitando di sviluppo."
    else:
        overall_sentiment = "Necessita di significativo sviluppo in quest'area."
        
    summary += f"\nValutazione complessiva della categoria: {overall_sentiment}\n"
    return summary

def generate_overall_evaluation(scores, evaluations):
    """Generate an overall evaluation of the candidate."""
    total_score = sum(scores.values())
    total_true = sum(1 for e in evaluations if e["Verita"].lower() == "vero")
    total_false = sum(1 for e in evaluations if e["Verita"].lower() == "falso")
    
    # Identify top categories
    sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strongest_categories = sorted_categories[:2]
    weakest_categories = sorted_categories[-2:]
    
    evaluation = "\n\nVALUTAZIONE COMPLESSIVA DEL CANDIDATO\n"
    evaluation += "=" * 40 + "\n\n"
    
    evaluation += f"Il candidato ha dimostrato {total_true} comportamenti positivi e {total_false} comportamenti negativi durante l'intervista.\n\n"
    
    evaluation += "Aree di maggior forza:\n"
    for category, score in strongest_categories:
        evaluation += f"- {category}\n"
        
    evaluation += "\nAree che richiedono sviluppo:\n"
    for category, score in weakest_categories:
        evaluation += f"- {category}\n"
    
    # Overall suitability assessment
    if total_true > total_false * 2:
        evaluation += "\nValutazione generale: Il candidato dimostra un profilo molto positivo, con forti competenze in diverse aree chiave. "
    elif total_true > total_false:
        evaluation += "\nValutazione generale: Il candidato mostra un profilo generalmente positivo, con alcune aree di forza significative e opportunità di sviluppo. "
    elif total_true == total_false:
        evaluation += "\nValutazione generale: Il profilo del candidato mostra risultati contrastanti, con alcune competenze positive ma significative aree di miglioramento. "
    else:
        evaluation += "\nValutazione generale: Il profilo del candidato richiede significativo sviluppo in diverse aree chiave. "
    
    return evaluation

def calculate_final_score(scores, evaluations):
    total_score = sum(scores.values())

    # Generate base output
    output = "Interview Scores:\n"
    for category, score in scores.items():
        output += f"{category}: {score:.1f}\n"
    output += f"\nTotal Score: {total_score:.1f}\n"

    output += "\nDetailed Evaluations:\n"
    for eval in evaluations:
        output += json.dumps(eval, indent=2) + "\n"

    # Generate category summaries
    output += "\n\nVALUTAZIONI PER CATEGORIA\n"
    output += "=" * 40 + "\n"
    for category in scoring_rules.keys():
        output += generate_category_summary(category, evaluations)

    # Add overall evaluation
    output += generate_overall_evaluation(scores, evaluations)

    # Write to both files
    with open("interview_evaluation_cot.txt", "w", encoding="utf-8") as file:
        file.write(output.split("\nVALUTAZIONI PER CATEGORIA")[0])  # Original content only

    with open("interview_evaluation_cot_with_summary.txt", "w", encoding="utf-8") as file:
        file.write(output)

    return total_score


def main():
    interview_file = "interview_response.txt"
    if not os.path.exists(interview_file):
        print(f"Error: {interview_file} does not exist.")
        return

    interview_response = read_interview(interview_file)
    
    scores, evaluations = analyze_interview(interview_response, scoring_rules)
    total_score = calculate_final_score(scores, evaluations)

    print(f"Total Score: {total_score}")
    print("Detailed evaluations have been saved to 'interview_evaluation_cot.txt' and 'interview_evaluation_cot_with_summary.txt'")


if __name__ == "__main__":
    main()
