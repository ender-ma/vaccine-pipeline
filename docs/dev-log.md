I find this very boaring comapaired with all the other cool things i'll be doing throughout.
So things will be kept simple and short. I think that's fair.

WEEK TWO
1. Why did the first run fail even though the file test.fasta existed on your computer?
2. What does -resume compare to decide whether to skip a process?
3. Why does output: path matter more than output: stdout in a chain?

ANSWERS AND CORRECTIONS.
1. Mostly right, with one refinement. The file existed, but the path written in the script (test.fasta) didn't point to where it actually was, relative to the folder you launched from. Moving it wasn't the whole fix. Updating the path in the script to test_data/test.fasta was. Nextflow also created a broken shortcut (symlink) inside work/, which is why the error said "cannot open file" rather than "path is wrong". The lesson: a path only means something relative to where you run the command.

2. This describes what resume does, not what it compares. You're right that it avoids restarting from the beginning. But the question was how it decides to skip. It builds a fingerprint (hash) for each process from three things:

the contents of the input files,
the script/command,
the parameters.

If all three match a previous successful run, the process is skipped (cached). If any changed, that process reruns, along with everything downstream of it. That's what you saw on Day 5 when adding sequence_4 triggered a rerun. Notice that it also isn't really about "where it stopped": it works even if the previous run finished successfully.

3. Right. To make it complete: a saved file can be handed to the next process as its input, while printed text can't. That's what made EXTRACT_HEADERS → UNIQUE_HEADERS possible.

WEEK THREE

