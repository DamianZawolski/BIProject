import csv

# Nazwa pliku wynikowego
output_file = "tripdata_connected.csv"

# Lista plików wejściowych
input_files = ["oct2021_tripdata.csv", "nov2021_tripdata.csv", "dec2021_tripdata.csv", "jan2022_tripdata.csv", "jan2022_tripdata.csv",
               "feb2022_tripdata.csv", "mar2022_tripdata.csv", "apr2022_tripdata.csv", "may2022_tripdata.csv", "jun2022_tripdata.csv",
               "jul2022_tripdata.csv", "sept2022_tripdata.csv"]

# Otwieranie pliku wynikowego w trybie zapisu
with open(output_file, "w", newline="") as output_csv:
    writer = csv.writer(output_csv)

    # Przetwarzanie każdego pliku wejściowego
    for i, input_file in enumerate(input_files):
        with open(input_file, "r", newline="") as input_csv:
            reader = csv.reader(input_csv)

            # Pomijanie nagłówka dla wszystkich plików oprócz pierwszego
            if i > 0:
                next(reader)

            # Zapisywanie danych do pliku wynikowego
            for row in reader:
                writer.writerow(row)

print("Pliki zostały połączone.")