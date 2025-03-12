import json
import re
import argparse
import random
from collections import defaultdict

def generate_ner_json(input_sample_path, glossary_path, output_json_path, min_sentences=1000, max_sentences=2000):
    # 🔹 Cargar los términos del glosario y ordenarlos por longitud (de mayor a menor)
    with open(glossary_path, "r", encoding="utf-8") as file:
        glossary_terms = sorted(set(term.strip() for term in file if term.strip()), key=len, reverse=True)
    
    # 🔹 Cargar oraciones y mapearlas a términos del glosario
    sentences_by_term = defaultdict(list)
    all_sentences = []

    with open(input_sample_path, "r", encoding="utf-8") as file:
        for sentence in file:
            sentence = sentence.strip()
            matched_terms = []
            term_spans = []
            
            # Paso 1: Anotar términos más largos primero
            for term in glossary_terms:
                for match in re.finditer(rf"\b{re.escape(term)}\b", sentence):
                    start, end = match.span()
                    # Evitar solapamientos y permitir solo términos largos primero
                    if not any(s <= start < e or s < end <= e for s, e in term_spans):
                        term_spans.append((start, end))
                        matched_terms.append((start, end, "TERM"))
            
            # Paso 2: Anotar 'corpus' solo si aparece solo y no dentro de otro término
            if re.search(r"\bcorpus\b", sentence):
                start = sentence.find("corpus")
                end = start + len("corpus")
                if not any(s <= start < e or s < end <= e for s, e in term_spans):
                    matched_terms.append((start, end, "TERM"))
            
            # Paso 3: Anotar 'type-token ratio' antes que 'type' o 'token'
            for match in re.finditer(r"\btype-token ratio\b", sentence):
                start, end = match.span()
                if not any(s <= start < e or s < end <= e for s, e in term_spans):
                    term_spans.append((start, end))
                    matched_terms.append((start, end, "TERM"))
            
            # Paso 4: Anotar 'type' y 'token' solo si no forman parte de 'type-token ratio'
            for match in re.finditer(r"\btype\b", sentence):
                start, end = match.span()
                after_word = sentence[end:end+3].strip().lower()
                if after_word != "of" and not any(s <= start < e or s < end <= e for s, e in term_spans):
                    matched_terms.append((start, end, "TERM"))
            
            for match in re.finditer(r"\btoken\b", sentence):
                start, end = match.span()
                if not any(s <= start < e or s < end <= e for s, e in term_spans):
                    matched_terms.append((start, end, "TERM"))
            
            if matched_terms:
                all_sentences.append(sentence)
                for _, _, term_label in matched_terms:
                    sentences_by_term[term_label].append(sentence)
    
    # 🔹 Asegurar que cada término tenga al menos 4 oraciones
    selected_sentences = set()
    for term, sentences in sentences_by_term.items():
        if len(sentences) >= 4:
            selected_sentences.update(random.sample(sentences, 4))  # Tomar 4 oraciones si hay muchas
        else:
            selected_sentences.update(sentences)  # Si hay menos de 4, tomar todas
    
    # 🔹 Si el número de oraciones es menor al mínimo deseado, añadir más balanceadamente
    if len(selected_sentences) < min_sentences:
        remaining_sentences = list(set(all_sentences) - selected_sentences)
        additional_sentences = random.sample(remaining_sentences, min(min_sentences - len(selected_sentences), len(remaining_sentences)))
        selected_sentences.update(additional_sentences)
    
    # 🔹 Si el número de oraciones es muy alto, reducirlo de forma balanceada
    if len(selected_sentences) > max_sentences:
        print(f"Reduciendo de {len(selected_sentences)} a {max_sentences} oraciones usando muestreo estratificado.")
        selected_sentences = random.sample(list(selected_sentences), max_sentences)
    
    # 🔹 Generar anotaciones para spaCy
    annotated_data = []
    for sentence in selected_sentences:
        entities = []
        term_spans = []
        
        for term in glossary_terms:
            for match in re.finditer(rf"\b{re.escape(term)}\b", sentence):
                start, end = match.span()
                if not any(s <= start < e or s < end <= e for s, e in term_spans):
                    term_spans.append((start, end))
                    entities.append([start, end, "TERM"])
        
        if entities:
            annotated_data.append({"text": sentence, "entities": entities})
    
    # 🔹 Guardar en formato JSON
    with open(output_json_path, "w", encoding="utf-8") as file:
        json.dump(annotated_data, file, indent=4, ensure_ascii=False)
    
    print(f"\n📂 Dataset anotado guardado en: {output_json_path}")
    print(f"🔹 Total de oraciones anotadas: {len(annotated_data)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar dataset anotado en JSON para fine-tuning de NER en spaCy")
    parser.add_argument("--input-sample", type=str, required=True, help="Archivo con oraciones extraídas")
    parser.add_argument("--glossary", type=str, required=True, help="Archivo del glosario base (cl_glossary.txt)")
    parser.add_argument("--output-json", type=str, required=True, help="Archivo de salida en formato JSON")
    parser.add_argument("--min-sentences", type=int, default=1000, help="Número mínimo de oraciones en el dataset")
    parser.add_argument("--max-sentences", type=int, default=2000, help="Número máximo de oraciones en el dataset")
    
    args = parser.parse_args()
    generate_ner_json(args.input_sample, args.glossary, args.output_json, args.min_sentences, args.max_sentences)
