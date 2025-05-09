import os
import json
import dspy
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv(".env.local")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in .env.local file")

lm = dspy.LM('openai/gpt-4o-mini', api_key=openai_api_key)
dspy.configure(lm=lm)

NODI_CONCETTO = {
    "Potenziale": { 
        "nome": "Potenziale",
        "positivo": [
            "Il candidato ha obiettivi chiari",
            "Il candidato è consapevole di sé, si conosce bene",
            "Il candidato è orientato al miglioramento continuo di se",
            "Mostra di saper crescere con impegno, riflessioni e aiuto da parte degli altri",
            "Il candidato riflette prima di esprimere il suo punto di vista",
            "Impara dall'esperienza",
            "È aperto al feedback",
            "Ricerca il feedback",
            "Ammette gli errori",
            "Rielabora criticamente le esperienze che vive",
            "È consapevole delle sue aree di competenza ed esprime liberamente quelle in cui non è competente",
            "Valuta più opzioni prima di agire",
            "Osserva gli altri per migliorare",
            "Comprende velocemente nuovi contesti e scenari",
            "È intraprendente",
            "Accetta e non cerca di evitare nuove esperienze e cambiamenti",
            "Può comunicare in modo efficace con diverse tipologie di persone",
            "Sa semplificare la complessità",
            "Fa domande per arrivare all'essenza dei problemi",
            "Porta risultati in situazioni sfidanti che affronta per la prima volta",
            "Riesce a pensare fuori dagli schemi ed identificare soluzioni inaspettate",
            "Trova soluzioni alternative di fronte agli ostacoli",
            "È consapevole dell'impatto che ha sugli altri",
            "Sa gestire il conflitto e non lo evita"
        ],
        "negativo": [
            "Fatica ad ammette errori",
            "Fatica ad ammettere di non conoscere un tema",
            "Non si mette in discussione",
            "Non mette in discussione il suo operato",
            "Poca chiarezza sui propri obiettivi",
            "Approccio passivo",
            "Accetta la prima soluzione a un problema che gli viene in mente",
            "Si fa influenzare facilmente dall'autorità senza analizzare criticamente l'opinione dell'altro",
            "È ripetitivo nella modalità di agire",
            "Fatica ad affrontare situazione e contesti nuovi",
            "È a disagio nel relazionarsi con persone diverse da lui",
            "Evita il conflitto",
            "Si ferma davanti agli ostacoli",
            "È poco consapevole delle sue aree di sviluppo",
            "È poco consapevole delle sue emozioni",
            "È poco consapevole dell'impatto che ha sugli altri",
            "È giudicante rispetto agli altri"
        ]
    },
    "Flessibilità": { 
        "nome": "Flessibilità",
        "positivo": [
            "Il candidato si adatta a diverse persone e situazioni senza difficoltà",
            "Il candidato modifica i suoi comportamenti e comunicazione in base all'interlocutore",
            "Il candidato sa cambiare modalità di lavoro o il suo approccio abituale per raggiungere l'obiettivo",
            "Resta positivo e focalizzato anche di fronte a cambi di programma, ostacoli e imprevisti",
            "Trova soluzioni alternative per superare i problemi",
            "È aperto ad accettare soluzioni che arrivano da altre persone e non da lui",
            "Sa integrare al suo pensiero idee e modalità di riflessione diverse dalle sue",
            "È aperto alle novità e ai cambiamenti"
        ],
        "negativo": [
            "Il candidato tende a seguire rigidamente le routine consolidate",
            "Il candidato fatica a cambiare le proprie abitudini",
            "Il candidato fatica a cambiare la propria idea",
            "Segue le regole in modo rigido",
            "Il candidato fatica a valutare se esistono modi migliori o più efficienti per svolgere determinate attività",
            "Il candidato è a disagio di fronte ai cambiamenti e alle situazioni nuove",
            "Il candidato utilizza lo stesso approccio e modalità di comunicazione anche con persone molto diverse tra loro",
            "Il candidato tende a bloccarsi di fronte ad ostacoli e imprevisti"
        ]
    },
    "Pensiero Strategico": { 
        "nome": "Pensiero Strategico",
        "positivo": [
            "Il candidato valuta più opzioni prima di prendere le decisioni",
            "Immagina il futuro",
            "Sa semplificare la complessità con una comunicazione chiara nella quale fornisce anche esempi",
            "Sa evitare di perdersi nel dettaglio delle situazioni, alzando lo sguardo per cogliere la complessità dell'insieme e le connessione tra le varie parti e lo schema sottostante",
            "Anticipa i problemi e i rischi delle diverse alternative",
            "Pianifica i differenti step per arrivare all'obbiettivo",
            "Sfida lo status-quo con pensieri fuori dagli schemi",
            "identifica le priorità su cui concentrarsi e guidare gli altri"
        ],
        "negativo": [
            "Visione di breve periodo, poco allenato a immaginare il futuro",
            "Focalizzato sull'implementazione di azioni pensate da altri",
            "Non mette in discussione il pensiero altrui con pensieri alternativi",
            "Si concentra sulla to-do-list e sulle urgenze, meno bravo a identificare le priorità"
        ]
    },
    "Stabilità Emotiva": { 
        "nome": "Stabilità Emotiva",
        "positivo": [
            "Il candidato comunica in modo calmo (non interrompe e non alza la voce)",
            "Sotto pressione e stress il candidato mostra di essere lucido",
            "Il candidato reagisce in modo proporzionato agli eventi sfidanti o inaspettati",
            "Il candidato si mostra collaborativo in situazioni conflittuali",
            "Il candidato si fida degli altri ed è aperto all'ascolto",
            "In situazioni conflittuali il candidato valuta i punti di vista divergenti rispetto ai suoi",
            "Il candidato si mostra controllato e di umore stabile",
            "Valuta lucidamente i possibili rischi ed elabora scelte consapevoli",
            "Il candidato si mostra comprensivo di fronte gli errori degli altri",
            "Il candidato mostra un atteggiamento resiliente",
            "Il candidato accetta la possibilità di commettere errori",
            "Il candidato resta focalizzato sugli obiettivi anche in situazioni di pressioe o difficoltà",
            "Il candidato mostra un atteggiamento positivo rispetto all'esito delle cose"
        ],
        "negativo": [
            "Il candidato agisce in modo impulsivo",
            "Il candidato si mostra ansioso o nervoso",
            "Il candidato perde lucidità in situazioni di stress o pressione",
            "Il candidato comunica in modo aggressivo",
            "Il candidato si mostra irritabile",
            "Il candidato si lamenta spesso",
            "Il candidato dimostra di essere permaloso",
            "Il candidato è concentrato solo sul suo punto di vista in situazioni conflittuali",
            "Il candidato si blocca di fronte a possibili rischi",
            "Il candidato di fronte ad aggressioni o qualsiasi conflitto si chiude",
            "Il candidato è pessimista rispetto all'esito delle cose"
        ]
    },
    "Relazione": { 
        "nome": "Relazione",
        "positivo": [
            "Il candidato ha fiducia negli altri e li incoraggia",
            "Il candidato è collaborativo",
            "Il candidato porta energia positiva in un gruppo",
            "Il candidato non è giudicante",
            "Il candidato è interessato alle opinioni altrui",
            "Il candidato è aperto al confronto",
            "Il candidato si mette nei panni degli altri",
            "Il candidato costruisce relazioni di fiducia mantenendo la parola data",
            "Il candidato comunica in modo trasparente e diretto",
            "Il candidato è flessibile e sa trovare punti di incontro",
            "Il candidato è flessibile nelle modalità di comportamento e comunicazione nei confronti degli altri",
            "Il candidato ha fiducia negli altri e chiede consigli sulle scelte da prendere",
            "Il candidato è interessato al benessere degli altri e lo dimostra nelle interazioni",
            "Il candidato è consapevole dell'impatto emotivo che ha sugli altri",
            "Il candidato si interroga sui bisogni degli altri e li considera"
        ],
        "negativo": [
            "Il candidato non è consapevole dell'impatto che ha sugli altri",
            "Non coinvolge gli altri nelle decisioni",
            "È giudicante",
            "Non ascolta, sovrappone la sua voce a quella degli altri nelle interazioni",
            "Comunica con le stesse modalità con tutti i tipi di interlocutori senza adattare stile e contenuto",
            "Non mantiene le promesse fatte",
            "Non è interessato a come stanno gli altri",
            "Non chiede consiglio",
            "Non si fida delle capacità degli altri",
            "È sospettoso",
            "Resta sempre fermo sui propri punti di vista",
            "È resistente a trovare compromessi"
        ]
    },
    "Coscienziositá": { 
        "nome": "Coscienziositá",
        "positivo": [
            "Le azioni che il candidato mette in atto sono orientate al raggiungimento degli obiettivi",
            "Il candidato è affidabile perché fa del suo meglio per portare a termine i progetti e rispettare le scadenze",
            "Il candidato si prepara e studia in modo da essere preparato e competente",
            "Il candidato è organizzato, agisce strutturando il processo e coordinando con efficienza il lavoro degli altri",
            "Il candidato è chiaro nel comunicare agli altri le scadenze",
            "Il candidato ha chiarezza sulle priorità",
            "Il candidato segue i progetti con accuratezza occupandosi anche dei dettagli che rendono il risultato di alta qualità",
            "Il candidato rispetta le regole stabilite o dategli dal suo capo",
            "Il candidato è tenace nel perseguire gli obiettivi",
            "Il candidato pianifica le attività",
            "Il candidato è disposto a rifare il lavoro se necessario",
            "Il candidato considera i rischi",
            "Il candidato tiene informate le persone sullo stato di avanzamento del progetto e condivide le informazioni nuove e importanti"
        ],
        "negativo": [
            "Procrastina",
            "Non mantiene le deadline",
            "A fronte di ostacoli si demotiva e non cerca soluzioni",
            "È approssimativo",
            "È disorganizzato",
            "Non è disponibile ad investire tempo oltre all'orario di lavoro se necessario",
            "È poco attento al dettaglio",
            "Non sa identificare le priorità",
            "Se non è competente lo nasconde",
            "Non pianifica",
            "Non si espone comunicando informazioni importanti se questo mette a rischio la sua immagine",
            "Non fa ciò che promette",
            "Si dimentica o non considera rilevante condividere le informazioni con il team di lavoro",
            "È impreparato rispetto al tema nelle riunioni o nelle presentazioni",
            "Agisce nel suo proprio interesse e non nell'interesse dell'azienda",
            "Non è attento a valutare i rischi derivanti dalle azioni che mette in atto"
        ]
    },
     "Comunicazione": { 
        "nome": "Comunicazione",
        "positivo": [
            "Il candidato è trasparente e ammette i propri errori con i suoi interlocutori",
            "Il candidato coinvolge con domande le persone",
            "Il candidato comunica le difficoltà che si stanno affrontando con trasparenza",
            "Il candidato ascolta lasciando spazio agli altri per esprimere il loro punto di vista anche se divergente al proprio",
            "Sa fare comunicazioni difficili utilizzando un linguaggio adeguato alla situazione e agli interlocutori",
            "Non ha paura di dire le cose che gli altri non hanno il coraggio di mettere in evidenza",
            "Con il linguaggio crea le condizioni per far sentire al sicuro le persone",
            "È capace di comunicare in modo semplice concetti complessi",
            "Non è giudicante in caso di errori commessi da altri e sa parlare degli errori rispettando chi li ha commessi",
            "Non si lamenta",
            "Sa fare richieste per se o per gli altri",
            "Il candidato influenza le decisioni"
        ],
        "negativo": [
            "Non è trasparente nella comunicazione",
            "La sua comunicazione è complicata e non comprensibile a tutti gli interlocutori",
            "Non sempre dice ciò che pensa",
            "Si lamenta",
            "È passivo di fronte alle decisioni che vengono prese dagli altri",
            "Non ascolta gli altri e non è quindi in grado di considerare gli elementi portati in evidenza dai suoi interlocutori",
            "È giudicante verso gli altri",
            "Attacca gli altri quando commettono errori",
            "Non fa domande"
        ]
    },
     "People Management": { 
        "nome": "People Management",
        "positivo": [
            "Il candidato si attiva perché i collaboratori si prendano la responsabilità sui progetti delegando e organizzando momenti di confronto",
            "Il candidato esprime fiducia nelle capacità dei suoi collaboratori di portare a termine le attività a loro affidategli",
            "Il candidato chiede il punto di vista dei collaboratori e li coinvolge quando deve prendere decisioni importanti",
            "Il candidato fa domande ai collaboratori per aiutarli a ragionare in modo autonomo senza dare subito la soluzione",
            "Il candidato è attento al benessere dei propri collaboratori",
            "Il candidato ha un dialogo con i collaboratori anche su aspetti personali tenendo conto dei momenti di criticità nella loro vita privata",
            "Il candidato si occupa del percorso di carriera dei suoi collaboratori",
            "Il candidato da feedback puntuali e costruttivi ai suoi collaboratori, sia per aiutarli a crescere che per dare rinforzi positivi",
            "Il candidato a fronte di errori commessi dai suoi collaboratori da feedback, considerando l'errore come occasione di crescita e sa comunicarlo in modo equilibrato senza perdere la calma",
            "Il candidato riesce a riconoscere le capacità dei collaboratori a dare il meglio di loro stessi spingendoli sempre più in alto permettendo a loro di imparare sperimentando cose nuove senza però portarli in una situazione di eccessivo disagio",
            "Il candidato celebra i successi del team o dei singoli collaboratori del suo team",
            "Il candidato mantiene la riservatezza rispetto alle confidenze che gli fanno i coillaboratori",
            "Il candidato è accessibile e dedica del tempo ad ascoltare le richieste dei suoi collaboratori",
            "Il candidato fa del suo meglio per mantenere le promesse fatte ai suoi collaboratori"
        ],
        "negativo": [
            "Il candidato è disinteressato ai problemi personali dei suoi collaboratori",
            "Il candidato non da feedback ai collaboratori",
            "Il candidato è orientato esclusivamente al raggiungimento degli obiettivi e non alla crescita dei suoi collaboratori",
            "Il candidato non ha mai tempo da dedicare ai suoi collaboratori",
            "Il candidato non crea le condizioni affinchè i collaboratori possano esprimere il loro punto di vista e il loro eventuale dissenso",
            "Il candidato non si fida dei suoi collaboratori e prende da solo le decisioni",
            "Il candidato aggredisce verbalmente i collaboratori quando commettono errori e crea le condizioni affinchè si sentano umiliati",
            "Il candidato a fronte di errori dei collaboratori perde la fiducia in loro",
            "Il candidato non celebra i risultati positivi ottenuti dal suo team o dei singoli collaboratori",
            "Il candidato trova subito le soluzioni senza aiutare i suoi collaboratori ad arrivarci da soli",
            "Il candidato non protegge il suo team a fronte di critiche da parte di persone esterne al suo team",
            "Il candidato non mantiene la riservatezza rispetto alle confidenze che gli fanno i suoi collaboratori",
            "Il candidato non si preoccupa di mantere la parola data ai suoi collaboratori"
        ]
    },
    "Leadership": { 
        "nome": "Leadership",
        "positivo": [
            "Il candidato si prende le responsabilità e non da la colpa agli altri quando ci sono problemi",
            "Guida le decisioni grazie alle sue competenze, ascoltando e facendo domande",
            "Ascolta i contributi degli altri e li coinvolge nelle decisioni",
            "Dopo attente riflessioni, sa prendere decisioni difficili che possono scontentare",
            "È coerente rispetto ai valori che dichiara",
            "Fa quello che dice",
            "Crea le condizioni affinchè tutti possano esprimere il loro dissenso senza paura",
            "Riesce ad affrontare temi scomodi portandoli sul tavolo perché vengano affrontati",
            "Esprime il suo punto di vista anche quando è in contrasto con quello dei superiori o dei peers",
            "È consapevole della difficoltà di prendere alcune decisioni collettivamente, per questo si confronta e coinvolge le persone in incontri individuali in modo che tutti siano pronti ad affrontare la discussione",
            "Riconosce i propri errori",
            "Comunica in modo chiaro a seconda delle differenze degli interlocutori",
            "Ispira e motiva gli altri",
            "Responsabilizza gli altri e li incoraggia",
            "Ha visione sul futuro e la comunica in modo chiaro",
            "Comunica forte energia e motivazione"
        ],
        "negativo": [
            "Impone le proprie idee e decisioni",
            "Scarica le responsabilità sugli altri a fronte di errori",
            "Non ammette i propri errori",
            "Critica colleghi o collaboratori con gli altri",
            "Non esprime il dissenso",
            "Non ha stabilità emotiva",
            "Non è interessato ad avere un proprio punto di vista rispetto agli obiettivi e alle attività che svolge, esegue senza riflettere e approfondire",
            "Non è motivato al raggiungimento degli obiettivi",
            "Non è chiaro nella comunicazione e non sa adattarla a seconda dei diversi interlocutori",
            "Non sa valutare i possibili rischi e non se ne preoccupa",
            "Demanda agli altri le decisioni difficili o impopolari",
            "Non ascolta",
            "È orientato solo al proprio avanzamento di carriera"
        ]
    },
    "Pensiero Analitico": { 
        "nome": "Pensiero Analitico",
        "positivo": [
            "È attento ai fatti e ai dati",
            "Prende decisioni basate su dati e fatti che ha analizzato",
            "È inquisitivo quindi fa domande per verificare le opinioni degli altri",
            "Ragiona in modo logico e strutturato",
            "È attento ai dettagli",
            "Scompone i problemi complessi in parti più semplici",
            "Usa prove, dati e fatti per sostenere le sue opinioni",
            "Prima di agire riflette, pianifica e valuta i rischi",
            "Riflette sull'essenza del problema",
            "Organizza il lavoro suo e degli altri",
            "Identifica gli schemi sottostanti alle situazioni e ai comportamenti"
        ],
        "negativo": [
            "Accetta le opinioni senza verificarle",
            "Prende decisioni basate sulle opinioni",
            "Non ricerca i dati alla base dei problemi",
            "Affronta i problemi senza entrare nei dettagli",
            "Si affida al proprio intuito",
            "È disordinato",
            "Non segue un percorso logico",
            "È più orientato all'azione che alla riflessione",
            "Non è attento ai dettagli",
            "Non sa fare connessioni tra le varie informazioni",
            "Non sa identificare i dati essenziali da considerare"
        ]
    },
}

TAG_A_CONCETTO = {
    "D": "Potenziale",
    "L": "Flessibilità",
    "I": "Pensiero Strategico",
    "A": "Stabilità Emotiva",
    "E": "Relazione",
    "F": "Coscienziositá",
    "G": "Comunicazione",
    "C": "People Management",
    "H": "Pensiero Analitico",
    "B": "Leadership"
}

class ValutazioneSpiegazione(dspy.Signature):
    testo_spiegazione = dspy.InputField(desc="Il testo della spiegazione da valutare")
    nodo_concetto = dspy.InputField(desc="Il nodo concetto che viene valutato")
    definizioni_positive = dspy.InputField(desc="Lista di definizioni positive per il concetto")
    definizioni_negative = dspy.InputField(desc="Lista di definizioni negative per il concetto")
    
    punteggio = dspy.OutputField(desc="Punteggio da 0 (totalmente negativo) a 10 (totalmente positivo) come numero intero. Ad esempio: 5 é da considerarsi come un punteggio 'nella media' ossia quasi vicino alla sufficienza, mentre 10 é un punteggio eccellente, perfetto.")
    corrispondenze_positive = dspy.OutputField(desc="Evidenze di definizioni positive nella spiegazione")
    corrispondenze_negative = dspy.OutputField(desc="Evidenze di definizioni negative nella spiegazione")
    giustificazione = dspy.OutputField(desc="Giustificazione per il punteggio. Per punteggi inferiori o uguali a 5, il giudizio dovrá valorizzare lievemente gli aspetti positivi e fare maggior focus sulla spiegazione delle aree di miglioramento.")

class ValutatoreSpiegazione(dspy.Module):
    def __init__(self):
        super().__init__()
        self.valutatore = dspy.ChainOfThought(ValutazioneSpiegazione)
    
    def forward(self, testo_spiegazione, chiave_nodo_concetto):
        if chiave_nodo_concetto not in NODI_CONCETTO:
            return {
                "nome": "Concetto Sconosciuto",
                "punteggio": 0,
                "corrispondenze_positive": [],
                "corrispondenze_negative": [],
                "giustificazione": "Impossibile mappare a un nodo concetto valido"
            }
            
        info_nodo = NODI_CONCETTO[chiave_nodo_concetto]
        definizioni_positive = info_nodo["positivo"]
        definizioni_negative = info_nodo["negativo"]
        
        risultato = self.valutatore(
            testo_spiegazione=testo_spiegazione,
            nodo_concetto=info_nodo["nome"],
            definizioni_positive=definizioni_positive,
            definizioni_negative=definizioni_negative
        )
        
        try:
            punteggio = int(risultato.punteggio)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert score '{risultato.punteggio}' to integer for {info_nodo['nome']}. Defaulting to 0.")
            punteggio = 0
            
        return {
            "nome": info_nodo["nome"],
            "punteggio": punteggio,
            "corrispondenze_positive": risultato.corrispondenze_positive,
            "corrispondenze_negative": risultato.corrispondenze_negative,
            "giustificazione": risultato.giustificazione
        }

class FirmaSpiegazioneNodo(dspy.Signature):
    nome_concetto = dspy.InputField(desc="The name of the concept node")
    punteggio_medio = dspy.InputField(desc="The average score for this concept node")
    corrispondenze_positive = dspy.InputField(desc="Evidence of positive aspects found in the evaluations")
    corrispondenze_negative = dspy.InputField(desc="Evidence of negative aspects found in the evaluations")
    
    spiegazione = dspy.OutputField(desc="A concise explanation in Italian explaining the score for this concept node")

class ValutazioneFinaleSignature(dspy.Signature):
    valutazioni_nodo = dspy.InputField(desc="Evaluations of each concept node")
    
    spiegazioni_nodo = dspy.OutputField(desc="List of explanations for each node in Italian")

class GeneratoreSpiegazioneNodo(dspy.Module):
    def __init__(self):
        super().__init__()
        self.spiegatore = dspy.ChainOfThought(FirmaSpiegazioneNodo)
    
    def forward(self, nome_concetto, punteggio_medio, giustificazioni, corrispondenze_positive, corrispondenze_negative):
        risultato = self.spiegatore(
            nome_concetto=nome_concetto,
            punteggio_medio=punteggio_medio,
            corrispondenze_positive=corrispondenze_positive,
            corrispondenze_negative=corrispondenze_negative
        )
        
        return risultato.spiegazione

class ValutazioneFinale(dspy.Module):
    def __init__(self):
        super().__init__()
        self.valutatore = dspy.ChainOfThought(ValutazioneFinaleSignature)
        self.valutatore_spiegazione = ValutatoreSpiegazione()
        self.spiegatore_nodo = GeneratoreSpiegazioneNodo()
    
    def valuta_spiegazioni(self, valutazioni):
        risultati = {}
        
        for valutazione in valutazioni:
            if "ID Regola" not in valutazione or "Spiegazione" not in valutazione:
                continue
                
            id_regola = valutazione["ID Regola"]
            spiegazione = valutazione["Spiegazione"]
            
            chiave_concetto = None
            for prefisso, concetto in TAG_A_CONCETTO.items():
                if id_regola.startswith(prefisso):
                    chiave_concetto = concetto
                    break
            
            if chiave_concetto:
                try:
                    risultato = self.valutatore_spiegazione(spiegazione, chiave_concetto)
                    
                    risultati[id_regola] = {
                        "id_regola": id_regola,
                        "concetto": risultato["nome"],
                        "punteggio": risultato["punteggio"],
                        "corrispondenze_positive": risultato["corrispondenze_positive"],
                        "corrispondenze_negative": risultato["corrispondenze_negative"],
                        "giustificazione": risultato["giustificazione"],
                        "spiegazione_originale": spiegazione
                    }
                except Exception as e:
                    print(f"Error scoring explanation for rule {id_regola}: {str(e)}")
        
        return risultati
    
    def aggrega_punteggi_per_concetto(self, spiegazioni_valutate):
        punteggi_concetto = {}
        
        for id_regola, risultato in spiegazioni_valutate.items():
            concetto = risultato["concetto"]
            punteggio = risultato["punteggio"]
            
            if concetto not in punteggi_concetto:
                punteggi_concetto[concetto] = {
                    "punteggi": [],
                    "punteggio_totale": 0,
                    "conteggio": 0,
                    "punteggio_medio": 0,
                    "giustificazioni": [],
                    "corrispondenze_positive": [],
                    "corrispondenze_negative": []
                }
            
            punteggi_concetto[concetto]["punteggi"].append(punteggio)
            punteggi_concetto[concetto]["punteggio_totale"] += punteggio
            punteggi_concetto[concetto]["conteggio"] += 1
            punteggi_concetto[concetto]["giustificazioni"].append(risultato["giustificazione"])
            
            if risultato["corrispondenze_positive"]:
                punteggi_concetto[concetto]["corrispondenze_positive"].append(risultato["corrispondenze_positive"])
            if risultato["corrispondenze_negative"]:
                punteggi_concetto[concetto]["corrispondenze_negative"].append(risultato["corrispondenze_negative"])
        
        for concetto, dati in punteggi_concetto.items():
            if dati["conteggio"] > 0:
                dati["punteggio_medio"] = dati["punteggio_totale"] / dati["conteggio"]
        
        return punteggi_concetto
    
    def genera_valutazione_finale(self, punteggi_concetto):
        giudizio_finale = []
        
        for nome_concetto, dati in punteggi_concetto.items():
            spiegazione = self.spiegatore_nodo(
                nome_concetto=nome_concetto,
                punteggio_medio=dati["punteggio_medio"],
                giustificazioni=dati["giustificazioni"],
                corrispondenze_positive=dati["corrispondenze_positive"],
                corrispondenze_negative=dati["corrispondenze_negative"]
            )
            
            punteggio_medio = round(dati["punteggio_medio"])
            
            giudizio_finale.append({
                "nodo": nome_concetto,
                "punteggio": punteggio_medio,
                "spiegazione": spiegazione
            })
        
        return giudizio_finale
    
    def forward(self, valutazioni):
        spiegazioni_valutate = self.valuta_spiegazioni(valutazioni)
        punteggi_concetto = self.aggrega_punteggi_per_concetto(spiegazioni_valutate)
        return self.genera_valutazione_finale(punteggi_concetto)


def estrai_oggetti_json(testo):
    oggetti = []
    righe_json = []
    in_json = False
    
    for riga in testo.split('\n'):
        riga = riga.strip()
        if not riga:
            continue
            
        if riga.startswith('{'):
            in_json = True
            righe_json = [riga]
        elif riga.startswith('}') and in_json:
            righe_json.append(riga)
            stringa_json = ' '.join(righe_json)
            try:
                obj = json.loads(stringa_json)
                oggetti.append(obj)
            except json.JSONDecodeError:
                print(f"Error parsing JSON: {stringa_json[:100]}...")
            in_json = False
        elif in_json:
            righe_json.append(riga)
    
    return oggetti


def leggi_dati_valutazione(percorso_file):
    try:
        with open(percorso_file, "r", encoding="utf-8") as file:
            contenuto = file.read()
            
        indici_inizio = [i for i, char in enumerate(contenuto) if char == '{']
        
        valutazioni = []
        for indice_inizio in indici_inizio:
            conteggio_parentesi = 1
            indice_fine = indice_inizio + 1
            
            while conteggio_parentesi > 0 and indice_fine < len(contenuto):
                if contenuto[indice_fine] == '{':
                    conteggio_parentesi += 1
                elif contenuto[indice_fine] == '}':
                    conteggio_parentesi -= 1
                indice_fine += 1
            
            if conteggio_parentesi == 0:
                stringa_json = contenuto[indice_inizio:indice_fine]
                try:
                    obj = json.loads(stringa_json)
                    valutazioni.append(obj)
                except json.JSONDecodeError:
                    json_pulito = stringa_json.replace('\n', ' ').replace('    ', ' ')
                    try:
                        obj = json.loads(json_pulito)
                        valutazioni.append(obj)
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON: {stringa_json[:100]}...")
        
        if not valutazioni:
            print("Using fallback parsing method...")
            valutazioni = estrai_oggetti_json(contenuto)
            
        return valutazioni
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []


def main():
    file_valutazione = "interview_evaluation.txt"
    file_output = "giudizio_finale.json"
    
    print(f"Looking for evaluation file: {file_valutazione}")
    if not os.path.exists(file_valutazione):
        print(f"Error: {file_valutazione} does not exist.")
        return
    
    valutazioni = leggi_dati_valutazione(file_valutazione)
    if not valutazioni:
        print("No evaluations could be extracted from the file.")
        return
    
    if len(valutazioni) == 1 and "Detailed Evaluations" in valutazioni[0]:
        valutazioni = valutazioni[0]["Detailed Evaluations"]
    
    print(f"Successfully read {len(valutazioni)} evaluations")
    
    try:
        valutazione_finale = ValutazioneFinale()
        giudizio_finale = valutazione_finale.forward(valutazioni)
        print("Successfully generated judgment")
    except Exception as e:
        import traceback
        print(f"Error generating judgment: {str(e)}")
        traceback.print_exc()
        return
    
    try:
        with open(file_output, "w", encoding="utf-8") as f:
            json.dump(giudizio_finale, f, ensure_ascii=False, indent=2)
        print(f"Judgment has been saved to '{file_output}'")
    except Exception as e:
        print(f"Error saving judgment to file: {str(e)}")


if __name__ == "__main__":
    main()