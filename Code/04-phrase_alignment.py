# Takes the aligned sentences from hunalign and produces an even more
# fine-grained alignment of phrases [sections of sentences] using the
# Berkeley Aligner
import os

import joblib

data_loc = os.path.join("..","Output")

def main():
    # Load the statement-aligned chapters
    data_file = os.path.join(data_loc, "capital.pkl")
    ch_data = joblib.load(data_file)
    print(ch_data[0])

if __name__ == "__main__":
    main()