import os
import spacy
import re
from collections import defaultdict

# Cargar el modelo spaCy con transformers
nlp = spacy.load("en_core_web_trf")

# Ruta de la carpeta con los textos
text_folder = "/content/nterm/original_texts/"
glossary_path = "/content/terment/cl_glossary"

# Cargar términos del glosario eliminando espacios en blanco y líneas vacías
with open(glossary_path, "r", encoding="utf-8") as file:
    glossary_terms = [term.strip() for term in file.readlines() if term.strip()]

# Ordenar términos por longitud para priorizar términos compuestos
glossary_terms.sort(key=len, reverse=True)

# Diccionario para almacenar oraciones por término
sentences_by_term = defaultdict(list)

# Procesar cada archivo en la carpeta
for file_name in os.listdir(text_folder):
    file_path = os.path.join(text_folder, file_name)
    
    # Leer el contenido del archivo
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    
    # Procesar con spaCy para segmentar en oraciones
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]  # Extraer oraciones y limpiar espacios
    
    # Filtrar oraciones bien formadas (empiezan con mayúscula y terminan en punto)
    valid_sentences = [sent for sent in sentences if re.match(r"^[A-Z].*\.$", sent)]
    
    # Filtrar oraciones que contienen términos del glosario
    for sentence in valid_sentences:
        for term in glossary_terms:
            if re.search(rf"\b{re.escape(term)}\b", sentence):  # Coincidencia exacta de palabra completa
                sentences_by_term[term].append(sentence)

# Verificar la cantidad de oraciones recolectadas
print(f"\n🔹 Se han extraído {sum(len(s) for s in sentences_by_term.values())} oraciones en total.")
print(f"🔹 Número de términos en el glosario: {len(glossary_terms)}")

# Asegurar que cada término aparece al menos 4 veces
selected_sentences = set()
for term, sentences in sentences_by_term.items():
    if len(sentences) >= 4:
        selected_sentences.update(sentences[:4])  # Tomar 4 oraciones por término
    else:
        selected_sentences.update(sentences)  # Tomar todas si hay menos de 4

# Mostrar algunas oraciones seleccionadas
print("\nEjemplo de oraciones seleccionadas:")
for i, sent in enumerate(list(selected_sentences)[:5]):
    print(f"{i+1}. {sent}")
