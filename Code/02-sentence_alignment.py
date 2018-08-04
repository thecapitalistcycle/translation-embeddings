# Uses the LF Align command-line interface to do the batch alignment of each
# chapter [and thus has to be run on Windows :(] [also you have to DISABLE
# DROPBOX!!!]

import glob
import os
import subprocess
import shutil
import codecs
from pathlib import Path

import tr_globals

#en_folder = "FirstEnglishEdition"
en_folder = "Fowkes"

en_path = os.path.join("..","Texts",en_folder,"cleaned")
de_path = os.path.join("..","Texts","ThirdGermanEdition","cleaned")

cmdline_template = "LF_aligner_4.1.exe --filetype=\"t\"" \
                   " --infiles=\"{en_file}\",\"{de_file}\"" \
                   " --outfile=\"{out_file}\" --languages=\"en\",\"de\"" \
                   " --segment=\"y\" --review=\"n\" --tmx=\"n\""

#cmdline_map = {'filetype':'"t"','infiles'}

def quotes(the_string):
    return '"' + the_string + '"'

def outputLogs(align_logs):
    with codecs.open("./logs/align_log.txt", "wb", "utf-8") as f:
        for log_num, cur_log in enumerate(align_logs):
            # (log_num starts at 0, whereas chapter numbers start at 1)
            ch_num = log_num + 1
            f.write("Chapter #" + str(ch_num))
            f.write("------------")
            f.write(str(cur_log))


def doSentenceAlign():
    align_logs = []
    # First we have to construct the command-line argument we're going to pass
    # into LF Align
    en_glob = os.path.join(en_path,"*.txt")
    print(en_glob)
    en_filepaths = glob.glob(en_glob)
    de_filepaths = glob.glob(os.path.join(de_path,"*.txt"))
    for path_num, cur_en_filepath in enumerate(en_filepaths):
        print("Processing chapter #" + str(path_num))
        en_filename, en_prefix, en_file_lang, en_ch_num = tr_globals.getFileInfo(cur_en_filepath)
        cur_de_filepath = de_filepaths[path_num]
        de_filename, de_prefix, de_file_lang, de_ch_num = tr_globals.getFileInfo(cur_de_filepath)

        # See if an "Aligned" folder exists. If not, make it
        aligned_dir = os.path.join("..","Texts","Aligned")
        if not os.path.isdir(aligned_dir):
            os.mkdir(aligned_dir)

        # Make the blank text file that LF_align will write into
        output_filename = "ch" + str(en_ch_num).zfill(2) + ".align.txt"
        output_filepath = os.path.join("..","Texts","Aligned",output_filename)
        # Check if it already exists, delete if so
        if os.path.isfile(output_filepath):
            os.remove(output_filepath)
        Path(output_filepath).touch()

        ## format the command
        ## OLD: trying to format into subproc.Popen() format...
        #infiles = quotes(cur_en_path) + "," + quotes(cur_de_path)
        #languages = quotes("en") + "," + quotes("de")
        #subproc_list = ['LF_aligner_4.1.exe','--filetype',quotes("t"),'--infiles',infiles,
        #                '--outfiles',quotes(output_path),'--languages',languages,
        #                '--segment',quotes("y"),'--review',quotes("n"),'--tmx',quotes("n")]
        #print(subproc_list)
        ## New: just use subprocess.call()
        cur_cmd = cmdline_template.format(en_file=cur_en_filepath,de_file=cur_de_filepath,out_file=output_filepath)

        # Temporarily change into the directory of LF_aligner, run the command,
        # then change back
        os.chdir(os.path.join("..","SentenceAligner"))
        result = subprocess.check_output(cur_cmd,shell=True)
        align_logs.append(result)
        os.chdir(os.path.join("..","Code"))
    # Done with for loop - just output the alignment logs to a file
    outputLogs(align_logs)
    # Last thing: delete the stupid align_<date> folder that it creates,
    # that we don't need (because we set the output file)
    align_folders = glob.glob(os.path.join("..","Texts","Aligned","align_*"))
    for cur_folder in align_folders:
        shutil.rmtree(cur_folder)


def main():
    doSentenceAlign()

if __name__ == "__main__":
    main()