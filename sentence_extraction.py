import os
import spacy
import re
import argparse
import time
from collections import defaultdict

def extract_sentences(text_folder, glossary_path, exclude_path):
    start_time = time.time()
    print("\n🔄 Cargando el modelo de spaCy...")
    nlp = spacy.load("en_core_web_trf")

    # Cargar términos del glosario
    print("\n📖 Cargando términos del glosario...")
    with open(glossary_path, "r", encoding="utf-8") as file:
        glossary_terms = set(term.strip() for term in file if term.strip())

    # Cargar términos a excluir
    print("🚫 Cargando términos a excluir...")
    with open(exclude_path, "r", encoding="utf-8") as file:
        exclude_terms = set(term.strip() for term in file if term.strip())

    # Filtrar términos: dejar solo los que están en el glosario pero NO en silver_standard
    filtered_terms = sorted(glossary_terms - exclude_terms, key=len, reverse=True)
    print(f"✅ {len(filtered_terms)} términos filtrados para la extracción.")

    # Diccionario para almacenar oraciones por término
    sentences_by_term = defaultdict(list)

    total_sentences_tokenized = 0  # Contador de oraciones tokenizadas

    print("\n📂 Procesando archivos de la carpeta...")

    # Procesar cada archivo en la carpeta
    for file_name in os.listdir(text_folder):
        file_path = os.path.join(text_folder, file_name)
        print(f"   📜 Procesando: {file_name}")

        # Leer el contenido del archivo
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        # Procesar con spaCy para tokenizar y segmentar en oraciones
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        total_sentences_tokenized += len(sentences)  # Contar oraciones analizadas

        # Filtrar solo oraciones bien formadas (mayúscula inicial y punto final)
        valid_sentences = [sent for sent in sentences if re.match(r"^[A-Z].*\.$", sent)]

        # Extraer todas las oraciones que contengan los términos filtrados y NO los excluidos
        for sentence in valid_sentences:
            for term in filtered_terms:
                if re.search(rf"\b{re.escape(term)}\b", sentence):  # Coincidencia exacta de palabra completa
                    contains_excluded_term = any(re.search(rf"\b{re.escape(excluded_term)}\b", sentence) for excluded_term in exclude_terms)
                    
                    if not contains_excluded_term:  # Si NO contiene términos excluidos, agregar la oración
                        sentences_by_term[term].append(sentence)

    # Contar las oraciones extraídas
    total_sentences_extracted = sum(len(s) for s in sentences_by_term.values())

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\n🔹 Se han tokenizado un total de {total_sentences_tokenized} oraciones.")
    print(f"🔹 Se han extraído {total_sentences_extracted} oraciones con los términos filtrados.")
    print(f"⏳ Tiempo total de procesamiento: {elapsed_time:.2f} segundos.")

    # Guardar las oraciones en un archivo de salida
    output_path = os.path.join(text_folder, "oraciones_filtradas.txt")
    with open(output_path, "w", encoding="utf-8") as file:
        for term, sentences in sentences_by_term.items():
            for sent in sentences:
                file.write(f"{sent}\n")

    print(f"\n📂 Oraciones guardadas en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraer oraciones con términos filtrados")
    parser.add_argument("--text-folder", type=str, required=True, help="Carpeta que contiene los textos")
    parser.add_argument("--glossary", type=str, required=True, help="Archivo del glosario base (cl_glossary.txt)")
    parser.add_argument("--exclude", type=str, required=True, help="Archivo con términos a excluir (silver_standard.txt)")

    args = parser.parse_args()
    extract_sentences(args.text_folder, args.glossary, args.exclude)
