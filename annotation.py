import re
import json
import argparse

def annotate_for_spacy(input_file, glossary_file, output_file):
    # Cargar términos del glosario eliminando espacios en blanco y líneas vacías
    with open(glossary_file, "r", encoding="utf-8") as file:
        glossary_terms = [term.strip() for term in file.readlines() if term.strip()]

    # Ordenar términos por longitud para priorizar términos compuestos
    glossary_terms.sort(key=len, reverse=True)

    # Leer las oraciones del archivo de entrada
    with open(input_file, "r", encoding="utf-8") as file:
        sentences = [line.strip() for line in file.readlines() if line.strip()]

    # Función para anotar términos en una oración con índices
    def annotate_entities(sentence, glossary):
        entities = []
        for term in glossary:
            for match in re.finditer(rf"\b{re.escape(term)}\b", sentence):
                start, end = match.span()
                entities.append((start, end, "TERM"))
        return (sentence, {"entities": entities}) if entities else None  # Solo devolver si hay entidades

    # Aplicar anotación a cada oración
    annotated_data = [annotate_entities(sent, glossary_terms) for sent in sentences]
    annotated_data = [entry for entry in annotated_data if entry is not None]  # Filtrar None

    # Guardar en formato JSON para spaCy
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(annotated_data, file, indent=4, ensure_ascii=False)

    print(f"\n✅ Se han anotado {len(annotated_data)} oraciones con términos del glosario.")
    print(f"📂 Archivo guardado en: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar anotaciones NER para spaCy.")
    parser.add_argument("--input-file", type=str, required=True, help="Archivo con oraciones a anotar")
    parser.add_argument("--glossary", type=str, required=True, help="Archivo con términos del glosario")
    parser.add_argument("--output-file", type=str, default="ner_annotations.json", help="Archivo JSON de salida")

    args = parser.parse_args()
    annotate_for_spacy(args.input_file, args.glossary, args.output_file)
