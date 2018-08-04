# This file takes the sentence-level distances produced by 03-compute_wmd.py
# and sums them to the chapter and document level (giving chapter- and
# document-level Translation Mover's Distance scores)
import os

import joblib
import numpy as np

data_loc = os.path.join("..","Output")
data_file = "fowkes.pkl"

def computeChapterScores():
    # Load the TMDs
    ch_scores = []
    pickle_filename = os.path.join(data_loc, data_file)
    score_data = joblib.load(pickle_filename)
    for ch_data in score_data:
        all_section_scores = []
        for section_data in ch_data:
            # The actual score is in slot 3
            cur_score = section_data[3]
            all_section_scores.append(cur_score)
        # Now we have to clean the inf's
        non_inf_scores = [score for score in all_section_scores if score != float("inf")]
        avg_score = np.mean(non_inf_scores)
        cleaned_scores = [score if score != float("inf") else avg_score for score in all_section_scores]
        summed_scores = sum(cleaned_scores)
        ch_scores.append(summed_scores)
    # Now print and then export csv
    print("Scores for " + str(data_file))
    for ch_score in ch_scores:
        print(ch_score)

def main():
    computeChapterScores()

if __name__ == "__main__":
    main()