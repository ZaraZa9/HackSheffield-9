from pymongo import MongoClient

with open("extracted_data_set.txt", "r") as file:
    lines = file.read().splitlines()

CONNECTION_STRING = "mongodb+srv://weitongsun01:qDUa12YFsLz1NCgd@cluster0.hxmx9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(CONNECTION_STRING)

try:
    db = client["brain_rot"]
    collection = db["brain_rot_collection"]
    print("Connected to the database.")
    print(collection.estimated_document_count())

    def get_decade(year):
        return f"{(year // 10) * 10}-{(year // 10) * 10 + 9}"

    for index in range(0, len(lines)-1, 5):
        word = lines[index].strip()
        year = int((lines[index + 1].strip()).split(":")[1].strip())
        word_type = lines[index + 2].strip().split(":")[1].strip()
        synonym = lines[index + 3].strip().split(":")[1].strip()
        definition = lines[index + 4].strip().split(":")[1].strip()

        print(f"WORD '{word}' for YEAR {year} with type '{word_type}' and definition '{definition}' and synonyms '{synonym}'.")

        decade = get_decade(year)

        document = collection.find_one({"decade": decade})

        if document:
            print(f"Document for decade {decade} exists. Preparing to update with word '{word}'.")
            collection.update_one(
                {"decade": decade},
                {"$push": {"words": {"word": word, "type": word_type, "definition": definition, "synonym": synonym}}}
            )
        else:
            print(f"Document for decade {decade} does not exist. Preparing to insert new document with word '{word}'.")
            collection.insert_one({
                "decade": decade,
                "words": [{"word": word, "type": word_type, "definition": definition, "synonym": synonym}]
            })

    print("Operation complete.")

finally:
    client.close()