import os
import json
import pandas as pd
import dspy
from dotenv import load_dotenv
import openai
from scoring_model.regolesegmentate.piadineria import scoring_rules
import unicodedata

# Load environment variables
load_dotenv(".env.local")

# Set up OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in .env.local file")

# Set up DSPY with new LM configuration
lm = dspy.LM('openai/gpt-4o-mini', api_key=openai_api_key)
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
        desc="Valuterai tutte le frasi dell'interview dove il candidato sta raccontando una situazione e poi dirai 'Vero' se all'interno della frase la regola é attivata e applicata all'interno della situazione descritta nell'intervista, 'Falso' se all'interno della frase si verifica l'opposto della regola applicata all'interno della situazione descritta nell'intervista, 'Non Trigger' se la regola non e applicabile alla situazione descritta nell'intervista, se il candidato si autovaluta come 'true' o 'false' rispetto a qualche regola, allora valuta quella frase come 'non trigger'. Un tag puó essere triggerato più volte all'interno dell'intervista. Un tag puó contenere frasi vere e frasi false. Le emozioni non sono considerate come azioni e non vanno valutate ne in positivo ne in negativo."	
    )
    relevant_sentence = dspy.OutputField(
        desc="Python list con le frasi rilevanti dell'intervista che hanno attivato la regola (nel vero o nel falso) o 'nessuna frase rilevante' se la regola non e attivata. Ad ogni frase dai un numero progressivo che parte da 1 e fornisci per ogni frase se é 'Vero' o 'Falso' basandoti su is_triggered. Quando vero o falso, formatta il tutto mettendo numero frase, vero o falso e la frase rilevante. All'interno di ogni list possono esserci frasi vere e frasi false."
    )
    explanation = dspy.OutputField(
        desc="Breve spiegazione della scelta che ha portato a questa valutazione basandoti su is_triggered e relevant_sentence. Esplica anche quante situazioni sono state valutate per arrivare a questa conclusione. Formatta il tutto con 'Situazioni valutate: [numero situazioni valutate]' e poi la spiegazione."
    )

    def __call__(self, interview_response, rule_id, rule_condition):
        messages = [
            {
                "role": "system",
                "content": "Sei un'IA che analizza le risposte delle interviste in italiano. Il candidato ti racconterá una o piú situazioni che ha vissuto. Valuta le frasi solo quando il candidato racconta azioni che ha svolto durante la situazione che ci racconta e poi processale secondo is_triggered."
            },
            {
                "role": "user", 
                "content": f"""
                Risposta dell'intervista:
                {interview_response}

                ID Regola: {rule_id}
                Condizione della Regola (applicale solo quando il candidato racconta azioni che ha svolto durante la situazione che ci racconta. Le intenzioni sono 'Non Trigger', cosí come le autovalutazioni del candidato): {rule_condition}

                # Guidelines
                Basandosi sulla risposta dell'intervista, la condizione della regola e soddisfatta?
                Rispondere con una delle seguenti opzioni:
                - 'Vero' se la regola è soddisfatta dalla azione messa in atto dal candidato e non perchè si è autovalutato come 'true' o 'false' rispetto a qualche regola
                - 'Falso' se la regola e chiaramente non soddisfatta, come ad esempio se il candidato risponde o agisce in maniera opposta rispetto alla regola
                - 'Non presente' se la regola non e chiaramente soddisfatta e non si applica alla situazione descritta nell'intervista, o se la regola non e applicabile alla situazione descritta nell'intervista ma e applicabile a livello generale

                'Vero' e 'Falso' vanno applicate solo se la risposta del candidato fa riferimento alla situazione descritta nell'intervista e non per una risposta che non si riferisce alla situazione descritta nell'intervista.
                Se il candidato valuta se stesso e avresti valutato la frase dove appunto si valuta da solo come 'true' o 'false' rispetto a qualche regola, allora valuta quella frase come 'non trigger'.

                Fornire sempre le frasi rilevanti dell'intervista che hanno portato a questa conclusione, sia per 'Vero' che per 'Falso'.

                Formato della risposta:
                Risposta: [Vero/Falso per ogni frase che hai associato a questa regola]
                Frasi rilevanti: [Python list con tutte le frasi dell'intervista che hanno portato a questa conclusione, separate da virgole o 'Non presente']
                Spiegazione: [Breve spiegazione della scelta che ti ha spinto a dare questa valutazione]
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
        explanation = (
            response_lines[2].split(": ")[1]
            if len(response_lines) > 2
            else "Non presente"
        )

        return {
            "is_triggered": is_triggered,
            "relevant_sentence": relevant_sentence,
            "explanation": explanation
        }


def read_interview(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def analyze_interview(interview_response, scoring_rules):
    """Analyze interview using standard method."""
    evaluations = []  # Removed scores calculation

    for category, rules in scoring_rules.items():
        for rule in rules:
            evaluation = evaluate_single_question(interview_response, rule)
            evaluations.append(evaluation)

    return evaluations  # Only return evaluations now


def evaluate_single_question(interview_response, rule):
    analyzer = dspy.Predict(AnalyzeRule)
    result = analyzer(
        interview_response=interview_response,
        rule_id=rule["id"],
        rule_condition=rule["trigger_condition"],
    )

    is_triggered_text = result["is_triggered"].lower()

    relevant_sentences = result["relevant_sentence"].split('"Candidate:')
    relevant_sentences = [
        sentence.strip() for sentence in relevant_sentences if sentence.strip()
    ]

    # Remove points calculation and other unused fields
    evaluation = {
        "ID Regola": rule["id"],
        "Descrizione": rule["description"],
        "Frasi rilevanti": relevant_sentences,
        "Spiegazione": result["explanation"]
    }

    return evaluation

#inizia giudizio.
class ValutazioneFinale(dspy.Module):
    def __init__(self):
        super().__init__()
        self.riassuntore = dspy.ChainOfThought("spiegazioni -> riassunto")
    
    def forward(self, spiegazioni):
        # Unisci tutte le spiegazioni in un unico contesto
        contesto = "\n".join([f"ID {s['ID Regola']}: {s['Spiegazione']}" for s in spiegazioni])
        
        riassunto = self.riassuntore(
            spiegazioni=contesto,
            instruct_1="Sintetizza una valutazione coerente del candidato in massimo 200 parole. Inizia con 'Flessibilitá' e poi spiega se il candidato/a é flessibile o meno.",
            instruct_2="Evidenzia sia punti di forza che aree di miglioramento",
            instruct_3="Mantieni un tono professionale e oggettivo basato sulle spiegazioni"
        )
        return str(riassunto)  # Convert to string to ensure JSON serialization




def main():
    interview_file = "interview_response.txt"
    if not os.path.exists(interview_file):
        print(f"Error: {interview_file} does not exist.")
        return

    interview_response = read_interview(interview_file)
    
    # Get the evaluations (no more scores)
    evaluations = analyze_interview(interview_response, scoring_rules)
    
    # Generate final judgment
    valutazione_finale = ValutazioneFinale()
    giudizio_finale = valutazione_finale.forward(evaluations)
    
    # Save evaluations and judgment to file (updated structure)
    with open("interview_evaluation.txt", "w", encoding="utf-8") as f:
        json.dump({
            "Detailed Evaluations": evaluations,
            "Giudizio Finale": giudizio_finale
        }, f, ensure_ascii=False, indent=4)

    print("Detailed evaluations have been saved to 'interview_evaluation.txt'")


if __name__ == "__main__":
    main()
