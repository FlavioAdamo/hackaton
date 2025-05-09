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
 

class AnalyzeRule(dspy.Signature):
    """Analyze if a specific rule is triggered based on the interview response."""

    interview_response = dspy.InputField()
    rule_id = dspy.InputField()
    rule_condition = dspy.InputField()
    is_triggered = dspy.OutputField(
        desc="'Vero' se la regola é attivata all'interno della situazione descritta nell'intervista, 'Falso' se é l'opposto della regola all'interno della situazione descritta nell'intervista, 'Non Trigger' se la regola non e applicabile alla situazione descritta nell'intervista. Un tag puó essere triggerato più volte all'interno dell'intervista"	
    )
    relevant_sentence = dspy.OutputField(
        desc="La frase rilevante dell'intervista che ha attivato la regola o ha portato alla conclusione che non e attivata."
    )

    def __call__(self, interview_response, rule_id, rule_condition):
        messages = [
            {
                "role": "system",
                "content": "Sei un'IA che analizza le risposte delle interviste in italiano. Valuta le frasi solo quando il candidato racconta azioni che ha svolto durante la situazione che ci racconta."
            },
            {
                "role": "user", 
                "content": f"""
                Risposta dell'intervista:
                {interview_response}

                ID Regola: {rule_id}
                Condizione della Regola (applicale solo quando il candidato racconta azioni che ha svolto durante la situazione che ci racconta. Le intenzioni sono 'Non Trigger'): {rule_condition}

                # Guidelines
                Basandosi sulla risposta dell'intervista, la condizione della regola e soddisfatta?
                Rispondere con una delle seguenti opzioni:
                - 'Vero' se la regola è soddisfatta dalla azione messa in atto dal candidato e non perchè si è autovalutato come 'true' o 'false' rispetto a qualche regola
                - 'Falso' se la regola e chiaramente non soddisfatta, come ad esempio se il candidato risponde o agisce in maniera opposta rispetto alla regola
                - 'Non presente' se la regola non e chiaramente soddisfatta e non si applica alla situazione descritta nell'intervista, o se la regola non e applicabile alla situazione descritta nell'intervista ma e applicabile a livello generale

                'Vero' e 'Falso' vanno applicate solo se la risposta del candidato fa riferimento alla situazione descritta nell'intervista e non per una risposta che non si riferisce alla situazione descritta nell'intervista.
                Se il candidato valuta se stesso e avresti valutato la frase dove appunto si valuta da solo come 'true' o 'false' rispetto a qualche regola, allora valuta quella frase come 'non trigger'.

                Fornire sempre la frase rilevante dell'intervista che ha portato a questa conclusione, sia per 'Vero' che per 'Falso'.

                Formato della risposta:
                Risposta: [Vero/Falso]
                Frase rilevante: [Frase dell'intervista o 'Non presente']
                Spiegazione: [Breve spiegazione della scelta]
                """
            }
        ]

        response = lm(messages=messages, temperature=0.1, max_tokens=20000)
        response_text = response[0]
        response_lines = response_text.split("\n")
        is_triggered = response_lines[0].split(": ")[1]
        relevant_sentence = (
            response_lines[1].split(": ")[1]
            if len(response_lines) > 1
            else "Non presente"
        )

        return dspy.Prediction(
            is_triggered=is_triggered,
            relevant_sentence=remove_accents(relevant_sentence),
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
    analyzer = dspy.Predict(AnalyzeRule)
    result = analyzer(
        interview_response=interview_response,
        rule_id=rule["id"],
        rule_condition=rule["trigger_condition"],
    )

    is_triggered_text = result.is_triggered.lower()

    relevant_sentences = result.relevant_sentence.split('"Candidate:')
    relevant_sentences = [
        sentence.strip() for sentence in relevant_sentences if sentence.strip()
    ]

    true_count = 0
    false_count = 0

    if "vero" in is_triggered_text:
        true_count = len(relevant_sentences)
    if "falso" in is_triggered_text:
        false_count = len(relevant_sentences)
    if "non presente" in is_triggered_text:
        not_triggered_count = len(relevant_sentences)

    points = (true_count * rule["true_score"]) + (false_count * rule["false_score"])

    evaluation = {
        "ID Regola": rule["id"],
        "Tag": remove_accents(rule["tag"]),
        "Tag aggiunto": is_triggered_text.capitalize(),
        "Punti vero": rule["true_score"],
        "Punti falso": rule["false_score"],
        "Punti non trigger": rule["notrigger_score"],
        "Punti": points,
        "Verita": is_triggered_text.capitalize(),
        "Frase rilevante": [
            remove_accents(sentence) for sentence in relevant_sentences
        ],
    }

    return evaluation


def calculate_final_score(scores, evaluations):
    total_score = sum(scores.values())

    output = "Interview Scores:\n"
    for category, score in scores.items():
        output += f"{category}: {score:.1f}\n"
    output += f"\nTotal Score: {total_score:.1f}\n"

    output += "\nDetailed Evaluations:\n"
    for eval in evaluations:
        output += json.dumps(eval, indent=2) + "\n"

    with open("interview_evaluation.txt", "w", encoding="utf-8") as file:
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
    print("Detailed evaluations have been saved to 'interview_evaluation.txt'")


if __name__ == "__main__":
    main()
